# State Management Guide

> **Last Updated:** 2025-01-16
> **Architecture:** Server-authoritative with incremental updates
> **Critical Reading:** Essential for game developers

Comprehensive guide to state management architecture in the Twitch Chat Games platform. Understanding the distinction between **persistent state** and **transient events** is critical for preventing bugs and building responsive games.

---

## Table of Contents

- [Overview](#overview)
- [Core Principles](#core-principles)
- [State Flow Architecture](#state-flow-architecture)
- [Critical Bug Patterns](#critical-bug-patterns)
- [Best Practices](#best-practices)
  - [Backend: State Updates](#backend-emitting-state-updates)
  - [Backend: Transient Events](#backend-transient-events)
  - [Frontend: Processing Events](#frontend-processing-events)
  - [Frontend: State Merging](#frontend-state-merging)
- [Testing State Management](#testing-state-management)
- [Architecture Diagrams](#architecture-diagrams)
- [Common Questions](#common-questions)
- [Summary](#summary)

---

## Overview

This document explains the state management architecture used in the Twitch Chat Games platform, including critical distinctions between **persistent state** and **transient events**.

### Why State Management Matters

**Problem scenario:**
- User sends `!boost` command
- All shapes fly upward (correct)
- New user joins and reconnects
- Shapes boost again (❌ WRONG - stale event)

**This guide prevents these bugs** by establishing clear patterns for state vs events.

---

## Core Principles

### 1. Server-Authoritative Architecture

**The backend is the source of truth for all game state.**

```
┌─────────────────┐
│  Twitch Chat    │ → Commands
└────────┬────────┘
         ↓
┌─────────────────┐
│  Backend        │ → Game Logic (Source of Truth)
└────────┬────────┘
         ↓
┌─────────────────┐
│  Frontend       │ → Presentation (Renders Backend State)
└─────────────────┘
```

**Key points:**
- Backend handles all game logic and state mutations
- Frontend is purely presentational - it renders what the backend tells it
- Users interact via Twitch chat → backend processes → frontend displays result

### 2. State vs Events

Understanding the difference between **state** and **events** is critical:

| Type | Description | Lifetime | Example | Method |
|------|-------------|----------|---------|--------|
| **Persistent State** | Data that represents the current condition of the game | Persists until explicitly changed | `shapes: [...]`, `score: 100` | `emit_state()` |
| **Transient Events** | One-time triggers for actions or effects | Should trigger once, then be cleared | `event: 'boost'`, `event: 'explode'` | `emit_event()` |

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
    └─ Calls emit_state({...}) or emit_event(...)
    ↓
BaseGame Methods
    ├─ emit_state() → Merges into self.game_state (accumulated)
    └─ emit_event() → Does NOT merge (transient)
    ↓
Flask-SocketIO
    └─ Broadcasts 'game_state_update' event
    ↓
Frontend GameManager (gameManager.ts)
    ├─ Receives update (just the changes)
    ├─ Merges into local gameState (for tracking)
    └─ Passes update as-is to game component
    ↓
ChatMinigames (ChatMinigames.ts)
    ├─ Routes update to active scene
    └─ Clears transient events from currentState
    ↓
Phaser Scene (ShapeSmashScene.ts)
    └─ Renders visual changes
```

### Key Points

1. **Backend sends incremental updates**, not full state snapshots
2. **GameManager passes updates as-is** (does NOT merge before passing)
3. **Scenes process updates and clear transient events**
4. **Reconnection sends fresh initial state** (not accumulated state)

### Backend State Methods

The `BaseGame` class provides two methods for emitting updates:

| Method | Purpose | Persists? | Use Case |
|--------|---------|-----------|----------|
| `emit_state(update)` | Send persistent state changes | ✅ Yes | Score updates, positions, flags |
| `emit_event(name, data)` | Send transient events | ❌ No | Visual effects, sounds, one-time actions |

📖 **See [base_game.py](../backend/base_game.py#L88-L161) for implementation details**

<!--
📊 **Interactive State Flow Diagram** (Placeholder)
Add interactive visualization showing state flow from Twitch chat to frontend rendering
-->

---

## Critical Bug Patterns

### ❌ Bug #1: Merging State Before Passing to Game Component

**Problem:**
```typescript
// WRONG - gameManager.ts
updateState(update: Partial<GameState>) {
  this.gameState = { ...this.gameState, ...update };
  this.currentGame.update(this.gameState);  // ❌ Passing merged state
}
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
- Shapes get boosted when they shouldn't

**Symptoms:**
- `!boost` command affects shapes spawned afterwards
- Visual effects repeat unexpectedly
- State grows with stale data

**Solution:**
```typescript
// CORRECT - gameManager.ts
updateState(update: Partial<GameState>) {
  // Merge for local tracking/debugging
  this.gameState = { ...this.gameState, ...update };

  // Pass only the update, NOT merged state
  this.currentGame.update(update);  // ✅ Pass only what changed
}
```

📖 **Implementation:** [gameManager.ts](../frontend/src/gameManager.ts#L76-L103)

---

### ❌ Bug #2: Sending Accumulated State on Reconnection

**Problem:**
```python
# WRONG - app.py or BaseGame
def get_initial_state(self):
    return self.game_state  # ❌ Accumulated state with old events
```

**Why it's wrong:**
- `game_state` accumulates ALL state updates since game start
- May contain old events like `{event: 'boost'}` from 10 minutes ago
- Reconnecting clients see stale events trigger

**Example timeline:**
```
10:00 AM - User sends !boost → {event: 'boost'} emitted
10:05 AM - New user joins
          → Receives initialState containing {event: 'boost'}
          → Boost triggers for new user (WRONG!)
```

**Symptoms:**
- Refreshing browser triggers old visual effects
- New viewers see effects that already happened
- Game state feels "haunted" by past events

**Solution:**
```python
# CORRECT - BaseGame
def get_initial_state(self) -> Dict[str, Any]:
    """
    Return FRESH initial state, NOT self.game_state.

    Why? self.game_state accumulates ALL updates including transient events.
    Returning it would cause old events to replay for reconnecting clients.
    """
    return {
        'score': 0,
        'shapes': [],
        'game_active': True
        # ✅ No events - this is clean initial state
    }
```

📖 **Implementation:** [base_game.py](../backend/base_game.py#L65-L83)

---

### ❌ Bug #3: Shape Sync Deleting Newly Added Shapes

**Problem:**
```typescript
// WRONG - ShapeSmashScene.ts
onStateUpdate(state: GameState) {
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
  - `shape_added` → Add new shape to frontend
  - `shapes: []` → Sync to empty array (backend uses incremental adds, not full state)
- Frontend adds shape, then immediately syncs to empty array
- Shape disappears

**Symptoms:**
- Shapes spawn then immediately vanish
- Shape count doesn't match what backend reports
- Intermittent "flashing" shapes

**Solution:**
```typescript
// CORRECT - ShapeSmashScene.ts
onStateUpdate(state: GameState) {
  if (state.shape_added) {
    this.addShape(state.shape_added);
  }

  // Only sync when NOT doing an incremental add
  if (state.shapes !== undefined && !state.shape_added) {
    this.syncShapes(state.shapes);
  }
}
```

**Alternative:** Don't send `shapes` array at all if using incremental updates.

---

## Best Practices

### Backend: Emitting State Updates

#### ✅ DO: Emit minimal updates

```python
# Good - only send what changed
def spawn_square(self, message):
    shape = self._create_shape('square', message.author.name)
    self.shapes.append(shape)

    # Emit only the new shape
    self.emit_state({
        'shape_added': shape,
        'shape_count': len(self.shapes)
    })
```

**Benefits:**
- Smaller payloads (faster transmission)
- Easier to debug (see exactly what changed)
- Clear intent (you know what triggered the update)

#### ❌ DON'T: Send entire state every time

```python
# Bad - sends everything
def spawn_square(self, message):
    shape = self._create_shape('square', message.author.name)
    self.shapes.append(shape)

    self.emit_state({
        'shapes': self.shapes,        # ❌ Entire array (wasteful)
        'shape_added': shape,
        'shape_count': len(self.shapes),
        'active_minigame': 'shape_smash',  # ❌ Unchanged data
        'score': self.score,          # ❌ Unchanged data
    })
```

**Problems:**
- Large payloads slow down transmission
- Harder to debug (can't tell what actually changed)
- May trigger unnecessary frontend updates

---

### Backend: Transient Events

The platform provides **two methods** for emitting updates:

#### Method 1: `emit_state()` - Persistent State

Use for data that should persist:

```python
def update_score(self, message):
    self.score += 10

    # This persists - reconnecting clients will receive it
    self.emit_state({'score': self.score})
```

#### Method 2: `emit_event()` - Transient Events

Use for one-time actions that should NOT persist:

```python
def boost_shapes(self, message):
    # This does NOT persist - won't replay for reconnecting clients
    self.emit_event('boost', {
        'username': message.author.name,
        'force': 500
    })
```

**Complete example:**

```python
# ✅ CORRECT - Use emit_event() for transient actions
def trigger_explosion(self, message):
    """!explode command - Shapes fly from center"""
    self.emit_event('explode', {
        'x': 960,
        'y': 540,
        'username': message.author.name
    })
```

**Why use `emit_event()`?**
- Explicitly marks the update as transient
- Does NOT merge into `self.game_state`
- Prevents events from replaying on reconnection
- Makes intent clear to other developers

📖 **Implementation:** [base_game.py](../backend/base_game.py#L124-L161)

#### ❌ DON'T: Use emit_state() for events

```python
# BAD - Event persists in game_state
def boost_shapes(self, message):
    self.emit_state({
        'event': 'boost',  # ❌ Will persist in game_state
        'username': message.author.name
    })
    # Problem: Reconnecting clients will receive this and boost will replay!
```

---

### Frontend: Processing Events

#### ✅ DO: Clear transient events after processing

```typescript
// Good - ChatMinigames.ts
update(state: GameState): void {
  // Merge for tracking/debugging
  this.currentState = { ...this.currentState, ...state };

  // Handle scene switching
  if (state.event === 'switch_scene' && state.active_scene) {
    this.switchScene(state.active_scene as string);
    // Clear event after processing
    delete this.currentState.event;
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

📖 **Implementation:** [ChatMinigames.ts](../frontend/src/games/ChatMinigames.ts)

#### ❌ DON'T: Let events persist in component state

```typescript
// Bad - events stick around
update(state: GameState): void {
  this.currentState = { ...this.currentState, ...state };  // ❌ Event persists

  const scene = this.getMainScene();
  if (scene && 'onStateUpdate' in scene) {
    scene.onStateUpdate(state);
  }
  // Missing event cleanup! Event will be in currentState forever
}
```

**Problem:**
- Event persists in `currentState`
- May trigger again when component re-renders
- Debugging shows event in state long after it should be gone

---

### Frontend: State Merging

#### ✅ DO: Track merged state locally, pass updates as-is

```typescript
// Good - gameManager.ts
updateState(update: Partial<GameState>) {
  if (!this.currentGame) {
    console.warn('⚠️ Received state update but no game is loaded');
    return;
  }

  // Merge update into current state for tracking/debugging
  this.gameState = { ...this.gameState, ...update };

  /**
   * CRITICAL: Pass the update as-is, NOT the merged state.
   *
   * Why? If backend sends:
   *   1. {event: 'boost'}
   *   2. {shape_added: {...}}
   *
   * Passing merged state would send {event: 'boost', shape_added: {...}}
   * on the second update, causing events to trigger multiple times.
   */
  this.currentGame.update(update);  // ✅ Pass only the update

  // Log for debugging
  if (Object.keys(update).length > 0) {
    console.debug(`State updated for ${this.currentGameId}:`, Object.keys(update));
  }
}
```

📖 **Implementation:** [gameManager.ts](../frontend/src/gameManager.ts#L76-L103)

#### ❌ DON'T: Pass merged state to components

```typescript
// Bad - passes accumulated state
updateState(update: Partial<GameState>) {
  this.gameState = { ...this.gameState, ...update };
  this.currentGame.update(this.gameState);  // ❌ Events persist, trigger multiple times
}
```

**Why this is wrong:**
```
Update 1: {event: 'boost'}
  → gameState becomes {event: 'boost'}
  → Pass {event: 'boost'} to game ✅

Update 2: {shape_added: {...}}
  → gameState becomes {event: 'boost', shape_added: {...}}
  → Pass {event: 'boost', shape_added: {...}} to game ❌
  → Boost triggers AGAIN for new shape!
```

---

## Testing State Management

### Manual Testing Checklist

#### 1. Event Single-Trigger Test

**Test:** Verify events only fire once

```
Steps:
1. Send !boost in chat
2. Send !square in chat
3. Observe: Square should NOT boost
4. Observe: Only one boost effect should occur
```

**Expected:**
- ✅ Existing shapes boost upward
- ✅ New square spawns at normal position
- ✅ New square does NOT boost

**If failing:**
- Check GameManager is passing `update` not `this.gameState`
- Check scene is not merging state before processing events

---

#### 2. Reconnection Test

**Test:** Verify old events don't replay

```
Steps:
1. Send !boost in chat
2. Wait for boost animation to complete
3. Refresh browser (forces reconnection)
4. Observe initial state
```

**Expected:**
- ✅ Game loads with current state
- ✅ Boost does NOT trigger on reconnect
- ✅ Shapes are at rest

**If failing:**
- Check `get_initial_state()` returns fresh state, not `self.game_state`
- Check initial state doesn't contain `event` field

---

#### 3. Incremental Updates Test

**Test:** Verify incremental adds work correctly

```
Steps:
1. Send !square 3 times rapidly
2. Observe shapes on screen
3. Check developer console for state updates
```

**Expected:**
- ✅ Three shapes appear and persist
- ✅ Shapes do NOT disappear after spawning
- ✅ Each !square command creates exactly one new shape

**If failing:**
- Check scene isn't syncing to full array while doing incremental adds
- Check `shape_added` and `shapes` aren't both being processed

---

### Console Debugging

Enable detailed logging to trace state flow:

#### Backend Logging

```python
import logging
logger = logging.getLogger(__name__)

def spawn_square(self, message):
    shape = self._create_shape('square', message.author.name)

    update = {
        'shape_added': shape,
        'shape_count': len(self.shapes)
    }

    logger.info(f"Emitting state: {list(update.keys())}")  # ← Add this
    self.emit_state(update)
```

#### Frontend Logging

```typescript
// In scene's onStateUpdate()
onStateUpdate(state: GameState) {
  console.log('📥 ShapeSmashScene received state:', Object.keys(state));

  if (state.event) {
    console.log('  ⚠️ State contains event:', state.event);
  }

  // Rest of processing...
}
```

#### What to Look For

**Good state flow:**
```
📥 ShapeSmashScene received state: ['shape_added', 'shape_count']
📥 ShapeSmashScene received state: ['event']
  ⚠️ State contains event: boost
📥 ShapeSmashScene received state: ['shape_added', 'shape_count']
```

**Bad state flow (events persisting):**
```
📥 ShapeSmashScene received state: ['shape_added', 'shape_count']
📥 ShapeSmashScene received state: ['event']
  ⚠️ State contains event: boost
📥 ShapeSmashScene received state: ['event', 'shape_added', 'shape_count']  ❌ Event still here!
  ⚠️ State contains event: boost  ❌ Boost triggers again!
```

---

## Architecture Diagrams

### State Storage Layers

```
┌─────────────────────────────────────┐
│  Backend (Python)                   │
│  ┌───────────────────────────────┐  │
│  │ BaseGame.game_state           │  │  ← Accumulated persistent state
│  │ {shapes: [], score: 100}      │  │     (via emit_state)
│  └───────────────────────────────┘  │
│                ↓                     │
│  ┌───────────────────────────────┐  │
│  │ emit_state({score: 110})      │  │  ← Merges into game_state
│  │ emit_event('boost')           │  │  ← Does NOT merge
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  SocketIO (WebSocket)               │
│  Broadcasts: 'game_state_update'    │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│  Frontend GameManager               │
│  ┌───────────────────────────────┐  │
│  │ this.gameState                │  │  ← Tracks merged state locally
│  │ (for debugging/logging only)  │  │     NOT passed to components
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
│  │   - Update visuals            │  │
│  │   - Clear transient events    │  │
│  └───────────────────────────────┘  │
└─────────────────────────────────────┘
```

### Event Lifecycle

```
Backend emits transient event:
┌────────────────────────────────┐
│ self.emit_event('boost', {     │
│   username: 'Alice'            │
│ })                             │
└───────────┬────────────────────┘
            │
            ↓ Sent via SocketIO
┌────────────────────────────────┐
│ Frontend receives:             │
│ {event: 'boost', username: '…'}│
└───────────┬────────────────────┘
            │
            ↓ Process once
┌────────────────────────────────┐
│ Scene.onStateUpdate(state)     │
│   if (state.event === 'boost') │
│     applyBoostEffect()         │
└───────────┬────────────────────┘
            │
            ↓ Clear event
┌────────────────────────────────┐
│ delete currentState.event      │
│ Event is gone, won't retrigger │
└────────────────────────────────┘
```

---

## Common Questions

### Q: Why not just send full state snapshots every time?

**A:** While simpler conceptually, it would:

| Problem | Impact |
|---------|--------|
| **Waste bandwidth** | Sending entire game state (all shapes, scores, etc.) every update |
| **Make debugging harder** | Can't see what actually changed in each update |
| **Increase CPU usage** | Parsing larger payloads on every update |
| **Make event handling ambiguous** | No clear distinction between "new event" and "existing state" |

**Real-world example:**
- Game has 50 shapes (each ~200 bytes)
- Full snapshot: ~10KB per update
- Incremental: ~200 bytes per update
- At 10 updates/second: **100KB/s vs 2KB/s** (50x difference!)

---

### Q: Why track `gameState` in GameManager if we don't pass it?

**A:** The merged state is useful for:

| Use Case | Example |
|----------|---------|
| **Debugging** | See accumulated state in DevTools |
| **Logging** | Track what's changed over time |
| **Future features** | State snapshots, time travel debugging |
| **Diagnostics** | Detect state bloat or memory leaks |

**Note:** It's tracked for observability, not for data flow.

---

### Q: Should minigames store their own state?

**A:** Yes! Each minigame should track its own state and emit updates.

**Good pattern:**
```python
class ShapeSmashMinigame:
    def __init__(self, parent):
        self.parent = parent  # ChatMinigamesGame orchestrator
        self.shapes = []
        self.score = 0

    def spawn_shape(self, message):
        shape = self._create_shape()
        self.shapes.append(shape)

        # Emit via parent
        self.parent.emit_state({'shape_added': shape})
```

**Why:**
- Separation of concerns (each minigame manages its data)
- Easier to test (minigame is self-contained)
- Easier to debug (state is localized)
- Parent orchestrator doesn't need to know minigame internals

---

### Q: When should I use `emit_state()` vs `emit_event()`?

**Use this decision tree:**

```
Is this data needed for new/reconnecting clients?
├─ YES → Use emit_state()
│  Examples:
│  - Current score
│  - Player positions
│  - Game active/inactive flag
│  - Leaderboard data
│
└─ NO → Use emit_event()
   Examples:
   - Visual effects (boost, explode, shake)
   - Sound effects
   - Temporary animations
   - Notifications
```

**Rule of thumb:**
- **State** = "What is" (current condition)
- **Event** = "What happened" (one-time action)

---

## Summary

### Key Takeaways

| # | Principle | Why It Matters |
|---|-----------|----------------|
| 1 | Backend emits incremental updates, not full snapshots | Smaller payloads, clearer debugging |
| 2 | Use `emit_event()` for transient actions | Prevents events from persisting/replaying |
| 3 | GameManager passes updates as-is, doesn't merge first | Prevents old events from re-triggering |
| 4 | `get_initial_state()` returns fresh state, not `game_state` | Prevents reconnection bugs |
| 5 | Scenes guard against sync during incremental updates | Prevents shapes from disappearing |

### Quick Reference: Method Comparison

| Method | Merges into game_state? | Sent on reconnect? | Use For |
|--------|------------------------|-------------------|---------|
| `emit_state(update)` | ✅ Yes | ✅ Yes | Persistent data (scores, positions) |
| `emit_event(name, data)` | ❌ No | ❌ No | Transient effects (boost, explode) |

### When in Doubt

**Add logging to trace state flow:**
```python
# Backend
logger.info(f"Emitting: {list(state.keys())}")
```

```typescript
// Frontend
console.log('Received:', Object.keys(state));
if (state.event) console.warn('Event:', state.event);
```

**Check for these red flags:**
- Events appearing in multiple consecutive updates
- Merged state growing unexpectedly large
- State updates containing unchanged data
- Visual effects triggering on reconnection

---

## Related Documentation

- 📖 [README.md](../README.md) - Platform overview
- 📖 [PHASER_GAME_TEMPLATE.md](PHASER_GAME_TEMPLATE.md) - Creating new games with proper state handling
- 📖 [base_game.py](../backend/base_game.py) - State management implementation
- 📖 [gameManager.ts](../frontend/src/gameManager.ts) - Frontend state routing

---

**Last Updated:** 2025-01-16
**Related Files:**
- [gameManager.ts](../frontend/src/gameManager.ts#L76-L103) - Frontend state routing
- [ChatMinigames.ts](../frontend/src/games/ChatMinigames.ts) - Event clearing
- [base_game.py](../backend/base_game.py#L88-L161) - emit_state() and emit_event()
- [app.py](../backend/app.py) - Initial state handling

---

> **Remember:** When implementing new features, always ask: "Is this **state** (persists) or an **event** (transient)?" Use the right method for the right data type!
