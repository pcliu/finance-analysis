"""
Sentiment Analysis: AMD, NVDA, GOOG
Date: 2026-05-03
Method: AKShare news fetch + web-search based news corpus + keyword sentiment
"""

import sys
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# ─────────────────────────────────────────────────────────────
# Sentiment keyword dictionaries (EN + ZH combined)
# ─────────────────────────────────────────────────────────────
POSITIVE_WORDS_EN = [
    'beat', 'record', 'surge', 'growth', 'strong', 'rally', 'upgrade',
    'bullish', 'buy', 'outperform', 'raises', 'exceeds', 'dominance',
    'partnership', 'demand', 'deal', 'backlog', 'accelerate',
]
NEGATIVE_WORDS_EN = [
    'miss', 'disappoint', 'delay', 'decline', 'sell', 'risk', 'concern',
    'warning', 'restrict', 'export control', 'ban', 'headwind', 'bearish',
    'downgrade', 'overbought', 'pullback', 'margin pressure', 'crash',
]
POSITIVE_WORDS_ZH = ['上涨','突破','利好','增长','创新高','强势','爆发','大涨','高增','合作','需求']
NEGATIVE_WORDS_ZH = ['下跌','暴跌','利空','风险','下调','疲软','受限','禁令','出口管制','回调']


def simple_sentiment(text: str) -> dict:
    """Keyword-based sentiment scoring for EN + ZH text."""
    text_lower = text.lower()
    pos = sum(1 for w in POSITIVE_WORDS_EN if w in text_lower)
    pos += sum(1 for w in POSITIVE_WORDS_ZH if w in text)
    neg = sum(1 for w in NEGATIVE_WORDS_EN if w in text_lower)
    neg += sum(1 for w in NEGATIVE_WORDS_ZH if w in text)
    score = pos - neg
    if score > 0:
        label = 'positive'
    elif score < 0:
        label = 'negative'
    else:
        label = 'neutral'
    return {'label': label, 'score': score, 'pos_count': pos, 'neg_count': neg}


# ─────────────────────────────────────────────────────────────
# News corpus: gathered via web search on 2026-05-03
# Sources: MarketBeat, TradingKey, 24/7 Wall St., TIKR, Motley Fool,
#          CNBC, Yahoo Finance, HeyGoTrade, 247wallst, BigGo Finance
# ─────────────────────────────────────────────────────────────

NEWS_CORPUS = {
    'AMD': [
        {
            'source': 'TradingKey (2026-05-01)',
            'title': 'AMD Q1 Earnings Preview: Record Revenue Fails to Mask Gross Margin Headwinds, OpenAI Partnership in Focus',
            'summary': 'AMD expected to beat revenue consensus at $9.84B (+32% YoY). Gross margin ~55% faces 2% QoQ decline. MI308 China sales drop from $390M to ~$100M. OpenAI 6GW MI450 deal and Meta 6GW deal are major catalysts for H2 2026.',
        },
        {
            'source': '24/7 Wall St. (2026-04-16)',
            'title': 'AMD Gains 6% Ahead of May Earnings: Is the AI Chip Challenger Finally Ready to Rival NVIDIA?',
            'summary': 'AMD stock rallied 6% on strong data center GPU demand signals. Analysts see AMD as a credible rival to Nvidia in AI inference workloads. Instinct MI350 roadmap on track.',
        },
        {
            'source': 'Motley Fool (2026-04-29)',
            'title': 'Advanced Micro Devices Rises After Analyst Upgrade Points to Data Center GPU Demand Ahead of Earnings',
            'summary': 'Analyst upgrades AMD citing AI accelerator demand surge, raises price target. AMD stock climbed near ATH. 37 Buy / 12 Hold / 0 Sell consensus, avg PT $289.35.',
        },
        {
            'source': 'Yahoo Finance (2026-04-28)',
            'title': 'Buy AMD Stock Before Q1 Earnings: What You Should Know',
            'summary': 'AMD expected Q1 EPS $1.27-1.28 (+33% YoY). EPYC processors and Instinct GPUs driving strength. Stock up 70% YTD. Key risk: stock trades above consensus PT, earnings event on May 5.',
        },
        {
            'source': 'Ad-hoc-news (2026-04-25)',
            'title': "AMD's Rally Faces a Reality Check as Earnings Day Approaches",
            'summary': 'AMD hit ATH $352.99 but overbought RSI ~81.7. Gross margin headwind from China MI308 export control. SAFE Chips Act risk could reimpose restrictions. Short-term pullback risk ahead of May 5 earnings.',
        },
        {
            'source': 'AMD IR (2026-04-15)',
            'title': 'AMD to Report Fiscal Q1 2026 Financial Results on May 5, 2026',
            'summary': 'AMD will host earnings call after market close on May 5, 2026. Guidance: revenue $9.8B ±$300M, gross margin ~55%.',
        },
        {
            'source': 'TrendForce (2026-02-04)',
            'title': 'AMD 1Q Sales to Slip Despite $100M MI308 China Boost, Next-Gen AI Chips Set for 2H Ramp',
            'summary': 'AMD MI308 China revenue declining sharply. MI350/MI450 AI chips ramp targeted for H2 2026. China export risk limits near-term GPU revenue.',
        },
    ],
    'NVDA': [
        {
            'source': 'Dev|Journal (2026-05-01)',
            'title': 'NVIDIA (NVDA) 21-Day Outlook: Earnings Catalyst and Blackwell Demand Drive Bullish Setup',
            'summary': 'Nvidia earnings May 20 expected to beat: Q1 FY2027 consensus $78.8B revenue. Blackwell sold out through mid-year. Strong Buy consensus, 12M PT ~$270.',
        },
        {
            'source': 'TIKR (2026-04-30)',
            'title': 'NVIDIA Stock Pulls Back Before May 20 Earnings: The $1 Trillion Demand Story',
            'summary': 'NVDA pulled back ~8% from ATH $216.61 to ~$198. $1 trillion purchase orders for Blackwell/Rubin through 2027. Key test: can revenue guidance top $78.8B consensus.',
        },
        {
            'source': 'Motley Fool (2026-01-03)',
            'title': "Nvidia's $65 Billion Forecast Sends a Clear Message About the AI Boom",
            'summary': 'Nvidia raised guidance to $65B+ for Q4 FY2026, signaling unstoppable AI infrastructure demand. Data center revenue leading growth.',
        },
        {
            'source': 'io-fund (2026-04-28)',
            'title': 'Is Nvidia Stock a Buy? Why Semiconductor Strength May Signal a Market Top',
            'summary': 'Some analysts caution that RSI ~74.76 suggests overbought conditions. Hardware moat becoming less absolute. One-quarter HBM4 delay for Rubin. Technical-fundamental divergence noted.',
        },
        {
            'source': 'TheStreet (2026-03-01)',
            'title': 'Forget Blackwell, Nvidia Future Is Vera Rubin and Agentic Software',
            'summary': 'Jensen Huang shipped first Vera Rubin samples to customers. H2 2026 production ramp on track. HBM4 delay risk (SK Hynix Q3 vs Q2 original ramp) of one quarter.',
        },
        {
            'source': 'Intellectia (2026-04-15)',
            'title': 'Nvidia Stock Analysis 2026: $1 Trillion AI Demand',
            'summary': 'Hyperscalers Microsoft, Amazon, Google, Meta collectively committed $1T+ in AI capex. NVDA primary beneficiary. Annual architecture cadence (Blackwell→Rubin) sustains moat.',
        },
    ],
    'GOOG': [
        {
            'source': 'CNBC (2026-04-29)',
            'title': "Alphabet Q1 2026 Earnings: Google Cloud Revenue Up 63%, Raises CapEx to $185-190B",
            'summary': 'Alphabet Q1 revenue $109.9B (+22% YoY), EPS $5.11. Google Cloud $20.03B (+63% YoY), far ahead of ~47% consensus. Cloud backlog $462B nearly doubled. CapEx raised to $180-190B.',
        },
        {
            'source': 'BigGo Finance / HeyGoTrade (2026-04-29)',
            'title': "Alphabet Shatters Records: Revenue Surges 22%, Cloud Backlog Nearly Doubles to $462B",
            'summary': 'Enterprise AI solutions first time primary driver for Google Cloud. Net income soared 81% to $62.6B. Search revenue +19%. 2027 CapEx to "significantly increase".',
        },
        {
            'source': '24/7 Wall St. (2026-04-30)',
            'title': "Wall Street Lifts Alphabet Price Targets After Cloud's 63% Growth: Is the AI Stack Story Just Getting Started?",
            'summary': 'Multiple analysts raised PTs: Susquehanna $460, Goldman Sachs $450, Canaccord $450, TD Cowen $450, Oppenheimer $425. Consensus avg PT $384.62. Strong Buy unanimous.',
        },
        {
            'source': 'Futurum (2026-04-30)',
            'title': "Alphabet Q1 FY 2026: AI Demand Surges as Cloud Capacity Caps Growth",
            'summary': 'Unprecedented internal/external demand for AI compute. Cloud capacity constraints limit near-term growth but backlog ensures multi-year revenue visibility. CapEx doubling YoY is FCF concern.',
        },
        {
            'source': 'CoinCodex (2026-04-28)',
            'title': "GOOG Stock Has 69.5% Probability of Hitting $400 in May 2026",
            'summary': 'Technical and fundamental convergence: 26/26 indicators bullish. Stock up 135% YoY, +34% in April alone. Strong momentum but SMA distances create pullback risk.',
        },
    ],
}


# ─────────────────────────────────────────────────────────────
# Score each news item and aggregate
# ─────────────────────────────────────────────────────────────

print("=" * 60)
print("Sentiment Analysis: AMD / NVDA / GOOG  |  2026-05-03")
print("=" * 60)

sentiment_results = {}
for ticker, news_list in NEWS_CORPUS.items():
    scored = []
    for item in news_list:
        combined = f"{item['title']} {item['summary']}"
        sent = simple_sentiment(combined)
        scored.append({**item, **sent})

    labels = [s['label'] for s in scored]
    scores = [s['score'] for s in scored]
    avg_score = sum(scores) / len(scores) if scores else 0
    pos_count = labels.count('positive')
    neg_count = labels.count('negative')
    neu_count = labels.count('neutral')

    if avg_score > 1.0:
        overall = 'positive'
    elif avg_score < -0.5:
        overall = 'negative'
    else:
        overall = 'neutral'

    sentiment_results[ticker] = {
        'overall_sentiment': overall,
        'avg_score':         round(avg_score, 2),
        'positive_count':    pos_count,
        'neutral_count':     neu_count,
        'negative_count':    neg_count,
        'news_count':        len(scored),
        'articles':          scored,
    }

    print(f"\n  {ticker}: overall={overall.upper()} | avg_score={avg_score:.2f} | "
          f"+{pos_count} ~{neu_count} -{neg_count} of {len(scored)} articles")
    for s in scored:
        print(f"    [{s['label']:8}] {s['title'][:72]}")


# ─────────────────────────────────────────────────────────────
# Market context summary (from web research)
# ─────────────────────────────────────────────────────────────
market_context = {
    'macro_environment': {
        'ai_capex_cycle': 'Hyperscalers (MSFT, AMZN, GOOG, Meta) collectively committed $180-190B+ AI capex in 2026',
        'semiconductor_market': 'Gartner forecasts global semiconductor revenue >$1.3T in 2026 (highest growth in 2 decades); AI chips 30% of total',
        'fed_policy': 'Fed holding rates; inflation contained; risk-on environment supports growth-tech',
        'geopolitical_risk': 'US-China chip export controls ongoing; SAFE Chips Act legislative risk for AMD MI308 sales',
        'sector_performance': 'Chip stocks up 14-51% YTD; AMD +70%, NVDA +26%, GOOG (not chip) +135% YoY',
    },
    'key_events_upcoming': [
        {'date': '2026-05-05', 'event': 'AMD Q1 FY2026 earnings (after close)', 'impact': 'HIGH'},
        {'date': '2026-05-20', 'event': 'NVDA Q1 FY2027 earnings (after close)', 'impact': 'HIGH'},
        {'date': '2026-H2',    'event': 'AMD MI450 first deliveries (OpenAI/Meta 6GW deals)', 'impact': 'MEDIUM'},
        {'date': '2026-H2',    'event': 'NVDA Vera Rubin production ramp', 'impact': 'MEDIUM'},
    ],
}

output = {
    'analysis_date':   '2026-05-03',
    'tickers':         list(NEWS_CORPUS.keys()),
    'sentiment':       sentiment_results,
    'market_context':  market_context,
}

out_path = os.path.join(SCRIPT_DIR, 'sentiment_AMD_NVDA_GOOG_data.json')
with open(out_path, 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2, ensure_ascii=False)

print(f"\n✅ Sentiment data saved: {out_path}")
