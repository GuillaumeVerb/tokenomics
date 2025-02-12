import { describe, it, expect, beforeEach } from 'vitest';
import { render, screen } from '../../test-utils';
import userEvent from '@testing-library/user-event';
import App from '../../App';
import { RootState } from '../../test-utils';
import { SimulationState } from '../../store/simulationSlice';

describe('App Component', () => {
  const mockSimulationState: SimulationState = {
    isSimulating: false,
    currentStep: 0,
    error: null,
  };

  const initialState: Partial<RootState> = {
    simulation: mockSimulationState,
  };

  it('should render without crashing', () => {
    const { store } = render(<App />, { preloadedState: initialState });
    expect(document.body).toBeDefined();
    expect(store.getState().simulation).toEqual(mockSimulationState);
  });

  it('should render main navigation elements', () => {
    render(<App />, { preloadedState: initialState });

    // Assuming your App has these navigation elements
    expect(screen.getByRole('navigation')).toBeInTheDocument();
    expect(screen.getByText(/simulation/i)).toBeInTheDocument();
  });

  it('should handle simulation start', async () => {
    const { store } = render(<App />, { preloadedState: initialState });
    const user = userEvent.setup();

    const startButton = screen.getByRole('button', { name: /start simulation/i });
    await user.click(startButton);

    expect(store.getState().simulation.isSimulating).toBe(true);
    expect(store.getState().simulation.error).toBeNull();
  });

  it('should handle simulation error state', () => {
    const errorState: Partial<RootState> = {
      simulation: {
        ...mockSimulationState,
        error: 'Test error message',
      },
    };

    render(<App />, { preloadedState: errorState });

    expect(screen.getByText(/test error message/i)).toBeInTheDocument();
  });

  it('should handle simulation progress', async () => {
    const { store } = render(<App />, { preloadedState: initialState });
    const user = userEvent.setup();

    // Start simulation
    const startButton = screen.getByRole('button', { name: /start simulation/i });
    await user.click(startButton);

    // Check progress updates
    expect(store.getState().simulation.currentStep).toBe(0);

    // Simulate progress
    const nextButton = screen.getByRole('button', { name: /next step/i });
    await user.click(nextButton);

    expect(store.getState().simulation.currentStep).toBe(1);
  });

  it('should handle simulation reset', async () => {
    const runningState: Partial<RootState> = {
      simulation: {
        ...mockSimulationState,
        isSimulating: true,
        currentStep: 5,
      },
    };

    const { store } = render(<App />, { preloadedState: runningState });
    const user = userEvent.setup();

    const resetButton = screen.getByRole('button', { name: /reset/i });
    await user.click(resetButton);

    expect(store.getState().simulation.isSimulating).toBe(false);
    expect(store.getState().simulation.currentStep).toBe(0);
  });
});
