# 使用指南

本指南涵盖 spotDL 的所有使用方法，从基础到高级功能。

---

## 🚀 基础使用

### 下载单曲

```bash
spotdl https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b
```

### 下载专辑

```bash
spotdl https://open.spotify.com/album/4aawyAB9vmqN3uQ7FjRGTy
```

### 下载播放列表

```bash
spotdl https://open.spotify.com/playlist/37i9dQZF1DX0XUsuxWHRQd
```

### 下载艺术家的歌曲

```bash
spotdl https://open.spotify.com/artist/0TnOYISbd1XYRBk9myaseg
```

### 搜索并下载

```bash
spotdl "周杰伦 - 晴天"
spotdl "Taylor Swift - Anti-Hero"
```

---

## ⚙️ 常用选项

### 指定输出目录

```bash
spotdl [链接] --output ~/Music
```

### 指定音频格式

```bash
spotdl [链接] --format mp3
spotdl [链接] --format flac
spotdl [链接] --format wav
```

支持的格式：`mp3`, `flac`, `wav`, `m4a`, `ogg`, `opus`

### 指定音频质量

```bash
# 设置比特率
spotdl [链接] --bitrate 320k

# 使用预设质量
spotdl [链接] --quality best
```

### 自定义文件名格式

```bash
spotdl [链接] --output "{artist} - {title}.{output-ext}"
spotdl [链接] --output "{album}/{artist} - {title}.{output-ext}"
```

可用变量：
- `{title}` - 歌曲标题
- `{artist}` - 艺术家名称
- `{album}` - 专辑名称
- `{track-number}` - 曲目编号
- `{disc-number}` - 光盘编号
- `{year}` - 发行年份
- `{output-ext}` - 输出扩展名

### 跳过已存在的文件

```bash
spotdl [链接] --overwrite skip
```

---

## 🌟 spotDL 操作模式

### 1. Download（下载）- 默认模式

下载歌曲并嵌入元数据：

```bash
spotdl download [链接]
# 或简写
spotdl [链接]
```

### 2. Save（保存元数据）

只保存元数据，不下载音频：

```bash
spotdl save [链接] --save-file playlist.spotdl
```

用途：
- 备份播放列表元数据
- 稍后下载
- 分享播放列表信息

### 3. Web（Web界面）

启动 Web 界面：

```bash
spotdl web
# 自定义端口
spotdl web --port 8080
# 自定义主机
spotdl web --host 0.0.0.0
```

访问：http://127.0.0.1:8080

### 4. Sync（同步）

保持目录与播放列表同步：

```bash
# 首次同步
spotdl sync [链接] --save-file sync.spotdl

# 更新目录
spotdl sync sync.spotdl
```

- 新增的歌曲会被下载
- 移除的歌曲会被删除
- 现有文件不会重新下载

### 5. Meta（更新元数据）

更新已存在文件的元数据：

```bash
spotdl meta [音频文件]
spotdl meta song1.mp3 song2.mp3
```

### 6. URL（获取链接）

获取友好的 URL：

```bash
spotdl url [链接]
```

---

## 🎵 音频格式和质量

### 支持的格式

| 格式 | 特点 | 推荐用途 |
|------|------|----------|
| **MP3** | 通用兼容性最好 | 日常使用、移动设备 |
| **FLAC** | 无损压缩 | 发烧友、存档 |
| **WAV** | 无损未压缩 | 专业制作、编辑 |
| **M4A** | Apple 生态优化 | iPhone、iPad、Mac |
| **OGG** | 开源格式 | Linux、开源软件 |
| **OPUS** | 高效压缩 | 网络传输、节省空间 |

### 音频质量

spotDL 从 YouTube 下载音频，质量取决于：

1. **YouTube 账户类型**
   - 标准用户: 128 kbps
   - YouTube Music Premium: 256 kbps

2. **原始视频质量**
   - 官方音乐视频通常质量更高
   - 用户上传视频质量不一

3. **选择的格式**
   - 有损格式 (MP3, M4A, OGG, OPUS)：保持原始比特率
   - 无损格式 (FLAC, WAV)：转换但不增加质量

### 推荐设置

**日常听歌**:
```bash
spotdl [链接] --format mp3 --bitrate 256k
```

**高保真收藏**:
```bash
spotdl [链接] --format flac
```

**节省空间**:
```bash
spotdl [链接] --format opus --bitrate 128k
```

---

## 🌟 增强功能（本仓库专属）

本仓库提供**完整元数据管理**功能，每首歌独立目录。

### 🌐 方式1: Web UI 增强版

```bash
# 使用启动脚本（推荐）
./start.sh
# 选择选项 1

# 或直接运行
source venv/bin/activate
python3 web_enhanced.py
```

访问：http://127.0.0.1:8800/ui

**功能**：
- ✅ 美观的标签页界面
- ✅ 实时下载进度和步骤提示
- ✅ 支持单曲、专辑、播放列表、艺术家
- ✅ 批量下载（多个URL一次提交）
- ✅ 自定义音频格式和输出目录
- ✅ 温馨提示预期下载时间

### 📝 方式2: 命令行批量下载

```bash
source venv/bin/activate
python3 download_batch.py "SPOTIFY_URL"
```

**示例**：

```bash
# 下载单曲
python3 download_batch.py "https://open.spotify.com/track/..."

# 下载专辑
python3 download_batch.py "https://open.spotify.com/album/..."

# 下载播放列表
python3 download_batch.py "https://open.spotify.com/playlist/..."

# 下载艺术家（限制20首）
python3 download_batch.py "https://open.spotify.com/artist/..." --max-songs 20

# 指定格式和目录
python3 download_batch.py "URL" -o ~/Music -f flac
```

**选项**：
- `-o, --output` - 输出目录（默认：downloads）
- `-f, --format` - 音频格式（默认：mp3）
- `--max-songs` - 艺术家模式最大歌曲数

### 📁 输出结构

增强功能会为每首歌创建独立目录：

```
downloads/
└── 周杰伦 - 晴天/
    ├── 周杰伦 - 晴天.mp3         # 音频（含完整ID3标签）
    ├── 周杰伦 - 晴天.lrc         # LRC同步歌词
    ├── cover.jpg                 # 高清专辑封面
    ├── metadata.txt              # 人类可读的元数据
    └── metadata.json             # 结构化元数据
```

**metadata.txt 示例**：
```
标题: 晴天
艺术家: 周杰伦
专辑: 叶惠美
发行日期: 2003-07-31
流派: Mandopop
时长: 4分29秒
比特率: 256 kbps
ISRC: TWK970300503
Spotify URL: https://open.spotify.com/track/...
YouTube URL: https://www.youtube.com/watch?v=...
```

**metadata.json 示例**：
```json
{
  "title": "晴天",
  "artist": "周杰伦",
  "album": "叶惠美",
  "date": "2003-07-31",
  "genre": "Mandopop",
  "duration_seconds": 269,
  "bitrate": "256 kbps",
  "isrc": "TWK970300503",
  "spotify_url": "https://open.spotify.com/track/...",
  "youtube_url": "https://www.youtube.com/watch?v=..."
}
```

---

## 📚 批量下载技巧

### 从文件读取链接

创建 `urls.txt`：
```
https://open.spotify.com/track/...
https://open.spotify.com/track/...
https://open.spotify.com/album/...
```

下载：
```bash
spotdl $(cat urls.txt)
```

或使用增强功能：
```bash
while read url; do
    python3 download_batch.py "$url"
done < urls.txt
```

### 下载用户所有播放列表

```bash
spotdl saved
```

### 下载 Liked Songs

```bash
spotdl https://open.spotify.com/collection/tracks
```

---

## 🎯 高级技巧

### 使用代理

```bash
export HTTP_PROXY="http://proxy.example.com:8080"
export HTTPS_PROXY="http://proxy.example.com:8080"
spotdl [链接]
```

### 指定 Spotify Cookie

用于访问私有播放列表：

```bash
spotdl [链接] --cookie-file cookies.txt
```

### 多线程下载

```bash
spotdl [链接] --threads 4
```

### 限制艺术家歌曲数

```bash
spotdl [艺术家链接] --max-songs 50
```

---

## ⚠️ 注意事项

### 下载速度

完整下载一首歌通常需要 **20-45秒**：

- 🔍 Spotify API 元数据获取：3-5秒
- 🎵 YouTube 搜索匹配：2-3秒
- ⬇️ 音频下载：10-30秒（最慢）
- 🎼 FFmpeg 转码：2-5秒
- 📝 元数据处理：1-2秒

**提示**: 增强版 Web UI 会显示详细的步骤提示，让你知道当前进度。

### 歌词来源

spotDL 从多个来源获取歌词：

1. **Genius** - 英文歌词，高质量
2. **Musixmatch** - Spotify 也使用的服务
3. **Deezer/NetEase** - 通过 syncedlyrics
4. **AZLyrics** - 备选源

中文歌词通常来自 Musixmatch 或 NetEase，与 Spotify 显示的一致。

### 版权和合法性

- spotDL 使用公开可访问的资源（Spotify API + YouTube）
- 用户需对下载行为负责
- 请确保符合当地法律
- 仅供个人使用

---

## 🆚 使用方式对比

| 特性 | spotdl CLI | Web UI | 增强 Web UI | download_batch.py |
|------|:----------:|:------:|:-----------:|:-----------------:|
| **易用性** | ⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **独立目录** | ❌ | ❌ | ✅ | ✅ |
| **LRC歌词文件** | ❌ | ❌ | ✅ | ✅ |
| **独立封面** | ❌ | ❌ | ✅ | ✅ |
| **元数据报告** | ❌ | ❌ | ✅ TXT+JSON | ✅ TXT+JSON |
| **实时步骤提示** | ✅ | ❌ | ✅ 详细 | ✅ |
| **批量下载** | ✅ | ✅ | ✅ | ✅ |
| **图形界面** | ❌ | ✅ 基础 | ✅ 增强 | ❌ |
| **适合场景** | 快速下载 | 简单使用 | 完整音乐库 | 脚本自动化 |

**推荐**：
- 🥇 完整音乐库管理 → 增强 Web UI
- 🥈 命令行自动化 → download_batch.py
- 🥉 快速单曲下载 → spotdl CLI

---

## 📖 更多资源

- [故障排除](troubleshooting_zh.md) - 解决常见问题
- [中文 README](../README_CN.md) - 完整功能说明
- [技术架构](../ARCHITECTURE_CN.md) - 系统架构文档
- [官方文档](https://spotdl.readthedocs.io) - 英文完整文档

