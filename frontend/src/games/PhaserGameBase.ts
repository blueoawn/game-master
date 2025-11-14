/**
 * Base class for Phaser-based games
 * Handles Phaser setup and integration with the game system
 */
import Phaser from 'phaser';
import type { GameComponent, GameState, GameConfig } from '../types';

export abstract class PhaserGameBase implements GameComponent {
  protected game: Phaser.Game | null = null;
  protected container: HTMLElement;
  protected config: GameConfig;
  protected currentState: GameState = {};

  constructor(container: HTMLElement, config: GameConfig) {
    this.container = container;
    this.config = config;
  }

  /**
   * Get the Phaser game configuration
   * Override this to customize Phaser settings
   */
  protected getPhaserConfig(): Phaser.Types.Core.GameConfig {
    return {
      type: Phaser.AUTO,
      parent: this.container,
      width: this.config.config.canvas_width || 1920,
      height: this.config.config.canvas_height || 1080,
      backgroundColor: '#1e1e1e',
      physics: {
        default: 'arcade',
        arcade: {
          gravity: { x: 0, y: 0 },
          debug: false,
        },
      },
      scene: this.getScenes(),
    };
  }

  /**
   * Get array of Phaser scenes for this game
   * Must be implemented by subclasses
   */
  protected abstract getScenes(): (typeof Phaser.Scene)[];

  /**
   * Get the main game scene
   * Must be implemented by subclasses
   */
  protected abstract getMainScene(): Phaser.Scene | null;

  /**
   * Initialize the Phaser game
   */
  init(initialState: GameState): void {
    this.currentState = initialState;
    const phaserConfig = this.getPhaserConfig();
    this.game = new Phaser.Game(phaserConfig);

    // Wait for game to be ready, then pass initial state to scene
    this.game.events.once('ready', () => {
      const scene = this.getMainScene();
      if (scene && 'onStateUpdate' in scene) {
        (scene as any).onStateUpdate(initialState);
      }
    });

    console.log(`🎮 Phaser game initialized: ${this.config.name}`);
  }

  /**
   * Update game with new state from backend
   */
  update(state: GameState): void {
    this.currentState = { ...this.currentState, ...state };

    const scene = this.getMainScene();
    if (scene && 'onStateUpdate' in scene) {
      (scene as any).onStateUpdate(state);
    }
  }

  /**
   * Clean up and destroy the Phaser game
   */
  destroy(): void {
    if (this.game) {
      this.game.destroy(true);
      this.game = null;
    }
    console.log(`🧹 Phaser game destroyed: ${this.config.name}`);
  }
}
