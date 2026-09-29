# epic-paper-weekly

**EPIC 组论文周报文献整理 Skill**：把一个论文 PDF 文件夹 + 一份周报模板 PPTX，自动逐篇生成中文周报幻灯片——每篇论文一页，严格复刻模板的 7 行 2 列表格版式，自动拆分中英文混排字体、从 PDF 渲染配图、导出 PPTX 并修复 Windows 字体与水印。

> 目录结构遵循 Anthropic [Agent Skills](https://github.com/anthropics/skills) 约定：`SKILL.md`（YAML frontmatter + Markdown 正文）+ `references/`（补充规则）+ `scripts/`（可执行工具）。

---

## 它解决什么问题

实验室组会/组报场景：导师发一份 `papers.pptx` 模板（一页样例：文章名称 / 作者 / 单位 / 期刊时间 / 关键词 / 内容总结 / 配图），要求你把当周读的 5–10 篇论文逐页填进去。手工做一页要 10–15 分钟，且经常出现：

- 中英文混排字体不一致（中文宋体、英文 Times New Roman 没有逐字符拆）
- 表格边框缺一条线、溢出画布
- 导出 PPTX 后 Windows 上字体回退成默认
- 导出文件带平台水印
- 作者名换行、关键词夹英文术语、总结太短

本 Skill 把上述所有规则固化为硬约束 + 可复用脚本，Agent 读一遍 `SKILL.md` 就能稳定产出与模板视觉一致的周报页。

## 特性

- **模板零修改**：样例页全程不动，新页逐页插入其后。
- **版式严格复刻**：7 行 2 列表格，标签列底 `#B4C7E7`、内容列底 `#E9EBF5`，黑色边框完整成框。
- **中英字体逐字符拆分**：中文字符走宋体（SimSun），英文/数字走 Times New Roman，连字符级混合都正确。
- **智能字段抽取**：作者放不下时自动取前三作者 + 通讯作者（带 `*`）；关键词只保留中文；总结 350–500 字纯中文。
- **PDF 配图渲染**：用 PyMuPDF 按指定页/裁剪框/2x 缩放导出论文 Figure，不裁剪原图内容。
- **导出后自动修 Windows 字体**：把飞书导出的 `Songti SC` 批量替换为 `SimSun`，并扫描复核。
- **自动去平台水印**：删除导出 PPTX 右下角的"AI 生成"水印图、关系引用与媒体文件。
- **lint 例外处理**：模板固有的 `table_covers_text` 用 `--no-lint` 单页例外提交，不挪动页码。

## 目录结构

```
epic-paper-weekly/
├── SKILL.md                  # 主入口：触发条件、硬约束、主流程（Agent 必读）
├── README.md                 # 本文件
├── LICENSE                   # MIT
├── .gitignore
├── references/
│   ├── template-spec.md       # 表格逐字段填写规则、字数/字号参考
│   └── gotchas.md             # 字体拆分/Songti SC 映射/拼写红线/Windows 兼容坑
└── scripts/
    ├── split_font_spans.py    # 中英文字符切分工具（zh→宋体, en→Times New Roman）
    ├── extract_figure.py      # 从论文 PDF 指定页/区域渲染 PNG
    ├── fix_exported_pptx.py   # 导出 PPTX 后替换 Mac 字体为 Windows SimSun
    └── scan_fonts.py          # 扫描 PPTX 字体声明，报告 Mac 字体残留
```

## 依赖

- Python 3.8+
- 第三方库：`pymupdf`（PDF 渲染）
  ```bash
  pip install pymupdf
  ```

> **⚠️ 平台分支说明**：当前 `doubao` 分支只适配**豆包 Agent**（依赖豆包内置的 `lark-cli slides` 完成在线 Slides 读写、截图、导出）。其他 Agent 宿主（Claude Code 等）的版本请切换到对应分支查看——分支之间只替换「宿主调用层」，`references/` 和 `scripts/` 完全共用。

## 快速开始（豆包 Agent）

1. 把整个 `epic-paper-weekly/` 目录放进豆包的 user skills 加载路径（`.user_skills/`）。
2. 准备好：
   - 一份模板 `papers.pptx`（含一页样例）
   - 一个论文 PDF 文件夹
3. 对豆包说：
   > 按 epic-paper-weekly skill，把这个文件夹里的论文逐篇做成周报页，插入到 papers.pptx 模板页后面。
4. 豆包会按 `SKILL.md` 的 6 步流程执行：导入模板 → 解析每篇 PDF → 逐页生成 → 截图验收 → 导出 PPTX + 修字体 + 去水印 → 交付。

## 脚本单独使用

不依赖 Agent 也可以单独跑脚本：

```bash
# 1) 从 PDF 第 3 页导出配图，2x 缩放
python scripts/extract_figure.py paper.pdf --page 3 --out fig3.png

# 2) 中英文字符切分（喂给 PPT 生成器按段套字体）
python scripts/split_font_spans.py "Self-evolving LLM Agents 自进化智能体"

# 3) 导出 PPTX 后修 Mac 字体为 SimSun
python scripts/fix_exported_pptx.py papers.pptx --out papers-fixed.pptx

# 4) 复核字体残留
python scripts/scan_fonts.py papers-fixed.pptx
```

## 作为 Skill 的写作约定

`SKILL.md` 头部 YAML frontmatter：

```yaml
---
name: epic-paper-weekly
description: EPIC 组周报文献整理——把论文 PDF 文件夹里的论文按 papers.pptx 模板逐篇做 PPT、每篇一页时使用。
---
```

完整规则见 [`SKILL.md`](./SKILL.md)，踩坑记录见 [`references/gotchas.md`](./references/gotchas.md)。

## 已知限制

- 只适配「7 行 2 列固定标签表格」这一种周报模板版式；其他版式需改 `references/template-spec.md`。
- 导出后去水印步骤针对"飞书 Slides 导出"场景加的水印；其他平台导出的水印需自行扩展 `fix_exported_pptx.py` 同款 zipfile 处理逻辑。
- 红色拼写波浪线无法从 PPTX 文件层关闭（OOXML 会被 PowerPoint 规范化），只能靠纯中文内容规避 + 指导用户在 PowerPoint 选项里关闭拼写检查。

## License

[MIT](./LICENSE)
