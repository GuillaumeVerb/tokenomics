import axios from 'axios'

const API_URL = process.env.VITE_API_URL || 'http://localhost:8000/api'

export interface TokenPoint {
  time: number
  total_supply: number
  circulating_supply: number
  burned_supply: number
  staked_supply: number
  vested_supply: number
}

export interface SimulationResponse {
  evolution: TokenPoint[]
  metrics: {
    total_burned: number
    total_staked: number
    total_vested: number
    final_supply: number
  }
}

export interface SimulationRequest {
  initial_supply: number
  time_step: 'monthly' | 'yearly'
  duration: number
  inflation_config: {
    type: 'constant' | 'dynamic'
    initial_rate: number
    min_rate?: number
    decay_rate?: number
  }
  burn_config: {
    type: 'continuous' | 'event-based'
    rate?: number
    events?: Array<{
      time: number
      amount: number
    }>
  }
  staking_config: {
    enabled: boolean
    target_rate?: number
    reward_rate?: number
    lock_duration?: number
  }
}

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export const simulationApi = {
  runScenario: async (data: SimulationRequest): Promise<SimulationResponse> => {
    const response = await api.post<SimulationResponse>('/simulate/scenario', data)
    return response.data
  },
  compareScenarios: async (scenarios: SimulationRequest[]): Promise<SimulationResponse[]> => {
    const response = await api.post<SimulationResponse[]>('/simulate/compare', { scenarios })
    return response.data
  },
} 