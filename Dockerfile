FROM python:3.11-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    ffmpeg \
    git \
    && rm -rf /var/lib/apt/lists/*

# 复制项目文件
COPY pyproject.toml ./
COPY spotdl ./spotdl
COPY web_enhanced.py ./
COPY download_batch.py ./

# 安装 Python 依赖
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -e . && \
    pip install --no-cache-dir fastapi uvicorn[standard]

# 创建下载目录
RUN mkdir -p /app/downloads

# 暴露端口
EXPOSE 8800

# 启动命令
CMD ["python3", "web_enhanced.py", "--host", "0.0.0.0", "--port", "8800"]
