import { createSlice, PayloadAction } from '@reduxjs/toolkit';

export interface SimulationState {
  isSimulating: boolean;
  currentStep: number;
  error: string | null;
}

const initialState: SimulationState = {
  isSimulating: false,
  currentStep: 0,
  error: null,
};

export const simulationSlice = createSlice({
  name: 'simulation',
  initialState,
  reducers: {
    startSimulation: (state) => {
      state.isSimulating = true;
      state.error = null;
    },
    stopSimulation: (state) => {
      state.isSimulating = false;
    },
    setStep: (state, action: PayloadAction<number>) => {
      state.currentStep = action.payload;
    },
    setError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.isSimulating = false;
    },
    resetSimulation: (state) => {
      state.isSimulating = false;
      state.currentStep = 0;
      state.error = null;
    },
  },
});

export const {
  startSimulation,
  stopSimulation,
  setStep,
  setError,
  resetSimulation,
} = simulationSlice.actions;

export default simulationSlice.reducer;
