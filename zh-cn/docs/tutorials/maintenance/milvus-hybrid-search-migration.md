---
sidebar_position: 320
title: "Milvus Native Hybrid Search Migration"
---

Open WebUI 在 Milvus 2.5 及更高版本上使用原生混合搜索。旧版本 Milvus 中的数据会在首次启动时迁移一次。不会重新做嵌入：Open WebUI 把每个集合连同其已有的向量和文本复制到一个新集合中，再由 Milvus 根据存储的文本构建关键词索引。视数据量大小，这一步可能耗时数分钟到数小时。

:::danger 请先备份
升级前请备份你的 Milvus 数据，并确保 Milvus 有足够的可用磁盘空间容纳完整的一份副本。完整检查清单参见[环境变量参考中的 Milvus 警告](/reference/env-configuration#milvus)。
:::

## 预期会发生什么 {#what-to-expect}

- 迁移在 [`ENABLE_DB_MIGRATIONS`](/reference/env-configuration#enable_db_migrations) 开启时执行，这也是默认设置。在低于 2.5 的 Milvus 上它会被跳过，混合搜索仍按此前的方式工作。复制随后会在 Milvus 升级到 2.5 之后的首次 Open WebUI 启动时执行，因此请同样提前备份并规划该次启动的停机时间。
- **迁移完成之前，Open WebUI 不会处理任何请求。**
- 日志在开始时会显示 `Migrating N Milvus collections to native hybrid search.`，完成时显示 `Migrated N Milvus collections to native hybrid search.`。其间不会有任何日志输出，因此请使用下方的[监控脚本](#monitoring-progress)跟踪进度。
- **迁移期间不要重启 Open WebUI。** 中断的运行会在下次启动时丢弃其部分副本，并从零重新开始。
- 只有在所有副本都成功之后，你原有的集合才会被删除。如果某个副本失败，日志会显示 `Milvus migration to native hybrid search failed, all collections are kept unchanged.`，Open WebUI 会继续使用原有集合。
- 如果你运行多个 Open WebUI 实例，升级时只启动其中一个，其余实例等出现 `Migrated` 那一行之后再启动。
- 迁移完成后，只要 **Settings > Admin > Documents** 中开启了 **Hybrid Search**，混合搜索就会由 Milvus 自行执行。开启 **Enrich Hybrid Search Text**（或 [`ENABLE_RAG_HYBRID_SEARCH_ENRICHED_TEXTS`](/reference/env-configuration#enable_rag_hybrid_search_enriched_texts)）则会继续使用 Open WebUI 自己的关键词搜索。

## 参考速度 {#reference-speeds}

| 硬件 | 数据量 | 耗时 |
|----------|------|------|
| 最新一代 Intel Xeon（分配 12 核）、250 GB 内存、局域网内高速 NVMe | 910 万个分块 | 约 50 分钟 |
| AMD Ryzen 7 8845HS、28 GB 内存、普通 NVMe | 200 GB | 约 3 小时 |

请据此规划停机时间。只要存储和内存跟得上，迁移的瓶颈就在 CPU：Milvus 需要为每个复制的行构建向量索引、关键词索引和 BM25 统计信息。为迁移给 Milvus 更多 CPU 核心可以加快速度。

## 监控进度 {#monitoring-progress}

下面的脚本可以显示迁移进度。它可以在任何能访问 Milvus 的机器上运行，每分钟打印一行，且只读取元数据，因此不会拖慢迁移速度。

它使用 Milvus REST API，Milvus standalone 与集群版本都提供该 API。Milvus Lite 没有 REST API，因此该脚本无法与其配合使用。

1. 把脚本保存为 `milvus-progress.sh`。
2. 如果 Milvus 需要认证，把 `TOKEN` 设为你的 `MILVUS_TOKEN` 值；否则留空。
3. 在迁移开始前或进行中启动它，因为它会在启动时统计总行数。传入你的 Milvus 地址：

```bash
bash milvus-progress.sh http://milvus-host:19530
```

```bash title="milvus-progress.sh"
#!/bin/bash
# Leave TOKEN empty if Milvus has no authentication. Change PREFIX only if you run Milvus multitenancy mode with a custom MILVUS_COLLECTION_PREFIX.
TOKEN='user:password'
PREFIX='open_webui'
URL="${1:-http://localhost:19530}/v2/vectordb"

auth=()
[ -n "$TOKEN" ] && auth=(-H "Authorization: Bearer $TOKEN")
post() { curl -s -X POST "$URL/$1" -H "Content-Type: application/json" "${auth[@]}" -d "$2"; }
field() { grep -o "\"$1\":[0-9]*" | head -1 | cut -d: -f2; }
rows() { post collections/get_stats "{\"collectionName\":\"$1\"}" | field rowCount; }
names() { post collections/list '{}' | grep -o "\"${PREFIX}_[^\"]*\"" | tr -d '"'; }
percent() { echo "$1/$2 ($((100 * $1 / ($2 ? $2 : 1)))%)"; }
index_progress() {
  local indexed=0 total=0 response collection_indexed collection_total
  for name in $2; do
    response=$(post indexes/describe "{\"collectionName\":\"$name\",\"indexName\":\"$1\"}")
    collection_indexed=$(field indexedRows <<<"$response")
    collection_total=$(field totalRows <<<"$response")
    indexed=$((indexed + ${collection_indexed:-0}))
    total=$((total + ${collection_total:-0}))
  done
  percent $indexed $total
}

originals=$(names | grep -v '_bm25_staging$')
total_rows=0
for name in $originals; do total_rows=$((total_rows + $(rows "$name"))); done
echo "$(grep -c . <<<"$originals") collections, $total_rows rows"

while true; do
  staging=$(names | grep '_bm25_staging$')
  if [ -z "$staging" ]; then
    collections=$(names)
    copy="no copies running (not started yet, or finished)"
  else
    collections=$staging
    copied=0
    for name in $staging; do copied=$((copied + $(rows "$name"))); done
    copy="copies started: $(grep -c . <<<"$staging")  |  rows copied: $(percent $copied $total_rows)"
  fi
  echo "$(date +%T)  $copy  |  vector index: $(index_progress vector "$collections")  |  keyword index: $(index_progress sparse "$collections")"
  sleep 60
done
```

输出解读：

- 启动时显示 `0 collections` 意味着 Milvus 拒绝了该请求。请检查 `TOKEN`。
- 迁移开始前，关键词索引显示 `0/0`，因为旧集合没有关键词索引。
- 复制进行中时，该行会显示已复制的行数以及 Milvus 为其建立索引的进度。
- 复制完成后，数字会归零，该行显示为 `no copies running`。随后新集合会被换上，Open WebUI 日志中接着出现 `Migrated` 那一行。
