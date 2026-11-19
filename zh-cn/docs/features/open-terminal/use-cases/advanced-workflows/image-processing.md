---
sidebar_position: 7
title: "图像处理"
---

# 📸 批量处理图像 {#batch-process-images}

对一个文件夹的图像进行调整大小、添加水印、格式转换或生成缩略图。

> **你：** $Image Processor <br/>
> /photos 中有产品图片。将它们调整到 800x800，添加水印，并制作缩略图。

## AI 的工作流程 {#what-the-ai-does}

1. 使用 PIL/Pillow（预装）处理所有图像
2. 创建带水印的原始大小版本
3. 按要求大小创建缩略图
4. 生成缩略图总览（将所有缩略图排成网格）
5. 报告处理的文件数量和节省的存储空间

![文件浏览器中显示处理后的图片和缩略图](/images/open-terminal-image-processing-outputs.png)

## 技能内容 {#skill-content}

将下面的内容复制到**工作区 → 技能 → 创建**：

```markdown
---
name: image-processor
description: Batch processes images - resize, watermark, convert, and generate thumbnails
---

## Image Processing

When processing images:

1. **Survey first**: Count files, check formats, note total size
2. **Process one file as a test**: Show the result before processing the rest
3. **Use Pillow (PIL)**:
   - Resize with aspect ratio preservation (use thumbnail or fit)
   - Watermarks: semi-transparent text in lower-right corner
   - Format conversion: handle RGBA→RGB for PNG→JPEG
4. **Organize output** into clear subdirectories (processed/, thumbnails/, etc.)
5. **Generate a summary**: files processed, size before/after
6. **For large batches**, report progress: "Processed 25/50..."

Always preview the first result before batch-processing.
```
