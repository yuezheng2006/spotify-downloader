# 安装指南

本指南详细说明如何在各种操作系统上安装 spotDL 及其增强功能。

---

## 📋 系统要求

- **Python**: 3.10 或以上
- **FFmpeg**: 4.2 或以上
- **操作系统**: Windows, macOS, Linux
- **网络**: 稳定的互联网连接

---

## 🐍 方式1: Python 安装（推荐）

### 第一步：安装 spotDL

```bash
# 安装 spotDL
pip install spotdl

# 更新到最新版本
pip install --upgrade spotdl
```

> **提示**: 在某些系统上可能需要使用 `pip3` 替代 `pip`

### 第二步：安装 FFmpeg

**选项 A：安装到 spotDL 目录（推荐）**

```bash
spotdl --download-ffmpeg
```

这会将 FFmpeg 安装到 spotDL 的安装目录，不影响系统其他部分。

**选项 B：系统级安装**

=== "Windows"
    1. 下载 [FFmpeg](https://www.gyan.dev/ffmpeg/builds/)
    2. 解压到 `C:\ffmpeg`
    3. 添加 `C:\ffmpeg\bin` 到 PATH
    4. [详细教程](https://windowsloop.com/install-ffmpeg-windows-10/)

=== "macOS"
    ```bash
    brew install ffmpeg
    ```

=== "Linux (Ubuntu/Debian)"
    ```bash
    sudo apt update
    sudo apt install ffmpeg
    ```

=== "Linux (Fedora)"
    ```bash
    sudo dnf install ffmpeg
    ```

### 第三步：验证安装

```bash
# 检查 spotDL 版本
spotdl --version

# 检查 FFmpeg
ffmpeg -version
```

---

## 🎁 方式2: 预编译可执行文件

适合不想安装 Python 的用户。

1. 访问 [Releases 页面](https://github.com/spotDL/spotify-downloader/releases)
2. 下载适合您系统的版本：
   - Windows: `spotdl-windows.exe`
   - macOS: `spotdl-macos`
   - Linux: `spotdl-linux`
3. 将文件移动到合适位置
4. (macOS/Linux) 添加执行权限：`chmod +x spotdl-macos`

---

## 🐋 方式3: Docker

适合熟悉 Docker 的用户。

### 构建镜像

```bash
git clone https://github.com/spotDL/spotify-downloader
cd spotify-downloader
docker build -t spotdl .
```

### 运行容器

```bash
# 创建映射卷来访问下载的文件
docker run --rm -v $(pwd):/music spotdl download [Spotify链接]
```

---

## 📱 方式4: Termux (Android)

在 Android 设备上使用：

```bash
curl -L https://raw.githubusercontent.com/spotDL/spotify-downloader/master/scripts/termux.sh | sh
```

---

## 🏗️ 方式5: 从源码构建

适合开发者或需要最新功能的用户。

```bash
# 克隆仓库
git clone https://github.com/spotDL/spotify-downloader
cd spotify-downloader

# 安装 uv (快速 Python 包管理器)
pip install uv

# 同步依赖
uv sync

# 构建
uv run scripts/build.py
```

可执行文件将在 `dist/` 目录中创建。

---

## 🌟 安装增强功能（本仓库）

如果您想使用**完整元数据管理**功能（独立目录、LRC歌词、封面等）：

### 第一步：克隆本仓库

```bash
git clone https://github.com/yuezheng2006/spotify-downloader.git
cd spotify-downloader
```

### 第二步：创建虚拟环境

```bash
# 创建虚拟环境
python3 -m venv venv

# 激活虚拟环境
source venv/bin/activate  # Mac/Linux
# 或
venv\Scripts\activate     # Windows
```

### 第三步：安装依赖

```bash
# 安装 spotDL 本体
pip install -e .

# 安装增强功能依赖
pip install fastapi uvicorn
```

### 第四步：运行启动脚本

```bash
# 添加执行权限（Mac/Linux）
chmod +x start.sh

# 运行
./start.sh
```

`start.sh` 会自动：
- 检查并创建虚拟环境
- 安装缺失的依赖
- 提供菜单选择（Web UI / 命令行）

---

## 🔍 验证安装

### 基础功能测试

```bash
# 下载单曲测试
spotdl https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b
```

### 增强功能测试

```bash
# Web UI 测试
python3 web_enhanced.py

# 访问 http://127.0.0.1:8800/ui
```

```bash
# 命令行批量下载测试
python3 download_batch.py "https://open.spotify.com/track/0VjIjW4GlUZAMYd2vXMi3b"
```

---

## ⚠️ 常见安装问题

### 问题1: `pip: command not found`

**解决方案**:
```bash
# 使用 Python 模块方式
python3 -m pip install spotdl
```

### 问题2: `error: externally-managed-environment`

**解决方案**: 使用虚拟环境（推荐）
```bash
python3 -m venv venv
source venv/bin/activate
pip install spotdl
```

或使用 `--break-system-packages` (不推荐):
```bash
pip install spotdl --break-system-packages
```

### 问题3: `ModuleNotFoundError: No module named 'fastapi'`

**解决方案**: 增强功能需要额外依赖
```bash
source venv/bin/activate
pip install fastapi uvicorn
```

或直接使用 `start.sh`，它会自动安装。

### 问题4: FFmpeg 未找到

**解决方案**:
```bash
# 方式1: 让 spotDL 自动安装
spotdl --download-ffmpeg

# 方式2: 手动安装到 PATH
# 确保 'ffmpeg' 命令可以在终端运行
ffmpeg -version
```

### 问题5: 权限错误 (Permission denied)

**解决方案**:
```bash
# Mac/Linux
sudo chmod +x start.sh
sudo chmod +x spotdl

# 或使用 pip 的 --user 选项
pip install --user spotdl
```

---

## 📚 下一步

安装完成后，查看：

- [使用指南](usage_zh.md) - 学习如何使用 spotDL
- [故障排除](troubleshooting_zh.md) - 解决常见问题
- [中文 README](../README_CN.md) - 完整功能说明

---

## 🆘 需要帮助？

- 📖 [官方文档](https://spotdl.readthedocs.io)
- 💬 [Discord 社区](https://discord.gg/xCa23pwJWY)
- 🐛 [GitHub Issues](https://github.com/spotDL/spotify-downloader/issues)
- 📝 [中文 README](../README_CN.md)

