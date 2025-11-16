/**
 * Game Component Registry
 * Maps component names to their implementations
 */
import type { GameComponentConstructor } from '../types';

// Import game components here
import { ChatMinigames } from './ChatMinigames';

export class GameRegistry {
  private static games = new Map<string, GameComponentConstructor>([
    ['ChatMinigames', ChatMinigames],
    // Add more games here as they're created
  ]);

  static get(componentName: string): GameComponentConstructor | undefined {
    const component = this.games.get(componentName);
    if (!component) {
      console.error(`Game component '${componentName}' not found in registry`);
      console.log('Available components:', Array.from(this.games.keys()));
    }
    return component;
  }

  static register(name: string, component: GameComponentConstructor) {
    console.log(`Registering game component: ${name}`);
    this.games.set(name, component);
  }

  static list(): string[] {
    return Array.from(this.games.keys());
  }
}
