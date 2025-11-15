#!/bin/bash
# spotDL 增强版 - 快速启动脚本

echo "╔══════════════════════════════════════════════════════════╗"
echo "║          spotDL Enhanced - 快速启动                       ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# 检查虚拟环境
if [ ! -d "venv" ]; then
    echo "❌ 未找到虚拟环境"
    echo "正在创建虚拟环境..."
    python3 -m venv venv
    echo "✅ 虚拟环境创建完成"
    echo ""
fi

# 激活虚拟环境
echo "🔄 激活虚拟环境..."
source venv/bin/activate

# 检查依赖
echo "🔍 检查依赖..."
if ! python3 -c "import fastapi" 2>/dev/null; then
    echo "⚠️  缺少依赖，正在安装..."
    pip install fastapi uvicorn 2>&1 | grep -v "Requirement already satisfied" || true
fi

if ! python3 -c "import spotdl" 2>/dev/null; then
    echo "⚠️  spotdl未安装，正在安装..."
    pip install -e . 2>&1 | grep -v "Requirement already satisfied" || true
fi

echo "✅ 依赖检查完成"
echo ""

# 显示选项
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "请选择启动方式:"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "  1. 🌐 启动增强版Web UI（推荐）- 完整元数据"
echo "     → 图形界面 + 独立目录 + LRC歌词 + 封面"
echo ""
echo "  2. 🌐 启动官方Web UI - 基础功能"
echo "     → 图形界面 + 单一目录"
echo ""
echo "  3. 📝 命令行下载（批量）- 完整元数据"
echo "     → 输入URL进行下载"
echo ""
echo "  4. 📝 命令行下载（原生）- 基础功能"
echo "     → 使用spotdl原生命令"
echo ""
echo "  5. ❌ 退出"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -n "请输入选项 (1-5): "
read choice

case $choice in
    1)
        echo ""
        echo "🚀 启动增强版Web UI..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "访问地址: http://127.0.0.1:8800/ui"
        echo "API文档:  http://127.0.0.1:8800/docs"
        echo "按 Ctrl+C 停止服务"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        python3 web_enhanced.py
        ;;
    2)
        echo ""
        echo "🚀 启动官方Web UI..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo "访问地址: http://127.0.0.1:8080"
        echo "按 Ctrl+C 停止服务"
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        echo ""
        python3 -m spotdl web --port 8080
        ;;
    3)
        echo ""
        echo -n "请输入Spotify URL: "
        read url
        if [ -z "$url" ]; then
            echo "❌ URL不能为空"
            exit 1
        fi
        echo ""
        echo "🚀 开始下载（完整元数据模式）..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        python3 download_batch.py "$url"
        ;;
    4)
        echo ""
        echo -n "请输入Spotify URL: "
        read url
        if [ -z "$url" ]; then
            echo "❌ URL不能为空"
            exit 1
        fi
        echo ""
        echo "🚀 开始下载（原生模式）..."
        echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
        python3 -m spotdl download "$url"
        ;;
    5)
        echo ""
        echo "👋 再见！"
        exit 0
        ;;
    *)
        echo ""
        echo "❌ 无效选项"
        exit 1
        ;;
esac

