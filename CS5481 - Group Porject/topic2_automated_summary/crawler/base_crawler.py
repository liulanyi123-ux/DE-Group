import requests
from abc import ABC, abstractmethod
import time
from typing import List, Dict, Optional
import logging

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class BaseCrawler(ABC):
    """爬虫基类，定义所有爬虫必须实现的接口"""
    
    def __init__(self, topic: str, max_articles: int = 10):
        self.topic = topic
        self.max_articles = max_articles
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    @abstractmethod
    def crawl(self) -> List[Dict]:
        """爬取文章的抽象方法，子类必须实现"""
        pass
    
    def fetch_url(self, url: str, retries: int = 3, delay: int = 2) -> Optional[str]:
        """带重试机制的URL获取方法"""
        for attempt in range(retries):
            try:
                response = requests.get(url, headers=self.headers, timeout=10)
                if response.status_code == 200:
                    return response.text
                else:
                    logger.warning(f"请求失败，状态码: {response.status_code}, URL: {url}")
            except Exception as e:
                logger.error(f"获取URL时出错: {e}, URL: {url}")
            
            if attempt < retries - 1:
                logger.info(f"第 {attempt + 1} 次尝试失败，等待 {delay} 秒后重试...")
                time.sleep(delay)
        
        logger.error(f"达到最大重试次数，无法获取URL: {url}")
        return None
    
    def clean_article(self, article: Dict) -> Dict:
        """清理文章数据，移除无效字段"""
        # 确保所有必要字段都存在
        required_fields = ['title', 'content', 'url', 'published_date', 'source']
        for field in required_fields:
            if field not in article:
                article[field] = ""
        
        # 移除空白字符
        for key, value in article.items():
            if isinstance(value, str):
                article[key] = value.strip()
        
        return article

# 定义爬虫工厂类，用于创建不同的爬虫实例
class CrawlerFactory:
    """爬虫工厂，根据新闻源创建对应的爬虫实例"""
    
    @staticmethod
    def create_crawler(source: str, topic: str, max_articles: int) -> BaseCrawler:
        """创建爬虫实例"""
        # 动态导入以避免循环依赖
        if source.lower() == 'bbc':
            from crawler.bbc_crawler import BBC_Crawler
            return BBC_Crawler(topic, max_articles)
        elif source.lower() == 'cnn':
            from crawler.cnn_crawler import CNN_Crawler
            return CNN_Crawler(topic, max_articles)
        elif source.lower() == 'nytimes':
            from crawler.nytimes_crawler import NYTimes_Crawler
            return NYTimes_Crawler(topic, max_articles)
        elif source.lower() == 'reuters':
            from crawler.reuters_crawler import Reuters_Crawler
            return Reuters_Crawler(topic, max_articles)
        elif source.lower() == 'xinhua':
            from crawler.xinhua_crawler import Xinhua_Crawler
            return Xinhua_Crawler(topic, max_articles)
        else:
            # 如果没有特定的爬虫实现，使用通用爬虫
            from crawler.generic_crawler import Generic_Crawler
            return Generic_Crawler(source, topic, max_articles)