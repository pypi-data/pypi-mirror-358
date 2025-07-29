from server import run as mcp_run


def main():
    """MCP Stock Indicator Calculator: 计算A股技术指标并提供投资建议"""
    import argparse
    parser = argparse.ArgumentParser(
        description="计算A股技术指标(MACD, RSI, KDJ等)并提供投资建议"
    )
    parser.add_argument('--host', type=str, default='0.0.0.0', help='服务监听地址')
    parser.add_argument('--port', type=int, default=5000, help='服务监听端口')
    args = parser.parse_args()

    print(f"启动A股技术指标计算服务: http://{args.host}:{args.port}")
    print("可用端点:")
    print("  GET /indicators?symbol=股票代码&start_date=开始日期&end_date=结束日期")
    print("  GET /health")
    mcp_run(host=args.host, port=args.port)


if __name__ == "__main__":
    main()