import tushare as ts

pro = ts.pro_api('602a0859f5c2f2cf0c5382dd3035f016b8b0dc18fd10cdd3e912f3c5')


#@df = ts.pro_bar(ts_code='688981.SZ', asset='I', start_date='20180101', end_date='20181011')

df = ts.pro_bar(ts_code='601899.SH', asset='E', start_date='20250101', end_date='20251011')

#df = pro.rt_etf_k(ts_code='688981.SZ', start_date='20251101', end_date='20251104')

#df = pro.daily(trade_date='20251114')
print(df)