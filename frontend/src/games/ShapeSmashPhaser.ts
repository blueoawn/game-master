/**
 * Shape Smash Game - Phaser 3 Version
 * Interactive physics sandbox where viewers spawn shapes
 */
import Phaser from 'phaser';
import { PhaserGameBase } from './PhaserGameBase';

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

interface ShapeSmashState {
  shapes?: Shape[];
  shape_count?: number;
  shape_added?: Shape;
  event?: string;
  username?: string;
}

class ShapeSmashScene extends Phaser.Scene {
  private shapes: Map<string, Phaser.GameObjects.GameObject> = new Map();
  private shapeData: Map<string, Shape> = new Map();
  private countText!: Phaser.GameObjects.Text;
  private notificationText!: Phaser.GameObjects.Text;

  constructor() {
    super({ key: 'ShapeSmashScene' });
  }

  create() {
    const width = this.cameras.main.width;
    const height = this.cameras.main.height;

    // Setup physics world bounds
    this.physics.world.setBounds(0, 0, width, height);
    this.physics.world.setBoundsCollision(true, true, true, true);

    // Create title
    this.add.text(width / 2, 60, 'Shape Smash!', {
      fontSize: '48px',
      color: '#9147ff',
      fontStyle: 'bold',
    }).setOrigin(0.5);

    // Create instructions
    this.add.text(
      20,
      height - 30,
      'Commands: !square, !circle, !triangle, !boost, !explode',
      {
        fontSize: '20px',
        color: '#adadb8',
      }
    ).setOrigin(0, 1);

    // Create shape count
    this.countText = this.add.text(
      width - 20,
      height - 30,
      'Shapes: 0',
      {
        fontSize: '20px',
        color: '#adadb8',
      }
    ).setOrigin(1, 1);

    // Create notification text (hidden by default)
    this.notificationText = this.add.text(width / 2, height / 2, '', {
      fontSize: '32px',
      color: '#ffffff',
      backgroundColor: '#000000aa',
      padding: { x: 20, y: 10 },
    }).setOrigin(0.5).setAlpha(0);

    console.log('✅ Shape Smash scene created');
  }

  /**
   * Called when backend sends state update
   */
  onStateUpdate(state: ShapeSmashState) {
    // Handle events
    if (state.event) {
      this.handleEvent(state.event, state);
    }

    // Handle new shape
    if (state.shape_added) {
      this.addShape(state.shape_added);
    }

    // Update all shapes if full list provided
    if (state.shapes) {
      this.syncShapes(state.shapes);
    }
  }

  private handleEvent(event: string, state: ShapeSmashState) {
    switch (event) {
      case 'boost':
        this.boostAllShapes();
        this.showNotification(`${state.username} boosted all shapes!`, 0x4ECDC4);
        break;
      case 'explode':
        this.explodeShapes();
        this.showNotification(`${state.username} exploded the shapes!`, 0xFF6B6B);
        break;
      case 'clear':
        this.clearAllShapes();
        this.showNotification(`${state.username} cleared all shapes!`, 0xFFA07A);
        break;
    }
  }

  private addShape(shapeData: Shape) {
    const { id, type, x, y, color, username } = shapeData;

    // Don't add if already exists
    if (this.shapes.has(id)) return;

    let sprite: Phaser.GameObjects.GameObject;
    const colorNum = parseInt(color.replace('#', ''), 16);

    // Create shape based on type
    switch (type) {
      case 'square':
        const square = this.add.rectangle(x, y, 40, 40, colorNum);
        this.physics.add.existing(square);
        sprite = square;
        break;

      case 'circle':
        const circle = this.add.circle(x, y, 20, colorNum);
        this.physics.add.existing(circle);
        sprite = circle;
        break;

      case 'triangle':
        const triangle = this.add.triangle(x, y, 0, 20, 20, -20, -20, -20, colorNum);
        this.physics.add.existing(triangle);
        sprite = triangle;
        break;

      default:
        return;
    }

    // Setup physics
    const body = (sprite as any).body as Phaser.Physics.Arcade.Body;
    if (body) {
      body.setBounce(0.7);
      body.setCollideWorldBounds(true);
      body.setDamping(true);
      body.setDrag(0.99);

      // Add some initial velocity variation
      body.setVelocity(
        (Math.random() - 0.5) * 100,
        0
      );
    }

    // Add username label
    const label = this.add.text(x, y + 35, username, {
      fontSize: '14px',
      color: '#ffffff',
    }).setOrigin(0.5);

    // Store references
    this.shapes.set(id, sprite);
    this.shapeData.set(id, shapeData);

    // Link label to sprite
    (sprite as any).usernameLabel = label;

    this.updateShapeCount();
  }

  private syncShapes(newShapes: Shape[]) {
    // Remove shapes that no longer exist
    const newIds = new Set(newShapes.map(s => s.id));
    for (const [shapeId, sprite] of this.shapes.entries()) {
      if (!newIds.has(shapeId)) {
        sprite.destroy();
        const label = (sprite as any).usernameLabel;
        if (label) label.destroy();
        this.shapes.delete(shapeId);
        this.shapeData.delete(shapeId);
      }
    }

    // Add new shapes
    for (const shape of newShapes) {
      if (!this.shapes.has(shape.id)) {
        this.addShape(shape);
      }
    }

    this.updateShapeCount();
  }

  private boostAllShapes() {
    for (const sprite of this.shapes.values()) {
      const body = (sprite as any).body as Phaser.Physics.Arcade.Body;
      if (body) {
        body.setVelocityY(body.velocity.y - 400);
      }
    }
  }

  private explodeShapes() {
    const centerX = this.cameras.main.width / 2;
    const centerY = this.cameras.main.height / 2;

    for (const sprite of this.shapes.values()) {
      const body = (sprite as any).body as Phaser.Physics.Arcade.Body;
      if (body) {
        const dx = body.x - centerX;
        const dy = body.y - centerY;
        const distance = Math.sqrt(dx * dx + dy * dy);

        if (distance > 0) {
          body.setVelocity(
            (dx / distance) * 400,
            (dy / distance) * 400
          );
        }
      }
    }
  }

  private clearAllShapes() {
    for (const sprite of this.shapes.values()) {
      sprite.destroy();
      const label = (sprite as any).usernameLabel;
      if (label) label.destroy();
    }
    this.shapes.clear();
    this.shapeData.clear();
    this.updateShapeCount();
  }

  private updateShapeCount() {
    this.countText.setText(`Shapes: ${this.shapes.size}`);
  }

  private showNotification(message: string, color: number) {
    this.notificationText.setText(message);
    this.notificationText.setColor(`#${color.toString(16).padStart(6, '0')}`);
    this.notificationText.setAlpha(1);

    // Fade out after 3 seconds
    this.tweens.add({
      targets: this.notificationText,
      alpha: 0,
      duration: 1000,
      delay: 2000,
    });
  }

  update() {
    // Update username labels to follow sprites
    for (const sprite of this.shapes.values()) {
      const label = (sprite as any).usernameLabel;
      if (label && 'x' in sprite && 'y' in sprite) {
        label.setPosition((sprite as any).x, (sprite as any).y + 35);
      }
    }
  }
}

export class ShapeSmash extends PhaserGameBase {
  private mainScene: ShapeSmashScene | null = null;

  protected getScenes(): (typeof Phaser.Scene)[] {
    return [ShapeSmashScene];
  }

  protected getMainScene(): Phaser.Scene | null {
    if (!this.mainScene && this.game) {
      this.mainScene = this.game.scene.getScene('ShapeSmashScene') as ShapeSmashScene;
    }
    return this.mainScene;
  }
}
