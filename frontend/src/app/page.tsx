'use client'

import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { TradingViewChart } from './components/charts/TradingViewChart'

export default function Home() {
  const [symbol, setSymbol] = useState('BTCUSDT')
  const [data, setData] = useState<any[]>([])
  const [signals, setSignals] = useState<any[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchData = async () => {
      try {
        setLoading(true)
        console.log('Fetching data for symbol:', symbol)
        // ATR analizi ve sinyalleri al
        const response = await axios.get(`/api/v1/atr-analysis?symbol=${symbol}&interval=1h`)
        console.log('API Response:', response.data)
        
        if (!response.data.klines || !Array.isArray(response.data.klines)) {
          console.error('Invalid klines data:', response.data.klines)
          return
        }

        // Mum verilerini formatla
        const formattedData = response.data.klines.map((k: any) => ({
          time: k[0],
          open: parseFloat(k[1]),
          high: parseFloat(k[2]),
          low: parseFloat(k[3]),
          close: parseFloat(k[4]),
          atr: response.data.atr
        }))
        console.log('Formatted candle data:', formattedData)

        // Sinyal verilerini formatla
        const formattedSignals = response.data.signals.map((s: any) => ({
          time: s.time,
          position: s.type,
          price: s.price
        }))
        console.log('Formatted signals:', formattedSignals)

        setData(formattedData)
        setSignals(formattedSignals)
      } catch (error) {
        console.error('Error fetching data:', error)
        if (axios.isAxiosError(error)) {
          console.error('Axios error details:', {
            message: error.message,
            status: error.response?.status,
            data: error.response?.data
          })
        }
      } finally {
        setLoading(false)
      }
    }

    fetchData()
    // Her 5 dakikada bir güncelle
    const interval = setInterval(fetchData, 5 * 60 * 1000)
    return () => clearInterval(interval)
  }, [symbol])

  return (
    <main className="min-h-screen bg-black p-4">
      <div className="max-w-7xl mx-auto">
        <div className="mb-4 flex items-center justify-between">
          <h1 className="text-2xl font-bold text-white">Trading Bot Dashboard</h1>
          <select 
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            className="bg-[#1B1B1F] text-white px-4 py-2 rounded-lg"
          >
            <option value="BTCUSDT">BTCUSDT</option>
            <option value="ETHUSDT">ETHUSDT</option>
            <option value="SOLUSDT">SOLUSDT</option>
          </select>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-96">
            <div className="animate-spin rounded-full h-32 w-32 border-t-2 border-b-2 border-white"></div>
          </div>
        ) : (
          <TradingViewChart 
            data={data} 
            signals={signals} 
            symbol={symbol} 
          />
        )}
      </div>
    </main>
  )
}
