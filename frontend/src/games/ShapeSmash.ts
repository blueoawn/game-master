/**
 * Shape Smash Game - Frontend
 * Handles rendering and physics simulation for the shape spawning game.
 */
import type { GameComponent, GameState, GameConfig } from '../types';

interface Shape {
  id: string;
  type: 'square' | 'circle' | 'triangle';
  x: number;
  y: number;
  vx: number;
  vy: number;
  color: string;
  username: string;
}

interface ShapeSmashState extends GameState {
  shapes: Shape[];
  shape_count?: number;
  shape_added?: Shape;
  event?: string;
  username?: string;
}

export class ShapeSmash implements GameComponent {
  private canvas: HTMLCanvasElement;
  private ctx: CanvasRenderingContext2D;
  private shapes: Shape[] = [];
  private animationFrame: number | null = null;
  private config: any;

  // Physics constants
  private readonly GRAVITY = 0.5;
  private readonly BOUNCE = 0.7;
  private readonly FRICTION = 0.99;
  private readonly SIZE = 40;

  constructor(container: HTMLElement, config: GameConfig) {
    this.config = config.config;

    // Create canvas
    this.canvas = document.createElement('canvas');
    this.canvas.width = this.config.canvas_width || 1920;
    this.canvas.height = this.config.canvas_height || 1080;
    this.canvas.style.width = '100%';
    this.canvas.style.height = '100%';
    this.canvas.style.objectFit = 'contain';
    this.canvas.style.backgroundColor = '#1e1e1e';

    const context = this.canvas.getContext('2d');
    if (!context) {
      throw new Error('Failed to get canvas 2D context');
    }
    this.ctx = context;

    container.appendChild(this.canvas);
  }

  init(initialState: ShapeSmashState): void {
    this.shapes = initialState.shapes || [];
    this.startRenderLoop();
    console.log('🎮 Shape Smash initialized');
  }

  update(state: ShapeSmashState): void {
    // Handle specific events
    if (state.event) {
      this.handleEvent(state.event, state);
    }

    // Handle shape addition with animation
    if (state.shape_added) {
      this.animateShapeSpawn(state.shape_added);
    }

    // Update shapes list
    if (state.shapes) {
      this.shapes = state.shapes;
    }
  }

  private handleEvent(event: string, state: ShapeSmashState): void {
    switch (event) {
      case 'boost':
        this.boostAllShapes();
        this.showNotification(`${state.username} boosted all shapes!`, '#4ECDC4');
        break;
      case 'explode':
        this.explodeShapes();
        this.showNotification(`${state.username} exploded the shapes!`, '#FF6B6B');
        break;
      case 'clear':
        this.shapes = [];
        this.showNotification(`${state.username} cleared all shapes!`, '#FFA07A');
        break;
    }
  }

  private boostAllShapes(): void {
    for (const shape of this.shapes) {
      shape.vy -= 20;
    }
  }

  private explodeShapes(): void {
    const centerX = this.canvas.width / 2;
    const centerY = this.canvas.height / 2;

    for (const shape of this.shapes) {
      const dx = shape.x - centerX;
      const dy = shape.y - centerY;
      const distance = Math.sqrt(dx * dx + dy * dy);

      if (distance > 0) {
        shape.vx = (dx / distance) * 20;
        shape.vy = (dy / distance) * 20;
      }
    }
  }

  private animateShapeSpawn(shape: Shape): void {
    // Add some initial randomness to spawn position
    shape.x += (Math.random() - 0.5) * 100;
    shape.vx = (Math.random() - 0.5) * 5;
  }

  private startRenderLoop(): void {
    const render = () => {
      this.updatePhysics();
      this.render();
      this.animationFrame = requestAnimationFrame(render);
    };
    render();
  }

  private updatePhysics(): void {
    for (const shape of this.shapes) {
      // Apply gravity
      shape.vy += this.GRAVITY;

      // Apply velocity
      shape.x += shape.vx;
      shape.y += shape.vy;

      // Apply friction
      shape.vx *= this.FRICTION;

      // Boundary collision - bottom
      if (shape.y + this.SIZE / 2 > this.canvas.height) {
        shape.y = this.canvas.height - this.SIZE / 2;
        shape.vy *= -this.BOUNCE;
        shape.vx *= this.FRICTION;
      }

      // Boundary collision - top
      if (shape.y - this.SIZE / 2 < 0) {
        shape.y = this.SIZE / 2;
        shape.vy *= -this.BOUNCE;
      }

      // Boundary collision - left
      if (shape.x - this.SIZE / 2 < 0) {
        shape.x = this.SIZE / 2;
        shape.vx *= -this.BOUNCE;
      }

      // Boundary collision - right
      if (shape.x + this.SIZE / 2 > this.canvas.width) {
        shape.x = this.canvas.width - this.SIZE / 2;
        shape.vx *= -this.BOUNCE;
      }
    }

    // Simple collision detection between shapes
    for (let i = 0; i < this.shapes.length; i++) {
      for (let j = i + 1; j < this.shapes.length; j++) {
        this.checkCollision(this.shapes[i], this.shapes[j]);
      }
    }
  }

  private checkCollision(shape1: Shape, shape2: Shape): void {
    const dx = shape2.x - shape1.x;
    const dy = shape2.y - shape1.y;
    const distance = Math.sqrt(dx * dx + dy * dy);
    const minDistance = this.SIZE;

    if (distance < minDistance) {
      // Collision detected - simple elastic collision
      const angle = Math.atan2(dy, dx);
      const targetX = shape1.x + Math.cos(angle) * minDistance;
      const targetY = shape1.y + Math.sin(angle) * minDistance;

      // Separate shapes
      const ax = (targetX - shape2.x) * 0.5;
      const ay = (targetY - shape2.y) * 0.5;
      shape1.x -= ax;
      shape1.y -= ay;
      shape2.x += ax;
      shape2.y += ay;

      // Exchange velocities (simplified)
      const tempVx = shape1.vx;
      const tempVy = shape1.vy;
      shape1.vx = shape2.vx * this.BOUNCE;
      shape1.vy = shape2.vy * this.BOUNCE;
      shape2.vx = tempVx * this.BOUNCE;
      shape2.vy = tempVy * this.BOUNCE;
    }
  }

  private render(): void {
    // Clear canvas
    this.ctx.fillStyle = '#1e1e1e';
    this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);

    // Draw title
    this.ctx.fillStyle = '#9147ff';
    this.ctx.font = 'bold 48px Arial';
    this.ctx.textAlign = 'center';
    this.ctx.fillText('Shape Smash!', this.canvas.width / 2, 60);

    // Draw instructions
    this.ctx.fillStyle = '#adadb8';
    this.ctx.font = '20px Arial';
    this.ctx.textAlign = 'left';
    this.ctx.fillText(
      'Commands: !square, !circle, !triangle, !boost, !explode',
      20,
      this.canvas.height - 30
    );

    // Draw shape count
    this.ctx.textAlign = 'right';
    this.ctx.fillText(
      `Shapes: ${this.shapes.length}`,
      this.canvas.width - 20,
      this.canvas.height - 30
    );

    // Draw all shapes
    for (const shape of this.shapes) {
      this.drawShape(shape);
    }
  }

  private drawShape(shape: Shape): void {
    this.ctx.fillStyle = shape.color;

    switch (shape.type) {
      case 'square':
        this.ctx.fillRect(
          shape.x - this.SIZE / 2,
          shape.y - this.SIZE / 2,
          this.SIZE,
          this.SIZE
        );
        break;

      case 'circle':
        this.ctx.beginPath();
        this.ctx.arc(shape.x, shape.y, this.SIZE / 2, 0, Math.PI * 2);
        this.ctx.fill();
        break;

      case 'triangle':
        this.ctx.beginPath();
        this.ctx.moveTo(shape.x, shape.y - this.SIZE / 2);
        this.ctx.lineTo(shape.x + this.SIZE / 2, shape.y + this.SIZE / 2);
        this.ctx.lineTo(shape.x - this.SIZE / 2, shape.y + this.SIZE / 2);
        this.ctx.closePath();
        this.ctx.fill();
        break;
    }

    // Draw username
    this.ctx.fillStyle = 'white';
    this.ctx.font = '14px Arial';
    this.ctx.textAlign = 'center';
    this.ctx.fillText(shape.username, shape.x, shape.y + this.SIZE);
  }

  private showNotification(message: string, color: string): void {
    const gameStats = document.getElementById('game-stats');
    if (gameStats) {
      gameStats.style.color = color;
      gameStats.textContent = message;

      // Clear after 3 seconds
      setTimeout(() => {
        if (gameStats.textContent === message) {
          gameStats.textContent = '';
        }
      }, 3000);
    }
  }

  destroy(): void {
    if (this.animationFrame) {
      cancelAnimationFrame(this.animationFrame);
    }
    if (this.canvas.parentElement) {
      this.canvas.parentElement.removeChild(this.canvas);
    }
    console.log('🧹 Shape Smash cleaned up');
  }
}
