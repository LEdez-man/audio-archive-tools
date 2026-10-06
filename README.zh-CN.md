# audio-archive-tools

[English](README.md) · [Deutsch](README.de.md) · [Français](README.fr.md) · [Español](README.es.md) · [日本語](README.ja.md) · **中文**

把一个装满录音的文件夹变成可检索、描述清晰的档案——**完全在本地运行，无需服务器，不上传任何内容。**

本工具使用 [noScribe](https://github.com/kaixxx/noScribe)（Whisper + 说话人识别）转写录音，生成字幕，为每个文件加上日期和
有意义的名称，并生成一个离线浏览页面：可筛选、全文检索，并可直接跳转到录音中的任意一句话。通过输入表单，无需手动编辑文件
即可填写项目信息和每个录音的描述。

本项目最初用于整理家庭的旧录音笔和手机录音，同样适用于：

| | |
|---|---|
| **家庭 / 私人** | 家庭录音、孩子的声音、与祖父母的谈话 |
| **口述历史** | 生平访谈与见证者访谈，含知情同意、访问权限与限制公开期限 |
| **语言学田野调查** | 包含 ISO 639-3 语言、发音人、体裁、刺激材料、知情同意和访问级别的会话（IMDI/ELAN 风格） |
| **社会语言学** | 含社会变量和访谈模块（自由谈话、朗读、词表、最小对立对）的访谈 |
| **野外录音 / 声景** | 记录地点、坐标、生境、设备的自然与环境声音——不转写 |
| **新闻** | 用于报道、专题、街头采访、游行、新闻发布会的素材与原声片段——含发布许可状态 |

## 功能

- 使用 noScribe 无界面 **批量转写**——可随时重新开始，内容相同的文件只转写一次，自动以无说话人识别方式重试，
  对困难录音可在音频处理后重新转写
- 每个录音旁生成 **字幕（.srt）**，VLC 会自动显示
- 过滤 Whisper 在静音或噪声中产生的 **幻觉文本**（电视台字幕署名、无限循环）
- **统一的文件名**：`YYYY-MM-DD_简短标题_设备编号.mp3`（估计日期带 `ca`），并记录以便撤销
- **浏览页面**：按年份和档案自定义的标签类别筛选，全文检索，内置播放器，点击句子即可跳转，章节或原声片段，项目信息
- **输入表单**：填写项目和每个录音（日期、标题、摘要、标签、配置字段、发音人姓名、章节）。更改保存在浏览器中，
  再保存为工具可导入的文件
- 针对上述用途的 **配置（profile）**，每个档案均可自由调整
- 用于电子表格、语料库工具或档案存储的 **CSV 导出**
- 页面、消息和批处理文件名支持 **六种语言**：中文、英语、德语、法语、西班牙语、日语
- 重复文件、AMR 原始文件（为浏览器转换为 MP3）和空文件会被 **移到一旁，绝不删除**
- 仅使用 Python 标准库，无需安装任何包

## 环境要求

- Windows 10/11（批处理文件适用于 Windows；Python 脚本本身可在任何系统运行）
- [Python](https://www.python.org/) 3.9 或更高版本
- `PATH` 中的 [ffmpeg](https://ffmpeg.org/)（例如 `winget install ffmpeg`）
- [noScribe](https://github.com/kaixxx/noScribe) 0.7 或更高版本（支持命令行）。NVIDIA 显卡可大幅加快转写，但不是必需的。

## 安装

1. 下载或克隆本仓库，例如到 `Documents\audio-archive-tools`。
2. 将 `settings.example.json` 复制为 `settings.json` 并修改：界面语言 `"language": "zh"`，
   录音语言 `"transcription_language": "zh"`（或 `auto`），以及 noScribe 的路径。

## 快速开始

1. 为录音文件夹 **做好备份**。
2. **把文件夹拖到 `setup-archive.bat` 上。** 选择配置、标题和录音语言，会生成一个包含批处理文件的 `_archive` 子文件夹。
3. 运行 **`1 转写`**。每个录音会得到 `.html` 转写文本和 `.srt` 字幕。
4. 运行 **`2 描述录音（输入表单）`**，填写后保存，保存位置选择 `_archive` 文件夹。
5. 运行 **`3 更新档案`**。文件被重命名，并打开 `音频档案.html`。

以后有新录音？放入文件夹，再依次运行 1 → 2 → 3。只会处理新文件。

| 批处理文件 | 作用 |
|---|---|
| `1 转写` | 转写所有尚无转写文本的录音并登记新录音 |
| `2 描述录音（输入表单）` | 生成并打开输入表单 |
| `3 更新档案` | 导入已保存的输入，重命名，重新生成字幕和页面 |
| `重新生成字幕` | 在 noScribe 编辑器中修改转写文本之后使用 |
| `重新转写问题录音` | 降噪并统一音量后重新转写 |
| `导出为CSV` | 写出 `<标题>.csv` 和 `<标题>_project.csv` |
| `撤销重命名` | 撤销所有已记录的重命名和移动 |

## 配置、数据格式、Claude

各配置的字段及其设计理由见 [docs/profiles.md](docs/profiles.md)，文件格式见 [docs/data-format.md](docs/data-format.md)（英文）。
如需让 [Claude Code](https://claude.com/claude-code) 根据转写文本描述录音，请将
[`claude-skill/audio-archive`](claude-skill/audio-archive/SKILL.md) 复制到 `~/.claude/skills/`。

## 隐私

一切都在您自己的电脑上运行，不会上传任何内容。`.gitignore` 排除了音频文件、`_archive` 文件夹和 `settings.json`。
如果使用 AI 助手描述录音，转写文本会发送给该服务——请针对每个档案自行判断，尤其是受知情同意限制的研究数据。

## 局限

- 自动转写只是草稿；儿童语音、方言、嘈杂或音量很低的录音识别效果较差。
- Whisper 并不支持所有语言；此时请设置 `"transcribe": false`。
- 暂不支持 IMDI/CMDI XML 导出；可通过 CSV 导出衔接。

## 参与 · 许可 · 致谢

参见 [CONTRIBUTING.md](CONTRIBUTING.md)。许可证：[MIT](LICENSE)。转写由 Kai Dröge 开发的 [noScribe](https://github.com/kaixxx/noScribe)
完成，其基于 [faster-whisper](https://github.com/SYSTRAN/faster-whisper) 和 [pyannote](https://github.com/pyannote/pyannote-audio)。
