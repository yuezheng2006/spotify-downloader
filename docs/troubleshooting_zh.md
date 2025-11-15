# 故障排除

遇到问题？本指南涵盖最常见的问题和解决方案。

---

## ⚡ 快速诊断

### 基础检查清单

在深入排查前，请确认：

- [ ] Python 版本 ≥ 3.10: `python --version`
- [ ] FFmpeg 已安装: `ffmpeg -version`
- [ ] spotDL 已安装: `spotdl --version`
- [ ] 网络连接正常
- [ ] Spotify 链接有效

---

## 🐛 常见错误

### 1. `ModuleNotFoundError: No module named 'spotdl'`

**原因**: spotDL 未安装或未在 PATH 中

**解决方案**:

```bash
# 方式1: 安装 spotDL
pip install spotdl

# 方式2: 作为模块运行
python -m pip install spotdl
python -m spotdl [链接]

# 方式3: 使用虚拟环境
python3 -m venv venv
source venv/bin/activate  # Mac/Linux
# 或 venv\Scripts\activate  # Windows
pip install spotdl
```

---

### 2. `ModuleNotFoundError: No module named 'fastapi'`

**原因**: 增强功能依赖未安装

**解决方案**:

```bash
# 方式1: 使用启动脚本（自动处理）
./start.sh

# 方式2: 手动安装
source venv/bin/activate
pip install fastapi uvicorn

# 方式3: 使用原生 spotDL（不需要这些依赖）
python3 -m spotdl [链接]
```

---

### 3. `error: externally-managed-environment`

**原因**: 系统 Python 被包管理器管理，禁止直接安装包

**解决方案（推荐使用虚拟环境）**:

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# 在虚拟环境中安装
pip install spotdl
```

**备选方案（不推荐）**:
```bash
pip install spotdl --break-system-packages
```

---

### 4. `FFmpeg not found`

**原因**: FFmpeg 未安装或不在 PATH

**解决方案**:

```bash
# 方式1: 让 spotDL 自动安装
spotdl --download-ffmpeg

# 方式2: 系统级安装
# macOS
brew install ffmpeg

# Linux (Ubuntu/Debian)
sudo apt update && sudo apt install ffmpeg

# Linux (Fedora)
sudo dnf install ffmpeg

# Windows
# 下载并添加到 PATH: https://ffmpeg.org/download.html
```

**验证安装**:
```bash
ffmpeg -version
```

---

### 5. `zsh: command not found: spotdl`

**原因**: spotDL 可执行文件不在 PATH 中

**解决方案**:

```bash
# 方式1: 作为模块运行
python3 -m spotdl [链接]

# 方式2: 激活虚拟环境
source venv/bin/activate
spotdl [链接]

# 方式3: 添加到 PATH (全局安装)
# 找到 spotdl 位置
python3 -m pip show spotdl

# 添加到 PATH (~/.zshrc 或 ~/.bashrc)
export PATH="$HOME/.local/bin:$PATH"
```

---

### 6. `HTTP Error 429: Too Many Requests`

**原因**: API 请求过于频繁，被限流

**解决方案**:

```bash
# 等待几分钟后重试

# 减少并发线程数
spotdl [链接] --threads 1

# 使用延迟
spotdl [链接] --delay 2
```

---

### 7. 下载速度非常慢

**原因**: 这是正常的！完整流程需要时间

**说明**:

每首歌的完整流程约需 **20-45秒**：

- 🔍 连接 Spotify API：3-5秒
- 🎵 YouTube 搜索匹配：2-3秒
- ⬇️ 音频下载：10-30秒（最慢）
- 🎼 FFmpeg 转码：2-5秒
- 📝 元数据处理：1-2秒

**优化建议**:

1. 使用更快的网络
2. 选择较低音质（下载更快）
3. 增强版 Web UI 有详细步骤提示，不会让你误以为卡死
4. 批量下载时自动并发处理

---

### 8. 找不到匹配的歌曲

**原因**: YouTube 搜索未找到匹配的音频

**解决方案**:

```bash
# 尝试调整搜索提供商
spotdl [链接] --audio-provider youtube-music

# 手动指定 YouTube URL
spotdl [链接] --yt-dlp-args "--default-search ytsearch"

# 降低匹配要求
spotdl [链接] --restrict false
```

---

### 9. 歌词未下载

**原因**: 多个可能原因

**解决方案**:

```bash
# 1. 确保启用歌词下载
spotdl [链接] --lyrics providers musixmatch,genius

# 2. 使用增强功能（自动下载 LRC 歌词）
python3 download_batch.py "[链接]"

# 3. 歌曲可能真的没有歌词
# 某些器乐曲或小众歌曲可能找不到歌词
```

**检查可用的歌词提供商**:
- Genius (英文歌词)
- Musixmatch (Spotify 使用的服务)
- Deezer/NetEase (通过 syncedlyrics)
- AZLyrics (备选)

---

### 10. 权限错误 (Permission denied)

**原因**: 没有写入权限或可执行权限

**解决方案**:

```bash
# Mac/Linux: 添加执行权限
chmod +x start.sh
chmod +x spotdl

# 更改输出目录权限
sudo chmod 755 /path/to/output

# 或使用用户目录
spotdl [链接] --output ~/Music

# Windows: 以管理员身份运行
# 右键 > 以管理员身份运行
```

---

### 11. 元数据不正确或缺失

**原因**: Spotify API 数据不完整或下载源问题

**解决方案**:

```bash
# 更新已存在文件的元数据
spotdl meta song.mp3

# 强制重新下载
spotdl [链接] --overwrite force

# 使用增强功能（更详细的元数据）
python3 download_batch.py "[链接]"
```

---

### 12. 虚拟环境问题

**问题**: 依赖冲突或环境错乱

**解决方案**:

```bash
# 完全重建虚拟环境
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install spotdl
pip install fastapi uvicorn

# 或使用启动脚本自动处理
./start.sh
```

---

## 🔍 调试技巧

### 启用详细日志

```bash
# 查看详细输出
spotdl [链接] --log-level DEBUG

# 保存日志到文件
spotdl [链接] --log-level DEBUG 2> debug.log
```

### 查看版本信息

```bash
# spotDL 版本
spotdl --version

# Python 版本
python --version

# FFmpeg 版本
ffmpeg -version

# 查看依赖版本
pip list | grep -E 'spotdl|spotipy|ytmusicapi|mutagen'
```

### 测试网络连接

```bash
# 测试 Spotify API
curl https://api.spotify.com/v1

# 测试 YouTube 访问
curl https://www.youtube.com

# 测试 Genius API
curl https://api.genius.com
```

---

## 💡 常见问题 (FAQ)

### Q1: 为什么下载的不是 Spotify 的音频？

**A**: spotDL **不从 Spotify 下载音频**。流程是：

1. 从 Spotify API 获取元数据
2. 在 YouTube 搜索匹配音频
3. 从 YouTube 下载
4. 嵌入 Spotify 元数据

这是设计使然，避免违反 Spotify 服务条款。

---

### Q2: 音频质量如何？

**A**: 取决于 YouTube 源：

- 标准用户: 128 kbps
- YouTube Music Premium: 256 kbps

虽然不是无损，但对日常听歌足够。

---

### Q3: 可以下载私有播放列表吗？

**A**: 需要提供 Spotify Cookie：

```bash
spotdl [链接] --cookie-file cookies.txt
```

如何获取 Cookie：
1. 在浏览器登录 Spotify
2. 打开开发者工具 (F12)
3. 导出 Cookie

---

### Q4: 为什么有些歌曲找不到？

**A**: 可能原因：

- 地区限制（某些歌曲仅在特定地区可用）
- YouTube 上没有对应音频
- 歌曲已从 Spotify 下架
- 网络问题

尝试使用 VPN 或手动指定 YouTube 链接。

---

### Q5: 如何批量下载多个播放列表？

**A**: 

```bash
# 方式1: 直接指定多个 URL
spotdl [URL1] [URL2] [URL3]

# 方式2: 从文件读取
spotdl $(cat urls.txt)

# 方式3: 使用增强功能的批量下载
# 在 Web UI 的"批量下载"标签页输入多个 URL
```

---

### Q6: 下载的文件名乱码怎么办？

**A**: 

```bash
# 自定义文件名格式，避免特殊字符
spotdl [链接] --output "{artist} - {title}.{output-ext}"

# 移除特殊字符
spotdl [链接] --restrict-filenames
```

---

### Q7: 如何获取繁体/简体中文歌词？

**A**: 歌词来源（Musixmatch, NetEase）会提供原始字符。通常已匹配 Spotify 显示的内容。

如需转换：

```bash
# 安装 opencc
pip install opencc-python-reimplemented

# 在代码中转换
from opencc import OpenCC
cc = OpenCC('s2t')  # 简体转繁体
cc = OpenCC('t2s')  # 繁体转简体
```

---

### Q8: 增强功能和原生 spotDL 有什么区别？

**A**:

| 特性 | 原生 spotDL | 增强功能 |
|------|:-----------:|:--------:|
| 文件组织 | 单一目录 | 独立目录 |
| LRC歌词文件 | ❌ | ✅ |
| 独立封面 | ❌ | ✅ |
| 元数据报告 | ❌ | ✅ TXT+JSON |
| 实时步骤提示 | 基础 | ✅ 详细 |
| 零配置启动 | ❌ | ✅ |

**推荐**: 如果需要完整的音乐库管理，使用增强功能。

---

## 🆘 获取帮助

如果以上方法都无法解决问题：

1. **搜索已知问题**: https://github.com/spotDL/spotify-downloader/issues
2. **提交新 Issue**: https://github.com/spotDL/spotify-downloader/issues/new
3. **加入 Discord**: https://discord.gg/xCa23pwJWY
4. **查看官方文档**: https://spotdl.readthedocs.io
5. **查看中文 README**: [README_CN.md](../README_CN.md)

提问时请提供：
- spotDL 版本 (`spotdl --version`)
- Python 版本 (`python --version`)
- 操作系统
- 完整错误信息
- 重现步骤

---

## 📚 相关文档

- [安装指南](installation_zh.md) - 安装问题
- [使用指南](usage_zh.md) - 使用方法
- [中文 README](../README_CN.md) - 功能说明
- [技术架构](../ARCHITECTURE_CN.md) - 系统架构

