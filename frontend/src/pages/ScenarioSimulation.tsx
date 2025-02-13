import React, { useState, useEffect } from 'react';
import { useDispatch, useSelector } from 'react-redux';
import { Card, Button, message, Progress } from 'antd';
import Plot from 'react-plotly.js';
import { ShockEventsForm } from '../components/ShockEventsForm';
import { SimulationParams, ShockEvent, SimulationResults } from '../types/simulation';
import { wsService } from '../services/websocket';
import { RootState } from '../store';
import { resetSimulation } from '../store/simulationSlice';

export const ScenarioSimulation: React.FC = () => {
  const dispatch = useDispatch();
  const {
    progress,
    results,
    error,
    isLoading
  }: {
    progress: number;
    results: SimulationResults | null;
    error: string | null;
    isLoading: boolean;
  } = useSelector((state: RootState) => state.simulation);

  const [params] = useState<SimulationParams>({
    initial_supply: 1000000,
    initial_price: 1.0,
    initial_liquidity: 0.3,
    simulation_months: 60,
    monthly_inflation: 0.02,
    vesting_period: 12
  });

  const [shockEvents, setShockEvents] = useState<ShockEvent[]>([]);

  useEffect(() => {
    // Connexion au WebSocket lors du montage du composant
    wsService.connect();

    // Nettoyage lors du démontage
    return () => {
      wsService.disconnect();
      dispatch(resetSimulation());
    };
  }, [dispatch]);

  useEffect(() => {
    if (error) {
      message.error(error);
    }
  }, [error]);

  const handleSimulate = async () => {
    try {
      // Démarrage de la simulation via WebSocket
      wsService.startSimulation({
        params,
        shock_events: shockEvents
      });
    } catch (error) {
      if (error instanceof Error) {
        message.error(error.message);
      }
    }
  };

  const getEventMonth = (event: ShockEvent): number => {
    return event.time_unit === 'years' ? event.time_step * 12 : event.time_step;
  };

  return (
    <div className="p-4 space-y-4">
      <Card title="Simulation de scénario avec événements">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
          {/* Formulaire des paramètres de base */}
          <Card title="Paramètres de base" className="mb-4">
            {/* Ajoutez ici votre formulaire de paramètres */}
          </Card>

          {/* Formulaire des événements de shock */}
          <ShockEventsForm
            onChange={setShockEvents}
            maxTimeSteps={params.simulation_months}
          />
        </div>

        <Button
          type="primary"
          onClick={handleSimulate}
          loading={isLoading}
          className="mt-4"
        >
          Lancer la simulation
        </Button>

        {isLoading && (
          <div className="mt-4">
            <Progress percent={progress} status="active" />
          </div>
        )}
      </Card>

      {results && (
        <Card title="Résultats de la simulation">
          <div className="space-y-4">
            {/* Graphique de l'offre */}
            <Plot
              data={[
                {
                  x: Array.from({ length: results.supply.length }, (_, i) => i),
                  y: results.supply,
                  type: 'scatter',
                  mode: 'lines',
                  name: 'Offre circulante',
                },
              ]}
              layout={{
                title: 'Évolution de l\'offre circulante',
                xaxis: { title: 'Mois' },
                yaxis: { title: 'Tokens' },
                height: 400,
                annotations: shockEvents.map(event => ({
                  x: getEventMonth(event),
                  y: results.supply[getEventMonth(event)],
                  text: `${event.event_type}: ${(event.value * 100).toFixed(1)}%`,
                  showarrow: true,
                  arrowhead: 1,
                  arrowsize: 1,
                  arrowwidth: 2,
                  arrowcolor: '#666',
                  ax: 0,
                  ay: -40,
                  font: { size: 12 },
                  bgcolor: 'rgba(255, 255, 255, 0.8)',
                  bordercolor: '#666',
                  borderwidth: 1,
                  borderpad: 4
                })),
                showlegend: true,
                hovermode: 'closest'
              }}
              useResizeHandler
              className="w-full"
            />

            {/* Graphique du prix */}
            <Plot
              data={[
                {
                  x: Array.from({ length: results.price.length }, (_, i) => i),
                  y: results.price,
                  type: 'scatter',
                  mode: 'lines',
                  name: 'Prix',
                },
              ]}
              layout={{
                title: 'Évolution du prix',
                xaxis: { title: 'Mois' },
                yaxis: { title: 'Prix ($)' },
                height: 400,
                annotations: shockEvents.map(event => ({
                  x: getEventMonth(event),
                  y: results.price[getEventMonth(event)],
                  text: `${event.event_type}: ${(event.value * 100).toFixed(1)}%`,
                  showarrow: true,
                  arrowhead: 1,
                  arrowsize: 1,
                  arrowwidth: 2,
                  arrowcolor: '#666',
                  ax: 0,
                  ay: -40,
                  font: { size: 12 },
                  bgcolor: 'rgba(255, 255, 255, 0.8)',
                  bordercolor: '#666',
                  borderwidth: 1,
                  borderpad: 4
                })),
                showlegend: true,
                hovermode: 'closest'
              }}
              useResizeHandler
              className="w-full"
            />

            {/* Journal des événements */}
            <Card title="Journal des événements" size="small">
              <div className="space-y-2">
                {results.event_logs.map((log, index) => (
                  <div
                    key={index}
                    className={`p-2 rounded ${
                      log.event_type === 'mass_burn' ? 'bg-red-50' :
                      log.event_type === 'inflation_spike' ? 'bg-yellow-50' :
                      'bg-blue-50'
                    }`}
                  >
                    <p className="font-medium">
                      Mois {log.month}: {log.message}
                    </p>
                    <p className="text-sm text-gray-600">
                      Impact - Supply: {log.impact.supply.toLocaleString()} |
                      Prix: ${log.impact.price.toFixed(4)} |
                      Liquidité: {(log.impact.liquidity * 100).toFixed(2)}%
                    </p>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </Card>
      )}
    </div>
  );
};
