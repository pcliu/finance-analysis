# Economic Sentiment Skill - Quick Examples

## Example 1: 查询芯片相关新闻
```python
import akshare as ak

# 获取芯片相关新闻（东方财富）
chip_news = ak.stock_news_em(symbol="芯片")

# 显示最新5条
print(chip_news.head(5))

# 或者获取百度财经新闻
econ_news = ak.news_economic_baidu()
print(econ_news.head(5))
```

## Example 2: 查看微博舆情
```python
import akshare as ak

# 获取微博舆情分析
weibo_sentiment = ak.stock_js_weibo_nlp_time(symbol="半导体")
print(weibo_sentiment)
```

## Example 3: 获取央视新闻
```python
import akshare as ak

# 查看央视新闻
cctv_news = ak.news_cctv()
print(cctv_news.head(10))
```

## Example 4: 简单情绪分析
```python
def simple_sentiment(text):
    """简单的关键词情绪分析"""
    positive_words = ['上涨', '突破', '利好', '增长', '创新高', '强势', '看多', '买入']
    negative_words = ['下跌', '暴跌', '利空', '风险', '下调', '疲软', '看空', '卖出']
    
    pos_count = sum(1 for word in positive_words if word in text)
    neg_count = sum(1 for word in negative_words if word in text)
    
    if pos_count > neg_count:
        return "positive ✅"
    elif neg_count > pos_count:
        return "negative ❌"
    else:
        return "neutral ➖"

# 应用到新闻
import akshare as ak
news = ak.news_economic()

for idx, item in news.head(5).itertuples():
    sentiment = simple_sentiment(item.content)
    print(f"{item.title}: {sentiment}")
```

## Example 5: 结合技术分析使用
```python
import akshare as ak

# 场景：用户问"159995（芯片ETF）技术分析，并结合舆情"

# Step 1: 技术分析（quantitative-trading skill）
# ... 计算 RSI, MACD, Bollinger 等指标 ...

# Step 2: 获取舆情背景（economic-sentiment skill）
chip_news = ak.stock_news_em(symbol="芯片")
latest_news = chip_news.head(5)

# Step 3: 情绪分析
sentiment_results = []
for idx, row in latest_news.iterrows():
    sentiment_results.append({
        'title': row['新闻标题'],
        'sentiment': simple_sentiment(row['新闻内容'])
    })

# Step 4: 整合结论
"""
【技术分析】
- RSI: 45（中性区域）
- MACD: 金叉形成，短期动能转强
- 布林带: 价格接近下轨，存在反弹空间

【舆情分析】
- 最新消息: "芯片国产化加速推进"（利好）
- 整体情绪: 偏积极（正面新闻占 70%）

【综合判断】
技术面显示短期反弹信号，舆情面支持行业发展，建议关注。
"""
```

## 常用 AkShare 函数速查

```python
import akshare as ak

# 股票新闻（东方财富）
ak.stock_news_em(symbol="关键词")

# 经济新闻（百度）
ak.news_economic_baidu()

# 央视新闻
ak.news_cctv()

# 微博舆情
ak.stock_js_weibo_nlp_time(symbol="关键词")
```
