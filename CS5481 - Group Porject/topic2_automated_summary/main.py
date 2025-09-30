import os
import logging
import argparse
from typing import List, Dict
from dotenv import load_dotenv
import time

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# 确保能正确导入自定义模块
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crawler.base_crawler import CrawlerFactory
from processor.data_processor import DataProcessor
from processor.llm_processor import LLMProcessor
from generator.page_generator import PageGenerator

class AutomatedSummarySystem:
    """自动化摘要系统主类"""
    
    def __init__(self, config: Dict):
        self.config = config
        self.topic = config.get('EVENT_TOPIC', '人工智能')
        self.news_sources = config.get('NEWS_SOURCES', 'bbc,cnn').split(',')
        self.max_articles_per_source = int(config.get('MAX_ARTICLES_PER_SOURCE', 10))
        self.min_text_length = int(config.get('MIN_TEXT_LENGTH', 200))
        self.top_n_entities = int(config.get('TOP_N_ENTITIES', 10))
        self.top_n_themes = int(config.get('TOP_N_THEMES', 5))
        self.embedding_model = config.get('EMBEDDING_MODEL', 'text-embedding-ada-002')
        self.api_key = config.get('OPENAI_API_KEY')
        
        # 初始化各个组件
        self.data_processor = DataProcessor(min_text_length=self.min_text_length)
        self.llm_processor = LLMProcessor(api_key=self.api_key, embedding_model=self.embedding_model)
        self.page_generator = PageGenerator(output_dir="./output")
    
    def run(self) -> str:
        """运行完整的摘要生成流程"""
        logger.info(f"开始为主题 '{self.topic}' 生成自动摘要")
        start_time = time.time()
        
        try:
            # 步骤1: 爬取文章
            articles = self._crawl_articles()
            
            if not articles:
                logger.error("未能获取任何文章，程序终止")
                return None
            
            # 步骤2: 预处理文章
            processed_articles = self._process_articles(articles)
            
            # 步骤3: 分析文章
            analysis_results = self._analyze_articles(processed_articles)
            
            # 步骤4: 生成摘要页面
            output_file = self._generate_summary_page(analysis_results, processed_articles)
            
            end_time = time.time()
            logger.info(f"摘要生成完成，总耗时: {end_time - start_time:.2f}秒")
            logger.info(f"摘要页面已保存至: {output_file}")
            
            return output_file
            
        except Exception as e:
            logger.error(f"运行过程中发生错误: {e}", exc_info=True)
            return None
    
    def _crawl_articles(self) -> List[Dict]:
        """爬取所有来源的文章"""
        all_articles = []
        
        for source in self.news_sources:
            try:
                logger.info(f"开始从 {source} 爬取文章")
                
                # 创建对应的爬虫实例
                crawler = CrawlerFactory.create_crawler(
                    source=source,
                    topic=self.topic,
                    max_articles=self.max_articles_per_source
                )
                
                # 执行爬取
                articles = crawler.crawl()
                all_articles.extend(articles)
                
                logger.info(f"从 {source} 成功获取 {len(articles)} 篇文章")
                
                # 避免爬取过快
                time.sleep(3)
                
            except Exception as e:
                logger.error(f"从 {source} 爬取时出错: {e}")
                continue
        
        logger.info(f"爬取完成，共获取 {len(all_articles)} 篇文章")
        return all_articles
    
    def _process_articles(self, articles: List[Dict]) -> List[Dict]:
        """预处理文章"""
        # 处理文章
        processed_articles = self.data_processor.process_articles(articles)
        
        # 移除重复文章
        unique_articles = self.data_processor.remove_duplicate_articles(processed_articles)
        
        # 按日期排序
        from datetime import datetime
        sorted_articles = sorted(
            unique_articles, 
            key=lambda x: x.get('normalized_date', datetime.now()),
            reverse=True  # 最新的文章在前
        )
        
        return sorted_articles
    
    def _analyze_articles(self, articles: List[Dict]) -> Dict:
        """分析文章内容"""
        # 使用LLM处理器分析文章
        analysis_results = self.llm_processor.analyze_articles(
            articles,
            top_n_entities=self.top_n_entities,
            top_n_themes=self.top_n_themes
        )
        
        return analysis_results
    
    def _generate_summary_page(self, analysis_results: Dict, articles: List[Dict]) -> str:
        """生成摘要页面"""
        # 生成HTML摘要页面
        output_file = self.page_generator.generate_summary_page(
            analysis_results=analysis_results,
            articles=articles,
            topic=self.topic
        )
        
        return output_file

def load_config() -> Dict:
    """加载配置"""
    # 加载.env文件
    load_dotenv()
    
    # 从环境变量读取配置
    config = {
        'EVENT_TOPIC': os.getenv('EVENT_TOPIC', '人工智能'),
        'NEWS_SOURCES': os.getenv('NEWS_SOURCES', 'bbc,cnn,nytimes,reuters,Xinhua'),
        'MAX_ARTICLES_PER_SOURCE': os.getenv('MAX_ARTICLES_PER_SOURCE', '10'),
        'MIN_TEXT_LENGTH': os.getenv('MIN_TEXT_LENGTH', '200'),
        'EMBEDDING_MODEL': os.getenv('EMBEDDING_MODEL', 'text-embedding-ada-002'),
        'TOP_N_ENTITIES': os.getenv('TOP_N_ENTITIES', '10'),
        'TOP_N_THEMES': os.getenv('TOP_N_THEMES', '5'),
        'OPENAI_API_KEY': os.getenv('OPENAI_API_KEY')
    }
    
    return config

def main():
    """主函数"""
    # 解析命令行参数
    parser = argparse.ArgumentParser(description='自动化主题摘要生成系统')
    parser.add_argument('--topic', type=str, help='要分析的事件主题')
    parser.add_argument('--output', type=str, help='输出目录')
    args = parser.parse_args()
    
    # 加载配置
    config = load_config()
    
    # 如果命令行提供了主题，覆盖配置
    if args.topic:
        config['EVENT_TOPIC'] = args.topic
    
    # 创建并运行系统
    system = AutomatedSummarySystem(config)
    output_file = system.run()
    
    if output_file:
        print(f"摘要页面已成功生成: {os.path.abspath(output_file)}")
    else:
        print("摘要页面生成失败")

if __name__ == "__main__":
    main()