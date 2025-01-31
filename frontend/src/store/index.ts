import { configureStore } from '@reduxjs/toolkit';
import simulationReducer from './simulationSlice';

export const store = configureStore({
  reducer: {
    simulation: simulationReducer,
  },
  middleware: (getDefaultMiddleware) =>
    getDefaultMiddleware({
      serializableCheck: {
        // Ignore les actions non-sérialisables des WebSockets
        ignoredActions: ['socket/connect', 'socket/disconnect'],
      },
    }),
});

export type RootState = ReturnType<typeof store.getState>;
export type AppDispatch = typeof store.dispatch;
