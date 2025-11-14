# Creating a New Phaser 3 Game

Template and guide for creating new games using Phaser 3.

## Quick Start

1. **Create game folder structure**
2. **Create manifest**
3. **Create Python backend**
4. **Create Phaser TypeScript frontend**
5. **Register in registry**
6. **Test!**

## Detailed Steps

### 1. Create Folder Structure

```bash
mkdir -p games/builtin/my_game/backend
mkdir -p games/builtin/my_game/frontend
```

### 2. Create Manifest (`game_manifest.json`)

```json
{
  "id": "my_game",
  "version": "1.0.0",
  "name": "My Awesome Game",
  "description": "Description of what the game does",
  "author": "your_name",
  "license": "MIT",

  "backend": {
    "entry_point": "game:MyGame"
  },

  "frontend": {
    "entry_point": "frontend/MyGame.ts",
    "component": "MyGame",
    "assets": []
  },

  "config": {
    "canvas_width": 1920,
    "canvas_height": 1080
  },

  "commands": [
    {"name": "start", "description": "Start the game"},
    {"name": "jump", "description": "Make player jump"}
  ]
}
```

### 3. Create Backend (`backend/game.py`)

```python
import sys
from pathlib import Path
import random

# Add backend to path
backend_path = Path(__file__).resolve().parent.parent.parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))

from base_game import BaseGame

class MyGame(BaseGame):
    def __init__(self, socketio=None):
        super().__init__(socketio)
        self.score = 0

    def get_title(self) -> str:
        return "My Awesome Game"

    def get_game_id(self) -> str:
        return "my_game"

    def get_commands(self) -> dict:
        return {
            'start': self.start_game,
            'jump': self.player_jump,
        }

    def get_initial_state(self) -> dict:
        return {
            'score': 0,
            'player': {
                'x': 100,
                'y': 100
            }
        }

    def get_frontend_config(self) -> dict:
        return {
            'component': 'MyGame',
            'canvas_width': 1920,
            'canvas_height': 1080
        }

    # Command handlers
    def start_game(self, message):
        """Handle !start command"""
        self.update_state({
            'event': 'game_start',
            'username': message.chatter.name
        })

    def player_jump(self, message):
        """Handle !jump command"""
        self.emit_state({
            'event': 'player_jump',
            'username': message.chatter.name
        })
```

### 4. Create Frontend (`frontend/src/games/MyGame.ts`)

```typescript
import Phaser from 'phaser';
import type { GameConfig } from '../types';
import { PhaserGameBase } from './PhaserGameBase';

interface MyGameState {
  score?: number;
  player?: { x: number; y: number };
  event?: string;
  username?: string;
}

class MyGameScene extends Phaser.Scene {
  private player!: Phaser.GameObjects.Sprite;
  private scoreText!: Phaser.GameObjects.Text;
  private score: number = 0;

  constructor() {
    super({ key: 'MyGameScene' });
  }

  preload() {
    // Load assets here
    // this.load.image('player', 'path/to/player.png');
  }

  create() {
    const width = this.cameras.main.width;
    const height = this.cameras.main.height;

    // Create player (using rectangle for now)
    this.player = this.add.rectangle(100, 100, 50, 50, 0x00ff00) as any;
    this.physics.add.existing(this.player);

    // Create score text
    this.scoreText = this.add.text(20, 20, 'Score: 0', {
      fontSize: '32px',
      color: '#ffffff',
    });

    console.log('✅ My Game scene created');
  }

  /**
   * Called when backend sends state update
   */
  onStateUpdate(state: MyGameState) {
    // Update score
    if (state.score !== undefined) {
      this.score = state.score;
      this.scoreText.setText(`Score: ${this.score}`);
    }

    // Update player position
    if (state.player) {
      this.player.setPosition(state.player.x, state.player.y);
    }

    // Handle events
    if (state.event) {
      this.handleEvent(state.event, state);
    }
  }

  private handleEvent(event: string, state: MyGameState) {
    switch (event) {
      case 'game_start':
        console.log(`${state.username} started the game!`);
        // Reset game state
        break;

      case 'player_jump':
        // Make player jump
        const body = this.player.body as Phaser.Physics.Arcade.Body;
        if (body) {
          body.setVelocityY(-500);
        }
        break;
    }
  }

  update() {
    // Game loop logic here
  }
}

export class MyGame extends PhaserGameBase {
  private mainScene: MyGameScene | null = null;

  protected getScenes(): (typeof Phaser.Scene)[] {
    return [MyGameScene];
  }

  protected getMainScene(): Phaser.Scene | null {
    if (!this.mainScene && this.game) {
      this.mainScene = this.game.scene.getScene('MyGameScene') as MyGameScene;
    }
    return this.mainScene;
  }
}
```

### 5. Register in Registry

Edit `frontend/src/games/registry.ts`:

```typescript
import { MyGame } from './MyGame';

export class GameRegistry {
  private static games = new Map<string, GameComponentConstructor>([
    ['ShapeSmash', ShapeSmash],
    ['MyGame', MyGame],  // Add this line
  ]);
  // ...
}
```

### 6. Test Your Game

```bash
# Build frontend
cd frontend
npm run build

# Start backend
cd ../backend
python app.py
```

Open `http://localhost:5000` and test your commands in Twitch chat!

## Phaser 3 Tips

### Physics

```typescript
// Enable physics on a sprite
this.physics.add.existing(sprite);

// Set velocity
const body = sprite.body as Phaser.Physics.Arcade.Body;
body.setVelocity(100, -200);

// Set gravity
body.setGravityY(300);

// Collisions
this.physics.add.collider(player, ground);
```

### Sprites & Graphics

```typescript
// Load image
preload() {
  this.load.image('key', 'path/to/image.png');
}

// Create sprite
const sprite = this.add.sprite(x, y, 'key');

// Create shape
const circle = this.add.circle(x, y, radius, color);
const rect = this.add.rectangle(x, y, width, height, color);
```

### Text

```typescript
const text = this.add.text(x, y, 'Hello!', {
  fontSize: '32px',
  color: '#ffffff',
  fontStyle: 'bold',
});
```

### Animations

```typescript
// Tween
this.tweens.add({
  targets: sprite,
  x: 500,
  duration: 1000,
  ease: 'Power2',
});
```

### Input

```typescript
// Keyboard
const cursors = this.input.keyboard.createCursorKeys();

// Mouse
this.input.on('pointerdown', (pointer) => {
  console.log(pointer.x, pointer.y);
});
```

## Best Practices

1. **Keep state in backend**: Frontend just renders what backend tells it
2. **Use events for actions**: Don't update state directly from events
3. **Keep scenes focused**: One scene per game mode
4. **Clean up resources**: Destroy sprites/sounds when done
5. **Test commands individually**: Make sure each command works

## Common Patterns

### Spawning Objects from Commands

```python
# Backend
def spawn_enemy(self, message):
    enemy_id = str(uuid.uuid4())
    self.emit_state({
        'event': 'enemy_spawn',
        'enemy': {
            'id': enemy_id,
            'x': random.randint(100, 1820),
            'y': 0,
            'type': 'basic'
        }
    })
```

```typescript
// Frontend
private handleEvent(event: string, state: any) {
  if (event === 'enemy_spawn') {
    this.spawnEnemy(state.enemy);
  }
}
```

### Scoreboard

```python
# Backend
self.scores = {}

def add_score(self, message):
    username = message.chatter.name
    self.scores[username] = self.scores.get(username, 0) + 1
    self.emit_state({
        'scores': self.scores
    })
```

### Power-ups / Effects

```python
def activate_powerup(self, message):
    self.emit_state({
        'event': 'powerup',
        'type': 'speed_boost',
        'duration': 5000  # ms
    })
```

## Resources

- [Phaser 3 API Docs](https://photonstorm.github.io/phaser3-docs/)
- [Phaser 3 Examples](https://phaser.io/examples)
- [Phaser 3 Tutorial](https://phaser.io/tutorials/making-your-first-phaser-3-game)

Happy game making! 🎮
