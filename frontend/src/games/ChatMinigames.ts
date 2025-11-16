/**
 * Chat Minigames - Collection Container
 * Manages multiple minigame scenes using Phaser's scene manager
 */
import Phaser from 'phaser';
import { PhaserGameBase } from './PhaserGameBase';
import type { GameState } from '../types';

// Import minigame scenes
import { ShapeSmashScene } from './chat-minigames/ShapeSmashScene';

/**
 * ChatMinigames game container
 * Uses Phaser's scene manager to switch between different minigames
 */
export class ChatMinigames extends PhaserGameBase {
  private activeSceneName: string = 'ShapeSmashScene';

  /**
   * Register all minigame scenes
   */
  protected getScenes(): (typeof Phaser.Scene)[] {
    return [
      ShapeSmashScene,
      // Add more minigame scenes here as they're created
      // ReactionTimeScene,
      // ColorMatchScene,
    ];
  }

  /**
   * Get the currently active scene
   * This changes based on which minigame is active
   */
  protected getMainScene(): Phaser.Scene | null {
    if (!this.game) {
      return null;
    }

    // Get the active scene by name
    const scene = this.game.scene.getScene(this.activeSceneName);
    return scene || null;
  }

  /**
   * Override init to set initial active scene and start it
   */
  init(initialState: GameState): void {
    // Set active scene from initial state if provided
    if (initialState.active_scene) {
      this.activeSceneName = initialState.active_scene as string;
    }

    // Call parent init (creates Phaser game)
    super.init(initialState);

    // Start the initial scene (Phaser creates scenes but doesn't start them)
    if (this.game) {
      this.game.events.once('ready', () => {
        console.log(`🎬 Starting scene: ${this.activeSceneName}`);
        this.game!.scene.start(this.activeSceneName);
        // Note: Parent class already sends initialState to scene, no need to duplicate
      });
    }

    console.log(`🎮 ChatMinigames initialized with scene: ${this.activeSceneName}`);
  }

  /**
   * Update game with new state from backend.
   * Routes updates to the active scene and handles scene switching.
   *
   * IMPORTANT: This method receives incremental updates from GameManager,
   * NOT merged state. We maintain our own merged state in this.currentState
   * for tracking, but clear transient events after processing.
   *
   * See STATE_MANAGEMENT.md for details.
   */
  update(state: GameState): void {
    console.log('📥 ChatMinigames.update received state:', Object.keys(state));
    if (state.event) {
      console.log('  ⚠️ State contains event:', state.event);
    }
    this.currentState = { ...this.currentState, ...state };

    // Handle scene switching
    if (state.event === 'switch_scene' && state.active_scene) {
      this.switchScene(state.active_scene as string);
      return;
    }

    // Route state update to active scene
    const scene = this.getMainScene();
    if (scene && 'onStateUpdate' in scene) {
      (scene as any).onStateUpdate(state);
    }

    /**
     * CRITICAL: Clear transient events from persistent state after processing.
     *
     * Events are one-time triggers that should NOT persist across updates.
     * If we don't clear them, they'll stick around in this.currentState and
     * could be re-triggered on the next update.
     *
     * Example:
     *   Update 1: {event: 'boost'} → boost triggers → delete event
     *   Update 2: {shape_added: {...}} → no event persists ✅
     *
     * Without this cleanup:
     *   Update 1: {event: 'boost'} → boost triggers
     *   Update 2: {shape_added: {...}} → {event: 'boost', shape_added} → boost triggers again ❌
     *
     * See STATE_MANAGEMENT.md § "Transient Events"
     */
    if (state.event) {
      delete this.currentState.event;
    }
  }

  /**
   * Switch to a different minigame scene
   */
  private switchScene(newSceneName: string): void {
    if (!this.game) {
      console.error('Cannot switch scene: game not initialized');
      return;
    }

    const oldSceneName = this.activeSceneName;

    // Check if new scene exists
    const newScene = this.game.scene.getScene(newSceneName);
    if (!newScene) {
      console.error(`Scene not found: ${newSceneName}`);
      return;
    }

    // Stop old scene
    if (oldSceneName && this.game.scene.isActive(oldSceneName)) {
      this.game.scene.stop(oldSceneName);
    }

    // Start new scene
    this.game.scene.start(newSceneName);
    this.activeSceneName = newSceneName;

    console.log(`🔄 Switched from ${oldSceneName} to ${newSceneName}`);
  }

  /**
   * Override Phaser config to enable gravity for physics-based minigames
   */
  protected getPhaserConfig(): Phaser.Types.Core.GameConfig {
    const baseConfig = super.getPhaserConfig();

    return {
      ...baseConfig,
      physics: {
        default: 'arcade',
        arcade: {
          gravity: { x: 0, y: 150 },  // Enable gravity for Shape Smash
          debug: false,
        },
      },
    };
  }
}
