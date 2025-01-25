import React from 'react'
import { useQuery } from 'react-query'
import { useParams } from 'react-router-dom'
import axios from 'axios'

interface TokenData {
  token_id: string
  price_usd: number
  market_cap: number
  volume_24h: number
  timestamp: string
}

const TokenDetails: React.FC = () => {
  const { id } = useParams<{ id: string }>()

  const { data: tokenData, isLoading } = useQuery<TokenData>(['token', id], async () => {
    const { data } = await axios.get(`/api/market-data/token/${id}`)
    return data as TokenData
  })

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  if (!tokenData) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-gray-800">Token not found</h2>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">{tokenData.token_id}</h1>
      <div className="bg-white rounded-lg shadow-md p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-600">Price (USD)</h3>
            <p className="text-2xl font-bold">${tokenData.price_usd.toLocaleString()}</p>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-600">Market Cap</h3>
            <p className="text-2xl font-bold">${tokenData.market_cap.toLocaleString()}</p>
          </div>
          <div className="p-4 bg-gray-50 rounded-lg">
            <h3 className="text-lg font-semibold text-gray-600">24h Volume</h3>
            <p className="text-2xl font-bold">${tokenData.volume_24h.toLocaleString()}</p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default TokenDetails 