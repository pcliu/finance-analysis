---
name: economic-sentiment
description: >
  Economic sentiment and news monitoring toolkit for real-time market intelligence.
  Use when users request:
  - Market news and sentiment analysis
  - Hot topics and trending events in finance/economy
  - Macroeconomic policy updates
  - Industry-specific news monitoring
  - Social media sentiment tracking
  - Risk events and geopolitical updates
version: 1.0.0
dependencies:
  - python>=3.8
  - akshare>=1.12.0
---

# Economic Sentiment & News Monitoring Skill

A **lightweight information gathering tool** for monitoring economic sentiment, news, and hot topics to support quantitative trading decisions.

> **💡 PURPOSE: Information Gathering Only**
> 
> This skill provides **real-time context** to complement `quantitative-trading` analysis:
> - 📰 **Market news** - What's happening right now
> - 🔥 **Hot topics** - What traders are talking about
> - 📊 **Sentiment** - Market mood indicators
> - ⚠️ **Risk events** - Sudden market-moving events
> 
> **NOT** designed for:
> - ❌ Complex analysis reports
> - ❌ Historical backtesting
> - ❌ Detailed research documents
> 
> **Typical Usage:**
> ```
> User: "为什么芯片 ETF 今天大涨？"
> → Use this skill to fetch recent semiconductor industry news
> → Return summary of key events/sentiment to user
> ```

## Quick Start

Use **web search** or **AkShare** to fetch information directly:

```python
import akshare as ak

# 1️⃣ Get stock news (东方财富)
news = ak.stock_news_em(symbol="芯片")
print(news.head(10))

# 2️⃣ Get economic news (百度)
economic_news = ak.news_economic_baidu()
print(economic_news.head(5))

# 3️⃣ Get CCTV news
cctv_news = ak.news_cctv()
print(cctv_news.head(5))
```

## Core Functions

### 1. Market News (市场新闻)

Use **AkShare** to fetch news directly:

```python
import akshare as ak

# Stock-specific news from East Money
chip_news = ak.stock_news_em(symbol="芯片")
latest_news = chip_news.head(5)

# Or get general economic news from Baidu
economic_news = ak.news_economic_baidu()
print(economic_news.head(5))
```

### 2. Hot Topics (热点追踪)

Track trending topics on major platforms:

```python
import akshare as ak

# Weibo sentiment and reports  
weibo_nlp = ak.stock_js_weibo_nlp_time(symbol="半导体")
print(weibo_nlp)

# Get stock news mentions (东方财富)
stock_news = ak.stock_news_em(symbol="芯片")
print(stock_news.head(10))
```

### 3. Macro Events (宏观事件)

Monitor important economic data releases:

```python
import akshare as ak

# Economic news from Baidu
economic_news = ak.news_economic_baidu()
print(economic_news.head(10))

# CCTV news (央视新闻)
cctv_news = ak.news_cctv()
print(cctv_news.head(10))

# For macro calendar, use web search:
# "央行 降息 最新消息"
# "美联储 加息 时间表"
```

### 4. Simple Sentiment (简单情绪分析)

Basic keyword-based sentiment (no complex ML):

```python
def simple_sentiment(text):
    """Simple keyword-based sentiment scoring"""
    positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势']
    negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软']
    
    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)
    
    if pos_count > neg_count:
        return "positive"
    elif neg_count > pos_count:
        return "negative"
    else:
        return "neutral"

# Apply to news
for item in news.itertuples():
    sentiment = simple_sentiment(item.content)
    print(f"{item.title}: {sentiment}")
```

## Environment Setup

```bash
ENV_PYTHON=/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/python
ENV_PIP=/opt/homebrew/Caskroom/miniforge/base/envs/finance-analysis/bin/pip

$ENV_PIP install akshare
```

## Data Sources

### AkShare (主要数据源)
- `ak.stock_news_em(symbol="关键词")` - 东方财富股票新闻
- `ak.news_economic_baidu()` - 百度财经新闻
- `ak.news_cctv()` - 央视新闻
- `ak.stock_js_weibo_nlp_time(symbol="关键词")` - 微博舆情分析

### Web Search (补充)
- Use Antigravity's `search_web` tool for:
  - Breaking news: "芯片 最新消息"
  - Policy updates: "央行 政策 2026"
  - Industry events: "半导体 会议"

## Integration with Quantitative Trading

**Example Workflow:**

```python
# User asks: "159995 技术分析，并结合最近舆情判断"

# Step 1: Technical analysis (quantitative-trading)
# ... RSI, MACD, Bollinger analysis ...

# Step 2: Fetch context (economic-sentiment)
import akshare as ak
chip_news = ak.stock_news_em(symbol="芯片")
chip_news = chip_news.head(5)

# Step 3: Simple sentiment
sentiment_summary = []
for item in chip_news.itertuples():
    sentiment_summary.append({
        'title': item.title,
        'sentiment': simple_sentiment(item.content)
    })

# Step 4: Combine in response
"""
技术分析：
- RSI: 45 (中性)
- MACD: 金叉形成

舆情背景：
- 最新消息：芯片国产化加速（利好）
- 行业情绪：偏积极
- 结论：技术面+舆情面均支持，建议关注
"""
```

## Usage Guidelines

1. **Keep it Simple**: This is for quick information gathering, not deep analysis
2. **Use AkShare First**: It's already installed and has most Chinese market data
3. **Web Search for Breaking News**: Use `search_web` for very recent events
4. **No Complex Reports**: Just summarize key findings in chat response
5. **Focus on Context**: Help explain "why" technical signals are happening

## Common Use Cases

| User Question               | How to Use This Skill                               |
| :-------------------------- | :-------------------------------------------------- |
| "为什么芯片 ETF 今天涨了？" | `ak.news_economic()` + filter "芯片"                |
| "最近有什么宏观利好消息？"  | `ak.economic_calendar()` + `search_web`             |
| "半导体行业热度如何？"      | `ak.baidu_search_index()` + `ak.weibo_hot_search()` |
| "市场情绪怎么样？"          | `ak.stock_comment_em()` + simple sentiment          |

## Notes

- **No report generation required** - just return information in chat
- **No complex scripts needed** - use AkShare + simple Python inline
- **Speed over accuracy** - quick context is more valuable than perfect analysis
- **Complement, not replace** - technical analysis is still primary, sentiment is context
