import { createSlice, PayloadAction } from '@reduxjs/toolkit';
import { SimulationResults } from '../types/simulation';

interface SimulationState {
  currentSimulationId: string | null;
  progress: number;
  results: SimulationResults | null;
  error: string | null;
  isLoading: boolean;
}

const initialState: SimulationState = {
  currentSimulationId: null,
  progress: 0,
  results: null,
  error: null,
  isLoading: false
};

const simulationSlice = createSlice({
  name: 'simulation',
  initialState,
  reducers: {
    startSimulation: (state, action: PayloadAction<string>) => {
      state.currentSimulationId = action.payload;
      state.isLoading = true;
      state.progress = 0;
      state.error = null;
    },
    updateSimulationProgress: (state, action: PayloadAction<number>) => {
      state.progress = action.payload;
    },
    updateSimulationData: (state, action: PayloadAction<SimulationResults>) => {
      state.results = action.payload;
      if (state.progress === 100) {
        state.isLoading = false;
      }
    },
    setSimulationError: (state, action: PayloadAction<string>) => {
      state.error = action.payload;
      state.isLoading = false;
    },
    resetSimulation: (state) => {
      state.currentSimulationId = null;
      state.progress = 0;
      state.results = null;
      state.error = null;
      state.isLoading = false;
    }
  }
});

export const {
  startSimulation,
  updateSimulationProgress,
  updateSimulationData,
  setSimulationError,
  resetSimulation
} = simulationSlice.actions;

export default simulationSlice.reducer;
