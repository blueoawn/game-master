/**
 * Frontend Game Manager - Handles game lifecycle and rendering
 */
import { Socket } from 'socket.io-client';
import { GameRegistry } from './games/registry';
import type {
  GameComponent,
  GameState,
  GameLoadedData,
} from './types';

export class GameManager {
  private socket: Socket;
  private container: HTMLElement;
  private currentGame: GameComponent | null = null;

  /**
   * Accumulated game state for tracking/debugging purposes.
   * IMPORTANT: This is NOT passed to game components - we pass incremental
   * updates instead to prevent transient events from persisting.
   * See STATE_MANAGEMENT.md for details.
   */
  private gameState: GameState = {};
  private currentGameId: string | null = null;

  constructor(socket: Socket, container: HTMLElement) {
    this.socket = socket;
    this.container = container;
    this.setupSocketListeners();
  }

  private setupSocketListeners() {
    this.socket.on('game_loaded', (data: GameLoadedData) => {
      console.log('🎮 Loading game:', data.gameId);
      this.loadGame(data);
    });

    this.socket.on('game_state_update', (update: Partial<GameState>) => {
      console.log('📡 State update received:', Object.keys(update));
      this.updateState(update);
    });

    this.socket.on('error', (error: { message: string }) => {
      console.error('❌ Server error:', error.message);
      this.showError(error.message);
    });
  }

  async loadGame(data: GameLoadedData) {
    try {
      // Cleanup previous game
      if (this.currentGame) {
        console.log('🧹 Cleaning up previous game');
        this.currentGame.destroy();
      }

      // Clear container
      this.container.innerHTML = '';

      // Get game component class from registry
      const GameClass = GameRegistry.get(data.config.component);
      if (!GameClass) {
        throw new Error(`Game component not found: ${data.config.component}`);
      }

      // Update UI
      this.updateGameInfo(data.title);

      // Initialize game
      console.log('🚀 Initializing game:', data.config.component);
      this.gameState = data.initialState;
      this.currentGameId = data.gameId;
      this.currentGame = new GameClass(this.container, data.config);
      this.currentGame.init(this.gameState);

      console.log('✅ Game loaded successfully');
    } catch (error) {
      console.error('Failed to load game:', error);
      this.showError(`Failed to load game: ${error}`);
    }
  }

  updateState(update: Partial<GameState>) {
    if (!this.currentGame) {
      console.warn('⚠️ Received state update but no game is loaded');
      return;
    }

    // Merge update into current state for tracking/debugging
    this.gameState = { ...this.gameState, ...update };

    /**
     * CRITICAL: Pass the update as-is, NOT the merged state.
     *
     * Why? If backend sends:
     *   1. {event: 'boost'}
     *   2. {shape_added: {...}}
     *
     * Passing merged state would send {event: 'boost', shape_added: {...}}
     * on the second update, causing events to trigger multiple times.
     *
     * See STATE_MANAGEMENT.md § "Bug #1: Merging State Before Passing"
     */
    this.currentGame.update(update);

    // Log for debugging (uses currentGameId)
    if (Object.keys(update).length > 0) {
      console.debug(`State updated for ${this.currentGameId}:`, Object.keys(update));
    }
  }

  private updateGameInfo(title: string) {
    const gameTitleElement = document.getElementById('game-title');
    if (gameTitleElement) {
      gameTitleElement.textContent = title;
    }
  }

  private showError(message: string) {
    this.container.innerHTML = `
      <div style="text-align: center; color: #ff4444; padding: 2rem;">
        <h2>Error</h2>
        <p>${message}</p>
      </div>
    `;
  }

  // Public API for manual game switching (if needed)
  requestGameSwitch(gameId: string) {
    this.socket.emit('load_game', { gameId });
  }
}
