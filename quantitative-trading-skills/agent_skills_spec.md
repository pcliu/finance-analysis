# Agent Skills Specification

This marketplace follows the official Agent Skills Specification. Each skill in this marketplace must:

1. **Directory Name**: Match the skill name (hyphen-case)
2. **SKILL.md File**: Required file with proper YAML frontmatter
3. **YAML Frontmatter**: Must include `name` and `description` fields
4. **Optional Features**: May include scripts, examples, and resources

## Required Structure

```
skill-name/
├── SKILL.md          # Required: Main skill definition
├── examples/          # Optional: Usage examples
├── scripts/           # Optional: Implementation scripts
└── resources/         # Optional: Additional resources
```

## YAML Frontmatter Requirements

```yaml
---
name: skill-name          # Required: hyphen-case, matches directory
description: Skill description  # Required: What the skill does
license: MIT             # Optional: License information
allowed-tools: []        # Optional: Pre-approved tools
metadata: {}             # Optional: Additional metadata
---
```

## Skills in This Marketplace

### quantitative-trading
- **Name**: quantitative-trading
- **Purpose**: Comprehensive quantitative trading toolkit
- **Features**: Stock analysis, technical indicators, strategies, backtesting
- **Dependencies**: Python, yfinance, pandas, numpy
- **License**: Permissive open-source license

## Usage

Skills in this marketplace can be referenced by name:
```
skill: "quantitative-trading"
```

The skill will be automatically loaded and made available for use.