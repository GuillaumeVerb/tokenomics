import * as React from 'react'
import Plot from 'react-plotly.js'
import { Config } from 'plotly.js'
import { Card } from './Card'
import { Button } from './Button'
import { exportToPDF } from '../utils/export'

interface TokenPoint {
  time: number
  total_supply: number
  circulating_supply: number
  burned_supply: number
  staked_supply: number
  vested_supply: number
  scenarioName?: string
}

interface PlotlyChartProps {
  data: TokenPoint[]
  timeStep: 'monthly' | 'yearly'
  className?: string
  showScenarioNames?: boolean
}

export const PlotlyChart: React.FC<PlotlyChartProps> = ({
  data,
  timeStep,
  className = '',
  showScenarioNames = false,
}) => {
  const chartRef = React.useRef<HTMLDivElement>(null)
  const timeUnit = timeStep === 'monthly' ? 'Months' : 'Years'

  const groupedData = React.useMemo(() => {
    if (!showScenarioNames) {
      return {
        default: data,
      }
    }

    return data.reduce<Record<string, TokenPoint[]>>((acc, point) => {
      const name = point.scenarioName || 'default'
      if (!acc[name]) {
        acc[name] = []
      }
      acc[name].push(point)
      return acc
    }, {})
  }, [data, showScenarioNames])

  const traces = React.useMemo(() => {
    return Object.entries(groupedData).flatMap(([scenarioName, points]) => [
      {
        name: `${scenarioName} - Total Supply`,
        x: points.map((point) => point.time),
        y: points.map((point) => point.total_supply),
        type: 'scatter',
        mode: 'lines',
        line: { dash: 'solid' },
      },
      {
        name: `${scenarioName} - Circulating Supply`,
        x: points.map((point) => point.time),
        y: points.map((point) => point.circulating_supply),
        type: 'scatter',
        mode: 'lines',
        line: { dash: 'dot' },
      },
      {
        name: `${scenarioName} - Burned Supply`,
        x: points.map((point) => point.time),
        y: points.map((point) => point.burned_supply),
        type: 'scatter',
        mode: 'lines',
        line: { dash: 'dashdot' },
      },
      {
        name: `${scenarioName} - Staked Supply`,
        x: points.map((point) => point.time),
        y: points.map((point) => point.staked_supply),
        type: 'scatter',
        mode: 'lines',
        line: { dash: 'dash' },
      },
      {
        name: `${scenarioName} - Vested Supply`,
        x: points.map((point) => point.time),
        y: points.map((point) => point.vested_supply),
        type: 'scatter',
        mode: 'lines',
        line: { dash: 'longdash' },
      },
    ])
  }, [groupedData])

  const layout = {
    title: 'Token Supply Evolution',
    xaxis: {
      title: timeUnit,
      showgrid: true,
      zeroline: true,
    },
    yaxis: {
      title: 'Supply',
      showgrid: true,
      zeroline: true,
    },
    showlegend: true,
    legend: {
      x: 1,
      xanchor: 'right',
      y: 1,
    },
    hovermode: 'x unified',
    autosize: true,
  }

  const config: Partial<Config> = {
    responsive: true,
    displayModeBar: true,
    displaylogo: false,
    modeBarButtonsToRemove: ['lasso2d', 'select2d'] as any,
  }

  const handleExport = async () => {
    if (chartRef.current) {
      const success = await exportToPDF(chartRef.current, {
        filename: `tokenomics-simulation-${new Date().toISOString()}.pdf`,
      })

      if (success) {
        // You could add a toast notification here
        console.log('PDF exported successfully')
      } else {
        console.error('Failed to export PDF')
      }
    }
  }

  return (
    <Card className={className}>
      <div ref={chartRef}>
        <Plot
          data={traces as any}
          layout={layout as any}
          config={config}
          className="w-full h-[500px]"
          useResizeHandler
        />
      </div>
      <div className="mt-4 flex justify-end">
        <Button onClick={handleExport}>
          Export as PDF
        </Button>
      </div>
    </Card>
  )
} 