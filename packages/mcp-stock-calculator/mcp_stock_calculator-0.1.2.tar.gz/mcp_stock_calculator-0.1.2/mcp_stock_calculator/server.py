from mcp_stock_calculator.calculator import StockCalculator
from mcp.server.fastmcp import FastMCP
from datetime import datetime
import asyncio
import logging
logger = logging.getLogger("AKShare-MCP")
mcp = FastMCP("CalculatorService",
                version = "1.2.0",
                description = "AKShare Financial Data Service",
                dependencies = ["akshare>=1.10.0", "pandas"],
                env_vars = {"CACHE_ENABLED": "true"},
                debug = False
                )

@mcp.tool()
def get_indicators(symbol: str = "000001", start_date: str = "20230101", end_date: str = None) -> dict:
    """
    获取指定股票在给定时间区间内的技术指标。

    参数：
        symbol (str): 股票代码，默认为"000001"。
        start_date (str): 开始日期，格式为"YYYYMMDD"，默认为"20230101"。
        end_date (str, 可选): 结束日期，格式为"YYYYMMDD"，默认为当前日期。

    返回：
        dict: 包含以下字段：
            - status (str): "success" 或 "error"。
            - symbol (str): 股票代码。
            - start_date (str): 开始日期。
            - end_date (str): 结束日期。
            - data (dict): 技术指标数据（status为success时返回）。
            - message (str): 错误信息（status为error时返回）。

    用途：
        用于获取指定股票在指定时间区间内的技术指标数据。
    """
    if end_date is None:
        end_date = datetime.now().strftime('%Y%m%d')
    try:
        result = StockCalculator.calculate(symbol, start_date, end_date)
        return {
            "status": "success",
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "data": result
        }
    except Exception as e:
        return {
            "status": "error",
            "message": f"计算指标时出错: {str(e)}"
        }

@mcp.tool()
def health_check() -> dict:
    """
    健康检查接口。

    参数：
        无

    返回：
        dict: 包含以下字段：
            - status (str): 服务健康状态，固定为"healthy"。

    用途：
        用于检测服务是否正常运行。
    """
    return {"status": "healthy"}


async def run_server():
    """启动服务"""
    print("Starting AKShare MCP service...")
    try:
        await mcp.run_sse_async()
    except Exception as e:
        print(f"服务启动失败: {str(e)}")
        raise

if __name__ == "__main__":
    asyncio.run(run_server())