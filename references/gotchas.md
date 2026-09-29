# 踩坑实录（全部实证，勿重试已验证死路）

## 1. 字体拆分（中文宋体 / 英文 Times New Roman）

- 一个文本框里**中文字符和英数字符必须拆成不同 run/span**：中文/全角标点 → 宋体（`SimSun`），英文字母/数字/半角标点 → Times New Roman。
- 整段只设一个 `fontFamily="宋体"` 会让英文也变成宋体质感；只设 Times New Roman 会让中文回退成默认字体。
- 用 `scripts/split_font_spans.py` 先把文本切成片段，再按片段分别套字体。
- **死路（勿试）**：飞书在线 Slides 里把字体写成"宋体"，导出 PPTX 时会被映射成 Mac 专用字体 **Songti SC**——Windows 上没这个字体，打开后中文错配。导出后必须跑 `scripts/fix_exported_pptx.py` 批量改回 `SimSun`，再跑 `scan_fonts.py` 复核。

## 2. 红色波浪线（拼写检查）——不要试图改文件关闭

**已验证死路，全部不要重试：**
- OOXML 给每个 run 加 `smtSpell="0"` / `smtClean="0"`：PowerPoint 打开文件时**丢弃**这些属性。
- COM 设 `TextRange.LanguageID = 1024`（msoLanguageIDNoProofing，"不检查拼写"）：PowerPoint 保存时把它规范化成实际语言（中文 2052 / 英文 1033），"不检查"状态不持久。
- 结论：**桌面 PowerPoint 的波浪线只由用户端「文件→选项→校对→键入时检查拼写」全局设置控制**，文档层没有可靠开关。

**正确做法：**
- 源头规避：内容总结写纯中文，把易被中文校对误判的词改平实。对照：
  - "消融证实" → "实验证实"
  - "具体代码面" → "具体代码位置"
  - "课程联合修复" → "在有界失败窗口内联合修复"
  - "写死" → "预先固定"
  - "留出测试集" → "独立测试集"
  - "多次择优" → "取最优成绩"
- 交付时**明确告知用户**：波浪线不代表内容错误；关闭路径：PowerPoint「文件→选项→校对→取消『键入时检查拼写』」（WPS：工具→选项→拼写检查→取消"输入时检查拼写"）。飞书在线版下划线来自飞书"智能纠错"云文档设置，SML 协议层无关闭属性。

## 3. lint 与模板例外

- 每页先带 lint 提交。新页唯一且稳定的报错是 `table_covers_text`：右下角页码 shape 压在表格右下角边框上——**这是模板固有设计**，模板页本身也这样。
- 处理：完整读完报告确认无其他问题后，对该页单独 `--no-lint` 重提。**不要移动页码去消除这个报错**。
- 4000153 被拒时 `error.message` 是 JSON 字符串，解码后读完整报告，不能只看摘要。

## 4. Windows PowerShell 兼容（lark-cli）

- `lark-cli` 的 `--output`/`--input`/`--file`/`--pages @` 只接受 **CWD 内相对路径**，先 `cd` 到工作目录再用 `./xxx`，绝对路径会被拒。
- 禁止命令行内联 JSON（`--data '{...}'` / `"{\"...\"}"` 在 PS 引号栈会散）：先 Write `payload.json`，再 `--data "@payload.json"`。
- 每次 Bash 只跑一条外部命令；禁止 `&&`/`||`/`$(...)`/heredoc，组合逻辑落成 `.py` 或多次调用。
- `.ps1` 脚本必须 **UTF-8 with BOM**（PS5.1 读无 BOM 的中文路径会乱码）。
- `python -c "..."` 里禁止 `\"` 等双引号转义，复杂逻辑一律 Write 成 `.py` 文件再跑。
- stderr 在 PS5 被包成 NativeCommandError，不等于真报错，要看具体 JSON。

## 5. 内容与图片

- 论文 Figure 从 PDF 用 pymupdf 渲染裁剪（`scripts/extract_figure.py`），**不裁论文原图内容**，只按原比例缩放适配最后一栏。
- `<img src>` 只能填 `+media-upload` 返回的 `file_token`，禁止 http 外链。
- 模板页（样例页）全程不动；新页 `+add-slide --before-slide-id` 插到模板页后，或按制作顺序追加后核对页序。

## 6. 交付

- 在线链接和本地 PPTX 都要 `present_files` 交付；只要本轮写入了幻灯片，即使链接不变，跨轮也必须重新交付最新版。
- 本地最终 PPTX 路径交给用户前，确认已做 `fix_exported_pptx.py` + `scan_fonts.py`。
