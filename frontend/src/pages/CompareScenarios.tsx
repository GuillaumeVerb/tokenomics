import * as React from 'react'
import { useMutation } from '@tanstack/react-query'
import { SimulationForm } from '../components/SimulationForm'
import { PlotlyChart } from '../components/PlotlyChart'
import { Button } from '../components/Button'
import { Card } from '../components/Card'
import { styles } from '../utils/styles'
import { useSimulation } from '../contexts/SimulationContext'
import { simulationApi } from '../services/api'
import { exportToPDF } from '../utils/export'

export const CompareScenarios: React.FC = () => {
  const { state, dispatch } = useSimulation()
  const chartRef = React.useRef<HTMLDivElement>(null)

  const compareMutation = useMutation({
    mutationFn: async () => {
      const activeScenarios = state.scenarios.filter((s) =>
        state.activeScenarios.includes(s.id)
      )
      const response = await simulationApi.compareScenarios(
        activeScenarios.map((s) => s.params)
      )
      return response
    },
    onSuccess: (data) => {
      dispatch({ type: 'SET_COMPARISON_RESULTS', payload: data })
    },
  })

  const handleScenarioUpdate = (id: string, params: any) => {
    dispatch({ type: 'UPDATE_SCENARIO', payload: { id, params } })
  }

  const handleCompare = () => {
    compareMutation.mutate()
  }

  const handleExport = async () => {
    if (chartRef.current && state.comparisonResults) {
      await exportToPDF(chartRef.current, {
        filename: `tokenomics-comparison-${new Date().toISOString()}.pdf`,
      })
    }
  }

  const activeScenarios = state.scenarios.filter((s) => state.activeScenarios.includes(s.id))

  return (
    <div className={styles.container}>
      <div className="py-8">
        <h1 className={styles.heading.h1}>Compare Scenarios</h1>
        <p className="mt-2 text-gray-600">
          Configure multiple scenarios and compare their outcomes side by side.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-8">
        {state.scenarios.map((scenario) => (
          <Card key={scenario.id} className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className={styles.heading.h2}>{scenario.name}</h2>
              <div className="flex items-center space-x-2">
                <input
                  type="checkbox"
                  checked={state.activeScenarios.includes(scenario.id)}
                  onChange={(e) => {
                    const newActive = e.target.checked
                      ? [...state.activeScenarios, scenario.id]
                      : state.activeScenarios.filter((id) => id !== scenario.id)
                    dispatch({ type: 'SET_ACTIVE_SCENARIOS', payload: newActive })
                  }}
                  className={styles.checkbox}
                />
                <span className="text-sm text-gray-500">Include in comparison</span>
              </div>
            </div>
            <SimulationForm
              initialValues={scenario.params}
              onSubmit={(params) => handleScenarioUpdate(scenario.id, params)}
              isLoading={false}
            />
          </Card>
        ))}

        <div className="flex justify-end space-x-4">
          <Button
            onClick={handleCompare}
            disabled={compareMutation.isLoading || state.activeScenarios.length < 2}
          >
            {compareMutation.isLoading ? 'Comparing...' : 'Compare Scenarios'}
          </Button>
        </div>

        {compareMutation.isError && (
          <div className="rounded-md bg-red-50 p-4">
            <div className="flex">
              <div className="ml-3">
                <h3 className="text-sm font-medium text-red-800">
                  Error comparing scenarios
                </h3>
                <div className="mt-2 text-sm text-red-700">
                  {compareMutation.error instanceof Error
                    ? compareMutation.error.message
                    : 'An unexpected error occurred'}
                </div>
              </div>
            </div>
          </div>
        )}

        {state.comparisonResults && (
          <div className="space-y-8" ref={chartRef}>
            <Card className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className={styles.heading.h2}>Comparison Results</h2>
                <Button onClick={handleExport}>Export Report</Button>
              </div>

              <PlotlyChart
                data={state.comparisonResults.flatMap((result, index) =>
                  result.evolution.map((point) => ({
                    ...point,
                    scenarioName: activeScenarios[index].name,
                  }))
                )}
                timeStep={state.scenarios[0].params.time_step}
                showScenarioNames
              />

              <div className="mt-8">
                <h3 className={styles.heading.h3}>Metrics Comparison</h3>
                <div className="mt-4 overflow-x-auto">
                  <table className="min-w-full divide-y divide-gray-200">
                    <thead>
                      <tr>
                        <th className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                          Metric
                        </th>
                        {activeScenarios.map((scenario) => (
                          <th
                            key={scenario.id}
                            className="px-6 py-3 bg-gray-50 text-left text-xs font-medium text-gray-500 uppercase tracking-wider"
                          >
                            {scenario.name}
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody className="bg-white divide-y divide-gray-200">
                      {[
                        { key: 'final_supply', label: 'Final Supply' },
                        { key: 'total_burned', label: 'Total Burned' },
                        { key: 'total_staked', label: 'Total Staked' },
                        { key: 'total_vested', label: 'Total Vested' },
                      ].map(({ key, label }) => (
                        <tr key={key}>
                          <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-gray-900">
                            {label}
                          </td>
                          {state.comparisonResults?.map((result, index) => (
                            <td
                              key={index}
                              className="px-6 py-4 whitespace-nowrap text-sm text-gray-500"
                            >
                              {result.metrics[key as keyof typeof result.metrics].toLocaleString()}
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </Card>
          </div>
        )}
      </div>
    </div>
  )
} 