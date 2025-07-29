from flask import Flask, jsonify, request
from mcp_stock_calculator.calculator import StockCalculator
from datetime import datetime

app = Flask(__name__)


@app.route('/indicators', methods=['GET'])
def get_indicators():
    symbol = request.args.get('symbol', default='000001', type=str)
    start_date = request.args.get('start_date', default='20230101', type=str)
    end_date = request.args.get('end_date', default=datetime.now().strftime('%Y%m%d'), type=str)

    try:
        result = StockCalculator.calculate(symbol, start_date, end_date)
        return jsonify({
            "status": "success",
            "symbol": symbol,
            "start_date": start_date,
            "end_date": end_date,
            "data": result
        })
    except Exception as e:
        return jsonify({
            "status": "error",
            "message": f"计算指标时出错: {str(e)}"
        }), 500


@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "healthy"})


def run(host='0.0.0.0', port=5000):
    app.run(host=host, port=port)


if __name__ == '__main__':
    run()