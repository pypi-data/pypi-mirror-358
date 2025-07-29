import akshare as ak
import pandas as pd
import numpy as np
from datetime import datetime

class StockCalculator:
    @staticmethod
    def ema(series, span):
        return series.ewm(span=span, adjust=False).mean()

    @staticmethod
    def calc_macd(close):
        ema12 = StockCalculator.ema(close, 12)
        ema26 = StockCalculator.ema(close, 26)
        macd = ema12 - ema26
        signal = StockCalculator.ema(macd, 9)
        hist = macd - signal
        return pd.DataFrame({
            'MACD_12_26_9': macd,
            'MACDs_12_26_9': signal,
            'MACDh_12_26_9': hist
        })

    @staticmethod
    def calc_rsi(close, length=14):
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).rolling(length).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(length).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi

    @staticmethod
    def calc_kdj(df, n=14, k_period=3, d_period=3):
        low_min = df['low'].rolling(window=n, min_periods=1).min()
        high_max = df['high'].rolling(window=n, min_periods=1).max()
        rsv = (df['close'] - low_min) / (high_max - low_min) * 100
        k = rsv.ewm(com=(k_period-1), adjust=False).mean()
        d = k.ewm(com=(d_period-1), adjust=False).mean()
        j = 3 * k - 2 * d
        return pd.DataFrame({
            'STOCHk_14_3_3': k,
            'STOCHd_14_3_3': d,
            'STOCHj_14_3_3': j
        })

    @staticmethod
    def calc_boll(close, length=20):
        ma = close.rolling(window=length).mean()
        std = close.rolling(window=length).std()
        upper = ma + 2 * std
        lower = ma - 2 * std
        return pd.DataFrame({
            f'BBL_{length}_2.0': lower,
            f'BBM_{length}_2.0': ma,
            f'BBU_{length}_2.0': upper
        })

    @staticmethod
    def calc_obv(close, volume):
        obv = [0]
        for i in range(1, len(close)):
            if close.iloc[i] > close.iloc[i-1]:
                obv.append(obv[-1] + volume.iloc[i])
            elif close.iloc[i] < close.iloc[i-1]:
                obv.append(obv[-1] - volume.iloc[i])
            else:
                obv.append(obv[-1])
        return pd.Series(obv, index=close.index)

    @staticmethod
    def calc_atr(df, length=14):
        high = df['high']
        low = df['low']
        close = df['close']
        prev_close = close.shift(1)
        tr = pd.concat([
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs()
        ], axis=1).max(axis=1)
        atr = tr.rolling(window=length).mean()
        return atr

    @staticmethod
    def fetch_stock_data(symbol, start_date, end_date):
        df = ak.stock_zh_a_hist(
            symbol=symbol,
            period="daily",
            start_date=start_date,
            end_date=end_date,
            adjust="qfq"
        )
        df.rename(columns={
            '日期': 'date',
            '开盘': 'open',
            '收盘': 'close',
            '最高': 'high',
            '最低': 'low',
            '成交量': 'volume'
        }, inplace=True)
        df['date'] = pd.to_datetime(df['date'])
        df.set_index('date', inplace=True)
        return df

    @staticmethod
    def calc_indicators(df):
        # MA
        df['MA5'] = df['close'].rolling(window=5).mean()
        df['MA20'] = df['close'].rolling(window=20).mean()
        df['MA60'] = df['close'].rolling(window=60).mean()
        # MACD
        macd = StockCalculator.calc_macd(df['close'])
        df = pd.concat([df, macd], axis=1)
        # RSI
        df['RSI'] = StockCalculator.calc_rsi(df['close'], length=14)
        # KDJ
        kdj = StockCalculator.calc_kdj(df)
        df = pd.concat([df, kdj], axis=1)
        # BOLL
        boll = StockCalculator.calc_boll(df['close'], length=20)
        df = pd.concat([df, boll], axis=1)
        # OBV
        df['OBV'] = StockCalculator.calc_obv(df['close'], df['volume'])
        # ATR
        df['ATR'] = StockCalculator.calc_atr(df, length=14)
        return df

    @staticmethod
    def generate_advice(df):
        latest = df.iloc[-1]
        advice = []
        # 趋势判断
        if latest['close'] > latest['MA20'] > latest['MA60']:
            advice.append("均线多头排列，趋势向上。")
        elif latest['close'] < latest['MA20'] < latest['MA60']:
            advice.append("均线空头排列，趋势向下。")
        # MACD
        if latest['MACD_12_26_9'] > 0 and latest['MACDh_12_26_9'] > 0:
            advice.append("MACD金叉，动能增强。")
        elif latest['MACD_12_26_9'] < 0 and latest['MACDh_12_26_9'] < 0:
            advice.append("MACD死叉，动能减弱。")
        # RSI
        if latest['RSI'] > 70:
            advice.append("RSI超买，短线需警惕回调。")
        elif latest['RSI'] < 30:
            advice.append("RSI超卖，短线或有反弹。")
        # KDJ
        if latest['STOCHk_14_3_3'] > 80:
            advice.append("KDJ超买，注意风险。")
        elif latest['STOCHk_14_3_3'] < 20:
            advice.append("KDJ超卖，关注反弹机会。")
        # BOLL
        if latest['close'] > latest['BBU_20_2.0']:
            advice.append("股价突破布林带上轨，短线或有回调。")
        elif latest['close'] < latest['BBL_20_2.0']:
            advice.append("股价跌破布林带下轨，或有超跌反弹。")
        # 成交量
        if latest['volume'] > df['volume'][-20:-1].mean() * 1.5:
            advice.append("近期放量，关注主力动向。")
        # 综合建议
        if "多头排列" in "".join(advice) and "金叉" in "".join(advice) and "超买" not in "".join(advice):
            final = "【建议】趋势向上，技术面较强，可考虑逢低关注，注意设置止损。"
        elif "空头排列" in "".join(advice) and "死叉" in "".join(advice):
            final = "【建议】趋势向下，技术面较弱，谨慎观望或逢高减持。"
        else:
            final = "【建议】信号不明显，建议观望或结合基本面进一步分析。"
        return {
            "indicators": latest.to_dict(),
            "advice_list": advice,
            "final_advice": final
        }

    @staticmethod
    def generate_prompt(symbol, start_date, end_date, indicators):
        return f"""请你作为一名资深股票分析师，结合以下A股个股的最新技术指标数据，给出专业、详细的投资建议。请从趋势判断、买卖时机、风险提示等方面进行分析，最后给出明确的操作建议（如买入、观望、减持等），并说明理由。

个股代码：{symbol}
分析区间：{start_date} 至 {end_date}
最新技术指标数据如下：
""" + "\n".join([f"- {k}：{v}" for k, v in indicators.items()]) + "\n\n请结合上述所有技术指标，给出你的详细分析和投资建议。"

    @staticmethod
    def calculate(symbol, start_date, end_date):
        df = StockCalculator.fetch_stock_data(symbol, start_date, end_date)
        df = StockCalculator.calc_indicators(df)
        result = StockCalculator.generate_advice(df)
        result["prompt"] = StockCalculator.generate_prompt(
            symbol, start_date, end_date, result["indicators"]
        )
        return result