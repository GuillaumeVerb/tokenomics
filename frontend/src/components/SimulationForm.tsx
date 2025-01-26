import * as React from 'react'
import { useForm, Controller, FieldValues } from 'react-hook-form'
import { Button } from './Button'
import { styles } from '../utils/styles'

interface SimulationFormData {
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

interface SimulationFormProps {
  onSubmit: (data: SimulationFormData) => void
  isLoading?: boolean
}

export const SimulationForm: React.FC<SimulationFormProps> = ({
  onSubmit,
  isLoading = false,
}) => {
  const { control, handleSubmit, watch } = useForm<SimulationFormData>({
    defaultValues: {
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
  })

  const inflationType = watch('inflation_config.type')
  const burnType = watch('burn_config.type')
  const stakingEnabled = watch('staking_config.enabled')

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Initial Supply */}
        <div className="space-y-2">
          <label htmlFor="initial_supply" className="block text-sm font-medium text-gray-700">
            Initial Supply
          </label>
          <Controller
            name="initial_supply"
            control={control}
            rules={{ required: true, min: 1 }}
            render={({ field: { value, onChange, ...field } }) => (
              <input
                type="number"
                value={value}
                onChange={(e) => onChange(Number(e.target.value))}
                {...field}
                className={styles.input}
                min={1}
              />
            )}
          />
        </div>

        {/* Time Configuration */}
        <div className="grid grid-cols-2 gap-4">
          <div className="space-y-2">
            <label htmlFor="time_step" className="block text-sm font-medium text-gray-700">
              Time Step
            </label>
            <Controller
              name="time_step"
              control={control}
              render={({ field: { value, onChange, ...field } }) => (
                <select value={value} onChange={onChange} {...field} className={styles.select}>
                  <option value="monthly">Monthly</option>
                  <option value="yearly">Yearly</option>
                </select>
              )}
            />
          </div>
          <div className="space-y-2">
            <label htmlFor="duration" className="block text-sm font-medium text-gray-700">
              Duration
            </label>
            <Controller
              name="duration"
              control={control}
              rules={{ required: true, min: 1 }}
              render={({ field: { value, onChange, ...field } }) => (
                <input
                  type="number"
                  value={value}
                  onChange={(e) => onChange(Number(e.target.value))}
                  {...field}
                  className={styles.input}
                  min={1}
                />
              )}
            />
          </div>
        </div>

        {/* Inflation Configuration */}
        <div className="space-y-4 col-span-full">
          <h3 className={styles.heading.h3}>Inflation Configuration</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label htmlFor="inflation_type" className="block text-sm font-medium text-gray-700">
                Type
              </label>
              <Controller
                name="inflation_config.type"
                control={control}
                render={({ field: { value, onChange, ...field } }) => (
                  <select value={value} onChange={onChange} {...field} className={styles.select}>
                    <option value="constant">Constant</option>
                    <option value="dynamic">Dynamic</option>
                  </select>
                )}
              />
            </div>
            <div className="space-y-2">
              <label htmlFor="initial_rate" className="block text-sm font-medium text-gray-700">
                Initial Rate (%)
              </label>
              <Controller
                name="inflation_config.initial_rate"
                control={control}
                rules={{ required: true, min: 0, max: 100 }}
                render={({ field: { value, onChange, ...field } }) => (
                  <input
                    type="number"
                    value={value}
                    onChange={(e) => onChange(Number(e.target.value))}
                    {...field}
                    className={styles.input}
                    min={0}
                    max={100}
                    step={0.1}
                  />
                )}
              />
            </div>
            {inflationType === 'dynamic' && (
              <>
                <div className="space-y-2">
                  <label htmlFor="min_rate" className="block text-sm font-medium text-gray-700">
                    Minimum Rate (%)
                  </label>
                  <Controller
                    name="inflation_config.min_rate"
                    control={control}
                    rules={{ required: true, min: 0, max: 100 }}
                    render={({ field: { value, onChange, ...field } }) => (
                      <input
                        type="number"
                        value={value}
                        onChange={(e) => onChange(Number(e.target.value))}
                        {...field}
                        className={styles.input}
                        min={0}
                        max={100}
                        step={0.1}
                      />
                    )}
                  />
                </div>
                <div className="space-y-2">
                  <label htmlFor="decay_rate" className="block text-sm font-medium text-gray-700">
                    Decay Rate (%)
                  </label>
                  <Controller
                    name="inflation_config.decay_rate"
                    control={control}
                    rules={{ required: true, min: 0, max: 100 }}
                    render={({ field: { value, onChange, ...field } }) => (
                      <input
                        type="number"
                        value={value}
                        onChange={(e) => onChange(Number(e.target.value))}
                        {...field}
                        className={styles.input}
                        min={0}
                        max={100}
                        step={0.1}
                      />
                    )}
                  />
                </div>
              </>
            )}
          </div>
        </div>

        {/* Burn Configuration */}
        <div className="space-y-4 col-span-full">
          <h3 className={styles.heading.h3}>Burn Configuration</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <label htmlFor="burn_type" className="block text-sm font-medium text-gray-700">
                Type
              </label>
              <Controller
                name="burn_config.type"
                control={control}
                render={({ field: { value, onChange, ...field } }) => (
                  <select value={value} onChange={onChange} {...field} className={styles.select}>
                    <option value="continuous">Continuous</option>
                    <option value="event-based">Event Based</option>
                  </select>
                )}
              />
            </div>
            {burnType === 'continuous' && (
              <div className="space-y-2">
                <label htmlFor="burn_rate" className="block text-sm font-medium text-gray-700">
                  Burn Rate (%)
                </label>
                <Controller
                  name="burn_config.rate"
                  control={control}
                  rules={{ required: true, min: 0, max: 100 }}
                  render={({ field: { value, onChange, ...field } }) => (
                    <input
                      type="number"
                      value={value}
                      onChange={(e) => onChange(Number(e.target.value))}
                      {...field}
                      className={styles.input}
                      min={0}
                      max={100}
                      step={0.1}
                    />
                  )}
                />
              </div>
            )}
          </div>
        </div>

        {/* Staking Configuration */}
        <div className="space-y-4 col-span-full">
          <div className="flex items-center space-x-2">
            <Controller
              name="staking_config.enabled"
              control={control}
              render={({ field: { value, onChange, ...field } }) => (
                <input
                  type="checkbox"
                  checked={value}
                  onChange={onChange}
                  {...field}
                  className={styles.checkbox}
                />
              )}
            />
            <h3 className={styles.heading.h3}>Enable Staking</h3>
          </div>
          {stakingEnabled && (
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <div className="space-y-2">
                <label htmlFor="target_rate" className="block text-sm font-medium text-gray-700">
                  Target Rate (%)
                </label>
                <Controller
                  name="staking_config.target_rate"
                  control={control}
                  rules={{ required: true, min: 0, max: 100 }}
                  render={({ field: { value, onChange, ...field } }) => (
                    <input
                      type="number"
                      value={value}
                      onChange={(e) => onChange(Number(e.target.value))}
                      {...field}
                      className={styles.input}
                      min={0}
                      max={100}
                      step={0.1}
                    />
                  )}
                />
              </div>
              <div className="space-y-2">
                <label htmlFor="reward_rate" className="block text-sm font-medium text-gray-700">
                  Reward Rate (%)
                </label>
                <Controller
                  name="staking_config.reward_rate"
                  control={control}
                  rules={{ required: true, min: 0, max: 100 }}
                  render={({ field: { value, onChange, ...field } }) => (
                    <input
                      type="number"
                      value={value}
                      onChange={(e) => onChange(Number(e.target.value))}
                      {...field}
                      className={styles.input}
                      min={0}
                      max={100}
                      step={0.1}
                    />
                  )}
                />
              </div>
              <div className="space-y-2">
                <label htmlFor="lock_duration" className="block text-sm font-medium text-gray-700">
                  Lock Duration
                </label>
                <Controller
                  name="staking_config.lock_duration"
                  control={control}
                  rules={{ required: true, min: 1 }}
                  render={({ field: { value, onChange, ...field } }) => (
                    <input
                      type="number"
                      value={value}
                      onChange={(e) => onChange(Number(e.target.value))}
                      {...field}
                      className={styles.input}
                      min={1}
                    />
                  )}
                />
              </div>
            </div>
          )}
        </div>
      </div>

      <div className="flex justify-end space-x-4">
        <Button
          type="submit"
          disabled={isLoading}
          className="w-full md:w-auto"
        >
          {isLoading ? 'Simulating...' : 'Run Simulation'}
        </Button>
      </div>
    </form>
  )
} 