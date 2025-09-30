from typing import List, Dict, Set
import logging
import re
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize, sent_tokenize
import string
from datetime import datetime
import numpy as np

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 下载必要的NLTK资源
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

class DataProcessor:
    """数据处理器，负责文本预处理、实体提取、主题识别等"""
    
    def __init__(self, min_text_length: int = 200):
        self.min_text_length = min_text_length
        self.stop_words = set(stopwords.words('english'))
        # 添加中文停用词
        self.chinese_stop_words = {'的', '了', '和', '是', '在', '有', '我', '你', '他', '她', '它', '这', '那', '之', '以', '于'}
    
    def process_articles(self, articles: List[Dict]) -> List[Dict]:
        """处理文章列表"""
        logger.info(f"开始处理 {len(articles)} 篇文章")
        processed_articles = []
        
        for article in articles:
            # 过滤太短的文章
            if len(article['content']) < self.min_text_length:
                logger.warning(f"文章过短，跳过: {article['title']}")
                continue
            
            # 预处理文章
            processed_article = self._preprocess_article(article)
            if processed_article:
                processed_articles.append(processed_article)
        
        logger.info(f"处理完成，保留 {len(processed_articles)} 篇有效文章")
        return processed_articles
    
    def _preprocess_article(self, article: Dict) -> Dict:
        """预处理单篇文章"""
        try:
            # 复制原文章数据
            processed = article.copy()
            
            # 清理文本
            processed['cleaned_content'] = self._clean_text(article['content'])
            processed['cleaned_title'] = self._clean_text(article['title'])
            
            # 分词
            processed['tokens'] = self._tokenize(processed['cleaned_content'])
            processed['sentences'] = sent_tokenize(processed['cleaned_content'])
            
            # 提取关键词（基于词频）
            processed['keywords'] = self._extract_keywords(processed['tokens'], top_n=10)
            
            # 规范化发布日期
            if 'published_date' in processed and processed['published_date']:
                processed['normalized_date'] = self._normalize_date(processed['published_date'])
            else:
                processed['normalized_date'] = datetime.now()
            
            return processed
        
        except Exception as e:
            logger.error(f"预处理文章时出错: {e}")
            return None
    
    def _clean_text(self, text: str) -> str:
        """清理文本"""
        # 转换为小写
        text = text.lower()
        
        # 移除HTML标签
        text = re.sub(r'<[^>]+>', '', text)
        
        # 移除特殊字符，保留字母、数字和中文
        text = re.sub(r'[^\w\s\u4e00-\u9fa5]', '', text)
        
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _tokenize(self, text: str) -> List[str]:
        """分词"""
        tokens = word_tokenize(text)
        
        # 过滤停用词和标点
        filtered_tokens = []
        for token in tokens:
            if token not in self.stop_words and \
               token not in self.chinese_stop_words and \
               token not in string.punctuation and \
               len(token) > 1:
                filtered_tokens.append(token)
        
        return filtered_tokens
    
    def _extract_keywords(self, tokens: List[str], top_n: int = 10) -> List[str]:
        """基于词频提取关键词"""
        # 计算词频
        from collections import Counter
        word_freq = Counter(tokens)
        
        # 获取频率最高的词
        top_words = [word for word, freq in word_freq.most_common(top_n)]
        
        return top_words
    
    def _normalize_date(self, date_str: str) -> datetime:
        """规范化日期字符串"""
        try:
            # 尝试不同的日期格式
            formats = [
                '%Y-%m-%d %H:%M:%S',
                '%Y-%m-%d',
                '%d %B %Y',
                '%B %d, %Y',
                '%Y/%m/%d',
                '%d/%m/%Y'
            ]
            
            for fmt in formats:
                try:
                    return datetime.strptime(date_str, fmt)
                except ValueError:
                    continue
            
            # 如果都失败，返回当前日期
            logger.warning(f"无法解析日期格式: {date_str}")
            return datetime.now()
        except Exception as e:
            logger.error(f"规范化日期时出错: {e}")
            return datetime.now()
    
    def remove_duplicate_articles(self, articles: List[Dict], similarity_threshold: float = 0.8) -> List[Dict]:
        """移除重复或高度相似的文章"""
        if len(articles) <= 1:
            return articles
        
        logger.info("开始移除重复文章")
        unique_articles = [articles[0]]
        
        for article in articles[1:]:
            # 检查与现有文章的相似度
            is_duplicate = False
            for unique_article in unique_articles:
                # 简单的相似度检查：标题相似度
                title_similarity = self._calculate_similarity(
                    article['cleaned_title'], 
                    unique_article['cleaned_title']
                )
                
                if title_similarity > similarity_threshold:
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_articles.append(article)
        
        logger.info(f"移除了 {len(articles) - len(unique_articles)} 篇重复文章")
        return unique_articles
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """计算文本相似度（简单实现）"""
        # 将文本转换为词集合
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        # 计算Jaccard相似度
        intersection = len(words1.intersection(words2))
        union = len(words1.union(words2))
        
        return intersection / union if union > 0 else 0