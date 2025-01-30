import React, { useState } from 'react';
import Plot from 'react-plotly.js';
import { Button, Card, Select, Space, Upload, message, Spin } from 'antd';
import type { UploadProps } from 'antd';
import { UploadOutlined, DownloadOutlined } from '@ant-design/icons';
import axios from 'axios';
import html2canvas from 'html2canvas';
import jsPDF from 'jspdf';
import type { RcFile } from 'antd/es/upload/interface';

interface TimeSeriesPoint {
  date: string;
  value: number;
}

interface PredictionRequest {
  historical_data: TimeSeriesPoint[];
  forecast_years: number;
  model_type: string;
  confidence_interval: number;
}

interface PredictionResponse {
  forecast: Array<{
    date: string;
    value: number;
    lower_bound: number;
    upper_bound: number;
  }>;
  model_type: string;
  model_params: Record<string, any>;
  metrics: Record<string, number>;
}

interface Scenario {
  name: string;
  historical_data: TimeSeriesPoint[];
  prediction?: PredictionResponse;
}

const PredictionsCompare: React.FC = () => {
  const [scenarios, setScenarios] = useState<Scenario[]>([]);
  const [loading, setLoading] = useState(false);
  const [modelType, setModelType] = useState<string>('prophet');
  const [forecastYears, setForecastYears] = useState<number>(5);

  const handleFileUpload = async (file: File, index: number): Promise<boolean> => {
    try {
      const text = await file.text();
      const data = JSON.parse(text) as TimeSeriesPoint[];

      setScenarios(prev => {
        const newScenarios = [...prev];
        newScenarios[index] = {
          name: `Scenario ${index + 1}`,
          historical_data: data
        };
        return newScenarios;
      });

      return false; // Prevent default upload behavior
    } catch (error) {
      message.error('Invalid JSON file format');
      return false;
    }
  };

  const uploadProps: UploadProps = {
    accept: '.json',
    showUploadList: false,
    beforeUpload: (file: File, fileList: File[]) => false,
  };

  const generatePredictions = async (): Promise<void> => {
    setLoading(true);
    try {
      const predictions = await Promise.all(
        scenarios.map(async (scenario) => {
          const request: PredictionRequest = {
            historical_data: scenario.historical_data,
            forecast_years: forecastYears,
            model_type: modelType,
            confidence_interval: 0.95
          };

          const response = await axios.post<PredictionResponse>(
            '/api/predict',
            request
          );

          return {
            ...scenario,
            prediction: response.data
          };
        })
      );

      setScenarios(predictions);
    } catch (error) {
      if (error instanceof Error) {
        message.error(`Failed to generate predictions: ${error.message}`);
      } else {
        message.error('Failed to generate predictions');
      }
    } finally {
      setLoading(false);
    }
  };

  const exportPDF = async () => {
    const element = document.getElementById('comparison-plot');
    if (!element) return;

    try {
      const canvas = await html2canvas(element);
      const imgData = canvas.toDataURL('image/png');

      const pdf = new jsPDF('l', 'mm', 'a4');
      const pdfWidth = pdf.internal.pageSize.getWidth();
      const pdfHeight = pdf.internal.pageSize.getHeight();

      // Add title
      pdf.setFontSize(16);
      pdf.text('Supply Predictions Comparison', pdfWidth/2, 20, { align: 'center' });

      // Add plot
      pdf.addImage(imgData, 'PNG', 10, 30, pdfWidth - 20, pdfHeight/2);

      // Add metrics table
      if (scenarios.length === 2 && scenarios[0].prediction && scenarios[1].prediction) {
        pdf.setFontSize(12);
        pdf.text('Comparison Metrics', 10, pdfHeight/2 + 40);

        const metrics1 = scenarios[0].prediction.metrics;
        const metrics2 = scenarios[1].prediction.metrics;

        pdf.setFontSize(10);
        pdf.text([
          `Scenario 1 RMSE: ${metrics1.rmse.toFixed(2)}`,
          `Scenario 2 RMSE: ${metrics2.rmse.toFixed(2)}`,
          `Model Type: ${modelType}`,
          `Forecast Years: ${forecastYears}`,
          `Confidence Interval: 95%`
        ], 10, pdfHeight/2 + 50);
      }

      pdf.save('predictions-comparison.pdf');
    } catch (error) {
      message.error('Failed to export PDF');
    }
  };

  return (
    <Card title="Compare Predictions" style={{ margin: 20 }}>
      <Space direction="vertical" style={{ width: '100%' }}>
        <Space>
          <Upload
            {...uploadProps}
            beforeUpload={(file) => handleFileUpload(file, 0)}
          >
            <Button icon={<UploadOutlined />}>Upload Scenario 1</Button>
          </Upload>

          <Upload
            {...uploadProps}
            beforeUpload={(file) => handleFileUpload(file, 1)}
          >
            <Button icon={<UploadOutlined />}>Upload Scenario 2</Button>
          </Upload>
        </Space>

        <Space>
          <Select
            value={modelType}
            onChange={setModelType}
            style={{ width: 120 }}
            options={[
              { value: 'prophet', label: 'Prophet' },
              { value: 'arima', label: 'ARIMA' },
              { value: 'lstm', label: 'LSTM' }
            ]}
          />

          <Select
            value={forecastYears}
            onChange={setForecastYears}
            style={{ width: 120 }}
            options={Array.from({ length: 10 }, (_, i) => ({
              value: i + 1,
              label: `${i + 1} Years`
            }))}
          />

          <Button
            type="primary"
            onClick={generatePredictions}
            disabled={scenarios.length !== 2}
            loading={loading}
          >
            Generate Predictions
          </Button>

          <Button
            icon={<DownloadOutlined />}
            onClick={exportPDF}
            disabled={!scenarios.some(s => s.prediction)}
          >
            Export PDF
          </Button>
        </Space>

        {loading && <Spin size="large" />}

        {scenarios.some(s => s.prediction) && (
          <div id="comparison-plot" style={{ marginTop: 20 }}>
            <Plot
              data={scenarios.flatMap((scenario, i) => {
                if (!scenario.prediction) return [];

                const color = i === 0 ? '#3498db' : '#e74c3c';

                return [
                  // Historical data
                  {
                    x: scenario.historical_data.map(d => d.date),
                    y: scenario.historical_data.map(d => d.value),
                    type: 'scatter',
                    mode: 'lines',
                    name: `${scenario.name} (Historical)`,
                    line: { color, width: 2 }
                  },
                  // Prediction
                  {
                    x: scenario.prediction.forecast.map(d => d.date),
                    y: scenario.prediction.forecast.map(d => d.value),
                    type: 'scatter',
                    mode: 'lines',
                    name: `${scenario.name} (Predicted)`,
                    line: { color, width: 2, dash: 'dash' }
                  },
                  // Confidence interval
                  {
                    x: [
                      ...scenario.prediction.forecast.map(d => d.date),
                      ...scenario.prediction.forecast.map(d => d.date).reverse()
                    ],
                    y: [
                      ...scenario.prediction.forecast.map(d => d.upper_bound),
                      ...scenario.prediction.forecast.map(d => d.lower_bound).reverse()
                    ],
                    fill: 'toself',
                    fillcolor: `${color}20`,
                    type: 'scatter',
                    mode: 'none',
                    showlegend: false,
                    hoverinfo: 'skip'
                  }
                ];
              })}
              layout={{
                title: 'Supply Predictions Comparison',
                xaxis: { title: 'Date' },
                yaxis: { title: 'Supply' },
                hovermode: 'x unified',
                height: 600,
                showlegend: true,
                legend: {
                  x: 0.01,
                  y: 0.99,
                  bgcolor: 'rgba(255,255,255,0.8)'
                }
              }}
              config={{
                responsive: true,
                displayModeBar: true,
                displaylogo: false
              }}
              style={{ width: '100%' }}
            />
          </div>
        )}

        {scenarios.every(s => s.prediction) && (
          <Card size="small" title="Comparison Metrics">
            <Space direction="vertical">
              {scenarios.map((scenario, i) => (
                <div key={i}>
                  <h4>{scenario.name}</h4>
                  <p>RMSE: {scenario.prediction?.metrics.rmse.toFixed(2)}</p>
                  <p>MAE: {scenario.prediction?.metrics.mae.toFixed(2)}</p>
                </div>
              ))}
            </Space>
          </Card>
        )}
      </Space>
    </Card>
  );
};

export default PredictionsCompare;
