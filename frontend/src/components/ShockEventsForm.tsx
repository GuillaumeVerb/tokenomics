import React, { useState } from 'react';
import { Form, Input, Select, Button, List, Tooltip } from 'antd';
import { DeleteOutlined } from '@ant-design/icons';
import { ShockEvent, EventType, TimeUnit, FormValues } from '../types/simulation';

interface ShockEventsFormProps {
  onChange: (events: ShockEvent[]) => void;
  maxTimeSteps: number;
}

const eventTypeDescriptions: Record<EventType, string> = {
  [EventType.MASS_BURN]: 'Destruction massive de tokens',
  [EventType.INFLATION_SPIKE]: 'Pic d\'inflation',
  [EventType.LIQUIDITY_INJECTION]: 'Injection de liquidité',
  [EventType.LIQUIDITY_REMOVAL]: 'Retrait de liquidité',
  [EventType.MARKET_SHOCK]: 'Choc de marché'
};

export const ShockEventsForm: React.FC<ShockEventsFormProps> = ({ onChange, maxTimeSteps }) => {
  const [form] = Form.useForm<FormValues>();
  const [events, setEvents] = useState<ShockEvent[]>([]);

  const handleAddEvent = (values: FormValues) => {
    const newEvent: ShockEvent = {
      time_step: Number(values.time_step),
      time_unit: values.time_unit,
      event_type: values.event_type,
      value: Number(values.value) / 100, // Convert percentage to decimal
      description: values.description
    };

    const updatedEvents = [...events, newEvent].sort((a, b) => {
      const aMonths = a.time_unit === TimeUnit.YEARS ? a.time_step * 12 : a.time_step;
      const bMonths = b.time_unit === TimeUnit.YEARS ? b.time_step * 12 : b.time_step;
      return aMonths - bMonths;
    });

    setEvents(updatedEvents);
    onChange(updatedEvents);
    form.resetFields();
  };

  const handleRemoveEvent = (index: number) => {
    const updatedEvents = events.filter((_, i) => i !== index);
    setEvents(updatedEvents);
    onChange(updatedEvents);
  };

  return (
    <div className="space-y-4">
      <Form<FormValues>
        form={form}
        onFinish={handleAddEvent}
        layout="vertical"
      >
        <div className="grid grid-cols-2 gap-4">
          <Form.Item
            name="time_step"
            label="Moment"
            rules={[
              { required: true, message: 'Moment requis' },
              { type: 'number', min: 1, max: maxTimeSteps, message: `Doit être entre 1 et ${maxTimeSteps}` }
            ]}
          >
            <Input type="number" min={1} max={maxTimeSteps} />
          </Form.Item>

          <Form.Item
            name="time_unit"
            label="Unité"
            rules={[{ required: true, message: 'Unité requise' }]}
          >
            <Select>
              <Select.Option value={TimeUnit.MONTHS}>Mois</Select.Option>
              <Select.Option value={TimeUnit.YEARS}>Années</Select.Option>
            </Select>
          </Form.Item>
        </div>

        <Form.Item
          name="event_type"
          label="Type d'événement"
          rules={[{ required: true, message: 'Type d\'événement requis' }]}
        >
          <Select>
            {Object.entries(eventTypeDescriptions).map(([type, description]) => (
              <Select.Option key={type} value={type}>
                {description}
              </Select.Option>
            ))}
          </Select>
        </Form.Item>

        <Form.Item
          name="value"
          label="Valeur (%)"
          rules={[
            { required: true, message: 'Valeur requise' },
            { type: 'number', min: -100, max: 100, message: 'Doit être entre -100% et 100%' }
          ]}
        >
          <Input type="number" min={-100} max={100} suffix="%" />
        </Form.Item>

        <Form.Item
          name="description"
          label="Description (optionnelle)"
        >
          <Input.TextArea rows={2} maxLength={200} showCount />
        </Form.Item>

        <Button type="primary" htmlType="submit">
          Ajouter l'événement
        </Button>
      </Form>

      <List
        size="small"
        bordered
        dataSource={events}
        renderItem={(event: ShockEvent, index: number) => (
          <List.Item
            actions={[
              <Tooltip title="Supprimer" key="delete">
                <Button
                  type="text"
                  danger
                  icon={<DeleteOutlined />}
                  onClick={() => handleRemoveEvent(index)}
                />
              </Tooltip>
            ]}
          >
            <div>
              <div className="font-medium">
                {event.time_step} {event.time_unit === TimeUnit.YEARS ? 'ans' : 'mois'} - {eventTypeDescriptions[event.event_type]}
              </div>
              <div className="text-sm text-gray-500">
                Impact: {(event.value * 100).toFixed(1)}%
                {event.description && <div className="italic">{event.description}</div>}
              </div>
            </div>
          </List.Item>
        )}
      />
    </div>
  );
};
