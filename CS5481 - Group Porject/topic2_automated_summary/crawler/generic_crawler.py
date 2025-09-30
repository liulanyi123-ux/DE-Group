from crawler.base_crawler import BaseCrawler
from typing import List, Dict
import logging
import json
from datetime import datetime
import time

logger = logging.getLogger(__name__)

class Generic_Crawler(BaseCrawler):
    """通用爬虫，适用于没有特定爬虫实现的新闻源"""
    
    def __init__(self, source_name: str, topic: str, max_articles: int = 10):
        super().__init__(topic, max_articles)
        self.source_name = source_name
        # 这里我们使用新闻API的通用搜索URL作为示例
        self.search_url = f"https://newsapi.org/v2/everything?q={self.topic}&sources={self.source_name}&pageSize={self.max_articles}"
    
    def crawl(self) -> List[Dict]:
        """执行爬取操作"""
        logger.info(f"开始使用通用爬虫爬取 {self.source_name} 关于 '{self.topic}' 的文章")
        
        # 由于真实API需要密钥，这里我们生成模拟数据
        articles = self._generate_mock_articles()
        
        logger.info(f"通用爬虫完成，成功获取 {len(articles)} 篇文章")
        return articles
    
    def _generate_mock_articles(self) -> List[Dict]:
        """生成模拟文章数据，用于开发和测试"""
        mock_articles = []
        sources = ["BBC News", "CNN", "The New York Times", "Reuters", "Xinhua News"]
        
        for i in range(self.max_articles):
            # 使用时间戳生成唯一ID
            article_id = f"mock-{int(time.time())}-{i}"
            
            article = {
                'id': article_id,
                'title': f"{self.topic}相关报道 #{i+1}",
                'content': f"这是关于{self.topic}的模拟文章内容 #{i+1}。\n\n本文详细讨论了{self.topic}的最新进展、影响和未来展望。专家表示，这一领域的发展将对社会产生深远影响。\n\n据报道，相关技术在过去一年取得了突破性进展，特别是在应用领域。研究人员正在努力解决面临的挑战，推动技术进一步发展。",
                'url': f"https://example.com/article/{article_id}",
                'published_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'source': sources[i % len(sources)]
            }
            
            # 清理文章数据
            cleaned_article = self.clean_article(article)
            mock_articles.append(cleaned_article)
        
        return mock_articles