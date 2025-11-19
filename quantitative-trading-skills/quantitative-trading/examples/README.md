# Examples

Small, copy-ready scripts showing how to call the skill.

| File | What it shows |
| ---- | ------------- |
| `basic_analysis.py` | Fetch a ticker, compute a couple of indicators, print a summary. |
| `api_usage_example.py` | Demonstrates the “import API module, run helper, print distilled output” workflow for Claude Code. |
| `progressive_discovery_example.py` | Walks through listing directories, reading docs, and composing scripts incrementally. |

Run any script from the repo root (after activating the `finance-analysis` env):

```bash
python quantitative-trading/examples/basic_analysis.py --ticker AAPL --period 6mo
```

Use these as templates—copy one into `workspace/`, adjust tickers/periods/weights, and keep only the prints you need to share back to the model.
