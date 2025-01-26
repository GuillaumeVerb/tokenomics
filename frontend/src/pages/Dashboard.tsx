import * as React from 'react'
import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import axios from 'axios'
import { styles } from '../utils/styles'
import { Card } from '../components/Card'

interface TrendingToken {
  item: {
    id: string
    name: string
    symbol: string
    thumb: string
  }
}

interface TrendingResponse {
  coins: TrendingToken[]
}

const Dashboard: React.FC = () => {
  const { data: trendingTokens, isLoading } = useQuery<TrendingToken[]>(['trending'], async () => {
    const { data } = await axios.get<TrendingResponse>('/api/market-data/trending')
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
      <h1 className={styles.heading.h1}>Trending Tokens</h1>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {trendingTokens?.map((token: TrendingToken) => (
          <Link
            key={token.item.id}
            to={`/token/${token.item.id}`}
          >
            <Card className="hover:shadow-lg transition-shadow">
              <div className="flex items-center space-x-4">
                <img
                  src={token.item.thumb}
                  alt={token.item.name}
                  className="w-12 h-12 rounded-full"
                />
                <div>
                  <h2 className={styles.heading.h2}>{token.item.name}</h2>
                  <p className="text-gray-500">{token.item.symbol.toUpperCase()}</p>
                </div>
              </div>
            </Card>
          </Link>
        ))}
      </div>
    </div>
  )
}

export default Dashboard 