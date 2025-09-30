# Topic 2: 自动主题摘要页面生成系统

## 项目概述

本项目是一个自动化的主题摘要页面生成系统，能够从多个新闻源爬取关于特定事件的文章，进行文本处理和分析，然后生成包含主摘要、关键实体、发展时间线和源文章链接的结构化摘要网页。

## 功能特点

- **多源数据爬取**：支持从BBC、CNN、纽约时报、路透社、新华社等多个新闻源获取文章
- **智能文本处理**：使用自然语言处理技术进行文本清洗、分词和关键词提取
- **LLM增强分析**：集成OpenAI API进行实体提取、主题识别和摘要生成
- **结构化摘要生成**：自动生成包含以下内容的HTML摘要页面：
  - 综合内容摘要
  - 关键实体列表（带类型和描述）
  - 主要主题分析
  - 事件发展时间线
  - 源文章链接列表
- **重复内容处理**：自动检测和移除重复或高度相似的文章

## 项目结构

```
topic2_automated_summary/
├── crawler/              # 爬虫模块
│   ├── base_crawler.py   # 爬虫基类
│   ├── bbc_crawler.py    # BBC爬虫
│   ├── cnn_crawler.py    # CNN爬虫
│   ├── nytimes_crawler.py # 纽约时报爬虫
│   ├── reuters_crawler.py # 路透社爬虫
│   ├── xinhua_crawler.py  # 新华社爬虫
│   └── generic_crawler.py # 通用爬虫（用于模拟数据）
├── processor/            # 数据处理模块
│   ├── data_processor.py # 基础数据处理器
│   └── llm_processor.py  # LLM增强处理器
├── generator/            # 页面生成模块
│   └── page_generator.py # HTML页面生成器
├── data/                 # 数据存储目录
├── config/               # 配置文件目录
├── output/               # 输出目录（生成的HTML页面）
├── main.py               # 主程序入口
├── requirements.txt      # 依赖包列表
├── .env                  # 环境变量配置
├── .env.example          # 环境变量示例
└── README.md             # 项目说明文档
```

## 环境要求

- Python 3.8+
- 依赖包见requirements.txt

## 安装指南

1. 克隆项目到本地：

```bash
git clone <repository_url>
cd topic2_automated_summary
```

2. 安装依赖：

```bash
pip install -r requirements.txt
```

3. 配置环境变量：

```bash
cp .env.example .env
# 编辑.env文件，填入OpenAI API密钥和其他配置
```

## 使用方法

### 基本使用

运行主程序，使用默认配置：

```bash
python main.py
```

### 自定义主题

指定要分析的事件主题：

```bash
python main.py --topic "2023年全球气候变化峰会"
```

### 自定义输出目录

```bash
python main.py --output ./my_outputs
```

## 配置说明

在`.env`文件中可以配置以下参数：

- `OPENAI_API_KEY`: OpenAI API密钥（可选，如果不提供则使用模拟数据）
- `EVENT_TOPIC`: 要爬取的事件主题
- `NEWS_SOURCES`: 新闻源列表，用逗号分隔
- `MAX_ARTICLES_PER_SOURCE`: 每个源最多爬取的文章数
- `MIN_TEXT_LENGTH`: 最小文本长度（过滤过短的文章）
- `EMBEDDING_MODEL`: 嵌入模型名称
- `TOP_N_ENTITIES`: 要提取的关键实体数量
- `TOP_N_THEMES`: 要提取的关键主题数量

## 运行流程

1. **数据爬取**：从配置的新闻源获取关于指定主题的文章
2. **数据预处理**：清理文本、分词、过滤重复内容
3. **内容分析**：使用LLM提取实体、识别主题、生成摘要、构建时间线
4. **页面生成**：将分析结果整合到HTML模板中，生成结构化摘要页面
5. **结果输出**：将生成的HTML页面保存到输出目录

## 注意事项

1. **API密钥**：如需使用真实的OpenAI API功能，请在.env文件中提供有效的API密钥
2. **爬虫限制**：由于真实新闻网站可能有反爬虫机制，默认情况下会返回模拟数据
3. **数据质量**：生成的摘要质量取决于爬取的文章质量和数量
4. **运行时间**：完整运行可能需要几分钟到十几分钟，取决于配置的新闻源数量和文章数量

## 技术栈

- **爬虫框架**：自定义爬虫 + BeautifulSoup
- **文本处理**：NLTK
- **LLM集成**：OpenAI Python API
- **页面生成**：Jinja2
- **配置管理**：python-dotenv

## 开发说明

### 添加新的新闻源

1. 在crawler目录下创建新的爬虫类，继承自BaseCrawler
2. 实现crawl()方法和_parse_article()方法
3. 在CrawlerFactory中添加新的爬虫类型

### 自定义页面样式

修改page_generator.py中的HTML模板来自定义页面样式和内容布局。

## 许可证

MIT License

## 联系方式

如有任何问题，请联系项目维护者。