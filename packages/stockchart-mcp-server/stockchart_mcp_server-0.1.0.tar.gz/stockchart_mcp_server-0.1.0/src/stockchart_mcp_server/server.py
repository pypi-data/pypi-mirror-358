#!/usr/bin/env python3
"""
주식 차트 MCP 서버
종목 코드를 입력하면 주식 차트를 생성해주는 MCP 서버입니다.
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from typing import Any, Sequence
import base64
import io

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib import font_manager
import numpy as np

from mcp.server.models import InitializationOptions
from mcp.server import NotificationOptions, Server
from mcp.types import (
    Resource,
    Tool,
    TextContent,
    ImageContent,
    EmbeddedResource,
    LoggingLevel
)

# 한글 폰트 설정
plt.rcParams['font.family'] = ['Arial Unicode MS', 'AppleGothic', 'Malgun Gothic', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("stock-chart-mcp")

app = Server("stock-chart-mcp")

def format_korean_number(num):
    """숫자를 한국어 단위로 포맷팅"""
    if num >= 1_000_000_000_000:  # 조
        return f"{num/1_000_000_000_000:.1f}조"
    elif num >= 100_000_000:  # 억
        return f"{num/100_000_000:.1f}억"
    elif num >= 10_000:  # 만
        return f"{num/10_000:.1f}만"
    else:
        return f"{num:,.0f}"

def get_stock_data(symbol: str, period: str = "1y") -> pd.DataFrame:
    """주식 데이터 가져오기"""
    try:
        # 한국 주식의 경우 .KS 또는 .KQ 접미사 추가
        if symbol.isdigit():
            # 코스피
            if symbol.startswith('0'):
                stock_symbol = f"{symbol}.KQ"  # 코스닥
            else:
                stock_symbol = f"{symbol}.KS"  # 코스피
        else:
            stock_symbol = symbol
        
        stock = yf.Ticker(stock_symbol)
        data = stock.history(period=period)
        
        if data.empty:
            # 접미사 없이 다시 시도
            stock = yf.Ticker(symbol)
            data = stock.history(period=period)
        
        return data, stock_symbol
    except Exception as e:
        logger.error(f"주식 데이터 가져오기 실패: {e}")
        raise

def create_stock_chart(symbol: str, period: str = "1y") -> str:
    """주식 차트 생성하고 base64 인코딩된 이미지 반환"""
    try:
        data, stock_symbol = get_stock_data(symbol, period)
        
        if data.empty:
            raise ValueError(f"'{symbol}' 종목의 데이터를 찾을 수 없습니다.")
        
        # 차트 생성
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10), 
                                       gridspec_kw={'height_ratios': [3, 1]})
        
        # 주가 차트
        ax1.plot(data.index, data['Close'], linewidth=2, color='#2E86C1', label='종가')
        ax1.fill_between(data.index, data['Close'], alpha=0.3, color='#85C1E9')
        
        # 이동평균선
        ma20 = data['Close'].rolling(window=20).mean()
        ma60 = data['Close'].rolling(window=60).mean()
        ax1.plot(data.index, ma20, '--', color='orange', alpha=0.8, label='MA20')
        ax1.plot(data.index, ma60, '--', color='red', alpha=0.8, label='MA60')
        
        ax1.set_title(f'{symbol} 주가 차트 ({period})', fontsize=16, fontweight='bold')
        ax1.set_ylabel('주가 (원)', fontsize=12)
        ax1.legend()
        ax1.grid(True, alpha=0.3)
        
        # 날짜 포맷팅
        ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax1.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        
        # 거래량 차트
        colors = ['red' if close >= open_price else 'blue' 
                 for close, open_price in zip(data['Close'], data['Open'])]
        ax2.bar(data.index, data['Volume'], color=colors, alpha=0.6)
        ax2.set_ylabel('거래량', fontsize=12)
        ax2.set_xlabel('날짜', fontsize=12)
        ax2.grid(True, alpha=0.3)
        
        # y축 포맷팅
        ax2.yaxis.set_major_formatter(plt.FuncFormatter(
            lambda x, p: format_korean_number(x)
        ))
        
        plt.tight_layout()
        
        # 이미지를 base64로 인코딩
        buffer = io.BytesIO()
        plt.savefig(buffer, format='png', dpi=150, bbox_inches='tight')
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode()
        plt.close()
        
        return image_base64
        
    except Exception as e:
        logger.error(f"차트 생성 실패: {e}")
        raise

def get_stock_info(symbol: str) -> dict:
    """주식 기본 정보 가져오기"""
    try:
        data, stock_symbol = get_stock_data(symbol, "5d")
        
        if data.empty:
            raise ValueError(f"'{symbol}' 종목의 데이터를 찾을 수 없습니다.")
        
        latest = data.iloc[-1]
        previous = data.iloc[-2] if len(data) > 1 else latest
        
        change = latest['Close'] - previous['Close']
        change_percent = (change / previous['Close']) * 100
        
        return {
            "symbol": stock_symbol,
            "current_price": latest['Close'],
            "change": change,
            "change_percent": change_percent,
            "volume": latest['Volume'],
            "high": latest['High'],
            "low": latest['Low'],
            "date": latest.name.strftime('%Y-%m-%d')
        }
    except Exception as e:
        logger.error(f"주식 정보 가져오기 실패: {e}")
        raise

@app.list_tools()
async def handle_list_tools() -> list[Tool]:
    """사용 가능한 도구 목록"""
    return [
        Tool(
            name="get_stock_chart",
            description="종목 코드를 입력하면 주식 차트를 생성합니다. 한국 주식의 경우 6자리 숫자 코드를 입력하세요. (예: 005930 for 삼성전자)",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "주식 종목 코드 (예: 005930, AAPL, TSLA)"
                    },
                    "period": {
                        "type": "string",
                        "description": "차트 기간",
                        "enum": ["1d", "5d", "1mo", "3mo", "6mo", "1y", "2y", "5y", "10y"],
                        "default": "1y"
                    }
                },
                "required": ["symbol"]
            }
        ),
        Tool(
            name="get_stock_info",
            description="종목의 현재 주가 정보를 가져옵니다.",
            inputSchema={
                "type": "object",
                "properties": {
                    "symbol": {
                        "type": "string",
                        "description": "주식 종목 코드 (예: 005930, AAPL, TSLA)"
                    }
                },
                "required": ["symbol"]
            }
        )
    ]

@app.call_tool()
async def handle_call_tool(name: str, arguments: dict) -> list[TextContent | ImageContent]:
    """도구 호출 처리"""
    try:
        if name == "get_stock_chart":
            symbol = arguments.get("symbol", "")
            period = arguments.get("period", "1y")
            
            if not symbol:
                return [TextContent(
                    type="text",
                    text="오류: 종목 코드를 입력해주세요."
                )]
            
            # 차트 생성
            image_base64 = create_stock_chart(symbol, period)
            
            # 주식 정보도 함께 제공
            stock_info = get_stock_info(symbol)
            
            info_text = f"""📈 {stock_info['symbol']} 주식 정보

💰 현재가: {stock_info['current_price']:,.0f}원
📊 전일대비: {stock_info['change']:+.0f}원 ({stock_info['change_percent']:+.2f}%)
📅 기준일: {stock_info['date']}
📈 고가: {stock_info['high']:,.0f}원
📉 저가: {stock_info['low']:,.0f}원
📊 거래량: {format_korean_number(stock_info['volume'])}주

차트 기간: {period}"""
            
            return [
                TextContent(type="text", text=info_text),
                ImageContent(
                    type="image",
                    data=image_base64,
                    mimeType="image/png"
                )
            ]
            
        elif name == "get_stock_info":
            symbol = arguments.get("symbol", "")
            
            if not symbol:
                return [TextContent(
                    type="text",
                    text="오류: 종목 코드를 입력해주세요."
                )]
            
            stock_info = get_stock_info(symbol)
            
            info_text = f"""📊 {stock_info['symbol']} 주식 정보

💰 현재가: {stock_info['current_price']:,.0f}원
📊 전일대비: {stock_info['change']:+.0f}원 ({stock_info['change_percent']:+.2f}%)
📅 기준일: {stock_info['date']}
📈 고가: {stock_info['high']:,.0f}원
📉 저가: {stock_info['low']:,.0f}원
📊 거래량: {format_korean_number(stock_info['volume'])}주"""
            
            return [TextContent(type="text", text=info_text)]
        
        else:
            return [TextContent(
                type="text",
                text=f"알 수 없는 도구입니다: {name}"
            )]
            
    except Exception as e:
        error_msg = f"오류가 발생했습니다: {str(e)}"
        logger.error(error_msg)
        return [TextContent(type="text", text=error_msg)]

async def main():
    # Stdin/stdout로 MCP 서버 실행
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="stock-chart-mcp",
                server_version="0.1.0",
                capabilities=app.get_capabilities(
                    notification_options=NotificationOptions(),
                    experimental_capabilities={},
                ),
            ),
        )

if __name__ == "__main__":
    print("Starting Stock Chart MCP Server")
    import mcp.server.stdio
    asyncio.run(main()) 