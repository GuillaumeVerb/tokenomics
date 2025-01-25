import React from 'react'
import { useQuery } from 'react-query'
import { Link } from 'react-router-dom'
import axios from 'axios'

interface TokenData {
  token_id: string
  price_usd: number
  market_cap: number
  volume_24h: number
  timestamp: string
}

interface TrendingToken {
  item: {
    id: string
    name: string
    symbol: string
    thumb: string
  }
}

const Dashboard: React.FC = () => {
  const { data: trendingTokens, isLoading } = useQuery<TrendingToken[]>('trending', async () => {
    const { data } = await axios.get('/api/market-data/trending')
    return data.coins
  })

  if (isLoading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-gray-900"></div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Trending Tokens</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {trendingTokens?.map((token) => (
          <Link
            key={token.item.id}
            to={`/token/${token.item.id}`}
            className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition-shadow"
          >
            <div className="flex items-center space-x-4">
              <img
                src={token.item.thumb}
                alt={token.item.name}
                className="w-12 h-12 rounded-full"
              />
              <div>
                <h2 className="text-xl font-semibold">{token.item.name}</h2>
                <p className="text-gray-500">{token.item.symbol.toUpperCase()}</p>
              </div>
            </div>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default Dashboard 