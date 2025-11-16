/**
 * Shape Smash Scene - Standalone Phaser Scene
 * Interactive physics sandbox where viewers spawn shapes
 * Can be used within ChatMinigames collection or standalone
 */
import Phaser from 'phaser';
import { socket } from '../../socket';

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

/**
 * ShapeSmashScene - Physics-based shape spawning game
 */
export class ShapeSmashScene extends Phaser.Scene {
  private shapes: Map<string, Phaser.GameObjects.GameObject> = new Map();
  private shapeData: Map<string, Shape> = new Map();
  private countText!: Phaser.GameObjects.Text;
  private notificationText!: Phaser.GameObjects.Text;
  private physicsGroup!: Phaser.Physics.Arcade.Group;
  private targetCircle!: Phaser.GameObjects.Arc;
  private scores: Map<string, number> = new Map();
  private leaderboardText!: Phaser.GameObjects.Text;
  private persistentScores: Map<string, number> = new Map();

  constructor() {
    super({ key: 'ShapeSmashScene' });
  }

  create() {
    const width = this.cameras.main.width;
    const height = this.cameras.main.height;

    // Setup physics world bounds
    this.physics.world.setBounds(0, 0, width, height);
    this.physics.world.setBoundsCollision(true, true, true, true);

    // Create physics group for all shapes with collision
    this.physicsGroup = this.physics.add.group();

    // Enable collisions between all shapes in the group
    this.physics.add.collider(this.physicsGroup, this.physicsGroup);

    // Create target circle in the middle
    const targetRadius = 80;
    this.targetCircle = this.add.circle(
      width / 2,
      height / 2,
      targetRadius,
      0xFFD700, // Gold color
      0.6 // Semi-transparent
    );
    this.physics.add.existing(this.targetCircle, true); // true makes it static
    (this.targetCircle.body as Phaser.Physics.Arcade.Body).setCircle(targetRadius);

    // Add target circle outline for better visibility
    const targetOutline = this.add.circle(width / 2, height / 2, targetRadius);
    targetOutline.setStrokeStyle(4, 0xFFD700);
    targetOutline.setFillStyle(0xFFD700, 0.3);

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
      'Commands: !square, !circle, !triangle, !boost, !explode, !clear',
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

    // Create leaderboard
    this.leaderboardText = this.add.text(20, 120, 'LEADERBOARD\n\nNo scores yet!', {
      fontSize: '20px',
      color: '#FFD700',
      fontStyle: 'bold',
      backgroundColor: '#00000088',
      padding: { x: 15, y: 10 },
    }).setOrigin(0, 0);

    // Request leaderboard from backend and set up listener
    this.setupLeaderboard();

    console.log('✅ Shape Smash scene created');
  }

  /**
   * Setup leaderboard from backend via Socket.IO
   */
  private setupLeaderboard() {
    // Request initial leaderboard
    socket.emit('get_leaderboard');

    // Listen for leaderboard updates
    socket.on('leaderboard_update', (data: { leaderboard: Array<{ username: string; score: number }> }) => {
      console.log('📊 Received leaderboard update:', data.leaderboard);

      // Update persistent scores cache
      this.persistentScores.clear();
      data.leaderboard.forEach(player => {
        this.persistentScores.set(player.username, player.score);
      });

      // Update the leaderboard display
      this.updateLeaderboard();
    });

    console.log('✅ Leaderboard connected via Socket.IO');
  }

  /**
   * Called when backend sends state update
   */
  onStateUpdate(state: ShapeSmashState) {
    console.log('🎯 ShapeSmashScene.onStateUpdate called:', state);

    // Handle events
    if (state.event) {
      console.log('  → Handling event:', state.event);
      this.handleEvent(state.event, state);
    }

    // Handle new shape
    if (state.shape_added) {
      console.log('  → Adding shape:', state.shape_added);
      this.addShape(state.shape_added);
    }

    /**
     * CRITICAL: Guard against syncing when doing incremental adds.
     *
     * Why? Backend might send: {shape_added: {...}, shapes: []}
     * Without this guard:
     *   1. addShape() adds the new shape to local state
     *   2. syncShapes([]) immediately removes it
     *   3. Shape flickers and disappears
     *
     * With this guard:
     *   1. addShape() adds the new shape
     *   2. Sync is skipped because shape_added is present
     *   3. Shape persists ✅
     *
     * See STATE_MANAGEMENT.md § "Bug #3: Shape Sync Deleting Newly Added Shapes"
     */
    if (state.shapes && !state.shape_added) {
      console.log('  → Syncing shapes:', state.shapes.length);
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
    let shapeSize = 40; // Base size for mass calculation

    // Create shape based on type
    switch (type) {
      case 'square':
        const square = this.add.rectangle(x, y, 40, 40, colorNum);
        this.physics.add.existing(square);
        sprite = square;
        shapeSize = 40;
        break;

      case 'circle':
        const circle = this.add.circle(x, y, 20, colorNum);
        this.physics.add.existing(circle);
        // Set circular body for more accurate collisions
        (circle.body as Phaser.Physics.Arcade.Body).setCircle(20);
        sprite = circle;
        shapeSize = 40;
        break;

      case 'triangle':
        const triangle = this.add.triangle(x, y, 0, 20, 20, -20, -20, -20, colorNum);
        this.physics.add.existing(triangle);
        sprite = triangle;
        shapeSize = 35;
        break;

      default:
        return;
    }

    // Add to physics group for automatic collision handling
    this.physicsGroup.add(sprite);

    // Add collision detection with target circle
    this.physics.add.overlap(sprite, this.targetCircle, () => {
      this.handleTargetHit(id, username, sprite);
    });

    // Setup physics properties for bouncy, lively behavior
    const body = (sprite as any).body as Phaser.Physics.Arcade.Body;
    if (body) {
      // High bounce for satisfying collisions
      body.setBounce(0.8, 0.8);
      body.setCollideWorldBounds(true);

      // Low drag so shapes keep moving
      body.setDrag(20);
      body.setAngularDrag(30);

      // Set mass based on size - larger shapes are heavier
      body.setMass(shapeSize / 20);

      // Add some initial velocity and spin for liveliness
      body.setVelocity(
        (Math.random() - 0.5) * 150,
        (Math.random() - 0.5) * 100
      );

      // Add random angular velocity (spinning)
      body.setAngularVelocity((Math.random() - 0.5) * 200);

      // Enable rotation dampening for realistic spin
      body.maxAngular = 300;
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

  private handleTargetHit(shapeId: string, username: string, sprite: Phaser.GameObjects.GameObject) {
    // Award point to player (local session score)
    const currentScore = this.scores.get(username) || 0;
    this.scores.set(username, currentScore + 1);

    // Save to backend database via Socket.IO
    socket.emit('add_score', {
      username: username,
      points: 1,
      game_name: 'ShapeSmash'
    });

    // Remove the shape
    sprite.destroy();
    const label = (sprite as any).usernameLabel;
    if (label) label.destroy();
    this.shapes.delete(shapeId);
    this.shapeData.delete(shapeId);

    // Update displays
    this.updateShapeCount();
    this.updateLeaderboard();

    // Show notification
    this.showNotification(`${username} scored! 🎯 +1 point`, 0xFFD700);
  }

  private updateLeaderboard() {
    // Merge persistent scores (from SpacetimeDB) with session scores
    const combinedScores = new Map<string, { total: number; session: number; persistent: number }>();

    // Add persistent scores
    this.persistentScores.forEach((score, username) => {
      combinedScores.set(username, {
        total: score,
        session: 0,
        persistent: score,
      });
    });

    // Add/merge session scores
    this.scores.forEach((sessionScore, username) => {
      const existing = combinedScores.get(username);
      if (existing) {
        existing.total = existing.persistent + sessionScore;
        existing.session = sessionScore;
      } else {
        combinedScores.set(username, {
          total: sessionScore,
          session: sessionScore,
          persistent: 0,
        });
      }
    });

    // Sort by total score (descending) and take top 10
    const sortedScores = Array.from(combinedScores.entries())
      .sort((a, b) => b[1].total - a[1].total)
      .slice(0, 10);

    // Build leaderboard text
    let text = 'LEADERBOARD \n'; 

    if (sortedScores.length === 0) {
      text += '\nNo scores yet!';
    } else {
      sortedScores.forEach(([username, scores], index) => {
        const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : '  ';

        // Show total score, with session score if different
        if (scores.session > 0 && scores.persistent > 0) {
          text += `\n${medal} ${username}: ${scores.total} (${scores.persistent}+${scores.session})`;
        } else {
          text += `\n${medal} ${username}: ${scores.total}`;
        }
      });
    }

    this.leaderboardText.setText(text);
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
        // Add some spin for extra flair
        body.setAngularVelocity(body.angularVelocity + (Math.random() - 0.5) * 300);
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
          // Add dramatic spinning based on distance from center
          body.setAngularVelocity((Math.random() - 0.5) * 400);
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

  /**
   * Called when the scene is shut down
   * Clean up Socket.IO listeners
   */
  shutdown() {
    socket.off('leaderboard_update');
    console.log('🔌 ShapeSmashScene shutdown - cleaned up Socket.IO listeners');
  }
}
