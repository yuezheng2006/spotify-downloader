# spotDL v4

> 最快、最简单、最准确的命令行音乐下载器

**spotDL** 从 Spotify 播放列表查找歌曲，从 YouTube 下载 - 自动嵌入专辑封面、歌词和元数据。

---

## ⚡ 快速开始

### 安装

推荐使用 Python 安装（最简单）：

```bash
pip install spotdl
```

在某些系统上可能需要使用 `pip3` 替代 `pip`。

### 安装 FFmpeg

FFmpeg 是 spotDL 的必需依赖。最简单的方式是安装到 spotDL 目录：

```bash
spotdl --download-ffmpeg
```

或者系统级安装：
- **Windows**: [查看教程](https://windowsloop.com/install-ffmpeg-windows-10/)
- **macOS**: `brew install ffmpeg`
- **Linux**: `sudo apt install ffmpeg` 或使用您的发行版包管理器

---

## 🚀 基础使用

### 下载歌曲

最简单的使用方式：

```bash
spotdl [Spotify链接]
```

示例：

```bash
# 下载单曲
spotdl https://open.spotify.com/track/...

# 下载专辑
spotdl https://open.spotify.com/album/...

# 下载播放列表
spotdl https://open.spotify.com/playlist/...

# 搜索并下载
spotdl "周杰伦 - 晴天"
```

### 作为 Python 模块运行

如果直接运行不工作，可以作为模块运行：

```bash
python -m spotdl [Spotify链接]
```

---

## 🌟 增强功能（本仓库）

本仓库在原 spotDL 基础上增加了**完整元数据管理**功能：

### 🎯 核心特性

- ✅ **独立目录** - 每首歌单独文件夹
- ✅ **LRC 同步歌词** - 带时间轴的歌词文件
- ✅ **高清专辑封面** - 独立的 cover.jpg
- ✅ **元数据报告** - metadata.txt + metadata.json
- ✅ **批量下载** - 支持单曲/专辑/播放列表/艺术家

### 📦 输出结构

```
downloads/
└── 周杰伦 - 晴天/
    ├── 周杰伦 - 晴天.mp3         # 音频文件（含完整ID3标签）
    ├── 周杰伦 - 晴天.lrc         # 同步歌词（带时间轴）
    ├── cover.jpg                 # 高清专辑封面
    ├── metadata.txt              # 人类可读的详细元数据
    └── metadata.json             # 结构化元数据（供程序使用）
```

### 🚀 使用增强功能

#### 方式1: Web UI（推荐）

```bash
./start.sh
```

选择菜单选项 1，然后访问 http://127.0.0.1:8800/ui

**特点**：
- 美观的图形界面
- 实时下载进度和步骤提示
- 支持单曲、专辑、播放列表批量输入
- 零配置，自动处理依赖

#### 方式2: 命令行批量下载

```bash
python3 download_batch.py "SPOTIFY_URL"

# 示例
python3 download_batch.py "https://open.spotify.com/album/..."
python3 download_batch.py "https://open.spotify.com/playlist/..."

# 高级选项
python3 download_batch.py "URL" -o music -f flac --max-songs 20
```

---

## 📖 详细文档

- [安装指南](installation_zh.md) - 详细安装步骤
- [使用指南](usage_zh.md) - 完整使用说明
- [故障排除](troubleshooting_zh.md) - 常见问题解决
- [中文 README](../README_CN.md) - 完整中文说明
- [技术架构](../ARCHITECTURE_CN.md) - 系统架构文档

---

## 🎵 音频来源和质量

spotDL **不从 Spotify 下载音频**。实际流程：

1. 从 Spotify API 获取元数据（歌名、艺术家、专辑等）
2. 在 YouTube 搜索匹配的音频
3. 从 YouTube 下载音频（128-256 kbps）
4. 嵌入 Spotify 元数据到音频文件
5. 从 Genius/Musixmatch 等获取歌词

### 音频质量

- **标准用户**: 128 kbps
- **YouTube Music Premium**: 256 kbps
- **格式支持**: MP3, WAV, FLAC, M4A, OGG, OPUS

查看[音频格式和质量](usage_zh.md#音频格式)了解更多。

---

## ⚠️ 法律声明

> **注意**: 用户需对下载行为和潜在法律后果负责。我们不支持未经授权下载受版权保护的材料，对用户行为不承担任何责任。

spotDL 使用公开可访问的资源，但请确保您的使用符合当地法律。

---

## 🤝 贡献

有兴趣贡献代码？查看我们的 [贡献指南](CONTRIBUTING.md) 了解如何参与和搭建开发环境。

---

## 📝 许可证

本项目采用 [MIT 许可证](../LICENSE)。

---

## 🌐 语言

- [English](index.md) - 英文文档
- [中文](index_zh.md) - 当前页面

---

**完整英文文档**: https://spotdl.readthedocs.io

