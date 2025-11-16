# Zeabur 部署指南

## 📦 快速部署到 Zeabur

### 方式1: 通过 Git 仓库部署（推荐）

1. **在 Zeabur 创建新服务**
   - 访问你的项目: https://zeabur.com/projects/68dab811030e2df4a56b2e23
   - 点击 "Add Service" → "Git"
   - 选择你的 GitHub 仓库: `yuezheng2006/spotify-downloader`
   - 分支: `master`

2. **Zeabur 会自动识别**
   - Dockerfile (Docker 部署方式)
   - 或使用 requirements.txt (Python 部署方式)

3. **环境变量（可选）**
   ```
   PORT=8800
   ```

4. **等待部署完成**
   - Zeabur 会自动构建并启动服务
   - 分配域名，例如: `xxx.zeabur.app`

5. **访问你的 Web UI**
   - 访问: `https://your-service.zeabur.app/ui`

---

### 方式2: 本地 Docker 测试

部署前先在本地测试：

```bash
# 构建镜像
docker build -t spotdl-enhanced .

# 运行容器
docker run -p 8800:8800 spotdl-enhanced

# 访问
open http://localhost:8800/ui
```

---

## 🔧 配置文件说明

### Dockerfile
- 使用 Python 3.11-slim 基础镜像
- 自动安装 FFmpeg
- 安装所有必需依赖
- 暴露 8800 端口

### .dockerignore
- 排除不必要的文件（下载目录、Git、IDE配置等）
- 减小镜像大小

### requirements.txt
- 所有 Python 依赖列表
- Zeabur 可以直接使用此文件部署

### zbpack.json (可选)
- Zeabur 构建配置
- 指定启动命令和环境

---

## ⚙️ Zeabur 部署步骤详解

### Step 1: 推送配置到 GitHub

```bash
# 提交新的部署文件
git add Dockerfile .dockerignore requirements.txt
git commit -m "feat: 添加 Zeabur 部署配置"
git push origin master
```

### Step 2: 在 Zeabur 创建服务

1. 进入你的项目页面
2. 点击 **"Add Service"**
3. 选择 **"Git"**
4. 连接你的 GitHub 账号（如果还没连接）
5. 选择仓库: `yuezheng2006/spotify-downloader`
6. 选择分支: `master`
7. Zeabur 会自动检测到 Dockerfile

### Step 3: 配置服务（可选）

**设置环境变量**（如需要）:
- `PORT`: 8800 (通常 Zeabur 会自动设置)

**服务名称**: 
- 建议: `spotdl-enhanced`

### Step 4: 部署

1. 点击 "Deploy"
2. 等待构建完成（首次约 2-5 分钟）
3. 查看日志确认启动成功

### Step 5: 访问应用

Zeabur 会自动分配域名：
- 格式: `https://your-service-name-xxx.zeabur.app`
- 访问 Web UI: `https://your-service-name-xxx.zeabur.app/ui`

---

## 🌐 绑定自定义域名（可选）

1. 在 Zeabur 服务页面，点击 "Domains"
2. 添加你的域名
3. 配置 DNS 记录（按照 Zeabur 提示）

---

## 📊 资源需求

推荐配置：
- **CPU**: 0.5 - 1 vCPU
- **内存**: 1GB - 2GB
- **磁盘**: 5GB（用于临时下载）

---

## ⚠️ 注意事项

### 1. 下载文件持久化

Zeabur 容器重启后，`/app/downloads` 目录会清空。如需持久化：

**方案A: 使用 Zeabur Volumes**
```yaml
# 在 Zeabur 控制台添加 Volume
/app/downloads -> 持久化卷
```

**方案B: 集成云存储**
- 下载后自动上传到 S3/OSS
- 提供下载链接给用户

### 2. 环境变量

确保设置以下环境变量（如果需要）：
```bash
PORT=8800                    # Zeabur 自动设置
SPOTIFY_CLIENT_ID=xxx        # 如果使用 Spotify API
SPOTIFY_CLIENT_SECRET=xxx    # 如果使用 Spotify API
```

### 3. 日志查看

在 Zeabur 控制台可以查看实时日志：
- 构建日志
- 运行日志
- 错误日志

### 4. 性能优化

如果下载较慢：
- 升级 Zeabur 计划（更多 CPU/内存）
- 使用 CDN 加速
- 考虑多实例部署

---

## 🐛 故障排除

### 构建失败

**错误**: FFmpeg 安装失败
**解决**: Dockerfile 已包含 FFmpeg 安装

**错误**: Python 依赖冲突
**解决**: 检查 requirements.txt 版本

### 运行失败

**错误**: Port already in use
**解决**: Zeabur 会自动设置 PORT 环境变量，无需担心

**错误**: Module not found
**解决**: 确保 requirements.txt 包含所有依赖

### 下载失败

**错误**: YouTube 访问受限
**解决**: Zeabur 服务器通常可以访问 YouTube，如果不行考虑使用代理

---

## 📚 相关链接

- [Zeabur 文档](https://zeabur.com/docs)
- [Dockerfile 最佳实践](https://docs.docker.com/develop/develop-images/dockerfile_best-practices/)
- [FastAPI 部署指南](https://fastapi.tiangolo.com/deployment/)

---

## 🚀 部署后

部署成功后，你可以：

1. ✅ 通过 Web UI 下载 Spotify 音乐
2. ✅ 获取完整元数据（LRC、封面、元数据报告）
3. ✅ 分享链接给其他用户使用
4. ✅ 查看实时下载进度

**示例 URL**: `https://spotdl-enhanced.zeabur.app/ui`

---

## 💡 提示

- 首次部署可能需要 2-5 分钟构建
- 后续更新推送到 GitHub 后会自动重新部署
- 建议配置 HTTPS（Zeabur 自动提供）
- 可以配置 CI/CD 自动测试和部署

