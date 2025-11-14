/**
 * Main entry point for the frontend application
 */
import { socket } from './socket';
import { GameManager } from './gameManager';

console.log('🚀 Twitch Chat Games - Frontend Starting...');

// Wait for DOM to be ready
document.addEventListener('DOMContentLoaded', () => {
  const gameRoot = document.getElementById('game-root');

  if (!gameRoot) {
    console.error('Game root element not found!');
    return;
  }

  // Initialize game manager
  const gameManager = new GameManager(socket, gameRoot);

  console.log('✅ Frontend initialized');

  // Expose gameManager globally for debugging
  (window as any).gameManager = gameManager;
  (window as any).socket = socket;

  console.log('💡 Debug: gameManager and socket available in window object');
});
