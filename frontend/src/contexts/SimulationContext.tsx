import * as React from 'react'
import { SimulationRequest, SimulationResponse } from '../services/api'

interface SimulationScenario {
  id: string
  name: string
  params: SimulationRequest
  results: SimulationResponse | null
}

interface SimulationContextState {
  scenarios: SimulationScenario[]
  activeScenarios: string[]
  comparisonResults: SimulationResponse[] | null
}

type SimulationAction =
  | { type: 'ADD_SCENARIO'; payload: SimulationScenario }
  | { type: 'UPDATE_SCENARIO'; payload: { id: string; params: SimulationRequest } }
  | { type: 'REMOVE_SCENARIO'; payload: string }
  | { type: 'SET_ACTIVE_SCENARIOS'; payload: string[] }
  | { type: 'SET_COMPARISON_RESULTS'; payload: SimulationResponse[] }
  | { type: 'RESET_COMPARISON' }

interface SimulationContextValue {
  state: SimulationContextState
  dispatch: React.Dispatch<SimulationAction>
}

const initialState: SimulationContextState = {
  scenarios: [
    {
      id: 'scenario-a',
      name: 'Scenario A',
      params: {
        initial_supply: 1000000,
        time_step: 'monthly',
        duration: 12,
        inflation_config: {
          type: 'constant',
          initial_rate: 5,
        },
        burn_config: {
          type: 'continuous',
          rate: 1,
        },
        staking_config: {
          enabled: false,
        },
      },
      results: null,
    },
    {
      id: 'scenario-b',
      name: 'Scenario B',
      params: {
        initial_supply: 1000000,
        time_step: 'monthly',
        duration: 12,
        inflation_config: {
          type: 'constant',
          initial_rate: 7,
        },
        burn_config: {
          type: 'continuous',
          rate: 2,
        },
        staking_config: {
          enabled: false,
        },
      },
      results: null,
    },
  ],
  activeScenarios: ['scenario-a', 'scenario-b'],
  comparisonResults: null,
}

const simulationReducer = (
  state: SimulationContextState,
  action: SimulationAction
): SimulationContextState => {
  switch (action.type) {
    case 'ADD_SCENARIO':
      return {
        ...state,
        scenarios: [...state.scenarios, action.payload],
        activeScenarios: [...state.activeScenarios, action.payload.id],
      }
    case 'UPDATE_SCENARIO':
      return {
        ...state,
        scenarios: state.scenarios.map((scenario) =>
          scenario.id === action.payload.id
            ? { ...scenario, params: action.payload.params }
            : scenario
        ),
      }
    case 'REMOVE_SCENARIO':
      return {
        ...state,
        scenarios: state.scenarios.filter((scenario) => scenario.id !== action.payload),
        activeScenarios: state.activeScenarios.filter((id) => id !== action.payload),
      }
    case 'SET_ACTIVE_SCENARIOS':
      return {
        ...state,
        activeScenarios: action.payload,
      }
    case 'SET_COMPARISON_RESULTS':
      return {
        ...state,
        comparisonResults: action.payload,
      }
    case 'RESET_COMPARISON':
      return {
        ...state,
        comparisonResults: null,
      }
    default:
      return state
  }
}

export const SimulationContext = React.createContext<SimulationContextValue | undefined>(
  undefined
)

export const SimulationProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [state, dispatch] = React.useReducer(simulationReducer, initialState)

  return (
    <SimulationContext.Provider value={{ state, dispatch }}>
      {children}
    </SimulationContext.Provider>
  )
}

export const useSimulation = () => {
  const context = React.useContext(SimulationContext)
  if (context === undefined) {
    throw new Error('useSimulation must be used within a SimulationProvider')
  }
  return context
} 