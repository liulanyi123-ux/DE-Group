#!/bin/bash

echo "=== 自动主题摘要页面生成系统 ==="
echo ""

# 检查Python版本
echo "检查Python版本..."
python3 --version
if [ $? -ne 0 ]; then
    echo "错误: 未找到Python3，请先安装Python 3.8+"
    exit 1
fi

# 创建输出目录
echo "创建输出目录..."
mkdir -p output

# 使用虚拟环境
echo "设置虚拟环境..."
VENV_DIR=".venv"

# 如果虚拟环境不存在，创建它
if [ ! -d "$VENV_DIR" ]; then
    echo "创建虚拟环境..."
    python3 -m venv $VENV_DIR
fi

# 激活虚拟环境
echo "激活虚拟环境..."
source $VENV_DIR/bin/activate

# 升级pip
echo "升级pip..."
pip install --upgrade pip

# 安装依赖
echo "安装依赖包..."
pip install -r requirements.txt
if [ $? -ne 0 ]; then
    echo "错误: 依赖安装失败"
    exit 1
fi

# 检查.env文件
if [ ! -f .env ]; then
    echo "创建.env文件..."
    cp .env.example .env
    echo "请编辑.env文件配置OpenAI API密钥和其他参数"
fi

# 运行主程序
echo ""
echo "开始运行摘要生成系统..."
echo "（按Ctrl+C可以随时停止）"
echo ""

python3 main.py

# 检查运行结果
if [ $? -eq 0 ] && [ -d "output" ] && [ "$(ls -A output)" ]; then
    echo ""
    echo "✅ 运行成功！"
    echo "生成的摘要页面已保存到 output/ 目录"
    
    # 显示生成的文件列表
    echo ""
    echo "生成的文件："
    find output -name "*.html" | sort
else
    echo ""
    echo "❌ 运行失败或未生成摘要页面"
fi

echo ""
echo "=== 运行完成 ==="