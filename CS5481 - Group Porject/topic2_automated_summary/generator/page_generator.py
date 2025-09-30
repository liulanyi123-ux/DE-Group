from jinja2 import Template, FileSystemLoader, Environment
import os
from typing import List, Dict
import logging
from datetime import datetime

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PageGenerator:
    """页面生成器，负责生成HTML摘要页面"""
    
    def __init__(self, output_dir: str = "./output"):
        self.output_dir = output_dir
        # 确保输出目录存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 设置Jinja2环境
        self.env = Environment(
            loader=FileSystemLoader(os.path.dirname(__file__)),
            autoescape=True
        )
    
    def generate_summary_page(self, analysis_results: Dict, articles: List[Dict], topic: str) -> str:
        """生成综合摘要页面"""
        logger.info(f"开始生成关于 '{topic}' 的摘要页面")
        
        # 准备模板数据
        template_data = {
            'topic': topic,
            'generation_time': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            'summary': analysis_results.get('summary', '暂无摘要'),
            'entities': analysis_results.get('entities', []),
            'themes': analysis_results.get('themes', []),
            'timeline': analysis_results.get('timeline', []),
            'articles': articles[:10]  # 限制显示的文章数量
        }
        
        # 使用模板生成HTML
        html_content = self._render_template(template_data)
        
        # 保存HTML文件
        output_file = os.path.join(self.output_dir, f"summary_{topic.replace(' ', '_')}.html")
        self._save_html(html_content, output_file)
        
        logger.info(f"摘要页面已保存至: {output_file}")
        return output_file
    
    def _render_template(self, data: Dict) -> str:
        """渲染HTML模板"""
        # 内联模板字符串
        template_str = '''
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ topic }} - 自动生成摘要页面</title>
    <style>
        /* 科技主题样式 */
        :root {
            --primary-color: #1a73e8;
            --secondary-color: #34a853;
            --accent-color: #ea4335;
            --background-color: #f8f9fa;
            --card-background: #ffffff;
            --text-color: #202124;
            --text-secondary: #5f6368;
            --border-color: #dadce0;
            --timeline-color: #e0e0e0;
        }
        
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        
        body {
            font-family: 'Segoe UI', 'Microsoft YaHei', sans-serif;
            line-height: 1.6;
            color: var(--text-color);
            background-color: var(--background-color);
        }
        
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
        }
        
        header {
            background: linear-gradient(135deg, var(--primary-color), #3a57e8);
            color: white;
            padding: 40px 0;
            margin-bottom: 30px;
            border-radius: 12px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        
        header h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
            text-align: center;
        }
        
        header .subtitle {
            text-align: center;
            font-size: 1.1rem;
            opacity: 0.9;
        }
        
        .card {
            background-color: var(--card-background);
            border-radius: 10px;
            box-shadow: 0 2px 10px rgba(0, 0, 0, 0.05);
            padding: 30px;
            margin-bottom: 25px;
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }
        
        .card:hover {
            transform: translateY(-3px);
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }
        
        .card h2 {
            color: var(--primary-color);
            margin-bottom: 20px;
            font-size: 1.8rem;
            border-bottom: 2px solid var(--border-color);
            padding-bottom: 10px;
        }
        
        .card h3 {
            color: var(--secondary-color);
            margin: 20px 0 10px;
            font-size: 1.3rem;
        }
        
        /* 摘要样式 */
        .summary-content {
            font-size: 1.1rem;
            line-height: 1.8;
            text-align: justify;
        }
        
        /* 实体和主题网格 */
        .entity-grid, .theme-grid {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
            gap: 20px;
            margin-top: 20px;
        }
        
        .entity-card, .theme-card {
            background-color: rgba(26, 115, 232, 0.05);
            border-radius: 8px;
            padding: 15px;
            border-left: 4px solid var(--primary-color);
        }
        
        .entity-card h4, .theme-card h4 {
            color: var(--primary-color);
            margin-bottom: 8px;
            font-size: 1.1rem;
        }
        
        .entity-card p, .theme-card p {
            color: var(--text-secondary);
            font-size: 0.95rem;
        }
        
        .entity-type {
            display: inline-block;
            background-color: var(--primary-color);
            color: white;
            font-size: 0.8rem;
            padding: 2px 8px;
            border-radius: 12px;
            margin-top: 5px;
        }
        
        /* 时间线样式 */
        .timeline {
            position: relative;
            margin: 20px 0;
        }
        
        .timeline::before {
            content: '';
            position: absolute;
            left: 20px;
            top: 0;
            bottom: 0;
            width: 4px;
            background-color: var(--timeline-color);
            border-radius: 2px;
        }
        
        .timeline-item {
            position: relative;
            padding-left: 60px;
            margin-bottom: 25px;
        }
        
        .timeline-item::before {
            content: '';
            position: absolute;
            left: 18px;
            top: 5px;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background-color: var(--primary-color);
            border: 2px solid var(--primary-color);
        }
        
        .timeline-date {
            color: var(--primary-color);
            font-weight: bold;
            margin-bottom: 5px;
        }
        
        .timeline-event {
            color: var(--text-color);
        }
        
        /* 文章列表样式 */
        .article-list {
            list-style: none;
        }
        
        .article-item {
            margin-bottom: 20px;
            padding: 15px;
            background-color: rgba(52, 168, 83, 0.05);
            border-radius: 8px;
            transition: background-color 0.3s ease;
        }
        
        .article-item:hover {
            background-color: rgba(52, 168, 83, 0.1);
        }
        
        .article-title {
            font-size: 1.2rem;
            color: var(--secondary-color);
            margin-bottom: 8px;
        }
        
        .article-title a {
            color: var(--secondary-color);
            text-decoration: none;
            transition: color 0.3s ease;
        }
        
        .article-title a:hover {
            color: #277b3e;
            text-decoration: underline;
        }
        
        .article-meta {
            font-size: 0.9rem;
            color: var(--text-secondary);
            margin-bottom: 10px;
        }
        
        .article-summary {
            font-size: 0.95rem;
            color: var(--text-color);
            line-height: 1.6;
        }
        
        /* 页脚样式 */
        footer {
            text-align: center;
            padding: 20px;
            color: var(--text-secondary);
            font-size: 0.9rem;
            margin-top: 40px;
        }
        
        /* 响应式设计 */
        @media (max-width: 768px) {
            header h1 {
                font-size: 2rem;
            }
            
            .card {
                padding: 20px;
            }
            
            .entity-grid, .theme-grid {
                grid-template-columns: 1fr;
            }
            
            .timeline::before {
                left: 15px;
            }
            
            .timeline-item {
                padding-left: 50px;
            }
            
            .timeline-item::before {
                left: 13px;
            }
        }
        
        /* 加载动画 */
        .loading {
            display: inline-block;
            width: 20px;
            height: 20px;
            border: 3px solid rgba(26, 115, 232, 0.3);
            border-radius: 50%;
            border-top-color: var(--primary-color);
            animation: spin 1s ease-in-out infinite;
        }
        
        @keyframes spin {
            to { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1>{{ topic }}</h1>
            <p class="subtitle">自动生成的结构化摘要 | 更新时间: {{ generation_time }}</p>
        </header>
        
        <!-- 主摘要部分 -->
        <section class="card">
            <h2>内容摘要</h2>
            <div class="summary-content">
                {{ summary }}
            </div>
        </section>
        
        <!-- 关键实体部分 -->
        <section class="card">
            <h2>关键实体</h2>
            <div class="entity-grid">
                {% for entity in entities %}
                <div class="entity-card">
                    <h4>{{ entity.name }}</h4>
                    <p>{{ entity.description }}</p>
                    <span class="entity-type">{{ entity.type }}</span>
                </div>
                {% endfor %}
            </div>
        </section>
        
        <!-- 主要主题部分 -->
        <section class="card">
            <h2>主要主题</h2>
            <div class="theme-grid">
                {% for theme in themes %}
                <div class="theme-card">
                    <h4>{{ theme.name }}</h4>
                    <p>{{ theme.description }}</p>
                </div>
                {% endfor %}
            </div>
        </section>
        
        <!-- 时间线部分 -->
        <section class="card">
            <h2>发展时间线</h2>
            <div class="timeline">
                {% for item in timeline %}
                <div class="timeline-item">
                    <div class="timeline-date">{{ item.date }}</div>
                    <div class="timeline-event">{{ item.event }}</div>
                </div>
                {% endfor %}
            </div>
        </section>
        
        <!-- 源文章链接部分 -->
        <section class="card">
            <h2>参考文章</h2>
            <ul class="article-list">
                {% for article in articles %}
                <li class="article-item">
                    <h3 class="article-title"><a href="{{ article.url }}" target="_blank">{{ article.title }}</a></h3>
                    <div class="article-meta">来源: {{ article.source }} | 发布时间: {{ article.published_date }}</div>
                    <p class="article-summary">{{ article.content[:200] }}...</p>
                </li>
                {% endfor %}
            </ul>
        </section>
        
        <footer>
            <p>自动生成的摘要页面 | 基于Topic 2项目实现</p>
        </footer>
    </div>
</body>
</html>
        '''
        
        template = Template(template_str)
        return template.render(**data)
    
    def _save_html(self, html_content: str, output_file: str) -> None:
        """保存HTML内容到文件"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            logger.info(f"HTML文件已成功保存: {output_file}")
        except Exception as e:
            logger.error(f"保存HTML文件时出错: {e}")
            raise