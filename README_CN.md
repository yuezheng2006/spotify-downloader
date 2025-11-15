# spotDL v4 - 中文简介

> 最快、最简单、最准确的Spotify音乐下载器

从Spotify播放列表查找歌曲，从YouTube下载 - 自动嵌入专辑封面、歌词和元数据。

[![MIT License](https://img.shields.io/github/license/spotdl/spotify-downloader?color=44CC11&style=flat-square)](https://github.com/spotDL/spotify-downloader/blob/master/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/spotdl?style=flat-square)](https://pypi.org/project/spotdl/)
[![Discord](https://img.shields.io/discord/771628785447337985?label=discord&logo=discord&style=flat-square)](https://discord.gg/xCa23pwJWY)

---

## 快速开始

### 安装

```bash
# 1. 安装 spotDL
pip install spotdl

# 2. 安装 FFmpeg（必需）
spotdl --download-ffmpeg

# 3. 克隆本仓库（获取增强工具）
git clone https://github.com/spotDL/spotify-downloader.git
cd spotify-downloader

# 4. 创建虚拟环境并安装依赖
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# 或 venv\Scripts\activate  # Windows
pip install -e .
pip install fastapi uvicorn
```

### 推荐使用方式（完整元数据）

#### 🚀 方式1: 使用启动脚本（最简单）⭐⭐⭐

```bash
./start.sh
```

**特点**：
- ✅ 自动检查并创建虚拟环境
- ✅ 自动安装缺失的依赖
- ✅ 提供菜单选择（Web UI / 命令行下载）
- ✅ 零配置，开箱即用

选择菜单选项：
- `1` - 启动增强版Web UI（推荐）
- `2` - 启动官方Web UI
- `3` - 命令行批量下载
- `4` - 原生spotdl命令

---

#### 🌐 方式2: 增强Web UI（图形界面）⭐⭐

```bash
# 先激活虚拟环境
source venv/bin/activate

# 启动增强版Web UI
python3 web_enhanced.py

# 自定义端口
python3 web_enhanced.py --port 3000

# 允许局域网访问
python3 web_enhanced.py --host 0.0.0.0 --port 8800
```

**访问地址**: http://127.0.0.1:8800/ui

**特点**: 
- ✅ 美观的图形界面，带标签页
- ✅ 实时下载进度（带详细步骤提示）
- ✅ 完整元数据结构（独立目录）
- ✅ LRC歌词 + 封面 + 元数据报告
- ✅ 支持单曲、专辑、播放列表批量输入
- ✅ 温馨提示预期下载时间

---

#### 📝 方式3: 命令行批量下载

```bash
# 激活虚拟环境
source venv/bin/activate

# 下载单曲/专辑/播放列表/艺术家（自动识别）
python3 download_batch.py "SPOTIFY_URL"

# 示例
python3 download_batch.py "https://open.spotify.com/track/..."
python3 download_batch.py "https://open.spotify.com/album/..."
python3 download_batch.py "https://open.spotify.com/playlist/..."

# 高级选项
python3 download_batch.py "URL" -o music -f flac --max-songs 20
```

**特点**: 
- ✅ 命令行操作，适合自动化
- ✅ 完整元数据结构（独立目录）
- ✅ 可集成到脚本中
- ✅ 显示详细的下载进度

### 标准使用方式（基础功能）

如果只需要音频文件（不需要独立歌词、封面文件），可以使用原生命令：

```bash
# 使用 spotdl 命令（需要在虚拟环境中）
source venv/bin/activate  # 激活虚拟环境
spotdl https://open.spotify.com/track/...

# 或使用 python 模块方式
python3 -m spotdl https://open.spotify.com/track/...
python3 -m spotdl https://open.spotify.com/album/...
python3 -m spotdl '周杰伦 - 晴天'

# 启动官方Web UI
python3 -m spotdl web --port 8080
# 访问: http://127.0.0.1:8080
```

**注意**: 原生方式只输出音频文件到单一目录，不包含独立的歌词、封面等文件。

---

## 📦 增强功能详解

### download_batch.py - 完整元数据管理工具

**这是推荐的下载方式**，提供专业的音乐库管理体验：

```bash
python3 download_batch.py "SPOTIFY_URL" [选项]
```

### ✨ 核心特点

- ✅ **独立目录** - 每首歌单独文件夹
- ✅ **完整元数据** - metadata.json + metadata.txt
- ✅ **同步歌词** - LRC格式，带时间轴
- ✅ **专辑封面** - 高清cover.jpg
- ✅ **批量下载** - 支持专辑/播放列表/艺术家
- ✅ **智能跳过** - 自动跳过已存在歌曲

### 选项

```
-o, --output       输出目录（默认：downloads）
-f, --format       音频格式（mp3/wav/flac等，默认：mp3）
--max-songs        艺术家模式限制歌曲数量
```

### 示例

```bash
# 下载专辑到指定目录
python3 download_batch.py "https://open.spotify.com/album/..." -o music

# 下载播放列表为WAV格式
python3 download_batch.py "https://open.spotify.com/playlist/..." -f wav

# 下载艺术家热门10首
python3 download_batch.py "https://open.spotify.com/artist/..." --max-songs 10
```

### 📁 输出结构（默认）

每首歌都会创建独立目录，包含所有相关文件：

```
downloads/
└── 周杰伦 - 晴天/
    ├── 周杰伦 - 晴天.mp3         # 音频文件（含完整ID3标签）
    ├── 周杰伦 - 晴天.lrc         # 同步歌词（带时间轴）
    ├── cover.jpg                 # 高清专辑封面
    ├── metadata.txt              # 人类可读的详细元数据
    └── metadata.json             # 结构化元数据（供程序使用）
```

**元数据包含**：标题、艺术家、专辑、发行日期、ISRC、流派、版权、时长、比特率、Spotify/YouTube链接等

---

## 🆚 下载方式对比

选择适合你的下载方式：

| 特性 | `./start.sh`<br/>**(极力推荐)** | `web_enhanced.py`<br/>**(推荐)** | `download_batch.py` | `spotdl` CLI | 官方Web UI |
|------|:-------------------------------:|:-------------------------------:|:-------------------:|:------------:|:----------:|
| **易用性** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ | ⭐⭐ | ⭐⭐⭐⭐ |
| **自动配置** | ✅ 全自动 | ❌ 需手动 | ❌ 需手动 | ❌ | ❌ |
| **文件组织** | 独立目录 ✅ | 独立目录 ✅ | 独立目录 ✅ | 单一目录 | 单一目录 |
| **LRC歌词文件** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **独立封面图片** | ✅ | ✅ | ✅ | ❌ | ❌ |
| **元数据报告** | TXT+JSON ✅ | TXT+JSON ✅ | TXT+JSON ✅ | ❌ | ❌ |
| **图形界面** | ✅ 菜单 | ✅ Web | ❌ | ❌ | ✅ 基础版 |
| **实时步骤提示** | ✅ | ✅ 详细 | ✅ | ❌ | ❌ |
| **批量下载** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **适合场景** | **所有用户** | **图形界面爱好者** | **命令行专家** | 快速下载 | 简单下载 |

**最佳选择**: 
- 🥇 **所有用户** → `./start.sh` （零配置，自动化）
- 🥈 **图形界面** → `web_enhanced.py` （需手动激活venv）
- 🥉 **命令行** → `download_batch.py` （适合脚本集成）

---

## 工作原理

spotDL **不从Spotify下载音频**，流程如下：

1. 从Spotify API获取元数据（歌名、艺术家、专辑等）
2. 在YouTube搜索匹配的音频
3. 从YouTube下载音频（128-256 kbps）
4. 嵌入Spotify元数据到音频文件
5. 从Genius/MusixMatch等获取歌词

**为什么合法？** 所有资源都是公开可访问的，唱片公司同时授权多个平台。

---

## 支持的格式

| 格式 | 说明 |
|------|------|
| mp3  | 最通用（默认）|
| wav  | 无损，文件大 |
| flac | 无损压缩 |
| m4a  | Apple设备 |
| ogg  | 开源格式 |
| opus | 高效压缩 |

---

## ⚠️ 常见问题

### Q: 运行时提示 "ModuleNotFoundError: No module named 'fastapi'"

**A**: 这是因为没有激活虚拟环境或未安装依赖。

**解决方法**：

```bash
# 方法1: 使用启动脚本（自动处理）
./start.sh

# 方法2: 手动激活虚拟环境
source venv/bin/activate
pip install fastapi uvicorn
python3 web_enhanced.py
```

### Q: 下载速度慢，感觉卡住了？

**A**: 这是正常的！完整下载流程需要时间：

- 🔍 连接Spotify API：3-5秒
- 🎵 YouTube搜索匹配：2-3秒  
- ⬇️ 音频下载：10-30秒（最慢）
- 🎼 FFmpeg转码：2-5秒
- 📝 元数据处理：1-2秒

**总计**: 约 **20-45秒/首歌**

Web UI 现在会显示详细的步骤提示，让你知道当前进度。

### Q: 启动脚本 vs 直接运行有什么区别？

| 方式 | `./start.sh` | `python3 web_enhanced.py` |
|------|:------------:|:-------------------------:|
| 虚拟环境 | ✅ 自动激活 | ❌ 需手动激活 |
| 依赖检查 | ✅ 自动安装 | ❌ 需手动安装 |
| 菜单选择 | ✅ 4种模式 | ❌ 只有Web UI |
| 推荐度 | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |

**推荐日常使用 `./start.sh`**

### Q: 歌词从哪里获取？

**A**: 多个来源，按优先级：

1. **Genius** - 高质量英文歌词
2. **Musixmatch** - Spotify 也使用此服务
3. **Deezer/NetEase** - 通过 syncedlyrics
4. **AZLyrics** - 备选源

**繁体/简体中文**：歌词源提供什么就是什么，通常已经匹配Spotify显示的内容。

### Q: 音频质量如何？

**A**: 
- **来源**: YouTube / YouTube Music
- **标准用户**: 128 kbps
- **Premium用户**: 256 kbps（需登录YouTube Premium）
- **格式**: 可选 MP3/FLAC/WAV/M4A/OGG/OPUS

虽然不是无损，但对于日常听歌已经足够。

---

## 📖 文档

- 📖 [完整文档](https://spotdl.readthedocs.io)（英文）
- 🛠️ [安装指南](docs/installation.md)
- 📝 [使用指南](docs/usage.md)
- 🐛 [故障排除](docs/troubleshooting.md)
- 💬 [Discord社区](https://discord.gg/xCa23pwJWY)

---

## 许可证

[MIT License](LICENSE) - 免费开源

---

## ⚠️ 免责声明

用户需对下载行为和潜在法律后果负责。本项目不支持未经授权下载受版权保护的材料。

---

**完整英文文档请参考 [README.md](README.md)**
