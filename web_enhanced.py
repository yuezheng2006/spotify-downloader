#!/usr/bin/env python3
"""
spotDL 增强版 Web UI
===================

提供与官方Web UI相同的界面，但输出完整元数据结构
- 每首歌独立目录
- LRC歌词 + 封面 + 元数据报告

使用方法：
  python3 web_enhanced.py [--port 8800] [--host 127.0.0.1]

访问：
  http://127.0.0.1:8800
"""

import os
import sys
import json
import asyncio
import argparse
import zipfile
import shutil
from pathlib import Path
from typing import List, Dict, Optional
from datetime import datetime

from fastapi import FastAPI, HTTPException, BackgroundTasks, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
import uvicorn

# 导入我们的批量下载器
from download_batch import SpotifyBatchDownloader


# ============================================================================
# 数据模型
# ============================================================================

class DownloadRequest(BaseModel):
    """下载请求模型"""
    url: str
    format: str = "mp3"
    output_dir: str = "downloads"
    max_songs: Optional[int] = None


class DownloadStatus(BaseModel):
    """下载状态模型"""
    id: str
    url: str
    status: str  # pending, downloading, completed, failed
    progress: int = 0
    total: int = 0
    current_song: str = ""
    message: str = ""
    output_dir: str = ""
    files: List[Dict[str, str]] = []


# ============================================================================
# 全局状态管理
# ============================================================================

app = FastAPI(title="spotDL Enhanced Web UI", version="1.0.0")

# 允许跨域（与官方Web UI保持一致）
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 下载任务存储
download_tasks: Dict[str, DownloadStatus] = {}


# ============================================================================
# API 端点
# ============================================================================

@app.get("/")
async def root():
    """根路径 - 返回静态HTML页面"""
    return {
        "name": "spotDL Enhanced Web UI",
        "version": "1.0.0",
        "message": "增强版Web UI - 完整元数据支持",
        "features": [
            "每首歌独立目录",
            "LRC同步歌词",
            "高清专辑封面",
            "完整元数据报告"
        ]
    }


@app.get("/api/status")
async def get_status():
    """获取服务状态"""
    return {
        "status": "running",
        "version": "1.0.0",
        "active_downloads": len([t for t in download_tasks.values() if t.status == "downloading"]),
        "total_downloads": len(download_tasks)
    }


@app.post("/api/download")
async def create_download(request: DownloadRequest, background_tasks: BackgroundTasks):
    """创建下载任务"""
    
    # 生成任务ID
    task_id = f"task_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(download_tasks)}"
    
    # 创建任务状态
    status = DownloadStatus(
        id=task_id,
        url=request.url,
        status="pending",
        output_dir=request.output_dir
    )
    
    download_tasks[task_id] = status
    
    # 在后台执行下载
    background_tasks.add_task(
        execute_download,
        task_id,
        request.url,
        request.format,
        request.output_dir,
        request.max_songs
    )
    
    return {
        "task_id": task_id,
        "status": "pending",
        "message": "下载任务已创建"
    }


@app.get("/api/download/{task_id}")
async def get_download_status(task_id: str):
    """获取下载任务状态"""
    if task_id not in download_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    return download_tasks[task_id]


@app.get("/api/downloads")
async def list_downloads():
    """列出所有下载任务"""
    return {
        "tasks": list(download_tasks.values()),
        "total": len(download_tasks)
    }


@app.delete("/api/download/{task_id}")
async def delete_download(task_id: str):
    """删除下载任务记录"""
    if task_id not in download_tasks:
        raise HTTPException(status_code=404, detail="任务不存在")
    
    del download_tasks[task_id]
    return {"message": "任务已删除"}


@app.get("/api/download/file")
async def download_file(file_path: str = Query(..., description="文件路径，相对于downloads目录")):
    """下载单个文件"""
    try:
        # 安全检查：确保路径在downloads目录内
        downloads_dir = Path("downloads").resolve()
        full_path = (downloads_dir / file_path).resolve()
        
        # 检查路径是否在downloads目录内（防止路径遍历攻击）
        if not str(full_path).startswith(str(downloads_dir)):
            raise HTTPException(status_code=403, detail="访问被拒绝：路径不安全")
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="文件不存在")
        
        if full_path.is_dir():
            raise HTTPException(status_code=400, detail="这是一个目录，请使用 /api/download/dir 下载")
        
        return FileResponse(
            str(full_path),
            filename=full_path.name,
            media_type='application/octet-stream'
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载失败: {str(e)}")


@app.get("/api/download/dir")
async def download_directory(dir_path: str = Query(..., description="目录路径，相对于downloads目录")):
    """下载整个目录（打包为zip）"""
    try:
        # 安全检查：确保路径在downloads目录内
        downloads_dir = Path("downloads").resolve()
        full_path = (downloads_dir / dir_path).resolve()
        
        # 检查路径是否在downloads目录内
        if not str(full_path).startswith(str(downloads_dir)):
            raise HTTPException(status_code=403, detail="访问被拒绝：路径不安全")
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="目录不存在")
        
        if not full_path.is_dir():
            raise HTTPException(status_code=400, detail="这不是一个目录")
        
        # 创建临时zip文件
        zip_path = Path(f"/tmp/{full_path.name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.zip")
        
        def generate_zip():
            with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                for file_path in full_path.rglob('*'):
                    if file_path.is_file():
                        arcname = file_path.relative_to(full_path)
                        zipf.write(file_path, arcname)
            
            # 读取zip文件并删除
            with open(zip_path, 'rb') as f:
                data = f.read()
            zip_path.unlink()
            return data
        
        zip_data = generate_zip()
        
        return StreamingResponse(
            iter([zip_data]),
            media_type='application/zip',
            headers={
                "Content-Disposition": f"attachment; filename={full_path.name}.zip"
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"打包失败: {str(e)}")


@app.get("/api/files/list")
async def list_files(dir_path: str = Query("", description="目录路径，相对于downloads目录")):
    """列出下载的文件"""
    try:
        downloads_dir = Path("downloads").resolve()
        full_path = (downloads_dir / dir_path).resolve() if dir_path else downloads_dir
        
        # 安全检查
        if not str(full_path).startswith(str(downloads_dir)):
            raise HTTPException(status_code=403, detail="访问被拒绝：路径不安全")
        
        if not full_path.exists():
            raise HTTPException(status_code=404, detail="目录不存在")
        
        files = []
        dirs = []
        
        for item in sorted(full_path.iterdir()):
            relative_path = str(item.relative_to(downloads_dir))
            if item.is_dir():
                dirs.append({
                    "name": item.name,
                    "path": relative_path,
                    "type": "directory"
                })
            else:
                files.append({
                    "name": item.name,
                    "path": relative_path,
                    "type": "file",
                    "size": item.stat().st_size,
                    "download_url": f"/api/download/file?file_path={relative_path}"
                })
        
        return {
            "current_path": dir_path or ".",
            "directories": dirs,
            "files": files
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"列出文件失败: {str(e)}")


# ============================================================================
# 下载执行逻辑
# ============================================================================

async def execute_download(
    task_id: str,
    url: str,
    audio_format: str,
    output_dir: str,
    max_songs: Optional[int]
):
    """执行下载任务"""
    
    status = download_tasks[task_id]
    status.status = "downloading"
    status.message = "正在初始化下载..."
    
    print(f"\n{'='*60}")
    print(f"[{task_id}] 开始下载任务")
    print(f"URL: {url}")
    print(f"格式: {audio_format}, 输出: {output_dir}")
    print(f"{'='*60}\n")
    
    try:
        # 创建下载器
        print(f"[{task_id}] 创建下载器...")
        downloader = SpotifyBatchDownloader(
            output_dir=output_dir,
            audio_format=audio_format,
            max_songs=max_songs
        )
        
        # 检测URL类型
        print(f"[{task_id}] 检测URL类型...")
        url_type = downloader.detect_url_type(url)
        status.message = f"检测到类型: {url_type}"
        print(f"[{task_id}] URL类型: {url_type}")
        
        # 如果是单曲，直接使用download_song
        if url_type == 'track':
            print(f"[{task_id}] 单曲模式，直接下载...")
            status.message = "正在下载单曲..."
            status.total = 1
            
            try:
                result = await asyncio.to_thread(downloader.download_song, url)
                if result and isinstance(result, dict):
                    # 检查是否是错误结果
                    if result.get("error"):
                        error_msg = result.get("message", "下载失败")
                        raise Exception(error_msg)
                    
                    # 成功结果（可能是完整下载或仅元数据）
                    is_metadata_only = result.get("metadata_only", False)
                    status.files.append({
                        "name": result["song_name"],
                        "path": result["directory"],
                        "files": result["files"],
                        "metadata_only": is_metadata_only
                    })
                    status.progress = 1
                    if is_metadata_only:
                        print(f"[{task_id}] ✅ 已获取元数据和歌词（无音频文件）: {result['song_name']}")
                        status.message = f"已获取元数据和歌词（音频文件未下载）"
                    else:
                        print(f"[{task_id}] ✅ 下载成功: {result['song_name']}")
                        status.message = f"下载完成！"
                else:
                    error_detail = "下载返回空结果"
                    if result is False:
                        error_detail = "spotdl命令执行失败，请检查错误日志"
                    raise Exception(error_detail)
            except Exception as e:
                error_msg = str(e)
                print(f"[{task_id}] ❌ 下载失败: {error_msg}")
                import traceback
                traceback.print_exc()
                raise Exception(error_msg)  # 直接抛出原始错误信息，不重复包装
        else:
            # 批量下载：获取歌曲列表（已下载到临时目录）
            print(f"[{task_id}] 批量模式，获取歌曲列表...")
            status.message = "正在获取歌曲列表..."
            audio_files = await asyncio.to_thread(downloader.get_songs_list, url)
            status.total = len(audio_files)
            status.message = f"找到 {len(audio_files)} 首歌曲"
            print(f"[{task_id}] 找到 {len(audio_files)} 首歌曲")
            
            # 处理每首已下载的歌曲
            downloaded_files = []
            for i, audio_file in enumerate(audio_files, 1):
                status.progress = i
                status.current_song = f"正在处理第 {i}/{len(audio_files)} 首"
                print(f"\n[{task_id}] 处理进度: {i}/{len(audio_files)}")
                print(f"[{task_id}] 文件: {audio_file}")
                
                try:
                    # 处理已下载的文件
                    result = await asyncio.to_thread(
                        downloader.process_single_file,
                        audio_file
                    )
                    
                    if result:
                        downloaded_files.append(result)
                        status.files.append({
                            "name": result["song_name"],
                            "path": result["directory"],
                            "files": result["files"]
                        })
                        print(f"[{task_id}] ✅ 处理成功: {result['song_name']}")
                    else:
                        print(f"[{task_id}] ⚠️  处理返回空结果")
                    
                except Exception as e:
                    print(f"[{task_id}] ❌ 处理失败: {str(e)}")
                    import traceback
                    traceback.print_exc()
                    continue
            
            # 清理临时目录
            temp_dir = downloader.output_dir / "temp"
            try:
                for f in temp_dir.glob("*"):
                    f.unlink()
                temp_dir.rmdir()
            except Exception as e:
                print(f"[{task_id}] ⚠️  清理临时目录失败: {e}")
        
        # 完成
        status.status = "completed"
        status.progress = status.total
        if url_type == 'track':
            status.message = f"下载完成！"
        else:
            downloaded_count = len(status.files)
            status.message = f"下载完成！成功 {downloaded_count}/{status.total} 首"
        print(f"\n[{task_id}] ✅ 任务完成！")
        if url_type != 'track':
            print(f"[{task_id}] 成功: {len(status.files)}/{status.total}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        status.status = "failed"
        status.message = f"下载失败: {str(e)}"
        print(f"\n[{task_id}] ❌ 任务失败: {str(e)}")
        import traceback
        traceback.print_exc()
        print(f"{'='*60}\n")


# ============================================================================
# 静态文件服务（简单HTML界面）
# ============================================================================

@app.get("/ui")
async def web_ui():
    """返回改进的Web界面"""
    html_content = """
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>spotDL Enhanced - 增强版Web UI</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 900px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }
        h1 {
            color: #333;
            margin-bottom: 10px;
            font-size: 32px;
        }
        .subtitle {
            color: #666;
            margin-bottom: 30px;
            font-size: 14px;
        }
        .features {
            background: #f8f9ff;
            border-radius: 10px;
            padding: 20px;
            margin-bottom: 30px;
        }
        .feature-item {
            display: flex;
            align-items: center;
            margin: 10px 0;
            color: #555;
        }
        .feature-item::before {
            content: "✓";
            color: #667eea;
            font-weight: bold;
            margin-right: 10px;
            font-size: 18px;
        }
        
        /* 标签页样式 */
        .tabs {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
            border-bottom: 2px solid #e0e0e0;
        }
        .tab {
            padding: 12px 24px;
            background: transparent;
            border: none;
            color: #666;
            font-size: 15px;
            font-weight: 500;
            cursor: pointer;
            border-bottom: 3px solid transparent;
            transition: all 0.3s;
        }
        .tab:hover {
            color: #667eea;
        }
        .tab.active {
            color: #667eea;
            border-bottom-color: #667eea;
        }
        
        /* 标签内容 */
        .tab-content {
            display: none;
        }
        .tab-content.active {
            display: block;
        }
        
        .input-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            margin-bottom: 8px;
            color: #333;
            font-weight: 500;
        }
        input, select, textarea {
            width: 100%;
            padding: 12px;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            font-size: 14px;
            transition: border-color 0.3s;
            font-family: inherit;
        }
        textarea {
            min-height: 120px;
            resize: vertical;
        }
        input:focus, select:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
        }
        .input-hint {
            font-size: 12px;
            color: #999;
            margin-top: 5px;
        }
        
        /* 快捷按钮 */
        .quick-actions {
            display: flex;
            gap: 10px;
            margin-bottom: 20px;
        }
        .quick-btn {
            flex: 1;
            padding: 10px;
            background: #f8f9ff;
            border: 2px solid #e0e0e0;
            border-radius: 8px;
            color: #667eea;
            font-size: 13px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .quick-btn:hover {
            background: #667eea;
            color: white;
            border-color: #667eea;
        }
        
        button.download-btn {
            width: 100%;
            padding: 15px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            border-radius: 8px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: transform 0.2s;
        }
        button.download-btn:hover {
            transform: translateY(-2px);
        }
        button.download-btn:disabled {
            opacity: 0.5;
            cursor: not-allowed;
            transform: none;
        }
        
        .status {
            margin-top: 30px;
            padding: 20px;
            background: #f8f9ff;
            border-radius: 10px;
            display: none;
        }
        .status.show {
            display: block;
        }
        .progress-bar {
            width: 100%;
            height: 8px;
            background: #e0e0e0;
            border-radius: 4px;
            overflow: hidden;
            margin: 15px 0;
        }
        .progress-fill {
            height: 100%;
            background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
            transition: width 0.3s;
        }
        .task-list {
            margin-top: 20px;
        }
        .task-item {
            padding: 15px;
            background: white;
            border-radius: 8px;
            margin: 10px 0;
            border-left: 4px solid #667eea;
        }
        
        /* 加载动画 */
        .loading-dots {
            display: inline-block;
        }
        .loading-dots::after {
            content: '';
            animation: dots 1.5s steps(4, end) infinite;
        }
        @keyframes dots {
            0%, 20% { content: ''; }
            40% { content: '.'; }
            60% { content: '..'; }
            80%, 100% { content: '...'; }
        }
        
        /* 脉冲动画 */
        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        .pulsing {
            animation: pulse 2s ease-in-out infinite;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🎵 spotDL Enhanced</h1>
        <div class="subtitle">增强版 - 完整元数据支持</div>
        
        <div class="features">
            <div class="feature-item">每首歌独立目录</div>
            <div class="feature-item">LRC同步歌词文件</div>
            <div class="feature-item">高清专辑封面</div>
            <div class="feature-item">完整元数据报告 (TXT + JSON)</div>
        </div>
        
        <!-- 标签页 -->
        <div class="tabs">
            <button class="tab active" onclick="switchTab('single')">🎵 单曲/专辑</button>
            <button class="tab" onclick="switchTab('batch')">📝 批量下载</button>
            <button class="tab" onclick="switchTab('settings')">⚙️ 设置</button>
        </div>
        
        <!-- 单曲/专辑下载 -->
        <div id="single" class="tab-content active">
            <div class="input-group">
                <label for="url">Spotify URL</label>
                <input type="text" id="url" placeholder="https://open.spotify.com/track/... 或 /album/..." />
                <div class="input-hint">支持单曲 (track) 或专辑 (album) 链接</div>
            </div>
            
            <div class="quick-actions">
                <button class="quick-btn" onclick="setExampleUrl('track')">示例：单曲</button>
                <button class="quick-btn" onclick="setExampleUrl('album')">示例：专辑</button>
                <button class="quick-btn" onclick="setExampleUrl('playlist')">示例：播放列表</button>
            </div>
        </div>
        
        <!-- 批量下载 -->
        <div id="batch" class="tab-content">
            <div class="input-group">
                <label for="batchUrls">批量URL（每行一个）</label>
                <textarea id="batchUrls" placeholder="https://open.spotify.com/track/...
https://open.spotify.com/album/...
https://open.spotify.com/playlist/..."></textarea>
                <div class="input-hint">每行输入一个URL，支持单曲/专辑/播放列表/艺术家</div>
            </div>
        </div>
        
        <!-- 设置 -->
        <div id="settings" class="tab-content">
            <div class="input-group">
                <label for="format">音频格式</label>
                <select id="format">
                    <option value="mp3">MP3（推荐，兼容性好）</option>
                    <option value="flac">FLAC（无损，文件大）</option>
                    <option value="wav">WAV（无损未压缩）</option>
                    <option value="m4a">M4A（Apple设备）</option>
                    <option value="ogg">OGG（开源格式）</option>
                    <option value="opus">OPUS（高效压缩）</option>
                </select>
            </div>
            
            <div class="input-group">
                <label for="output">输出目录</label>
                <input type="text" id="output" value="downloads" />
                <div class="input-hint">所有歌曲将保存在此目录下的独立文件夹中</div>
            </div>
            
            <div class="input-group">
                <label for="maxSongs">最大歌曲数（艺术家模式）</label>
                <input type="number" id="maxSongs" value="20" min="1" max="100" />
                <div class="input-hint">下载艺术家链接时的最大歌曲数量</div>
            </div>
        </div>
        
        <button class="download-btn" id="downloadBtn" onclick="startDownload()">开始下载</button>
        
        <div id="status" class="status">
            <h3>下载状态</h3>
            <div id="statusMessage" class="pulsing">准备中<span class="loading-dots"></span></div>
            <div id="currentStep" style="font-size: 13px; color: #999; margin-top: 8px;">等待任务开始...</div>
            <div class="progress-bar">
                <div id="progressFill" class="progress-fill" style="width: 0%"></div>
            </div>
            <div id="progressText">0 / 0</div>
            
            <!-- 耗时提示 -->
            <div style="background: #fff3cd; padding: 12px; border-radius: 6px; margin: 15px 0; font-size: 13px; color: #856404;">
                <strong>💡 温馨提示：</strong><br/>
                • 初始化连接约需 <strong>3-5秒</strong>（连接Spotify + 搜索YouTube）<br/>
                • 音频下载约需 <strong>10-30秒/首</strong>（取决于网速和歌曲长度）<br/>
                • 整个流程包括：<span style="color: #667eea;">元数据获取 → YouTube搜索 → 音频下载 → 格式转换 → 歌词获取</span><br/>
                • 请耐心等待，系统正在后台努力工作中...
            </div>
            
            <div id="taskList" class="task-list"></div>
        </div>
    </div>
    
    <script>
        let currentTaskId = null;
        let currentTab = 'single';
        
        // 切换标签页
        function switchTab(tabName) {
            // 更新标签按钮状态
            document.querySelectorAll('.tab').forEach(tab => {
                tab.classList.remove('active');
            });
            event.target.classList.add('active');
            
            // 更新内容显示
            document.querySelectorAll('.tab-content').forEach(content => {
                content.classList.remove('active');
            });
            document.getElementById(tabName).classList.add('active');
            
            currentTab = tabName;
        }
        
        // 设置示例URL
        function setExampleUrl(type) {
            const examples = {
                'track': 'https://open.spotify.com/track/0Id7swY6cWbvYLtVVF0wvq',
                'album': 'https://open.spotify.com/album/0E5yojmnEdbs68b1wM6Kla',
                'playlist': 'https://open.spotify.com/playlist/37i9dQZEVXbMDoHDwVN2tF'
            };
            document.getElementById('url').value = examples[type] || '';
        }
        
        // 开始下载
        async function startDownload() {
            let urls = [];
            
            // 根据当前标签页获取URL
            if (currentTab === 'single') {
                const url = document.getElementById('url').value.trim();
                if (!url) {
                    alert('请输入Spotify URL');
                    return;
                }
                urls = [url];
            } else if (currentTab === 'batch') {
                const batchText = document.getElementById('batchUrls').value.trim();
                if (!batchText) {
                    alert('请输入至少一个URL');
                    return;
                }
                urls = batchText.split('\\n').filter(u => u.trim());
            } else {
                alert('请切换到下载标签页');
                return;
            }
            
            const format = document.getElementById('format').value;
            const output = document.getElementById('output').value;
            const maxSongs = parseInt(document.getElementById('maxSongs').value);
            
            const btn = document.getElementById('downloadBtn');
            const status = document.getElementById('status');
            
            btn.disabled = true;
            btn.textContent = '下载中...';
            status.classList.add('show');
            
            // 批量下载处理
            if (urls.length > 1) {
                document.getElementById('statusMessage').textContent = 
                    `批量下载模式：共 ${urls.length} 个链接`;
                
                let successCount = 0;
                let failCount = 0;
                
                for (let i = 0; i < urls.length; i++) {
                    const url = urls[i];
                    document.getElementById('statusMessage').textContent = 
                        `正在处理 ${i + 1}/${urls.length}: ${url.substring(0, 50)}...`;
                    
                    try {
                        await downloadSingle(url, format, output, maxSongs);
                        successCount++;
                    } catch (error) {
                        console.error(`下载失败: ${url}`, error);
                        failCount++;
                    }
                    
                    await new Promise(resolve => setTimeout(resolve, 1000));
                }
                
                document.getElementById('statusMessage').textContent = 
                    `✅ 批量下载完成！成功: ${successCount}, 失败: ${failCount}`;
                btn.disabled = false;
                btn.textContent = '开始下载';
                
            } else {
                // 单个下载
                try {
                    await downloadSingle(urls[0], format, output, maxSongs);
                } catch (error) {
                    alert('下载失败: ' + error.message);
                    btn.disabled = false;
                    btn.textContent = '开始下载';
                }
            }
        }
        
        // 下载单个URL
        async function downloadSingle(url, format, output, maxSongs) {
            const response = await fetch('/api/download', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    url, 
                    format, 
                    output_dir: output,
                    max_songs: maxSongs
                })
            });
            
            if (!response.ok) {
                throw new Error('创建下载任务失败');
            }
            
            const data = await response.json();
            currentTaskId = data.task_id;
            
            // 轮询状态
            await pollStatus();
        }
        
        // 轮询下载状态
        async function pollStatus() {
            if (!currentTaskId) return;
            
            try {
                const response = await fetch(`/api/download/${currentTaskId}`);
                const task = await response.json();
                
                // 更新主状态消息
                document.getElementById('statusMessage').textContent = task.message;
                
                // 更新详细步骤提示
                const stepEl = document.getElementById('currentStep');
                if (task.status === 'downloading') {
                    if (task.progress === 0 && task.total === 0) {
                        stepEl.textContent = '🔍 正在连接Spotify API，获取歌曲信息...';
                        stepEl.style.color = '#667eea';
                    } else if (task.progress === 0 && task.total > 0) {
                        stepEl.textContent = '🎵 已找到歌曲，准备在YouTube搜索匹配音频...';
                        stepEl.style.color = '#667eea';
                    } else if (task.current_song) {
                        stepEl.textContent = `⬇️ ${task.current_song} - 正在从YouTube下载音频...`;
                        stepEl.style.color = '#28a745';
                    }
                } else if (task.status === 'completed') {
                    stepEl.textContent = '✅ 所有任务已完成！';
                    stepEl.style.color = '#28a745';
                } else if (task.status === 'failed') {
                    stepEl.textContent = '❌ 任务失败';
                    stepEl.style.color = '#dc3545';
                }
                
                // 更新进度
                document.getElementById('progressText').textContent = 
                    `${task.progress} / ${task.total}`;
                
                const progress = task.total > 0 ? (task.progress / task.total * 100) : 0;
                document.getElementById('progressFill').style.width = progress + '%';
                
                // 显示文件列表
                if (task.files && task.files.length > 0) {
                    const taskList = document.getElementById('taskList');
                    taskList.innerHTML = '<h4>已完成:</h4>' + 
                        task.files.map(f => {
                            const dirPath = encodeURIComponent(f.path);
                            const downloadDirUrl = `/api/download/dir?dir_path=${dirPath}`;
                            const fileItems = f.files.map(fileName => {
                                const filePath = encodeURIComponent(f.path + '/' + fileName);
                                const downloadFileUrl = `/api/download/file?file_path=${filePath}`;
                                return `<a href="${downloadFileUrl}" style="color: #667eea; text-decoration: none; margin-right: 10px;" download>📥 ${fileName}</a>`;
                            }).join('');
                            const isMetadataOnly = f.metadata_only || false;
                            return `<div class="task-item">
                                <div style="font-weight: 600; margin-bottom: 8px;">
                                    ${isMetadataOnly ? '⚠️' : '✓'} ${f.name}
                                    ${isMetadataOnly ? '<span style="font-size: 11px; color: #ff9800; margin-left: 8px;">(仅元数据)</span>' : ''}
                                </div>
                                <div style="font-size: 12px; color: #999; margin-top: 5px; margin-bottom: 10px;">
                                    📂 ${f.path}<br/>
                                    📄 ${f.files.join(', ')}
                                </div>
                                ${isMetadataOnly ? '<div style="background: #fff3cd; padding: 8px; border-radius: 4px; margin-bottom: 10px; font-size: 12px; color: #856404;">⚠️ 注意：音频文件未下载，仅获取了元数据和歌词</div>' : ''}
                                <div style="margin-top: 10px;">
                                    <a href="${downloadDirUrl}" style="display: inline-block; padding: 6px 12px; background: #667eea; color: white; text-decoration: none; border-radius: 4px; font-size: 13px; margin-right: 8px;" download>📦 下载整个目录 (ZIP)</a>
                                    <div style="margin-top: 8px;">
                                        ${fileItems}
                                    </div>
                                </div>
                            </div>`;
                        }).join('');
                }
                
                // 如果还在下载，继续轮询
                if (task.status === 'downloading' || task.status === 'pending') {
                    setTimeout(pollStatus, 1000);
                } else {
                    // 完成或失败
                    const btn = document.getElementById('downloadBtn');
                    btn.disabled = false;
                    btn.textContent = '开始下载';
                    
                    if (task.status === 'completed') {
                        document.getElementById('statusMessage').textContent = 
                            '✅ ' + task.message;
                    } else if (task.status === 'failed') {
                        document.getElementById('statusMessage').textContent = 
                            '❌ ' + task.message;
                    }
                }
                
            } catch (error) {
                console.error('获取状态失败:', error);
                const stepEl = document.getElementById('currentStep');
                stepEl.textContent = '⚠️ 无法获取状态，请检查网络连接';
                stepEl.style.color = '#dc3545';
            }
        }
    </script>
</body>
</html>
    """
    from fastapi.responses import HTMLResponse
    return HTMLResponse(content=html_content)


# ============================================================================
# 主函数
# ============================================================================

def main():
    import os
    parser = argparse.ArgumentParser(description="spotDL 增强版 Web UI")
    parser.add_argument("--host", default="0.0.0.0", help="监听地址")
    parser.add_argument("--port", type=int, default=int(os.getenv("PORT", 8800)), help="监听端口")
    parser.add_argument("--reload", action="store_true", help="开发模式（自动重载）")
    
    args = parser.parse_args()
    
    print("\n" + "=" * 60)
    print("🎵 spotDL Enhanced Web UI")
    print("=" * 60)
    print(f"\n✅ 服务启动成功!")
    print(f"\n📍 访问地址: http://{args.host}:{args.port}/ui")
    print(f"📍 API文档: http://{args.host}:{args.port}/docs")
    print("\n特性:")
    print("  • 每首歌独立目录")
    print("  • LRC同步歌词")
    print("  • 高清专辑封面")
    print("  • 完整元数据报告")
    print("\n按 Ctrl+C 停止服务\n")
    print("=" * 60 + "\n")
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        reload=args.reload,
        log_level="info"
    )


if __name__ == "__main__":
    main()

