import * as React from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import TokenDetails from './pages/TokenDetails'
import { SimulationPage } from './pages/SimulationPage'
import { CompareScenarios } from './pages/CompareScenarios'
import { SimulationProvider } from './contexts/SimulationContext'

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
    },
  },
})

const App: React.FC = () => {
  return (
    <QueryClientProvider client={queryClient}>
      <SimulationProvider>
        <Router>
          <div className="min-h-screen bg-gray-100">
            <Navbar />
            <main className="container mx-auto px-4 py-8">
              <Routes>
                <Route path="/" element={<SimulationPage />} />
                <Route path="/compare" element={<CompareScenarios />} />
                <Route path="/token/:id" element={<TokenDetails />} />
              </Routes>
            </main>
          </div>
        </Router>
      </SimulationProvider>
    </QueryClientProvider>
  )
}

export default App 