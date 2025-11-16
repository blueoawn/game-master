/**
 * Socket.IO client setup and connection management
 */
import { io, Socket } from 'socket.io-client';

// Create socket connection
export const socket: Socket = io('http://localhost:5000', {
  transports: ['websocket', 'polling'],
  reconnection: true,
  reconnectionDelay: 1000,
  reconnectionAttempts: 5,
});

// Connection event handlers
socket.on('connect', () => {
  console.log('✅ Connected to server');
  updateConnectionStatus(true);
});

socket.on('disconnect', () => {
  console.log('❌ Disconnected from server');
  updateConnectionStatus(false);
});

socket.on('connect_error', (error) => {
  console.error('Connection error:', error);
  updateConnectionStatus(false);
});

// Update UI connection status
function updateConnectionStatus(connected: boolean) {
  const statusDot = document.getElementById('status-dot');
  const statusText = document.getElementById('status-text');

  if (statusDot && statusText) {
    if (connected) {
      statusDot.classList.remove('disconnected');
      statusText.textContent = 'Connected';
    } else {
      statusDot.classList.add('disconnected');
      statusText.textContent = 'Disconnected';
    }
  }
}

export default socket;
