import * as React from 'react'
import { useMutation } from '@tanstack/react-query'
import { SimulationForm } from '../components/SimulationForm'
import { PlotlyChart } from '../components/PlotlyChart'
import { styles } from '../utils/styles'
import { simulationApi, SimulationRequest, SimulationResponse } from '../services/api'

export const SimulationPage: React.FC = () => {
  const [simulationResult, setSimulationResult] = React.useState<SimulationResponse | null>(null)
  const [timeStep, setTimeStep] = React.useState<'monthly' | 'yearly'>('monthly')

  const simulationMutation = useMutation({
    mutationFn: (data: SimulationRequest) => simulationApi.runScenario(data),
    onSuccess: (data) => {
      setSimulationResult(data)
      setTimeStep(data.evolution[0]?.time % 12 === 0 ? 'yearly' : 'monthly')
    },
  })

  const handleSimulation = (formData: SimulationRequest) => {
    simulationMutation.mutate(formData)
  }

  return (
    <div className={styles.container}>
      <div className="py-8">
        <h1 className={styles.heading.h1}>Tokenomics Simulation</h1>
        <p className="mt-2 text-gray-600">
          Configure your token parameters and run simulations to analyze supply evolution.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-8">
        <SimulationForm
          onSubmit={handleSimulation}
          isLoading={simulationMutation.isLoading}
        />

        {simulationMutation.isError && (
          <div className="rounded-md bg-red-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">
                  Error running simulation
                </h3>
                <div className="mt-2 text-sm text-red-700">
                  {simulationMutation.error instanceof Error
                    ? simulationMutation.error.message
                    : 'An unexpected error occurred'}
                </div>
              </div>
            </div>
          </div>
        )}

        {simulationResult && (
          <div className="space-y-8">
            <PlotlyChart
              data={simulationResult.evolution}
              timeStep={timeStep}
            />

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <div className="bg-white rounded-lg shadow-sm p-6">
                <dt className="text-sm font-medium text-gray-500">Final Supply</dt>
                <dd className="mt-1 text-3xl font-semibold text-gray-900">
                  {simulationResult.metrics.final_supply.toLocaleString()}
                </dd>
              </div>
              <div className="bg-white rounded-lg shadow-sm p-6">
                <dt className="text-sm font-medium text-gray-500">Total Burned</dt>
                <dd className="mt-1 text-3xl font-semibold text-red-600">
                  {simulationResult.metrics.total_burned.toLocaleString()}
                </dd>
              </div>
              <div className="bg-white rounded-lg shadow-sm p-6">
                <dt className="text-sm font-medium text-gray-500">Total Staked</dt>
                <dd className="mt-1 text-3xl font-semibold text-yellow-600">
                  {simulationResult.metrics.total_staked.toLocaleString()}
                </dd>
              </div>
              <div className="bg-white rounded-lg shadow-sm p-6">
                <dt className="text-sm font-medium text-gray-500">Total Vested</dt>
                <dd className="mt-1 text-3xl font-semibold text-indigo-600">
                  {simulationResult.metrics.total_vested.toLocaleString()}
                </dd>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
} 