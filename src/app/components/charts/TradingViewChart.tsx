'use client'

import React, { useEffect, useRef } from 'react'
import { createChart, ColorType, CrosshairMode } from 'lightweight-charts'

interface ChartData {
  time: string
  open: number
  high: number
  low: number
  close: number
  atr: number
}

interface TradeSignal {
  time: string
  position: 'buy' | 'sell'
  price: number
}

interface TradingViewChartProps {
  data: ChartData[]
  signals: TradeSignal[]
  symbol: string
}

export function TradingViewChart({ data, signals, symbol }: TradingViewChartProps) {
  const chartContainerRef = useRef<HTMLDivElement>(null)
  const chartRef = useRef<any>(null)

  useEffect(() => {
    if (!chartContainerRef.current) return

    // Chart oluştur
    const chart = createChart(chartContainerRef.current, {
      layout: {
        background: { color: '#1B1B1F' },
        textColor: '#DDD',
      },
      grid: {
        vertLines: { color: '#2B2B3F' },
        horzLines: { color: '#2B2B3F' },
      },
      crosshair: {
        mode: CrosshairMode.Normal,
      },
      rightPriceScale: {
        borderColor: '#2B2B3F',
      },
      timeScale: {
        borderColor: '#2B2B3F',
      },
      width: chartContainerRef.current.clientWidth,
      height: 500,
    })

    // Candlestick serisi
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: false,
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
    })

    // ATR serisi
    const atrSeries = chart.addLineSeries({
      color: '#9B59B6',
      lineWidth: 2,
      priceScaleId: 'right',
    })

    // Verileri ayarla
    const candleData = data.map(d => ({
      time: d.time,
      open: d.open,
      high: d.high,
      low: d.low,
      close: d.close,
    }))

    const atrData = data.map(d => ({
      time: d.time,
      value: d.atr,
    }))

    candlestickSeries.setData(candleData)
    atrSeries.setData(atrData)

    // Alış-satış sinyallerini ekle
    signals.forEach(signal => {
      const marker = {
        time: signal.time,
        position: signal.position === 'buy' ? 'belowBar' : 'aboveBar',
        color: signal.position === 'buy' ? '#26a69a' : '#ef5350',
        shape: signal.position === 'buy' ? 'arrowUp' : 'arrowDown',
        text: signal.position === 'buy' ? 'BUY' : 'SELL',
      }
      candlestickSeries.setMarkers([marker])
    })

    // Responsive davranış
    const handleResize = () => {
      if (chartContainerRef.current) {
        chart.applyOptions({
          width: chartContainerRef.current.clientWidth,
        })
      }
    }

    window.addEventListener('resize', handleResize)
    chartRef.current = chart

    return () => {
      window.removeEventListener('resize', handleResize)
      chart.remove()
    }
  }, [data, signals])

  return (
    <div className="p-4 rounded-lg bg-[#1B1B1F]">
      <h2 className="text-xl font-bold mb-4 text-white">{symbol} Chart with ATR</h2>
      <div ref={chartContainerRef} />
    </div>
  )
} 