import { io, Socket } from 'socket.io-client';
import { store } from '../store';
import {
  updateSimulationProgress,
  updateSimulationData,
  setSimulationError
} from '../store/simulationSlice';

const SOCKET_URL = process.env.VITE_WS_URL || 'ws://localhost:8000';

class WebSocketService {
  private socket: Socket | null = null;
  private token: string | null = null;

  constructor() {
    this.token = localStorage.getItem('jwt_token');
  }

  connect() {
    if (this.socket?.connected) return;

    this.socket = io(SOCKET_URL, {
      auth: {
        token: this.token
      },
      transports: ['websocket'],
      reconnection: true,
      reconnectionDelay: 1000,
      reconnectionDelayMax: 5000,
      reconnectionAttempts: 5
    });

    this.setupEventListeners();
  }

  private setupEventListeners() {
    if (!this.socket) return;

    // Gestion de la connexion
    this.socket.on('connect', () => {
      console.log('WebSocket connecté');
    });

    this.socket.on('disconnect', () => {
      console.log('WebSocket déconnecté');
    });

    // Gestion des erreurs
    this.socket.on('error', (error: string) => {
      console.error('Erreur WebSocket:', error);
      store.dispatch(setSimulationError(error));
    });

    // Mise à jour de la progression
    this.socket.on('simulation_progress', (data: { progress: number }) => {
      store.dispatch(updateSimulationProgress(data.progress));
    });

    // Mise à jour des données de simulation
    this.socket.on('simulation_update', (data: any) => {
      store.dispatch(updateSimulationData(data));
    });

    // Mise à jour des données CoinGecko
    this.socket.on('data_update', (_data: { timestamp: number; prices: Record<string, number> }) => {
      // Déclenche une nouvelle simulation avec les données mises à jour
      const simulationId = store.getState().simulation.currentSimulationId;
      if (simulationId) {
        this.socket?.emit('request_simulation_update', { simulationId });
      }
    });
  }

  // Méthode pour démarrer une nouvelle simulation
  startSimulation(params: any) {
    if (!this.socket?.connected) {
      throw new Error('WebSocket non connecté');
    }
    this.socket.emit('start_simulation', params);
  }

  // Méthode pour s'abonner à une simulation spécifique
  subscribeToSimulation(simulationId: string) {
    if (!this.socket?.connected) return;
    this.socket.emit('subscribe_simulation', { simulationId });
  }

  // Méthode pour se désabonner d'une simulation
  unsubscribeFromSimulation(simulationId: string) {
    if (!this.socket?.connected) return;
    this.socket.emit('unsubscribe_simulation', { simulationId });
  }

  // Mise à jour du token JWT
  updateToken(newToken: string) {
    this.token = newToken;
    localStorage.setItem('jwt_token', newToken);
    if (this.socket?.connected) {
      this.socket.disconnect();
      this.connect();
    }
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect();
      this.socket = null;
    }
  }
}

export const wsService = new WebSocketService();
