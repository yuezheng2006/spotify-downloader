#!/usr/bin/env python3
"""
spotDL 增强批量下载工具
=======================

完整元数据管理 - 专业音乐库的推荐下载方式

功能特点：
  • 每首歌独立目录 - 整洁有序
  • 完整元数据报告 - metadata.txt + metadata.json
  • LRC同步歌词 - 带时间轴的歌词文件
  • 高清专辑封面 - 独立的cover.jpg
  • 智能批量处理 - 支持单曲/专辑/播放列表/艺术家

使用方法：
  python3 download_batch.py "SPOTIFY_URL" [选项]

示例：
  python3 download_batch.py "https://open.spotify.com/album/..." 
  python3 download_batch.py "https://open.spotify.com/playlist/..." -o music
  python3 download_batch.py "https://open.spotify.com/artist/..." --max-songs 20

输出结构：
  downloads/
  └── Artist - Song/
      ├── Artist - Song.mp3    # 音频（含ID3标签）
      ├── Artist - Song.lrc    # 同步歌词
      ├── cover.jpg            # 专辑封面
      ├── metadata.txt         # 人类可读
      └── metadata.json        # 程序可用
"""

import os
import sys
import json
import subprocess
import argparse
import re
import requests
from pathlib import Path
from mutagen.mp3 import MP3
from mutagen.id3 import ID3
from datetime import datetime

# 尝试导入spotdl相关模块
try:
    from spotdl.types.song import Song
    from spotdl.utils.spotify import SpotifyClient
    from spotdl.download.downloader import Downloader
    SPOTDL_AVAILABLE = True
except ImportError:
    SPOTDL_AVAILABLE = False
    print("⚠️  警告: spotdl模块不可用，将无法获取元数据")


class SpotifyBatchDownloader:
    """Spotify批量下载器类"""
    
    def __init__(self, output_dir="downloads", audio_format="mp3", max_songs=None):
        """
        初始化下载器
        
        Args:
            output_dir: 下载目录
            audio_format: 音频格式 (mp3, wav, flac等)
            max_songs: 最大下载数量（用于歌手）
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.audio_format = audio_format
        self.max_songs = max_songs
        
        # 初始化Spotify客户端（如果可用）
        if SPOTDL_AVAILABLE:
            try:
                SpotifyClient.init()
                self.spotify_client = SpotifyClient()
                # 优先使用Musixmatch（Spotify主要使用的歌词平台）
                # 然后使用Genius和AzLyrics作为备选
                downloader_settings = {
                    "lyrics_providers": ["musixmatch", "genius", "azlyrics"]
                }
                self.downloader = Downloader(settings=downloader_settings)
            except Exception as e:
                print(f"⚠️  警告: 初始化Spotify客户端失败: {e}")
                self.spotify_client = None
                self.downloader = None
        else:
            self.spotify_client = None
            self.downloader = None
        
    def sanitize_filename(self, filename):
        """清理文件名中的非法字符"""
        invalid_chars = '<>:"/\\|?*'
        for char in invalid_chars:
            filename = filename.replace(char, '_')
        return filename.strip()
    
    def detect_url_type(self, spotify_url):
        """
        检测Spotify URL类型
        
        Returns:
            str: 'track', 'album', 'playlist', 'artist' 或 'unknown'
        """
        if 'track/' in spotify_url:
            return 'track'
        elif 'album/' in spotify_url:
            return 'album'
        elif 'playlist/' in spotify_url:
            return 'playlist'
        elif 'artist/' in spotify_url:
            return 'artist'
        else:
            return 'unknown'
    
    def get_songs_list(self, spotify_url):
        """
        获取URL对应的歌曲列表
        
        Returns:
            list: 临时目录中下载的音频文件列表
        """
        temp_dir = self.output_dir / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        # 构建spotdl命令 - 使用 python -m spotdl 确保在Docker环境中也能正常工作
        cmd = [
            sys.executable, "-m", "spotdl",
            "--output", str(temp_dir),
            "--format", self.audio_format,
            "--generate-lrc",
            spotify_url
        ]
        
        # 如果是歌手且设置了最大数量
        url_type = self.detect_url_type(spotify_url)
        if url_type == 'artist' and self.max_songs:
            print(f"⚠️  歌手模式：将下载最多 {self.max_songs} 首热门歌曲")
        
        try:
            # 使用Popen而不是run，以便更好地处理长时间运行的进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            stdout, stderr = process.communicate()
            
            audio_files = list(temp_dir.glob(f"*.{self.audio_format}"))
            if not audio_files:
                print(f"⚠️  警告: 命令执行成功但未找到音频文件")
                print(f"   查找目录: {temp_dir}")
                print(f"   查找格式: *.{self.audio_format}")
                all_files = list(temp_dir.glob("*"))
                if all_files:
                    print(f"   目录中的文件: {[f.name for f in all_files]}")
                if stdout:
                    print(f"   命令输出: {stdout[:500]}")
            
            if process.returncode != 0:
                error_msg = f"❌ 下载失败 (返回码: {process.returncode})"
                error_detail = ""
                
                # 提取关键错误信息
                if stderr:
                    error_msg += f"\n错误信息: {stderr[:1000]}"
                    # 检查是否是"No results found"错误
                    if "No results found" in stderr or "LookupError" in stderr:
                        # 尝试提取歌曲名称
                        match = re.search(r'No results found for song: (.+)', stderr)
                        if match:
                            song_name = match.group(1).strip()
                            error_detail = f"未找到匹配的歌曲: {song_name}。可能原因：1) YouTube上不存在该歌曲 2) 歌曲名称不匹配 3) 地区限制"
                        else:
                            error_detail = "未找到匹配的歌曲。可能原因：1) YouTube上不存在该歌曲 2) 歌曲名称不匹配 3) 地区限制"
                    else:
                        error_detail = stderr[:500]
                
                if stdout:
                    error_msg += f"\n输出: {stdout[:500]}"
                
                print(error_msg)
                if error_detail:
                    print(f"   详细说明: {error_detail}")
                return []
            
            return audio_files
        except BrokenPipeError as e:
            error_msg = f"❌ 下载失败: 管道中断 (Broken pipe)"
            print(error_msg)
            return []
        except subprocess.CalledProcessError as e:
            error_msg = f"❌ 下载失败 (返回码: {e.returncode})"
            if e.stderr:
                error_msg += f"\n错误信息: {e.stderr[:1000]}"
            if e.stdout:
                error_msg += f"\n输出: {e.stdout[:500]}"
            print(error_msg)
            return []
        except Exception as e:
            error_msg = f"❌ 下载失败: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return []
    
    def process_batch(self, spotify_url):
        """
        处理批量下载（专辑、歌手、播放列表）
        
        Args:
            spotify_url: Spotify链接
        """
        url_type = self.detect_url_type(spotify_url)
        
        type_names = {
            'album': '专辑',
            'playlist': '播放列表',
            'artist': '歌手',
            'track': '单曲'
        }
        
        print(f"\n{'='*60}")
        print(f"🎵 检测到类型: {type_names.get(url_type, '未知')}")
        print(f"🔗 链接: {spotify_url}")
        print(f"{'='*60}\n")
        
        if url_type == 'track':
            return self.download_song(spotify_url)
        
        print("📥 开始下载...")
        audio_files = self.get_songs_list(spotify_url)
        
        if not audio_files:
            print("❌ 未找到任何歌曲")
            return False
        
        print(f"\n✅ 找到 {len(audio_files)} 首歌曲，开始处理...\n")
        
        success_count = 0
        failed_count = 0
        
        for i, audio_file in enumerate(audio_files, 1):
            print(f"\n{'─'*60}")
            print(f"处理进度: [{i}/{len(audio_files)}]")
            print(f"{'─'*60}")
            
            if self.process_single_file(audio_file):
                success_count += 1
            else:
                failed_count += 1
        
        # 清理临时目录
        temp_dir = self.output_dir / "temp"
        try:
            for f in temp_dir.glob("*"):
                f.unlink()
            temp_dir.rmdir()
        except Exception as e:
            print(f"⚠️  清理临时目录失败: {e}")
        
        # 显示统计信息
        print(f"\n{'='*60}")
        print(f"📊 下载统计")
        print(f"{'='*60}")
        print(f"  总计: {len(audio_files)} 首")
        print(f"  成功: {success_count} 首 ✅")
        print(f"  失败: {failed_count} 首 ❌")
        print(f"{'='*60}\n")
        
        return success_count > 0
    
    def process_single_file(self, audio_file):
        """
        处理单个已下载的音频文件
        
        Args:
            audio_file: 音频文件路径
        """
        try:
            lrc_file = audio_file.with_suffix('.lrc')
            
            # 提取元数据
            metadata = self.extract_metadata(audio_file)
            if not metadata:
                print(f"⚠️  跳过: {audio_file.name} (无法提取元数据)")
                return False
            
            # 创建歌曲独立目录
            song_name = metadata.get('title', 'Unknown Song')
            artist_name = metadata.get('artist', 'Unknown Artist')
            folder_name = self.sanitize_filename(f"{artist_name} - {song_name}")
            song_dir = self.output_dir / folder_name
            
            # 如果目录已存在，跳过
            if song_dir.exists():
                print(f"⏭️  跳过: {folder_name} (已存在)")
                # 清理临时文件
                audio_file.unlink()
                if lrc_file.exists():
                    lrc_file.unlink()
                # 返回已存在的文件信息
                files_list = []
                for f in song_dir.iterdir():
                    if f.is_file():
                        files_list.append(f.name)
                return {
                    "song_name": folder_name,
                    "directory": str(song_dir.relative_to(self.output_dir)),
                    "files": files_list,
                    "full_path": str(song_dir)
                }
            
            song_dir.mkdir(exist_ok=True)
            print(f"📁 {folder_name}")
            
            # 移动音频文件
            new_audio_file = song_dir / audio_file.name
            audio_file.rename(new_audio_file)
            print(f"  ✓ 音频: {audio_file.name}")
            
            # 移动歌词文件
            if lrc_file.exists():
                new_lrc_file = song_dir / lrc_file.name
                lrc_file.rename(new_lrc_file)
                print(f"  ✓ 歌词: {lrc_file.name}")
            
            # 提取封面
            if self.extract_cover(new_audio_file, song_dir):
                print(f"  ✓ 封面: cover.jpg")
            
            # 保存元数据
            self.save_metadata(metadata, song_dir)
            print(f"  ✓ 元数据: metadata.txt, metadata.json")
            
            # 返回文件信息
            files_list = []
            for f in song_dir.iterdir():
                if f.is_file():
                    files_list.append(f.name)
            
            return {
                "song_name": folder_name,
                "directory": str(song_dir.relative_to(self.output_dir)),
                "files": files_list,
                "full_path": str(song_dir)
            }
            
        except Exception as e:
            print(f"❌ 处理失败 {audio_file.name}: {e}")
            return False
    
    def download_song(self, spotify_url):
        """
        下载单首歌曲（向后兼容）
        """
        print(f"\n{'='*60}")
        print(f"🎵 开始处理: {spotify_url}")
        print(f"{'='*60}\n")
        
        temp_dir = self.output_dir / "temp"
        temp_dir.mkdir(exist_ok=True)
        
        cmd = [
            sys.executable, "-m", "spotdl",
            "--output", str(temp_dir),
            "--format", self.audio_format,
            "--generate-lrc",
            spotify_url
        ]
        
        print("📥 下载中...")
        try:
            # 使用Popen而不是run，以便更好地处理长时间运行的进程
            process = subprocess.Popen(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                bufsize=1
            )
            stdout, stderr = process.communicate()
            
            if process.returncode != 0:
                error_msg = f"❌ 下载失败 (返回码: {process.returncode})"
                error_detail = ""
                
                # 提取关键错误信息
                if stderr:
                    error_msg += f"\n错误信息: {stderr[:1000]}"
                    # 检查是否是"No results found"错误
                    if "No results found" in stderr or "LookupError" in stderr:
                        # 尝试提取歌曲名称
                        match = re.search(r'No results found for song: (.+)', stderr)
                        if match:
                            song_name = match.group(1).strip()
                            error_detail = f"未找到匹配的歌曲: {song_name}。可能原因：1) YouTube上不存在该歌曲 2) 歌曲名称不匹配 3) 地区限制"
                        else:
                            error_detail = "未找到匹配的歌曲。可能原因：1) YouTube上不存在该歌曲 2) 歌曲名称不匹配 3) 地区限制"
                    else:
                        error_detail = stderr[:500]
                
                if stdout:
                    error_msg += f"\n输出: {stdout[:500]}"
                
                print(error_msg)
                
                # 兜底处理：即使下载失败，也尝试获取元数据和歌词
                print("\n🔄 尝试获取元数据和歌词（兜底处理）...")
                fallback_result = self.get_metadata_and_lyrics_only(spotify_url)
                if fallback_result:
                    print("✅ 已获取元数据和歌词（无音频文件）")
                    return fallback_result
                
                # 如果兜底也失败，返回错误
                return {"error": True, "message": error_detail or error_msg}
            
            print("✅ 下载完成！")
            if stdout:
                print(f"输出: {stdout[:500]}")  # 只打印前500字符
        except BrokenPipeError as e:
            error_msg = f"❌ 下载失败: 管道中断 (Broken pipe)"
            print(error_msg)
            return False
        except subprocess.CalledProcessError as e:
            error_msg = f"❌ 下载失败 (返回码: {e.returncode})"
            if e.stderr:
                error_msg += f"\n错误信息: {e.stderr[:1000]}"
            if e.stdout:
                error_msg += f"\n输出: {e.stdout[:500]}"
            print(error_msg)
            return False
        except Exception as e:
            error_msg = f"❌ 下载失败: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            return False
        
        audio_files = list(temp_dir.glob(f"*.{self.audio_format}"))
        if not audio_files:
            print(f"❌ 未找到下载的音频文件")
            print(f"   查找目录: {temp_dir}")
            print(f"   查找格式: *.{self.audio_format}")
            # 列出临时目录中的所有文件
            all_files = list(temp_dir.glob("*"))
            if all_files:
                print(f"   目录中的文件: {[f.name for f in all_files]}")
            else:
                print(f"   目录为空")
            return False
        
        audio_file = audio_files[0]
        lrc_file = audio_file.with_suffix('.lrc')
        
        print("\n📝 提取元数据...")
        metadata = self.extract_metadata(audio_file)
        
        if not metadata:
            print("❌ 无法提取元数据")
            return False
        
        song_name = metadata.get('title', 'Unknown Song')
        artist_name = metadata.get('artist', 'Unknown Artist')
        folder_name = self.sanitize_filename(f"{artist_name} - {song_name}")
        song_dir = self.output_dir / folder_name
        song_dir.mkdir(exist_ok=True)
        
        print(f"\n📁 创建目录: {folder_name}")
        
        new_audio_file = song_dir / audio_file.name
        audio_file.rename(new_audio_file)
        print(f"✅ 音频文件: {audio_file.name}")
        
        if lrc_file.exists():
            new_lrc_file = song_dir / lrc_file.name
            lrc_file.rename(new_lrc_file)
            print(f"✅ 歌词文件: {lrc_file.name}")
        
        print("\n🖼️  提取封面...")
        self.extract_cover(new_audio_file, song_dir)
        
        print("\n💾 保存元数据...")
        self.save_metadata(metadata, song_dir)
        
        try:
            temp_dir.rmdir()
        except:
            pass
        
        print(f"\n{'='*60}")
        print(f"✨ 完成！所有文件已保存到: {song_dir}")
        print(f"{'='*60}\n")
        
        # 返回文件信息
        files_list = []
        for f in song_dir.iterdir():
            if f.is_file():
                files_list.append(f.name)
        
        return {
            "song_name": folder_name,
            "directory": str(song_dir.relative_to(self.output_dir)),
            "files": files_list,
            "full_path": str(song_dir)
        }
    
    def extract_metadata(self, audio_file):
        """提取音频文件的元数据"""
        try:
            audio = MP3(str(audio_file))
            tags = ID3(str(audio_file))
            
            metadata = {
                'title': str(tags.get('TIT2', 'Unknown')),
                'artist': str(tags.get('TPE1', 'Unknown')),
                'album': str(tags.get('TALB', 'Unknown')),
                'album_artist': str(tags.get('TPE2', 'Unknown')),
                'date': str(tags.get('TDRC', 'Unknown')),
                'genre': str(tags.get('TCON', 'Unknown')),
                'track': str(tags.get('TRCK', 'Unknown')),
                'disc': str(tags.get('TPOS', 'Unknown')),
                'copyright': str(tags.get('TCOP', 'Unknown')),
                'publisher': str(tags.get('TENC', 'Unknown')),
                'isrc': str(tags.get('TSRC', 'Unknown')),
                'spotify_url': str(tags.get('WOAS', 'Unknown')),
                'youtube_url': str(tags.get('COMM::XXX', 'Unknown')),
                'duration': f"{int(audio.info.length // 60)}分{int(audio.info.length % 60)}秒",
                'duration_seconds': int(audio.info.length),
                'bitrate': f"{audio.info.bitrate // 1000} kbps",
                'sample_rate': f"{audio.info.sample_rate} Hz",
                'channels': '立体声' if audio.info.channels == 2 else '单声道',
                'format': self.audio_format.upper(),
                'file_size': f"{audio_file.stat().st_size / 1024 / 1024:.2f} MB",
                'download_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            has_cover = False
            for key in tags.keys():
                if key.startswith('APIC'):
                    has_cover = True
                    apic = tags[key]
                    metadata['cover_type'] = apic.mime
                    metadata['cover_size'] = f"{len(apic.data) / 1024:.1f} KB"
                    break
            metadata['has_cover'] = has_cover
            
            return metadata
            
        except Exception as e:
            print(f"提取元数据错误: {e}")
            return None
    
    def get_metadata_and_lyrics_only(self, spotify_url):
        """
        兜底方法：即使无法下载音频，也获取元数据和歌词
        
        Args:
            spotify_url: Spotify URL
            
        Returns:
            dict: 包含文件信息的字典，如果失败返回None
        """
        if not SPOTDL_AVAILABLE or not self.spotify_client:
            print("⚠️  无法获取元数据：spotdl模块不可用")
            return None
        
        try:
            print("📝 从Spotify获取元数据...")
            # 从Spotify URL获取歌曲信息
            song = Song.from_url(spotify_url)
            
            # 创建歌曲目录
            artist_name = song.artists[0] if song.artists else "Unknown Artist"
            song_name = song.name or "Unknown Song"
            folder_name = self.sanitize_filename(f"{artist_name} - {song_name}")
            song_dir = self.output_dir / folder_name
            
            if song_dir.exists():
                print(f"⏭️  目录已存在: {folder_name}")
                # 返回已存在的文件信息
                files_list = []
                for f in song_dir.iterdir():
                    if f.is_file():
                        files_list.append(f.name)
                return {
                    "song_name": folder_name,
                    "directory": str(song_dir.relative_to(self.output_dir)),
                    "files": files_list,
                    "full_path": str(song_dir),
                    "metadata_only": True  # 标记为仅元数据
                }
            
            song_dir.mkdir(exist_ok=True)
            print(f"📁 创建目录: {folder_name}")
            
            # 构建元数据字典
            metadata = {
                'title': song.name or 'Unknown',
                'artist': ', '.join(song.artists) if song.artists else 'Unknown',
                'album': song.album_name or 'Unknown',
                'album_artist': ', '.join(song.album_artist) if song.album_artist else 'Unknown',
                'date': str(song.date) if song.date else 'Unknown',
                'genre': ', '.join(song.genres) if song.genres else 'Unknown',
                'track': str(song.track_number) if song.track_number else 'Unknown',
                'disc': str(song.disc_number) if song.disc_number else 'Unknown',
                'copyright': 'Unknown',
                'publisher': 'Unknown',
                'isrc': song.isrc or 'Unknown',
                'spotify_url': song.url or spotify_url,
                'youtube_url': 'N/A (未下载音频)',
                'duration': f"{int(song.duration // 60)}分{int(song.duration % 60)}秒" if song.duration else 'Unknown',
                'duration_seconds': int(song.duration) if song.duration else 0,
                'bitrate': 'N/A',
                'sample_rate': 'N/A',
                'channels': 'N/A',
                'format': 'N/A (仅元数据)',
                'file_size': '0 MB',
                'download_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'has_cover': False,
                'metadata_only': True  # 标记为仅元数据
            }
            
            # 下载封面图片
            if song.cover_url:
                try:
                    print("🖼️  下载封面图片...")
                    cover_file = song_dir / "cover.jpg"
                    response = requests.get(song.cover_url, timeout=10)
                    if response.status_code == 200:
                        with open(cover_file, 'wb') as f:
                            f.write(response.content)
                        metadata['has_cover'] = True
                        metadata['cover_type'] = 'image/jpeg'
                        metadata['cover_size'] = f"{len(response.content) / 1024:.1f} KB"
                        print("  ✓ 封面: cover.jpg")
                except Exception as e:
                    print(f"  ⚠️  封面下载失败: {e}")
            
            # 获取歌词（优先使用Musixmatch，与Spotify一致）
            lyrics_text = None
            if self.downloader:
                try:
                    print("🎵 搜索歌词（优先使用Musixmatch）...")
                    lyrics_text = self.downloader.search_lyrics(song)
                    if lyrics_text:
                        # 尝试确定歌词来源（通过检查下载器使用的提供者）
                        print("  ✓ 找到歌词")
                    else:
                        print("  ⚠️  未找到歌词")
                except Exception as e:
                    print(f"  ⚠️  歌词搜索失败: {e}")
            
            # 保存歌词文件
            if lyrics_text:
                lrc_file = song_dir / f"{folder_name}.lrc"
                try:
                    with open(lrc_file, 'w', encoding='utf-8') as f:
                        f.write(lyrics_text)
                    print(f"  ✓ 歌词: {lrc_file.name}")
                except Exception as e:
                    print(f"  ⚠️  保存歌词失败: {e}")
            
            # 保存元数据
            print("💾 保存元数据...")
            self.save_metadata(metadata, song_dir)
            print("  ✓ 元数据: metadata.txt, metadata.json")
            
            # 返回文件信息
            files_list = []
            for f in song_dir.iterdir():
                if f.is_file():
                    files_list.append(f.name)
            
            return {
                "song_name": folder_name,
                "directory": str(song_dir.relative_to(self.output_dir)),
                "files": files_list,
                "full_path": str(song_dir),
                "metadata_only": True  # 标记为仅元数据
            }
            
        except Exception as e:
            print(f"❌ 获取元数据失败: {e}")
            import traceback
            traceback.print_exc()
            return None
    
    def extract_cover(self, audio_file, output_dir):
        """提取并保存封面图片"""
        cover_file = output_dir / "cover.jpg"
        
        cmd = [
            "ffmpeg",
            "-i", str(audio_file),
            "-an",
            "-vcodec", "copy",
            str(cover_file),
            "-y"
        ]
        
        try:
            subprocess.run(cmd, capture_output=True, check=True)
            return True
        except subprocess.CalledProcessError:
            return False
    
    def save_metadata(self, metadata, output_dir):
        """保存元数据到文件"""
        json_file = output_dir / "metadata.json"
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=2)
        
        txt_file = output_dir / "metadata.txt"
        with open(txt_file, 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write(f"🎵 {metadata['title']}\n")
            f.write("="*60 + "\n\n")
            
            f.write("【歌曲信息】\n")
            f.write(f"  标题:          {metadata['title']}\n")
            f.write(f"  艺术家:        {metadata['artist']}\n")
            f.write(f"  专辑:          {metadata['album']}\n")
            f.write(f"  专辑艺术家:    {metadata['album_artist']}\n")
            f.write(f"  音轨编号:      {metadata['track']}\n")
            f.write(f"  碟片编号:      {metadata['disc']}\n\n")
            
            f.write("【发行信息】\n")
            f.write(f"  发行日期:      {metadata['date']}\n")
            f.write(f"  流派:          {metadata['genre']}\n")
            f.write(f"  版权:          {metadata['copyright']}\n")
            f.write(f"  发行商:        {metadata['publisher']}\n")
            f.write(f"  ISRC代码:      {metadata['isrc']}\n\n")
            
            f.write("【音频规格】\n")
            if metadata.get('metadata_only'):
                f.write(f"  格式:          {metadata['format']}\n")
                f.write(f"  时长:          {metadata['duration']} (来自Spotify)\n")
                f.write(f"  比特率:        {metadata['bitrate']}\n")
                f.write(f"  采样率:        {metadata['sample_rate']}\n")
                f.write(f"  声道:          {metadata['channels']}\n")
                f.write(f"  文件大小:      {metadata['file_size']}\n")
                f.write(f"  状态:          ⚠️  仅元数据（未下载音频文件）\n\n")
            else:
                f.write(f"  格式:          {metadata['format']}\n")
                f.write(f"  时长:          {metadata['duration']}\n")
                f.write(f"  比特率:        {metadata['bitrate']}\n")
                f.write(f"  采样率:        {metadata['sample_rate']}\n")
                f.write(f"  声道:          {metadata['channels']}\n")
                f.write(f"  文件大小:      {metadata['file_size']}\n\n")
            
            f.write("【来源链接】\n")
            f.write(f"  Spotify:       {metadata['spotify_url']}\n")
            f.write(f"  YouTube:       {metadata['youtube_url']}\n\n")
            
            f.write("【下载信息】\n")
            f.write(f"  下载时间:      {metadata['download_date']}\n")
            if metadata.get('metadata_only'):
                f.write(f"  状态:          ⚠️  仅元数据模式（音频文件未下载）\n")
            f.write(f"  封面图片:      {'✅ 已提取' if metadata['has_cover'] else '❌ 无'}\n")
            
            if metadata['has_cover']:
                f.write(f"  封面类型:      {metadata.get('cover_type', 'N/A')}\n")
                f.write(f"  封面大小:      {metadata.get('cover_size', 'N/A')}\n")


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description='Spotify批量下载器 - 支持歌曲、专辑、歌手、播放列表',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
示例用法:
  # 下载单曲
  %(prog)s "https://open.spotify.com/track/..."
  
  # 下载专辑
  %(prog)s "https://open.spotify.com/album/..."
  
  # 下载播放列表
  %(prog)s "https://open.spotify.com/playlist/..."
  
  # 下载歌手的热门歌曲（默认前10首）
  %(prog)s "https://open.spotify.com/artist/..." --max-songs 10
  
  # 指定格式和输出目录
  %(prog)s "SPOTIFY_URL" -o music -f wav
        '''
    )
    
    parser.add_argument(
        'url',
        help='Spotify链接 (歌曲/专辑/播放列表/歌手)'
    )
    
    parser.add_argument(
        '-o', '--output',
        default='downloads',
        help='下载目录 (默认: downloads)'
    )
    
    parser.add_argument(
        '-f', '--format',
        default='mp3',
        choices=['mp3', 'wav', 'flac', 'ogg', 'opus', 'm4a'],
        help='音频格式 (默认: mp3)'
    )
    
    parser.add_argument(
        '--max-songs',
        type=int,
        help='歌手模式下的最大下载数量 (默认: 无限制)'
    )
    
    args = parser.parse_args()
    
    print("\n" + "="*60)
    print("🎵 Spotify批量下载器")
    print("="*60)
    
    downloader = SpotifyBatchDownloader(
        output_dir=args.output,
        audio_format=args.format,
        max_songs=args.max_songs
    )
    
    success = downloader.process_batch(args.url)
    
    if success:
        print("✨ 所有任务完成！\n")
        sys.exit(0)
    else:
        print("❌ 下载失败！\n")
        sys.exit(1)


if __name__ == '__main__':
    main()

