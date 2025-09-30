import os
import sys

# 检查HTML文件是否存在
html_path = "/Users/wangyuan/Desktop/CS5481 - Group Porject/topic2_automated_summary/output/summary_2023年人工智能进展.html"

if os.path.exists(html_path):
    print(f"✅ 文件存在: {html_path}")
    print(f"文件大小: {os.path.getsize(html_path)} 字节")
    print("\n文件内容预览:")
    
    # 读取前500个字符作为预览
    with open(html_path, 'r', encoding='utf-8') as f:
        content = f.read(500)
        print(content)
        print("...")
        
    # 推荐使用系统默认应用打开
    print("\n建议使用以下命令打开HTML文件:")
    print("在终端中执行: open", html_path)
else:
    print(f"❌ 文件不存在: {html_path}")
    print("请检查文件路径是否正确")