import React, { ReactElement } from 'react';
import { render as rtlRender } from '@testing-library/react';
import { configureStore, combineReducers, Store } from '@reduxjs/toolkit';
import type { Store as ReduxStore } from 'redux';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import type { RenderOptions } from '@testing-library/react';
import simulationReducer from './store/simulationSlice';

// Import your reducers here
// import yourReducer from './store/yourSlice';

// Define root state type
const rootReducer = combineReducers({
  simulation: simulationReducer,
  // Add your reducers here
  // example: yourReducer,
});

export type RootState = ReturnType<typeof rootReducer>;
export type AppStore = Store;

// Create a store setup function
function setupStore(preloadedState?: Partial<RootState>) {
  return configureStore({
    reducer: rootReducer,
    preloadedState
  });
}

interface ExtendedRenderOptions extends Omit<RenderOptions, 'queries'> {
  preloadedState?: Partial<RootState>;
  store?: AppStore;
}

function render(
  ui: ReactElement,
  {
    preloadedState = {} as Partial<RootState>,
    store = setupStore(preloadedState),
    ...renderOptions
  }: ExtendedRenderOptions = {}
) {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <Provider store={store}>
        <BrowserRouter>
          {children}
        </BrowserRouter>
      </Provider>
    );
  }

  return {
    store,
    ...rtlRender(ui, { wrapper: Wrapper, ...renderOptions })
  };
}

// Re-export everything
export * from '@testing-library/react';

// Override render method
export { render, setupStore };
