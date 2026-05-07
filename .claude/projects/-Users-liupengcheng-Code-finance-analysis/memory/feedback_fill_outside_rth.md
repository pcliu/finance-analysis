---
name: 美股下单必须 fill_outside_rth=True
description: 美股限价单必须显式传 fill_outside_rth=True，否则只在 RTH 盘中撮合
type: feedback
---

美股限价单**必须**在 API 调用时显式传 `fill_outside_rth=True`，否则订单只在 RTH（09:30–16:00 ET）撮合，等同于只下了盘中单。

**Why:** 连续三次因为 `place_order` 封装函数没有该参数，导致下单后发现只覆盖盘中，被用户纠正。

**How to apply:**
- 直接调用 moomoo `ctx.place_order()` 时，始终加 `fill_outside_rth=True` 和 `time_in_force=ft.TimeInForce.DAY`
- 使用 skill 封装的 `place_order()` 时，已修复为默认 `fill_outside_rth=True`（2026-05-07），但仍要确认底层参数是否传递
- 下单前在订单摘要中明确标注「覆盖盘前/盘中/盘后」，作为提交前的检查项
