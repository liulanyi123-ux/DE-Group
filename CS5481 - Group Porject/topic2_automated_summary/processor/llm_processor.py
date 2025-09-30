import os
from typing import List, Dict, Tuple, Set
import logging
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# 配置日志
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# 加载环境变量
load_dotenv()

class LLMProcessor:
    """使用LLM进行文本处理，包括实体提取、摘要生成和主题分析"""
    
    def __init__(self, api_key: str = None, embedding_model: str = "text-embedding-3-small"):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            logger.warning("未提供OpenAI API密钥，将使用模拟数据")
            self.client = None
        else:
            try:
                self.client = OpenAI(api_key=self.api_key)
            except Exception as e:
                logger.error(f"OpenAI客户端初始化失败: {e}")
                self.client = None
        self.embedding_model = embedding_model
    
    def analyze_articles(self, articles: List[Dict], top_n_entities: int = 10, top_n_themes: int = 5) -> Dict:
        """分析多篇文章，提取关键信息"""
        logger.info(f"开始使用LLM分析 {len(articles)} 篇文章")
        
        # 合并所有文章内容用于综合分析
        combined_text = "\n\n".join([article['content'] for article in articles])
        
        # 提取关键实体
        entities = self.extract_entities(combined_text, top_n=top_n_entities)
        
        # 生成综合摘要
        summary = self.generate_summary(combined_text)
        
        # 分析主要主题
        themes = self.identify_themes(combined_text, top_n=top_n_themes)
        
        # 构建时间线
        timeline = self.build_timeline(articles)
        
        result = {
            'entities': entities,
            'summary': summary,
            'themes': themes,
            'timeline': timeline
        }
        
        logger.info("LLM分析完成")
        return result
    
    def extract_entities(self, text: str, top_n: int = 10) -> List[Dict]:
        """提取关键实体"""
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "你是一个实体提取专家。请从文本中提取关键实体，并按重要性排序。"},
                        {"role": "user", "content": f"请从以下文本中提取最重要的{top_n}个实体。为每个实体提供类型（如人物、组织、地点、技术等）和简要描述。以JSON格式返回：[{{\"name\": \"实体名\", \"type\": \"实体类型\", \"description\": \"简要描述\"}}, ...]\n\n文本：{text[:2000]}..."}
                    ],
                    response_format={"type": "json_object"}
                )
                
                import json
                entities = json.loads(response.choices[0].message.content)
                return entities[:top_n] if len(entities) > top_n else entities
                
            except Exception as e:
                logger.error(f"使用LLM提取实体时出错: {e}")
                # 出错时返回模拟数据
                return self._generate_mock_entities(top_n)
        else:
            # 没有API密钥时返回模拟数据
            return self._generate_mock_entities(top_n)
    
    def generate_summary(self, text: str, max_length: int = 500) -> str:
        """生成综合摘要"""
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "你是一个专业的摘要生成器。请生成简洁、全面且信息丰富的摘要。"},
                        {"role": "user", "content": f"请为以下文本生成一个全面的摘要，长度不超过{max_length}个字符。摘要应包含关键事件、重要发现和主要结论。\n\n文本：{text[:3000]}..."}
                    ]
                )
                
                return response.choices[0].message.content
                
            except Exception as e:
                logger.error(f"使用LLM生成摘要时出错: {e}")
                # 出错时返回模拟摘要
                return "这是关于人工智能最新进展的综合摘要。近期研究表明，人工智能技术在多个领域取得了重大突破，包括大型语言模型、计算机视觉和机器人技术。专家预测，这些技术将在未来几年对社会和经济产生深远影响。"
        else:
            # 没有API密钥时返回模拟摘要
            return "这是关于人工智能最新进展的综合摘要。近期研究表明，人工智能技术在多个领域取得了重大突破，包括大型语言模型、计算机视觉和机器人技术。专家预测，这些技术将在未来几年对社会和经济产生深远影响。"
    
    def identify_themes(self, text: str, top_n: int = 5) -> List[Dict]:
        """识别主要主题"""
        if self.client:
            try:
                response = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "你是一个主题分析专家。请从文本中识别主要主题和趋势。"},
                        {"role": "user", "content": f"请从以下文本中识别最重要的{top_n}个主题。为每个主题提供名称和简要描述。以JSON格式返回：[{{\"name\": \"主题名称\", \"description\": \"主题描述\"}}, ...]\n\n文本：{text[:2000]}..."}
                    ],
                    response_format={"type": "json_object"}
                )
                
                import json
                themes = json.loads(response.choices[0].message.content)
                return themes[:top_n] if len(themes) > top_n else themes
                
            except Exception as e:
                logger.error(f"使用LLM识别主题时出错: {e}")
                # 出错时返回模拟数据
                return self._generate_mock_themes(top_n)
        else:
            # 没有API密钥时返回模拟数据
            return self._generate_mock_themes(top_n)
    
    def build_timeline(self, articles: List[Dict]) -> List[Dict]:
        """构建事件时间线"""
        # 按日期排序文章
        sorted_articles = sorted(articles, key=lambda x: x.get('normalized_date', datetime.now()))
        
        timeline = []
        
        if self.client:
            try:
                # 使用LLM提取时间线上的关键事件
                for article in sorted_articles[:10]:  # 限制文章数量
                    response = self.client.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=[
                            {"role": "system", "content": "你是一个时间线分析专家。请从文章中提取具体的事件和时间信息。"},
                            {"role": "user", "content": f"请从以下文章中提取具体的事件信息。以JSON格式返回：[{{\"date\": \"日期\", \"event\": \"事件描述\"}}, ...]\n\n文章标题：{article['title']}\n文章内容：{article['content'][:1000]}..."}
                        ],
                        response_format={"type": "json_object"}
                    )
                    
                    import json
                    events = json.loads(response.choices[0].message.content)
                    timeline.extend(events)
                    
            except Exception as e:
                logger.error(f"使用LLM构建时间线时出错: {e}")
                # 出错时返回基于文章日期的模拟时间线
                timeline = self._generate_mock_timeline(sorted_articles)
        else:
            # 没有API密钥时返回模拟时间线
            timeline = self._generate_mock_timeline(sorted_articles)
        
        # 按日期排序并去重
        timeline.sort(key=lambda x: x.get('date', datetime.now().strftime('%Y-%m-%d')))
        
        return timeline[:20]  # 限制时间线事件数量
    
    def _generate_mock_entities(self, top_n: int) -> List[Dict]:
        """生成模拟实体数据"""
        mock_entities = [
            {"name": "大型语言模型", "type": "技术", "description": "能够理解和生成人类语言的AI系统"},
            {"name": "GPT-4", "type": "产品", "description": "OpenAI开发的最新一代大型语言模型"},
            {"name": "计算机视觉", "type": "技术领域", "description": "让计算机理解和解释图像的技术"},
            {"name": "深度学习", "type": "技术方法", "description": "基于神经网络的机器学习方法"},
            {"name": "人工智能伦理", "type": "研究领域", "description": "研究AI技术的道德和社会影响"},
            {"name": "OpenAI", "type": "组织", "description": "领先的人工智能研究公司"},
            {"name": "Google DeepMind", "type": "组织", "description": "专注于人工智能研究的公司"},
            {"name": "自然语言处理", "type": "技术领域", "description": "让计算机处理人类语言的技术"},
            {"name": "强化学习", "type": "技术方法", "description": "通过奖惩机制学习最优策略的方法"},
            {"name": "自动驾驶", "type": "应用领域", "description": "使用AI技术实现车辆自动行驶"}
        ]
        return mock_entities[:top_n]
    
    def _generate_mock_themes(self, top_n: int) -> List[Dict]:
        """生成模拟主题数据"""
        mock_themes = [
            {"name": "大型语言模型的发展", "description": "大型语言模型在规模、能力和应用方面的最新进展"},
            {"name": "人工智能的伦理挑战", "description": "AI技术发展带来的隐私、偏见和安全等伦理问题"},
            {"name": "跨模态AI系统", "description": "能够处理文本、图像、音频等多种数据类型的AI系统"},
            {"name": "AI在医疗领域的应用", "description": "人工智能技术在医疗诊断、药物研发等方面的应用"},
            {"name": "AI监管与政策", "description": "全球范围内对人工智能技术的监管框架和政策讨论"}
        ]
        return mock_themes[:top_n]
    
    def _generate_mock_timeline(self, articles: List[Dict]) -> List[Dict]:
        """基于文章日期生成模拟时间线"""
        timeline = []
        event_templates = [
            "研究人员发布了关于{topic}的重要研究成果",
            "{topic}技术在{field}领域取得突破",
            "主要科技公司发布新一代{topic}产品",
            "专家召开关于{topic}发展趋势的研讨会",
            "相关监管机构提出{topic}监管框架草案"
        ]
        
        fields = ["医疗健康", "金融服务", "智能制造", "交通运输", "教育科技"]
        
        for i, article in enumerate(articles):
            date = article.get('normalized_date', datetime.now())
            event_template = event_templates[i % len(event_templates)]
            field = fields[i % len(fields)]
            
            event = event_template.format(topic="人工智能", field=field)
            
            timeline.append({
                "date": date.strftime("%Y-%m-%d"),
                "event": event
            })
        
        return timeline