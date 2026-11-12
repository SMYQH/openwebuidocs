import React from "react";
import { useDoc } from "@docusaurus/plugin-content-docs/client";
import useDocusaurusContext from "@docusaurus/useDocusaurusContext";

import styles from "./styles.module.css";

export default function DocsFeedback() {
	const { metadata } = useDoc();
	const { siteConfig } = useDocusaurusContext();
	const params = new URLSearchParams({
		template: "docs-feedback.yml",
		title: `[Docs feedback]: ${metadata.title}`,
		"page-title": metadata.title,
		"page-url": new URL(metadata.permalink, siteConfig.url).href,
	});

	return (
		<aside className={styles.card} aria-label="改进此页面">
			<strong>改进此页面</strong>
			<p>缺少步骤？内容不清楚或已经过时？</p>
			<a href={`https://github.com/open-webui/docs/issues/new?${params}`}>
				提交反馈 <span aria-hidden="true">↗</span>
			</a>
		</aside>
	);
}