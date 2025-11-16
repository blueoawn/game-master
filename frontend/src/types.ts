/**
 * TypeScript type definitions for the game system
 */

export interface GameState {
  [key: string]: any;
}

export interface GameConfig {
  id: string;
  name: string;
  component: string;
  entryPoint: string;
  assets: string[];
  config: {
    [key: string]: any;
  };
}

export interface GameLoadedData {
  gameId: string;
  title: string;
  initialState: GameState;
  config: GameConfig;
}

export interface GameComponent {
  /**
   * Initialize the game with initial state
   */
  init(initialState: GameState): void;

  /**
   * Update the game with new state
   */
  update(state: GameState): void;

  /**
   * Clean up and destroy the game
   */
  destroy(): void;
}

export interface GameComponentConstructor {
  new (container: HTMLElement, config: GameConfig): GameComponent;
}
