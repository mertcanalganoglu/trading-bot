'use client'

import React, { useEffect, useRef } from 'react'
import { createChart, ColorType, CrosshairMode, SeriesMarkerPosition, SeriesMarkerShape } from 'lightweight-charts'

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
    console.log('TradingViewChart data:', data)
    console.log('TradingViewChart signals:', signals)
    
    if (!chartContainerRef.current) {
      console.error('Chart container ref is not available')
      return
    }

    if (!data.length) {
      console.warn('No data available for chart')
      return
    }

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
        scaleMargins: {
          top: 0.1,
          bottom: 0.1,
        },
        autoScale: true,
      },
      timeScale: {
        borderColor: '#2B2B3F',
        timeVisible: true,
        secondsVisible: false,
        tickMarkFormatter: (time: number) => {
          const date = new Date(time * 1000)
          return date.toLocaleDateString('tr-TR', {
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
          })
        }
      },
      width: chartContainerRef.current.clientWidth,
      height: 500,
    })

    // Candlestick serisi
    const candlestickSeries = chart.addCandlestickSeries({
      upColor: '#26a69a',
      downColor: '#ef5350',
      borderVisible: true,
      borderColor: '#378658',
      borderUpColor: '#26a69a',
      borderDownColor: '#ef5350',
      wickUpColor: '#26a69a',
      wickDownColor: '#ef5350',
      priceFormat: {
        type: 'price',
        precision: 2,
        minMove: 0.01,
      },
      priceScaleId: 'right',
    })

    // ATR serisi
    const atrSeries = chart.addLineSeries({
      color: '#9B59B6',
      lineWidth: 2,
      title: 'ATR (14)',
      priceScaleId: 'right',
      priceFormat: {
        type: 'price',
        precision: 2,
        minMove: 0.01,
      },
    })

    // Verileri ayarla
    const candleData = data
      .map(d => {
        const timestamp = Math.floor(new Date(d.time).getTime() / 1000)
        return {
          time: timestamp as any,  // Lightweight Charts için time tipini any olarak belirt
          open: d.open,
          high: d.high,
          low: d.low,
          close: d.close,
        }
      })
      .sort((a, b) => a.time - b.time)  // Zamana göre sırala

    const atrData = data
      .map(d => {
        const timestamp = Math.floor(new Date(d.time).getTime() / 1000)
        return {
          time: timestamp as any,  // Lightweight Charts için time tipini any olarak belirt
          value: d.atr,
        }
      })
      .sort((a, b) => a.time - b.time)  // Zamana göre sırala

    candlestickSeries.setData(candleData)
    atrSeries.setData(atrData)

    // Alış-satış sinyallerini ekle
    const sortedSignals = signals
      .map(signal => {
        const timestamp = Math.floor(new Date(signal.time).getTime() / 1000)
        return {
          time: timestamp as any,  // Lightweight Charts için time tipini any olarak belirt
          position: signal.position === 'buy' ? 'belowBar' as SeriesMarkerPosition : 'aboveBar' as SeriesMarkerPosition,
          color: signal.position === 'buy' ? '#26a69a' : '#ef5350',
          shape: signal.position === 'buy' ? 'arrowUp' as SeriesMarkerShape : 'arrowDown' as SeriesMarkerShape,
          text: signal.position === 'buy' ? 'BUY' : 'SELL',
        }
      })
      .sort((a, b) => a.time - b.time)  // Zamana göre sırala

    candlestickSeries.setMarkers(sortedSignals)

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
      
      {/* Lejant */}
      <div className="mt-4 flex flex-wrap gap-4 text-sm">
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-[#26a69a]" />
          <span className="text-white">Yükselen Mum (Alıcıların Baskın Olduğu Dönem)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-[#ef5350]" />
          <span className="text-white">Düşen Mum (Satıcıların Baskın Olduğu Dönem)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-4 bg-[#9B59B6]" />
          <span className="text-white">ATR (Average True Range) Göstergesi</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center justify-center w-4 h-4 text-[#26a69a]">▲</div>
          <span className="text-white">Alış Sinyali (ATR Breakout)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center justify-center w-4 h-4 text-[#ef5350]">▼</div>
          <span className="text-white">Satış Sinyali (ATR Breakdown)</span>
        </div>
      </div>

      {/* Strateji Açıklaması */}
      <div className="mt-6 space-y-4 text-sm">
        <div className="text-white">
          <h3 className="font-bold mb-2">📊 Mum Çubukları Nasıl Okunur?</h3>
          <ul className="list-disc pl-5 space-y-1 text-gray-300">
            <li>Yeşil/Mavi Mum (<span className="text-[#26a69a]">■</span>): Kapanış fiyatı açılış fiyatından yüksek</li>
            <li>Kırmızı Mum (<span className="text-[#ef5350]">■</span>): Kapanış fiyatı açılış fiyatından düşük</li>
            <li>Mumun Gövdesi: Açılış ve kapanış fiyatları arasındaki fark</li>
            <li>Mumun Fitili: O periyottaki en yüksek ve en düşük fiyatlar</li>
          </ul>
        </div>

        <div className="text-white">
          <h3 className="font-bold mb-2">📈 ATR (Average True Range) Nedir?</h3>
          <ul className="list-disc pl-5 space-y-1 text-gray-300">
            <li>ATR (<span className="text-[#9B59B6]">■</span>), grafikte mor renkli çizgi ile gösterilen volatilite göstergesidir</li>
            <li>14 periyotluk hareketli ortalama kullanılarak hesaplanır</li>
            <li>True Range = En yüksek değer (Yüksek, Önceki Kapanış) - En düşük değer (Düşük, Önceki Kapanış)</li>
            <li>ATR değeri ne kadar yüksekse, o kadar fazla fiyat oynaklığı var demektir</li>
          </ul>
        </div>

        <div className="text-white">
          <h3 className="font-bold mb-2">📊 ATR Stratejisi Nasıl Kullanılır?</h3>
          <ul className="list-disc pl-5 space-y-1 text-gray-300">
            <li>Alış Sinyali (<span className="text-[#26a69a]">▲</span>): 
              <ul className="list-disc pl-5 mt-1">
                <li>Fiyat, önceki kapanışın ATR kadar üzerine çıktığında oluşur</li>
                <li>Trend yukarı yönlü olabilir</li>
                <li>Stop-loss için ATR değeri kadar aşağısı kullanılabilir</li>
              </ul>
            </li>
            <li>Satış Sinyali (<span className="text-[#ef5350]">▼</span>):
              <ul className="list-disc pl-5 mt-1">
                <li>Fiyat, önceki kapanışın ATR kadar altına düştüğünde oluşur</li>
                <li>Trend aşağı yönlü olabilir</li>
                <li>Stop-loss için ATR değeri kadar yukarısı kullanılabilir</li>
              </ul>
            </li>
          </ul>
        </div>

        <div className="text-white">
          <h3 className="font-bold mb-2">⚠️ Risk Yönetimi</h3>
          <ul className="list-disc pl-5 space-y-1 text-gray-300">
            <li>ATR, stop-loss seviyelerini belirlemek için kullanılabilir</li>
            <li>Yüksek ATR dönemlerinde pozisyon büyüklüğünü azaltmak düşünülebilir</li>
            <li>Düşük ATR dönemlerinde daha yakın stop-loss seviyeleri kullanılabilir</li>
          </ul>
        </div>

        <div className="text-gray-400 mt-4">
          <p><strong>Not:</strong> Bu göstergeler ve sinyaller sadece bilgi amaçlıdır ve kesin alım-satım tavsiyeleri değildir. Yatırım kararlarınızı verirken her zaman kendi araştırmanızı yapmalı ve risk yönetimi kurallarına uymalısınız.</p>
        </div>
      </div>
    </div>
  )
} 