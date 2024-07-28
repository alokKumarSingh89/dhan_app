from fastapi import FastAPI
# from statements import report
# from fyers_api import api as FyerAPI
from strategy.router import strategy
# from backtests.router import backtest
from paper_trade.router import paper_trade

app = FastAPI(title="Trading App")

# app.include_router(report.router)
# app.include_router(FyerAPI.router)
app.include_router(strategy)
# app.include_router(backtest)
app.include_router(paper_trade)


@app.get("/")
def alph_test():
    return {"Name": "Alok"}
