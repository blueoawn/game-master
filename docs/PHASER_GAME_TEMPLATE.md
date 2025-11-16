# Phaser 3 Game Development Guide

> **Last Updated:** 2025-01-16
> **Template Version:** 2.0
> **For:** Twitch Chat Games Platform

Complete guide and template for creating new Phaser 3-powered games. This guide covers everything from project setup to advanced patterns, with working code examples and best practices.

---

## Table of Contents

- [Overview](#overview)
- [Quick Start Checklist](#quick-start-checklist)
- [Step-by-Step Setup](#step-by-step-setup)
  - [1. Create Directory Structure](#1-create-directory-structure)
  - [2. Create Game Manifest](#2-create-game-manifest)
  - [3. Create Backend Game Class](#3-create-backend-game-class)
  - [4. Create Frontend Phaser Scene](#4-create-frontend-phaser-scene)
  - [5. Register in Frontend Registry](#5-register-in-frontend-registry)
  - [6. Test Your Game](#6-test-your-game)
- [State Management](#state-management)
- [Phaser 3 Quick Reference](#phaser-3-quick-reference)
- [Common Patterns](#common-patterns)
- [Best Practices](#best-practices)
- [Troubleshooting](#troubleshooting)
- [Resources](#resources)

---

## Overview

### What You'll Build

A real-time interactive game where:
- **Twitch viewers** send commands via chat (`!jump`, `!spawn`, etc.)
- **Python backend** processes commands and manages game logic
- **Phaser 3 frontend** renders visuals with physics and animations
- **WebSocket (SocketIO)** syncs state in real-time

### Architecture Flow

```
Twitch Chat (!jump)
       ↓
Python Backend (BaseGame) → Processes command
       ↓
emit_state({'event': 'jump'})
       ↓
SocketIO WebSocket
       ↓
Frontend (Phaser Scene) → Renders jump animation
```

### Prerequisites

| Requirement | Details |
|-------------|---------|
| **Python 3.11+** | Backend game logic |
| **Node.js 18+** | Frontend build tools |
| **TypeScript knowledge** | Frontend development |
| **Phaser 3 basics** | Game engine familiarity (helpful) |

📖 **See also:** [README.md](../README.md) for platform architecture overview

---

## Quick Start Checklist

Follow these steps in order:

- [ ] **Create directory structure** - Backend and frontend folders
- [ ] **Write game manifest** - JSON configuration file
- [ ] **Implement backend class** - Extends `BaseGame`
- [ ] **Create Phaser scene** - TypeScript game scene
- [ ] **Register in frontend** - Add to registry
- [ ] **Build & test** - Verify game loads and commands work

**Estimated time:** 30-60 minutes for a basic game

---

## Step-by-Step Setup

### 1. Create Directory Structure

```bash
# Navigate to project root
cd "stream tools/chat-games"

# Create game directories
mkdir -p backend/games/my_game/backend
mkdir -p backend/games/my_game/assets  # Optional: for game-specific assets
```

**Result:**
```
backend/games/my_game/
├── game_manifest.json    # [Next step]
├── backend/
│   └── game.py          # [Step 3]
└── assets/              # Optional
```

---

### 2. Create Game Manifest

Create `backend/games/my_game/game_manifest.json`:

```json
{
  "id": "my_game",
  "name": "My Awesome Game",
  "version": "1.0.0",
  "description": "A fun interactive game where viewers control the action",
  "author": "your_name",
  "license": "MIT",

  "backend": {
    "entry_point": "game:MyGame"
  },

  "frontend": {
    "component": "MyGame"
  },

  "config": {
    "canvas_width": 1920,
    "canvas_height": 1080,
    "default_minigame": "my_game"
  },

  "commands": [
    {
      "name": "start",
      "description": "Start the game",
      "permission": "everyone"
    },
    {
      "name": "jump",
      "description": "Make player jump",
      "permission": "everyone"
    },
    {
      "name": "reset",
      "description": "Reset game state",
      "permission": "moderator"
    }
  ]
}
```

**Manifest Fields Explained:**

| Field | Purpose | Example |
|-------|---------|---------|
| `id` | Unique game identifier (lowercase, no spaces) | `"my_game"` |
| `backend.entry_point` | Python class to load (`file:ClassName`) | `"game:MyGame"` |
| `frontend.component` | TypeScript class name | `"MyGame"` |
| `config.canvas_width` | Phaser canvas width (pixels) | `1920` |
| `config.canvas_height` | Phaser canvas height (pixels) | `1080` |
| `commands` | List of available chat commands | See example |

---

### 3. Create Backend Game Class

Create `backend/games/my_game/backend/game.py`:

```python
"""
My Awesome Game - Backend orchestrator
Handles Twitch commands and game logic
"""
import sys
import os
import logging
import random
from typing import Dict, Any, Callable

# Add backend to path for BaseGame import
# Path: backend/games/my_game/backend/game.py → ../../ → backend/
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, backend_path)

from base_game import BaseGame

logger = logging.getLogger(__name__)


class MyGame(BaseGame):
    """
    Main game orchestrator for My Awesome Game.
    Processes Twitch commands and emits state to frontend.
    """

    def __init__(self, socketio=None):
        super().__init__(socketio)
        self.score = 0
        self.player_position = {'x': 100, 'y': 100}

    # === METADATA ===

    def get_title(self) -> str:
        """Display name shown in logs"""
        return "My Awesome Game"

    def get_game_id(self) -> str:
        """Unique identifier matching manifest"""
        return "my_game"

    # === COMMANDS ===

    def get_commands(self) -> Dict[str, Callable]:
        """
        Register Twitch chat commands.
        Returns: {command_name: handler_function}
        """
        return {
            'start': self.start_game,
            'jump': self.player_jump,
            'reset': self.reset_game,
        }

    # === STATE MANAGEMENT ===

    def get_initial_state(self) -> Dict[str, Any]:
        """
        Return fresh initial state for new clients.

        IMPORTANT: Return new state dict, NOT self.game_state
        See STATE_MANAGEMENT.md for details.
        """
        return {
            'score': 0,
            'player': {
                'x': 100,
                'y': 100
            },
            'game_active': False
        }

    def get_frontend_config(self) -> Dict[str, Any]:
        """Frontend configuration"""
        config = {
            'component': 'MyGame',
            'canvas_width': 1920,
            'canvas_height': 1080
        }

        # Override with manifest config if available
        if self._manifest and 'config' in self._manifest:
            config.update(self._manifest['config'])

        return config

    # === COMMAND HANDLERS ===

    def start_game(self, message):
        """
        Handle !start command
        Args:
            message: TwitchIO message object
        """
        username = message.author.name
        logger.info(f"{username} started the game")

        # Update persistent state
        self.score = 0
        self.emit_state({
            'game_active': True,
            'score': 0
        })

    def player_jump(self, message):
        """
        Handle !jump command (transient event)
        """
        username = message.author.name

        # Emit transient event (won't persist in game_state)
        self.emit_event('player_jump', {
            'username': username,
            'force': random.randint(300, 600)
        })

        logger.debug(f"{username} jumped")

    def reset_game(self, message):
        """Handle !reset command (moderator only)"""
        # Permission check handled by twitch_bot.py
        self.reset()
        self.emit_state(self.get_initial_state())
        logger.info("Game reset by moderator")

    # === LIFECYCLE ===

    def on_game_start(self):
        """Called when game becomes active"""
        logger.info("My Awesome Game activated")

    def on_game_end(self):
        """Called when switching to another game"""
        logger.info("My Awesome Game deactivated")
```

**Key Backend Concepts:**

| Method | Purpose | When to Use |
|--------|---------|-------------|
| `emit_state(update)` | Send persistent state changes | Score updates, position changes |
| `emit_event(name, data)` | Send transient events | Jump effects, explosions, sounds |
| `get_initial_state()` | Return fresh state for new clients | Must NOT return `self.game_state` |

📖 **See [State Management](#state-management) section below for details**

<!--
🎥 **Video Tutorial** (Placeholder)
Add backend development walkthrough video here
-->

---

### 4. Create Frontend Phaser Scene

Create `frontend/src/games/my-game/MyGameScene.ts`:

```typescript
import Phaser from 'phaser';
import type { GameState } from '../../types';

/**
 * Interface for state updates from backend
 */
interface MyGameState extends GameState {
  score?: number;
  player?: { x: number; y: number };
  game_active?: boolean;
  event?: string;
  username?: string;
  force?: number;
}

/**
 * Main game scene for My Awesome Game
 */
export class MyGameScene extends Phaser.Scene {
  private player!: Phaser.Physics.Arcade.Sprite;
  private scoreText!: Phaser.GameObjects.Text;
  private score: number = 0;
  private ground!: Phaser.Physics.Arcade.StaticGroup;

  constructor() {
    super({ key: 'MyGameScene' });
  }

  preload() {
    // Load assets here
    // this.load.image('player', 'assets/player.png');
    // this.load.image('ground', 'assets/ground.png');
  }

  create() {
    const width = this.cameras.main.width;
    const height = this.cameras.main.height;

    // Create background
    this.add.rectangle(0, 0, width, height, 0x1a1a2e).setOrigin(0);

    // Create ground
    this.ground = this.physics.add.staticGroup();
    const groundRect = this.add.rectangle(
      width / 2,
      height - 50,
      width,
      100,
      0x16213e
    );
    this.ground.add(groundRect);

    // Create player (using rectangle for now)
    this.player = this.physics.add.sprite(100, 100, '') as any;
    const playerRect = this.add.rectangle(0, 0, 50, 50, 0x0f3460);
    (this.player as any).add(playerRect);

    // Configure physics
    this.player.setCollideWorldBounds(true);
    this.player.setGravityY(800);
    this.physics.add.collider(this.player, this.ground);

    // Create UI
    this.scoreText = this.add.text(20, 20, 'Score: 0', {
      fontSize: '32px',
      color: '#ffffff',
      fontFamily: 'Arial, sans-serif',
    });

    const titleText = this.add.text(width / 2, 60, 'My Awesome Game', {
      fontSize: '48px',
      color: '#e94560',
      fontFamily: 'Arial, sans-serif',
    }).setOrigin(0.5);

    console.log('✅ MyGameScene created');
  }

  /**
   * Called by container when backend sends state update
   * This is where you handle ALL backend messages
   */
  onStateUpdate(state: MyGameState) {
    // Update persistent state
    if (state.score !== undefined) {
      this.score = state.score;
      this.scoreText.setText(`Score: ${this.score}`);
    }

    if (state.player) {
      this.player.setPosition(state.player.x, state.player.y);
    }

    // Handle transient events
    if (state.event) {
      this.handleEvent(state.event, state);
    }
  }

  /**
   * Handle transient events from backend
   */
  private handleEvent(event: string, state: MyGameState) {
    switch (event) {
      case 'player_jump':
        this.handleJump(state.force || 500);
        this.showJumpEffect(state.username || 'Player');
        break;

      case 'game_start':
        this.resetPlayer();
        break;

      default:
        console.warn(`Unknown event: ${event}`);
    }
  }

  private handleJump(force: number) {
    const body = this.player.body as Phaser.Physics.Arcade.Body;

    // Only jump if on ground
    if (body && body.touching.down) {
      body.setVelocityY(-force);

      // Visual feedback
      this.cameras.main.shake(100, 0.005);
    }
  }

  private showJumpEffect(username: string) {
    // Show username near player
    const label = this.add.text(
      this.player.x,
      this.player.y - 50,
      username,
      {
        fontSize: '20px',
        color: '#ffffff',
        backgroundColor: '#000000',
        padding: { x: 8, y: 4 },
      }
    ).setOrigin(0.5);

    // Fade out and destroy
    this.tweens.add({
      targets: label,
      alpha: 0,
      y: label.y - 30,
      duration: 1000,
      onComplete: () => label.destroy(),
    });
  }

  private resetPlayer() {
    this.player.setPosition(100, 100);
    this.player.setVelocity(0, 0);
  }

  update(time: number, delta: number) {
    // Per-frame game loop logic
    // Example: Check for collisions, update animations, etc.
  }
}
```

Now create the game container `frontend/src/games/MyGame.ts`:

```typescript
import Phaser from 'phaser';
import type { GameComponent, GameConfig, GameState } from '../types';
import { PhaserGameBase } from './PhaserGameBase';
import { MyGameScene } from './my-game/MyGameScene';

/**
 * MyGame component - Phaser game container
 */
export class MyGame extends PhaserGameBase implements GameComponent {
  private mainScene: MyGameScene | null = null;

  /**
   * Return array of scenes to register with Phaser
   */
  protected getScenes(): (typeof Phaser.Scene)[] {
    return [MyGameScene];
  }

  /**
   * Get reference to main scene for state updates
   */
  protected getMainScene(): Phaser.Scene | null {
    if (!this.mainScene && this.game) {
      this.mainScene = this.game.scene.getScene('MyGameScene') as MyGameScene;
    }
    return this.mainScene;
  }

  /**
   * Optional: Custom initialization
   */
  init(config: GameConfig): void {
    super.init(config);
    console.log('🎮 MyGame initialized with config:', config);
  }

  /**
   * Optional: Cleanup when game unloads
   */
  destroy(): void {
    this.mainScene = null;
    super.destroy();
  }
}
```

<!--
🎥 **Interactive Demo** (Placeholder)
Add animated GIF or video showing the game scene in action
-->

---

### 5. Register in Frontend Registry

Edit `frontend/src/games/registry.ts` and add your game:

```typescript
import { ChatMinigames } from './ChatMinigames';
import { MyGame } from './MyGame';  // Add this import

/**
 * Central registry for all game components
 */
export class GameRegistry {
  private static games = new Map<string, GameComponentConstructor>([
    ['ChatMinigames', ChatMinigames],
    ['MyGame', MyGame],  // Add this line
  ]);

  static get(componentName: string): GameComponentConstructor | undefined {
    return this.games.get(componentName);
  }

  static getAll(): Map<string, GameComponentConstructor> {
    return new Map(this.games);
  }
}
```

---

### 6. Test Your Game

#### Build Frontend

```bash
cd frontend
npm run build
```

**Expected output:**
```
✓ built in 3.5s
dist/index.html                    1.2 kB
dist/assets/index-abc123.js        287 kB
```

#### Start Backend

```bash
cd ../backend
python app.py
```

**Look for these success messages:**
```
INFO:GameManager: Found 2 games
INFO:GameManager: Loaded initial game: my_game
INFO:werkzeug: * Running on http://0.0.0.0:5000
```

#### Test in Browser

1. **Open** `http://localhost:5000`
2. **Check console** - Should see `✅ MyGameScene created`
3. **Test commands** in Twitch chat:
   - `!start` - Should activate game
   - `!jump` - Player should jump

#### Test Without Twitch (Browser Console)

```javascript
// Simulate jump command
socket.emit('game_state_update', {
  event: 'player_jump',
  username: 'TestUser',
  force: 500
});
```

---

## State Management

### Understanding State vs Events

The platform uses two types of communication from backend to frontend:

| Type | Method | Persists? | Use Case | Example |
|------|--------|-----------|----------|---------|
| **Persistent State** | `emit_state(update)` | ✅ Yes | Scores, positions, game flags | `{'score': 100}` |
| **Transient Events** | `emit_event(name, data)` | ❌ No | Visual effects, sounds, notifications | `emit_event('jump')` |

### Backend: When to Use Each

**Use `emit_state()` for persistent changes:**

```python
def update_score(self, message):
    self.score += 10

    # This state persists - new clients will receive it
    self.emit_state({'score': self.score})
```

**Use `emit_event()` for transient effects:**

```python
def trigger_explosion(self, message):
    # This event fires once - won't replay for reconnecting clients
    self.emit_event('explosion', {
        'x': 500,
        'y': 300,
        'username': message.author.name
    })
```

### Frontend: Handling Updates

```typescript
onStateUpdate(state: GameState) {
    // Persistent state
    if (state.score !== undefined) {
        this.updateScore(state.score);
    }

    // Transient events
    if (state.event === 'explosion') {
        this.playExplosionEffect(state.x, state.y);
        // Effect plays once, then cleared
    }
}
```

📖 **See [STATE_MANAGEMENT.md](../STATE_MANAGEMENT.md) for comprehensive state flow documentation**

---

## Phaser 3 Quick Reference

### Physics

```typescript
// Enable Arcade physics on sprite
this.physics.add.existing(sprite);

// Access physics body
const body = sprite.body as Phaser.Physics.Arcade.Body;

// Set velocity
body.setVelocity(100, -200);
body.setVelocityX(100);
body.setVelocityY(-200);

// Apply forces
body.setGravityY(800);
body.setAccelerationX(50);

// Collisions
this.physics.add.collider(player, ground);
this.physics.add.overlap(player, coins, this.collectCoin, undefined, this);

// Collision detection
if (body.touching.down) {
  // Player is on ground
}
```

### Sprites & Graphics

```typescript
// Preload assets
preload() {
  this.load.image('player', 'assets/player.png');
  this.load.spritesheet('enemy', 'assets/enemy.png', {
    frameWidth: 32,
    frameHeight: 32
  });
}

// Create sprite
const sprite = this.add.sprite(x, y, 'player');

// Create shapes
const circle = this.add.circle(x, y, radius, color);
const rect = this.add.rectangle(x, y, width, height, color);
const triangle = this.add.triangle(x, y, x1, y1, x2, y2, x3, y3, color);

// Set origin (0,0 = top-left, 0.5 = center)
sprite.setOrigin(0.5);

// Rotation & scale
sprite.setRotation(Math.PI / 4);
sprite.setScale(2);

// Depth (z-index)
sprite.setDepth(10);
```

### Text

```typescript
const text = this.add.text(x, y, 'Hello World!', {
  fontSize: '32px',
  fontFamily: 'Arial',
  color: '#ffffff',
  backgroundColor: '#000000',
  padding: { x: 10, y: 5 },
  align: 'center',
  stroke: '#000000',
  strokeThickness: 2,
});

// Update text
text.setText('New text');

// Set origin
text.setOrigin(0.5);
```

### Animations & Tweens

```typescript
// Create tween
this.tweens.add({
  targets: sprite,
  x: 500,
  y: 300,
  alpha: 0,
  scale: 2,
  rotation: Math.PI * 2,
  duration: 1000,
  ease: 'Power2',
  yoyo: true,
  repeat: 2,
  onComplete: () => {
    sprite.destroy();
  }
});

// Create animation from spritesheet
this.anims.create({
  key: 'walk',
  frames: this.anims.generateFrameNumbers('player', { start: 0, end: 3 }),
  frameRate: 10,
  repeat: -1
});

// Play animation
sprite.play('walk');
```

### Camera Effects

```typescript
// Shake camera
this.cameras.main.shake(duration, intensity);

// Flash
this.cameras.main.flash(duration, red, green, blue);

// Fade
this.cameras.main.fadeOut(duration);
this.cameras.main.fadeIn(duration);

// Follow sprite
this.cameras.main.startFollow(player);
```

### Timers

```typescript
// Delayed call
this.time.delayedCall(1000, () => {
  console.log('Executed after 1 second');
});

// Repeating timer
this.time.addEvent({
  delay: 1000,
  callback: () => {
    console.log('Every second');
  },
  loop: true
});
```

### Input (Optional for Testing)

```typescript
// Keyboard
const cursors = this.input.keyboard.createCursorKeys();

update() {
  if (cursors.left.isDown) {
    player.setVelocityX(-200);
  }
}

// Mouse/Touch
this.input.on('pointerdown', (pointer: Phaser.Input.Pointer) => {
  console.log(`Clicked at ${pointer.x}, ${pointer.y}`);
});
```

---

## Common Patterns

### Pattern 1: Spawning Objects from Chat

**Backend:**

```python
import uuid

def spawn_enemy(self, message):
    """!spawn command - Create enemy at random location"""
    enemy_id = str(uuid.uuid4())

    self.emit_state({
        'enemy_added': {
            'id': enemy_id,
            'x': random.randint(100, 1820),
            'y': 0,
            'type': 'basic',
            'username': message.author.name
        }
    })
```

**Frontend:**

```typescript
onStateUpdate(state: GameState) {
    if (state.enemy_added) {
        this.spawnEnemy(state.enemy_added);
    }
}

private spawnEnemy(data: any) {
    const enemy = this.physics.add.sprite(data.x, data.y, 'enemy');
    enemy.setData('id', data.id);
    enemy.setGravityY(300);

    // Add username label
    const label = this.add.text(data.x, data.y - 30, data.username, {
        fontSize: '16px',
        color: '#ffffff',
    }).setOrigin(0.5);

    // Store reference for cleanup
    this.enemies.set(data.id, { sprite: enemy, label: label });
}
```

### Pattern 2: Leaderboard / Scoring

**Backend:**

```python
def __init__(self, socketio=None):
    super().__init__(socketio)
    self.scores = {}  # username -> score

def hit_target(self, message):
    """Award points when player hits target"""
    username = message.author.name
    self.scores[username] = self.scores.get(username, 0) + 10

    # Sort leaderboard
    sorted_scores = sorted(
        self.scores.items(),
        key=lambda x: x[1],
        reverse=True
    )[:10]  # Top 10

    self.emit_state({
        'leaderboard': [
            {'username': u, 'score': s}
            for u, s in sorted_scores
        ]
    })
```

**Frontend:**

```typescript
private leaderboardText: Phaser.GameObjects.Text[] = [];

onStateUpdate(state: GameState) {
    if (state.leaderboard) {
        this.updateLeaderboard(state.leaderboard);
    }
}

private updateLeaderboard(entries: Array<{username: string, score: number}>) {
    // Clear old
    this.leaderboardText.forEach(t => t.destroy());
    this.leaderboardText = [];

    // Render new leaderboard
    entries.forEach((entry, index) => {
        const text = this.add.text(
            20,
            100 + (index * 30),
            `${index + 1}. ${entry.username}: ${entry.score}`,
            { fontSize: '20px', color: '#ffffff' }
        );
        this.leaderboardText.push(text);
    });
}
```

### Pattern 3: Power-ups / Temporary Effects

**Backend:**

```python
def boost_speed(self, message):
    """!boost command - Temporary speed increase"""
    self.emit_event('speed_boost', {
        'username': message.author.name,
        'duration': 5000,  # 5 seconds
        'multiplier': 2.0
    })
```

**Frontend:**

```typescript
private speedMultiplier: number = 1.0;

private handleEvent(event: string, state: any) {
    if (event === 'speed_boost') {
        this.applySpeedBoost(state.duration, state.multiplier);
    }
}

private applySpeedBoost(duration: number, multiplier: number) {
    this.speedMultiplier = multiplier;

    // Visual feedback
    this.player.setTint(0xffff00);

    // Revert after duration
    this.time.delayedCall(duration, () => {
        this.speedMultiplier = 1.0;
        this.player.clearTint();
    });
}
```

### Pattern 4: Clearing/Resetting Game State

**Backend:**

```python
def clear_all(self, message):
    """!clear command - Remove all objects"""
    self.emit_event('clear_all', {
        'username': message.author.name
    })
```

**Frontend:**

```typescript
private enemies = new Map<string, any>();

private handleEvent(event: string, state: any) {
    if (event === 'clear_all') {
        this.clearAll();
    }
}

private clearAll() {
    // Destroy all enemies
    this.enemies.forEach(enemy => {
        enemy.sprite.destroy();
        enemy.label.destroy();
    });
    this.enemies.clear();

    // Visual effect
    this.cameras.main.flash(500);
}
```

---

## Best Practices

### Backend Best Practices

| Practice | Why | Example |
|----------|-----|---------|
| ✅ **Use `emit_event()` for effects** | Prevents events from replaying on reconnect | `emit_event('jump')` |
| ✅ **Use `emit_state()` for persistence** | New clients receive current state | `emit_state({'score': 100})` |
| ✅ **Return fresh state in `get_initial_state()`** | Avoid stale events | `return {'score': 0}` NOT `return self.game_state` |
| ✅ **Add logging** | Easier debugging | `logger.info(f"{username} jumped")` |
| ✅ **Validate input** | Prevent crashes | Check `message.author.name` exists |

### Frontend Best Practices

| Practice | Why | Example |
|----------|-----|---------|
| ✅ **Destroy unused objects** | Prevent memory leaks | `sprite.destroy()` |
| ✅ **Use object pools for frequent spawns** | Better performance | Reuse sprites instead of creating new |
| ✅ **Check state properties exist** | Avoid undefined errors | `if (state.score !== undefined)` |
| ✅ **Handle events in switch statement** | Organized code | `switch (state.event)` |
| ✅ **Use `setDepth()` for layering** | Control z-index | Background at depth 0, UI at depth 100 |

### Performance Tips

```typescript
// ✅ Good: Object pooling
private createEnemyPool() {
    this.enemyPool = this.physics.add.group({
        defaultKey: 'enemy',
        maxSize: 50,
    });
}

// ❌ Bad: Creating/destroying frequently
private spawnEnemy() {
    const enemy = this.add.sprite(x, y, 'enemy'); // Creates new object
    // Later...
    enemy.destroy(); // Destroys and garbage collects
}

// ✅ Good: Reuse from pool
private spawnEnemy() {
    const enemy = this.enemyPool.get(x, y);
    enemy.setActive(true).setVisible(true);
}
```

---

## Troubleshooting

<details>
<summary><strong>❌ Game not discovered by backend</strong></summary>

**Symptoms:**
- Flask console doesn't show your game in "Found X games"

**Checklist:**
- [ ] `game_manifest.json` is valid JSON (use [JSONLint](https://jsonlint.com/))
- [ ] `backend.entry_point` matches your class name exactly (`"game:MyGame"`)
- [ ] Game is in `backend/games/` directory
- [ ] Backend path calculation is correct (should be `'../..'` from `backend/games/my_game/backend/game.py`)

**Test:**
```bash
python -m json.tool backend/games/my_game/game_manifest.json
```
</details>

<details>
<summary><strong>❌ ImportError: No module named 'base_game'</strong></summary>

**Cause:** Backend path calculation incorrect

**Fix:** In `backend/games/my_game/backend/game.py`:

```python
# Correct path calculation
backend_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.insert(0, backend_path)
```

**Verify:**
```python
print(f"Backend path: {backend_path}")
# Should print: .../stream tools/chat-games/backend
```
</details>

<details>
<summary><strong>❌ Frontend shows "Component not found: MyGame"</strong></summary>

**Checklist:**
- [ ] Added import to `frontend/src/games/registry.ts`
- [ ] Added to registry Map: `['MyGame', MyGame]`
- [ ] Component name in manifest matches registry key exactly
- [ ] Rebuilt frontend: `npm run build`

**Test:**
```typescript
// In browser console
GameRegistry.getAll()
// Should show MyGame in the list
```
</details>

<details>
<summary><strong>❌ Commands not working in Twitch chat</strong></summary>

**Checklist:**
- [ ] Commands registered in `get_commands()` method
- [ ] Using correct prefix (`!` by default)
- [ ] Twitch bot is connected (check Flask console)
- [ ] Command name matches exactly (case-sensitive)

**Debug:**
```python
def get_commands(self):
    commands = {
        'jump': self.player_jump
    }
    logger.info(f"Registered commands: {list(commands.keys())}")
    return commands
```
</details>

<details>
<summary><strong>❌ Phaser canvas not rendering</strong></summary>

**Symptoms:**
- Blank screen or missing game elements

**Checklist:**
- [ ] `create()` method called (check console for "✅ Scene created")
- [ ] Objects positioned within canvas bounds (0-1920, 0-1080)
- [ ] Camera visible (not faded out or following off-screen object)
- [ ] Check browser console for Phaser errors

**Debug:**
```typescript
create() {
    console.log('Camera:', this.cameras.main.width, this.cameras.main.height);
    console.log('World bounds:', this.physics.world.bounds);

    // Draw test rectangle
    this.add.rectangle(100, 100, 200, 200, 0xff0000);
}
```
</details>

<details>
<summary><strong>❌ State updates not reaching frontend</strong></summary>

**Symptoms:**
- Backend logs show `emit_state()` called
- Frontend `onStateUpdate()` not receiving data

**Checklist:**
- [ ] Flask-SocketIO running (not standard Flask dev server)
- [ ] Browser console shows "✅ Connected to server"
- [ ] Joined room: `socket.emit('join', {room: 'main_room'})`
- [ ] Check browser Network tab for WebSocket connection

**Debug Backend:**
```python
def player_jump(self, message):
    update = {'event': 'jump'}
    logger.info(f"Emitting update: {update}")
    self.emit_state(update)
```

**Debug Frontend:**
```typescript
onStateUpdate(state: GameState) {
    console.log('🔄 State update received:', state);
    // Rest of logic...
}
```
</details>

---

## Resources

### Official Documentation

| Resource | URL | Use For |
|----------|-----|---------|
| **Phaser 3 API Docs** | [photonstorm.github.io/phaser3-docs](https://photonstorm.github.io/phaser3-docs/) | Method reference |
| **Phaser 3 Examples** | [phaser.io/examples](https://phaser.io/examples) | Code snippets |
| **Phaser 3 Tutorials** | [phaser.io/tutorials](https://phaser.io/tutorials) | Learning basics |
| **Flask-SocketIO** | [flask-socketio.readthedocs.io](https://flask-socketio.readthedocs.io/) | WebSocket server |
| **TwitchIO** | [twitchio.dev](https://twitchio.dev/) | Twitch bot framework |

### Platform Documentation

- 📖 [README.md](../README.md) - Platform overview and architecture
- 📖 [QUICKSTART.md](QUICKSTART.md) - Installation and setup guide
- 📖 [STATE_MANAGEMENT.md](../STATE_MANAGEMENT.md) - **Essential reading for state handling**
- 📖 [FILE_LOCATIONS.md](FILE_LOCATIONS.md) - Project structure reference
- 📖 [OBS_SETUP.md](OBS_SETUP.md) - Streaming configuration

### Example Games

| Game | Location | Features Demonstrated |
|------|----------|----------------------|
| **Chat Minigames** | `backend/games/chat_minigames/` | Minigame collection, scene switching |
| **Shape Smash** | `backend/games/chat_minigames/minigames/shape_smash.py` | Physics, spawning, leaderboard |

---

**Happy game development!** 🎮✨

> **Questions?** Open an issue on GitHub or check existing games for reference examples.
