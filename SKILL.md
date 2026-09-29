---
name: epic-paper-weekly
description: EPIC 组论文周报文献整理——按 papers.pptx 模板（7 行 2 列表格版式）把论文 PDF 文件夹里的每篇论文做成一页中文周报幻灯片，插入模板页之后。当用户要求把"周报文献/论文 PDF 文件夹"里的论文按 papers.pptx 逐篇做 PPT、每篇一页、插入到模板页后面时使用。覆盖：Slides 导入与回读、论文信息抽取（标题/作者/单位/期刊日期/关键词/内容总结/配图）、模板版式严格复刻、中文宋体与英文 Times New Roman 逐字符拆分、作者一行（前三作者+通讯作者）、内容总结详尽阐述核心内容与创新、PDF 配图渲染上传、逐页 lint 与模板例外、导出 PPTX 的字体修正（Songti SC→SimSun）、去平台水印，以及红色拼写波浪线的正确处置。
---

# 论文周报 PPT（模板复刻）

为每篇论文产出一页与模板 `papers.pptx` **视觉完全一致**的周报页。模板页本身永不修改，新页逐页插入其后。

## 硬约束（用户锁定，逐条执行）

1. **模板页零修改**：第一页（或前两页）模板样例页的 slide_id 记下，全程不动。
2. **版式**：新页 = 7 行 2 列表格，行标签依次为：文章名称 / 作者 / 单位 / 期刊及时间 / 关键词 / 内容总结 / 图片或原文摘录。右下角保留页码。
3. **配色**：标签列底 `#B4C7E7`，内容列底 `#E9EBF5`，文字与边框黑色，不得引入其他色。
4. **字体**：中文字符用宋体，英文/数字字符用 Times New Roman，**逐字符拆分**（见 references/gotchas.md「字体拆分」）。
5. **作者栏一行**：放不下时只写**前三名作者 + 通讯作者**（通讯作者名后加 `*`），不得换行成两行。
6. **关键词栏只保留中文**，去掉英文术语。
7. **内容总结**：350–500 字，详尽阐述论文核心内容与创新点；用纯中文表达（模型/机构专名除外），见 gotchas「波浪线规避」。
8. **字号**：内容总结按文本量 11–12pt 自适应，不得溢出单元格；其余字段按模板。
9. **配图**：论文 Figure 放在最后一栏，从 PDF 渲染裁剪（scripts/extract_figure.py），按原比例缩放，**不裁剪论文原图内容**。
10. **表格边框必须完整成框**：第一行**两个 td 都必须写 `borderTop`**。模板页回读 XML 里第一行右 td 通常缺 `borderTop`（靠表格整体外框补齐），新页若照抄会导致**顶部右侧黑线缺失**——必须手动给第一行右 td 补上 `borderTop`，确保表格四周是完整黑框。
11. **表格完全落在 960×540 画布内**：模板页表格底部常超出画布约 16px（lint 报 `table_out_of_canvas`），这是模板本身的瑕疵。新页**不要照抄这个溢出尺寸**；推荐用 `topLeftX=6, topLeftY=8, width=948, height=524`（底部=532，留 8px 边距），各行高按 `524/原总高` 等比收缩，配图与页码位置同步内移。

## 主流程

0. **依赖主 skill**：本 skill 只固化模板规格与本任务的坑；所有 Slides 操作命令（`lark-cli slides`）必须先按 `ppt` skill 的 `SKILL.md` 与 `references/workflow/slides-editing.md` / `windows-compat.md` 执行。新轮次先重读 ppt skill，禁止凭记忆写命令。

1. **导入模板并建基线**：模板 PPTX 用 `lark-cli drive +import --type slides` 导入在线 Slides（禁止本地 python-pptx 解析）。立即 `+xml-get --output source.xml` 保存模板页完整 XML 与 lint 基线，截图模板页作为视觉对照。记下模板页 slide_id。

2. **解析每篇 PDF**：pymupdf（`fitz`）读标题、作者、单位、arXiv/期刊与日期、摘要、关键词；用 `scripts/extract_figure.py` 把代表性 Figure 渲染成 PNG。图先用 `+media-upload` 上传拿 `file_token`。

3. **逐页制作（一页一论文，禁止批量）**：
   - 新页 XML 以模板页表格结构为骨架改写（坐标、列宽、配色照抄模板 XML，不要自创布局）。
   - 文本按 references/template-spec.md 的字段规则填。
   - 中/英文本用 `scripts/split_font_spans.py` 预切分，中文 span 用宋体、英数 span 用 Times New Roman。
   - 先带 lint 提交；若唯一报错是 `table_covers_text`（页码 shape 压表格右下角边框）——这是**模板固有设计**，读完报告后按单页例外 `--no-lint` 重提，不要移动页码。

4. **逐页验收**：每页写入后 `+xml-get` 回读 + `+screenshot` 截图：核对七行标签齐全、作者单行、无文字溢出/异常换行、颜色与模板一致、配图在单元格内。

5. **导出、修字体、去水印**：
   - `lark-cli drive +export` 导出 PPTX；
   - **必须**用 `scripts/fix_exported_pptx.py` 把飞书导出时产生的 `Songti SC` 批量替换为 `SimSun`，再用 `scripts/scan_fonts.py` 复核无 Mac 字体残留；
   - **必须去水印**：飞书导出时会在**新做的论文页**右下角自动加一张"豆包工作 AI 生成"水印图（包内通常是 `ppt/media/imageN.png`，约 7KB，在该页 `rels` 里是最后一个 image 关系）。用 Python zipfile 打开导出的 PPTX：①在对应 `ppt/slides/slideN.xml` 里删掉引用该 rId 的整个 `<p:pic>...</p:pic>` 元素；②在 `ppt/slides/_rels/slideN.xml.rels` 里删掉该 rId 关系；③跳过写出 `ppt/media/imageN.png`。保存后用 `zipfile.testzip()` 验证包完整。**模板页本身不带水印，只处理新写的论文页。**

6. **交付**：在线 Slides 链接 + 本地 PPTX 路径，均经 `present_files` 交付；本轮只要对幻灯片有写入，跨轮也必须重新交付最新版本。

## 波浪线（红色下划线）的正确处置

**不要试图从 PPTX 文件本身关闭波浪线。** 已实证：OOXML 的 `smtSpell`/`smtClean` 属性与 `LanguageID=1024`（不检查）在 PowerPoint 保存时会被丢弃/规范化，文档层无法持久关闭。波浪线由用户 PowerPoint 的「文件→选项→校对→键入时检查拼写」全局设置控制。

正确做法：
- 内容上规避：内容总结写纯中文、专业术语改平实说法（见 gotchas 对照表），从源头减少误判；
- 交付说明里明确告知用户：红色波浪线不代表内容错误，关闭方法为 PowerPoint「文件→选项→校对→取消勾选『键入时检查拼写』」（WPS：工具→选项→拼写检查）。用户在飞书在线版看到的下划线则来自飞书「智能纠错」云文档设置。

## 配套资源

- `references/template-spec.md` — 模板表格逐字段填写规则、字数与字号参考、作者栏示例。
- `references/gotchas.md` — 字体拆分/Songti SC 映射/波浪线机制/lint 例外/Windows PowerShell 兼容坑（全部为踩坑实证，勿重试已验证死路）。
- `scripts/split_font_spans.py` — 按中英字符类别预切分文本，输出带语言标记的片段 JSON。
- `scripts/extract_figure.py` — 从论文 PDF 指定页渲染裁剪区域为 PNG。
- `scripts/fix_exported_pptx.py` — 导出 PPTX 后替换 Mac 字体为 Windows 宋体。
- `scripts/scan_fonts.py` — 扫描 PPTX 全部字体声明，报告错配与 Mac 字体残留。
