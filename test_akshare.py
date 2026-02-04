#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test updated economic-sentiment skill with correct API
"""

import akshare as ak


stock_zh_a_hist_df = ak.stock_zh_a_hist(
    symbol="159241",
    period="daily",
    start_date="20260203",
    end_date="20260203",
    adjust="hfq"
)
print(stock_zh_a_hist_df)
