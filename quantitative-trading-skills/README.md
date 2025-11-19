# Quantitative Trading Marketplace

A dedicated marketplace for quantitative trading and financial analysis skills.

## About This Marketplace

This marketplace contains specialized skills for:
- Stock market data analysis
- Technical indicator calculations
- Trading strategy development
- Portfolio optimization
- Risk management
- Backtesting frameworks

## Available Skills

### quantitative-trading
A comprehensive quantitative trading toolkit using yfinance for global markets and tushare for China/Hong Kong data, covering stock analysis, technical indicators, and trading strategy development.

**Key Features:**
- Real-time and historical stock data fetching (yfinance global + tushare for CN/HK)
- Technical indicators (RSI, MACD, Bollinger Bands, etc.)
- Trading strategy implementation
- Portfolio analysis and optimization
- Risk assessment and management
- Backtesting capabilities

**China & Hong Kong Support:**  
Set the environment variable `TUSHARE_TOKEN` (available from [tushare](https://tushare.pro/register)) to unlock mainland/HK coverage. The toolkit auto-detects Chinese/HK tickers and routes them through tushare for improved accuracy; override manually with the new `provider` and `market` parameters on each API call if needed.

## Usage

To use skills from this marketplace, simply reference them by name when working with Claude Code:

```
skill: "quantitative-trading"
```

## Installation

This marketplace is automatically available when using Claude Code with the skills plugin system.

## Contributing

To add new skills to this marketplace:
1. Create a new directory following the skill naming conventions
2. Include a properly formatted `SKILL.md` file
3. Follow the Agent Skills Specification guidelines

## License

Each skill in this marketplace may have its own license. Please check the individual skill documentation for specific licensing information.
