# State Management Guide

## Overview

This document explains the state management architecture used in the Twitch Chat Games platform, including critical distinctions between **persistent state** and **transient events**.

---

## Core Principles

### 1. Server-Authoritative Architecture

**The backend is the source of truth for all game state.**

- Backend handles all game logic and state mutations
- Frontend is purely presentational - it renders what the backend tells it
- Users interact via Twitch chat → backend processes → frontend displays result

### 2. State vs Events

Understanding the difference between **state** and **events** is critical:

| Type | Description | Lifetime | Example |
|------|-------------|----------|---------|
| **Persistent State** | Data that represents the current condition of the game | Persists until explicitly changed | `shapes: [...]`, `score: 100` |
| **Transient Events** | One-time triggers for actions or effects | Should trigger once, then be cleared | `event: 'boost'`, `event: 'explode'` |

**Critical Rule:** Events should NEVER persist across multiple state updates. They must be cleared after being processed.

---

## State Flow Architecture

### Complete Data Flow

```
Twitch Chat (!square)
    ↓
TwitchIO Bot (twitch_bot.py)
    ↓
Game Backend (shape_smash.py)
    ├─ Mutates internal state
    └─ Calls emit_state({...})
    ↓
BaseGame.emit_state()
    └─ Merges into self.game_state (accumulated state)
    ↓
Flask-SocketIO
    └─ Broadcasts 'game_state_update' event
    ↓
Frontend GameManager (gameManager.ts)
    ├─ Receives update (just the changes)
    └─ Passes update to game component
    ↓
ChatMinigames (ChatMinigames.ts)
    └─ Routes update to active scene
    ↓
Phaser Scene (ShapeSmashScene.ts)
    └─ Renders visual changes
```

### Key Points

1. **Backend sends incremental updates**, not full state snapshots
2. **GameManager passes updates as-is** (does NOT merge before passing)
3. **Scenes process updates and clear transient events**
4. **Reconnection sends fresh initial state** (not accumulated state)

---

## Critical Bug Patterns

### ❌ Bug #1: Merging State Before Passing to Game Component

**Problem:**
```typescript
// WRONG - gameManager.ts
this.gameState = { ...this.gameState, ...update };
this.currentGame.update(this.gameState);  // ❌ Passing merged state
```

**Why it's wrong:**
- If backend sends `{event: 'boost'}` followed by `{shape_added: {...}}`, the second update becomes:
  ```typescript
  {
    event: 'boost',      // ❌ Still here from previous update!
    shape_added: {...}
  }
  ```
- Events trigger multiple times

**Solution:**
```typescript
// CORRECT - gameManager.ts
this.gameState = { ...this.gameState, ...update };
this.currentGame.update(update);  // ✅ Pass only the update
```

---

### ❌ Bug #2: Sending Accumulated State on Reconnection

**Problem:**
```python
# WRONG - app.py
@socketio.on('connect')
def handle_connect():
    emit('game_loaded', {
        'initialState': game_manager.active_game.game_state  # ❌ Accumulated state
    })
```

**Why it's wrong:**
- `game_state` accumulates ALL state updates since game start
- May contain old events like `{event: 'boost'}` from 10 minutes ago
- Reconnecting clients see stale events trigger

**Solution:**
```python
# CORRECT - app.py
@socketio.on('connect')
def handle_connect():
    emit('game_loaded', {
        'initialState': game_manager.active_game.get_initial_state()  # ✅ Fresh state
    })
```

---

### ❌ Bug #3: Shape Sync Deleting Newly Added Shapes

**Problem:**
```typescript
// WRONG - ShapeSmashScene.ts
onStateUpdate(state) {
  if (state.shape_added) {
    this.addShape(state.shape_added);
  }
  if (state.shapes) {
    this.syncShapes(state.shapes);  // ❌ Syncs immediately after adding
  }
}
```

**Why it's wrong:**
- Backend sends: `{shape_added: {...}, shapes: []}`
- Frontend adds shape, then immediately syncs to empty array
- Shape disappears

**Solution:**
```typescript
// CORRECT - ShapeSmashScene.ts
onStateUpdate(state) {
  if (state.shape_added) {
    this.addShape(state.shape_added);
  }
  // Only sync when NOT doing an incremental add
  if (state.shapes && !state.shape_added) {
    this.syncShapes(state.shapes);
  }
}
```

---

## Best Practices

### Backend: Emitting State Updates

#### ✅ DO: Emit minimal updates
```python
# Good - only send what changed
def spawn_square(self, message):
    shape = self._create_shape('square', message.chatter.name)
    self.parent.emit_state({
        'shape_added': shape,
        'shape_count': len(self.shapes)
    })
```

#### ❌ DON'T: Send entire state every time
```python
# Bad - sends everything
def spawn_square(self, message):
    shape = self._create_shape('square', message.chatter.name)
    self.parent.emit_state({
        'shapes': self.shapes,        # ❌ Unnecessary full array
        'shape_added': shape,
        'shape_count': len(self.shapes),
        'active_minigame': 'shape_smash',  # ❌ Unchanged data
    })
```

---

### Backend: Transient Events

#### ✅ DO: Use transient events for one-time actions
```python
# Good - backend sends event
def boost_shapes(self, message):
    self.parent.emit_state({
        'event': 'boost',
        'username': message.chatter.name
    })
```

#### ❌ DON'T: Store events in persistent state
```python
# Bad - event persists in game state
def boost_shapes(self, message):
    self.game_state['event'] = 'boost'  # ❌ Will persist
    self.emit_state(self.game_state)
```

**Future improvement:** Use a dedicated `emit_event()` helper that doesn't store in `game_state`.

---

### Frontend: Processing Events

#### ✅ DO: Clear transient events after processing
```typescript
// Good - ChatMinigames.ts
update(state: GameState): void {
  // Merge for tracking
  this.currentState = { ...this.currentState, ...state };

  // Handle scene switching
  if (state.event === 'switch_scene' && state.active_scene) {
    this.switchScene(state.active_scene as string);
    return;
  }

  // Route to scene
  const scene = this.getMainScene();
  if (scene && 'onStateUpdate' in scene) {
    (scene as any).onStateUpdate(state);
  }

  // Clear transient event from persistent state
  if (state.event) {
    delete this.currentState.event;  // ✅ Prevents re-triggering
  }
}
```

#### ❌ DON'T: Let events persist in component state
```typescript
// Bad - events stick around
update(state: GameState): void {
  this.currentState = { ...this.currentState, ...state };  // ❌ Event persists
  const scene = this.getMainScene();
  if (scene && 'onStateUpdate' in scene) {
    scene.onStateUpdate(state);
  }
  // Missing event cleanup!
}
```

---

### Frontend: State Merging

#### ✅ DO: Track merged state locally, pass updates as-is
```typescript
// Good - gameManager.ts
updateState(update: Partial<GameState>) {
  // Merge for local tracking
  this.gameState = { ...this.gameState, ...update };

  // Pass update as-is to component
  this.currentGame.update(update);  // ✅
}
```

#### ❌ DON'T: Pass merged state to components
```typescript
// Bad - passes accumulated state
updateState(update: Partial<GameState>) {
  this.gameState = { ...this.gameState, ...update };
  this.currentGame.update(this.gameState);  // ❌ Events persist
}
```

---

## Testing State Management

### Manual Testing Checklist

1. **Event Single-Trigger Test:**
   - Send `!boost` in chat
   - Send `!square` in chat
   - ✅ Square should NOT boost
   - ✅ Only one boost effect should occur

2. **Reconnection Test:**
   - Send `!boost` in chat
   - Refresh browser (reconnect)
   - ✅ Boost should NOT trigger on reconnect

3. **Incremental Updates Test:**
   - Send `!square` multiple times
   - ✅ Each shape should persist
   - ✅ Shapes should NOT disappear after spawning

### Console Debugging

Enable detailed logging to trace state flow:

**Backend:**
```python
logger.info(f"Emitting state: {list(state.keys())}")
```

**Frontend:**
```typescript
console.log('📥 ChatMinigames.update received state:', Object.keys(state));
if (state.event) {
  console.log('  ⚠️ State contains event:', state.event);
}
```

Look for:
- Events appearing in multiple consecutive updates
- Merged state growing unexpectedly
- State updates containing unchanged data

---

## Architecture Diagrams

### State Storage Layers

```
┌─────────────────────────────────────┐
│  Backend (Python)                   │
│  ┌───────────────────────────────┐  │
│  │ BaseGame.game_state           │  │  ← Accumulated state (persistent)
│  │ {shapes: [...], score: 100}   │  │
│  └───────────────────────────────┘  │
│                ↓                     │
│  ┌───────────────────────────────┐  │
│  │ emit_state({event: 'boost'})  │  │  ← Emits update (may contain events)
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  Frontend GameManager               │
│  ┌───────────────────────────────┐  │
│  │ this.gameState                │  │  ← Tracks merged state locally
│  │ (for debugging/logging only)  │  │
│  └───────────────────────────────┘  │
│                ↓                     │
│       Passes update (not merged)    │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  Game Component                     │
│  ┌───────────────────────────────┐  │
│  │ update(state)                 │  │  ← Receives fresh update
│  │   - Process events            │  │
│  │   - Merge if needed           │  │
│  │   - Clear transient events    │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

---

## Future Improvements

### Planned Enhancements

1. **Backend: Add `emit_event()` Helper**
   ```python
   # Proposed API
   class BaseGame:
       def emit_event(self, event_name: str, data: dict = None):
           """Emit transient event that won't be stored in game_state"""
           event_data = {'event': event_name}
           if data:
               event_data.update(data)
           self.socketio.emit('game_state_update', event_data, room='main_room')
   ```

2. **Backend: Separate Persistent and Transient State**
   ```python
   class BaseGame:
       def __init__(self):
           self.persistent_state = {}  # Stored and sent on reconnect
           self.transient_state = {}   # Never stored, immediate only
   ```

3. **Frontend: Type-Safe Event Handling**
   ```typescript
   interface GameEvent {
     type: 'boost' | 'explode' | 'clear';
     data?: any;
   }

   interface GameState {
     shapes: Shape[];
     score: number;
     event?: GameEvent;  // Clearly marked as optional/transient
   }
   ```

---

## Common Questions

### Q: Why not just send full state snapshots every time?

**A:** While simpler, it would:
- Waste bandwidth (sending unchanged data)
- Make debugging harder (can't see what actually changed)
- Increase CPU usage (parsing larger payloads)
- Make event handling ambiguous

### Q: Why track `gameState` in GameManager if we don't pass it?

**A:** The merged state is useful for:
- Debugging (seeing accumulated state)
- Logging (tracking what's changed over time)
- Future features (state snapshots, time travel debugging)

### Q: Should minigames store their own state?

**A:** Yes! Each minigame should track its own state (like `self.shapes`) and emit updates. The parent game orchestrator should NOT try to track minigame state - let each minigame be responsible for its own data.

---

## Summary

**Key Takeaways:**
1. ✅ Backend emits incremental updates, not full snapshots
2. ✅ Events are transient - clear them after processing
3. ✅ GameManager passes updates as-is, doesn't merge before passing
4. ✅ Reconnection sends fresh initial state via `get_initial_state()`
5. ✅ Scenes guard against sync when doing incremental updates

**When in doubt:**
- Add console logging to trace state flow
- Check if events are persisting (look for duplicate logs)
- Verify state is minimal (only changed data)
- Test reconnection behavior

---

**Last Updated:** 2025-11-15
**Related Files:**
- [gameManager.ts](frontend/src/gameManager.ts#L87)
- [ChatMinigames.ts](frontend/src/games/ChatMinigames.ts#L94-L96)
- [app.py](backend/app.py#L122)
- [base_game.py](backend/base_game.py)
