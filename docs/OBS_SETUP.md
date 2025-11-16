# OBS Studio Setup Guide

Complete guide for integrating Twitch Chat Games into OBS Studio as a browser source. Configure transparent overlays, optimize performance, and troubleshoot common streaming issues.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Setup (5 Minutes)](#quick-setup-5-minutes)
- [Detailed Configuration](#detailed-configuration)
- [Transparency & Visual Effects](#transparency--visual-effects)
- [Performance Optimization](#performance-optimization)
- [Scene Management](#scene-management)
- [Testing & Interaction](#testing--interaction)
- [Troubleshooting](#troubleshooting)
- [Advanced Configurations](#advanced-configurations)

---

## Prerequisites

### Required Software

| Software | Minimum Version | Download | Status |
|----------|----------------|----------|--------|
| **OBS Studio** | 28.0+ | [obsproject.com](https://obsproject.com/) | Required |
| **Chat Games Backend** | Running | See [QUICKSTART.md](QUICKSTART.md) | Required |
| **Web Browser** | Any modern browser | For testing | Required |

### Before You Start

- [ ] **Backend running** - `python app.py` in `backend/` directory
- [ ] **Game loads in browser** - Test at `http://localhost:5000`
- [ ] **Twitch bot connected** - Check Flask console for "Bot connected"
- [ ] **Commands working** - Try `!square` in Twitch chat or browser console

📖 **Not set up yet?** See [QUICKSTART.md](QUICKSTART.md) for installation instructions.

---

## Quick Setup (5 Minutes)

### Step 1: Start the Backend

```bash
cd backend
python app.py
```

**Verify:** Open `http://localhost:5000` in your browser - you should see the game canvas.

### Step 2: Add Browser Source

1. In OBS Studio, go to **Sources** panel (bottom)
2. Click the **+** button
3. Select **Browser**
4. Name it: `Twitch Chat Games`
5. Click **OK**

### Step 3: Configure Basic Settings

| Setting | Value | Why |
|---------|-------|-----|
| **URL** | `http://localhost:5000` | Points to Flask backend |
| **Width** | `1920` | Matches game canvas width |
| **Height** | `1080` | Matches game canvas height |
| **FPS** | `60` | Smooth animations |
| **Control audio via OBS** | ✅ Checked | If games have sound |
| **Shutdown source when not visible** | ✅ Checked | Saves CPU/GPU |
| **Refresh browser when scene becomes active** | ✅ Checked | Prevents stale state |

Click **OK** to save!

### Step 4: Test

1. **Send Twitch command:** Type `!square` in your chat
2. **Watch OBS:** Shape should appear in the preview
3. **Success!** Your game is now streaming

<!--
📸 **Screenshot Guide** (Placeholder)
Add annotated screenshot showing OBS Browser Source properties dialog with all settings highlighted
-->

---

## Detailed Configuration

### Browser Source Properties

**Access:** Right-click source → **Properties**

#### URL Configuration

| Environment | URL | Use Case |
|-------------|-----|----------|
| **Local (Same PC)** | `http://localhost:5000` | Development, single-PC streaming |
| **Network (Streaming PC)** | `http://192.168.1.100:5000` | Dedicated streaming PC setup |
| **Production** | `http://your-domain.com:5000` | Cloud/remote deployment |

#### Canvas Dimensions

Default game canvas is **1920×1080**. Match these in OBS for pixel-perfect rendering.

**Custom resolutions:**
1. Update `game_manifest.json` in your game directory:
   ```json
   "config": {
     "canvas_width": 1280,
     "canvas_height": 720
   }
   ```
2. Restart Flask backend
3. Update OBS browser source width/height to match

**Common resolutions:**

| Resolution | Width | Height | Use Case |
|------------|-------|--------|----------|
| **Full HD** | 1920 | 1080 | Full screen overlay |
| **720p** | 1280 | 720 | Lower resource usage |
| **Half HD** | 960 | 540 | Small corner overlay |
| **Custom** | Any | Any | Creative layouts |

#### Custom CSS

Add to **Custom CSS** field for styling:

**Transparent background:**
```css
body {
  background-color: rgba(0, 0, 0, 0) !important;
  margin: 0;
  overflow: hidden;
}

#app {
  background-color: transparent !important;
}
```

**Remove scrollbars:**
```css
body {
  overflow: hidden;
}
```

**Hide cursor:**
```css
* {
  cursor: none !important;
}
```

#### Advanced Options

| Option | Recommended | Why |
|--------|-------------|-----|
| **Use custom frame rate** | ✅ | Set to 60 FPS for smooth animations |
| **FPS** | `60` | Matches game physics tick rate |
| **Control audio via OBS** | ✅ | Required if games have sound effects |
| **Shutdown source when not visible** | ✅ | Saves CPU/GPU when scene is inactive |
| **Refresh browser when scene becomes active** | ✅ | Prevents stale game state |
| **Reroute audio** | ❌ | Not needed unless separating audio tracks |

---

## Transparency & Visual Effects

### Making the Background Transparent

By default, the game has a dark background. To make it fully transparent:

**Method 1: Custom CSS (Easiest)**

Add to **Custom CSS** in browser source properties:

```css
body, #app {
  background-color: transparent !important;
}
```

**Method 2: Game Configuration**

Edit the Phaser scene's `create()` method:

```typescript
// Remove or comment out background rectangle
// this.add.rectangle(0, 0, width, height, 0x1a1a2e).setOrigin(0);
```

Then rebuild frontend: `npm run build`

### Chroma Key (Green Screen)

Alternative to CSS transparency:

1. Set game background to solid green in Phaser:
   ```typescript
   this.add.rectangle(0, 0, width, height, 0x00ff00).setOrigin(0);
   ```

2. In OBS, right-click browser source → **Filters** → **+** → **Chroma Key**

3. Configure:
   - **Key Color Type:** Green
   - **Similarity:** 400
   - **Smoothness:** 100

### Blend Modes

Experiment with blend modes for creative effects:

1. Right-click browser source → **Filters**
2. Add **Blend Mode** filter
3. Try: **Add**, **Multiply**, **Screen**

---

## Performance Optimization

### OBS Settings

**Settings → Advanced:**

| Setting | Recommended | Impact |
|---------|-------------|--------|
| **Browser Source Hardware Acceleration** | ✅ Enabled | Major GPU performance boost |
| **Color Format** | NV12 | Best for streaming |
| **Color Space** | 709 | Standard for 1080p |

**Settings → Video:**

| Setting | Recommended | Notes |
|---------|-------------|-------|
| **Base (Canvas) Resolution** | 1920×1080 | Match your stream resolution |
| **Output (Scaled) Resolution** | 1920×1080 or 1280×720 | Lower for better performance |
| **FPS** | 60 or 30 | Match browser source FPS |

### Browser Source Optimization

**If experiencing lag:**

1. **Lower resolution:**
   - Change game to 1280×720 (see [Detailed Configuration](#canvas-dimensions))
   - Update OBS browser source dimensions

2. **Reduce FPS:**
   - Set browser source FPS to 30 instead of 60
   - Less smooth but lower CPU usage

3. **Disable unused features:**
   - Uncheck "Control audio via OBS" if no sound
   - Enable "Shutdown source when not visible"

4. **Close other browser sources:**
   - Each browser source uses resources
   - Limit to 2-3 active sources maximum

### Game-Specific Optimization

**For Shape Smash minigame:**

Limit maximum shapes to reduce physics calculations:

```python
# In backend/games/chat_minigames/minigames/shape_smash.py
MAX_SHAPES = 30  # Reduce from default 50
```

---

## Scene Management

### Single Browser Source (Recommended)

**Use game switching commands:**
- `!nextgame` - Cycle to next game
- `!minigame shape_smash` - Switch to specific minigame

Games automatically transition in the same browser source.

### Multiple Browser Sources

**For separate game scenes:**

1. Create browser source per game: `Chat Games - Shape Smash`
2. Use scene switching in OBS
3. Enable "Refresh browser when scene becomes active"

**Trade-offs:**

| Approach | Pros | Cons |
|----------|------|------|
| **Single Source** | Lower resource usage, seamless transitions | All games share one canvas |
| **Multiple Sources** | Separate positioning/effects per game | Higher resource usage |

### Positioning & Transform

**Quick positioning:**
- Drag red bounding box in OBS preview
- `Alt+Drag` to crop edges

**Precise positioning:**
- Right-click source → **Transform** → **Edit Transform**
- Set exact X/Y position and size

**Common layouts:**

| Layout | Position | Size | Use Case |
|--------|----------|------|----------|
| **Full Screen** | 0, 0 | 1920×1080 | Main game focus |
| **Bottom Third** | 0, 720 | 1920×360 | Chat interaction |
| **Corner Overlay** | 1440, 600 | 480×270 | Picture-in-picture |
| **Side Panel** | 1600, 0 | 320×1080 | Leaderboard display |

---

## Testing & Interaction

### Testing Commands in OBS

**Method 1: Twitch Chat**
- Send commands in your Twitch chat
- Watch OBS preview for responses

**Method 2: OBS Interact Mode**
1. Right-click browser source → **Interact**
2. Opens interactive window
3. Open browser console (F12)
4. Run test commands:
   ```javascript
   // Simulate !square command
   socket.emit('game_state_update', {
     shape_added: {
       id: 'test_1',
       type: 'square',
       x: 500,
       y: 200,
       color: '#FF6B6B',
       username: 'TestUser'
     }
   });
   ```

### Refreshing the Source

**Manual refresh:**
- Right-click browser source → **Refresh**

**Auto-refresh options:**
- ✅ **Refresh browser when scene becomes active** (in properties)
- Set up OBS hotkey: Settings → Hotkeys → "Refresh Browser Source"

### Debugging

**Check browser console in Interact mode:**

1. Right-click source → **Interact**
2. Press **F12** to open DevTools
3. Check Console tab for:
   - ✅ `Connected to server` - SocketIO working
   - ✅ `Game loaded: chat_minigames` - Game initialized
   - ❌ Red errors - Connection/loading issues

---

## Troubleshooting

<details>
<summary><strong>❌ Browser source shows blank/black screen</strong></summary>

**Checklist:**
- [ ] Flask backend is running (`python app.py`)
- [ ] URL is exactly `http://localhost:5000` (check for typos)
- [ ] Browser source dimensions match game canvas (1920×1080)
- [ ] OBS version is 28.0 or newer

**Test:**
1. Open `http://localhost:5000` in regular browser
2. If it works there but not in OBS, restart OBS
3. Delete and recreate the browser source

**Common causes:**
- Flask not running on port 5000
- Firewall blocking localhost connections
- Outdated OBS version (update to latest)
</details>

<details>
<summary><strong>❌ Game shows but doesn't update/respond to commands</strong></summary>

**Symptoms:**
- Static image in OBS
- No shapes spawn when using `!square`

**Checklist:**
- [ ] Twitch bot connected (check Flask console)
- [ ] SocketIO connected (check browser console in Interact mode)
- [ ] Commands work in regular browser
- [ ] "Shutdown source when not visible" is disabled (for testing)

**Debug steps:**

1. **Check Flask console:**
   ```
   INFO:TwitchBot: Bot connected to Twitch
   INFO:GameManager: Loaded initial game: chat_minigames
   ```

2. **Check browser console in OBS:**
   - Right-click source → Interact → F12
   - Look for: `✅ Connected to server`

3. **Test command manually:**
   - In Interact mode console, run:
     ```javascript
     socket.emit('game_state_update', {event: 'test'});
     ```
   - Should see response in console

**Solution:**
- Refresh the browser source
- Restart Flask backend
- Check `.env` file has correct Twitch credentials
</details>

<details>
<summary><strong>❌ Performance issues / choppy animations</strong></summary>

**Symptoms:**
- Low FPS in OBS preview
- Shapes move in jerky motions
- Stream drops frames

**Quick fixes:**

1. **Lower resolution:**
   - Change game to 1280×720
   - Update browser source dimensions

2. **Reduce browser source FPS:**
   - Properties → FPS → Change to 30

3. **Enable hardware acceleration:**
   - OBS Settings → Advanced → Browser Source Hardware Acceleration ✅

4. **Close other sources:**
   - Disable unused browser sources
   - Remove heavy filters/effects

**Advanced optimization:**
- Limit max shapes in game config
- Use OBS performance mode (Settings → General)
- Monitor CPU/GPU usage in Task Manager
</details>

<details>
<summary><strong>❌ Transparent background shows checkerboard pattern</strong></summary>

**Cause:** CSS transparency is working, but OBS is showing transparency indicator.

**Solution:**
1. Add a **Color Source** behind the browser source
2. Sources panel → **+** → **Color Source**
3. Set color to match your stream background
4. Drag **Color Source** below **Browser Source** in layers
</details>

<details>
<summary><strong>❌ Audio not playing from game</strong></summary>

**Checklist:**
- [ ] "Control audio via OBS" is checked in browser source properties
- [ ] OBS Audio Mixer shows browser source (not muted)
- [ ] Game has audio implementation (not all games do)

**Test:**
- Right-click source → Interact
- Check if audio plays in Interact window
- If yes: Enable "Control audio via OBS"
- If no: Game doesn't have audio yet
</details>

<details>
<summary><strong>❌ Can't connect from streaming PC to gaming PC</strong></summary>

**Symptoms:**
- Browser source works on gaming PC (`localhost:5000`)
- Doesn't work on streaming PC (`192.168.1.100:5000`)

**Checklist:**
- [ ] Flask is bound to `0.0.0.0` not `127.0.0.1`
- [ ] Firewall allows port 5000
- [ ] Both PCs on same network
- [ ] Correct IP address in OBS URL

**Fix Flask binding:**

In `backend/app.py` (line ~461):
```python
# Change from:
socketio.run(app, host='127.0.0.1', port=5000)

# To:
socketio.run(app, host='0.0.0.0', port=5000)
```

**Test connection:**
```bash
# From streaming PC
ping 192.168.1.100
curl http://192.168.1.100:5000
```
</details>

---

## Advanced Configurations

### Custom Game URL Parameters

**Future feature:** Direct game loading via URL

```
http://localhost:5000/game/chat_minigames
http://localhost:5000/game/shape_smash
```

*Currently: Use `!nextgame` command to cycle games*

### Multiple Monitor Setup

**Recommended layout:**

| Monitor | Content | OBS Source |
|---------|---------|------------|
| **Primary** | OBS Studio, game controls | N/A |
| **Secondary** | Twitch chat, alerts | Window Capture |
| **Virtual** | Game browser preview | Browser Source |

### Production Deployment

**Cloud hosting setup:**

1. **Deploy Flask to cloud** (Heroku, AWS, etc.)
2. **Configure HTTPS** (required for some OBS features)
3. **Update OBS URL:** `https://your-domain.com`
4. **Test latency:** Cloud adds ~50-200ms delay

**Pros:** Accessible from anywhere, uptime monitoring
**Cons:** Higher latency, requires internet connection

### Filters & Effects

**Recommended filters for game overlay:**

| Filter | Purpose | Settings |
|--------|---------|----------|
| **Color Correction** | Match stream color grading | Gamma: 0, Contrast: 0, Brightness: 0 |
| **Sharpen** | Crisp pixel art | Amount: 0.1 |
| **Chroma Key** | Remove background | Green key if using green bg |

### Hotkey Automation

**Setup quick controls:**

1. OBS Settings → **Hotkeys**
2. Search for your browser source name
3. Assign keys:
   - `F5` - Refresh Browser Source
   - `F6` - Show/Hide Source
   - `F7` - Interact with Source

---

## Verification Checklist

Use this checklist to verify your OBS setup is working correctly:

- [ ] **Backend running** - Flask console shows no errors
- [ ] **Browser source added** - Shows in OBS Sources panel
- [ ] **Correct URL** - `http://localhost:5000` (or network IP)
- [ ] **Correct dimensions** - 1920×1080 matches game canvas
- [ ] **FPS set** - 60 FPS for smooth animations
- [ ] **Hardware acceleration** - Enabled in OBS Advanced settings
- [ ] **SocketIO connected** - Check browser console in Interact mode
- [ ] **Twitch bot connected** - Flask console shows "Bot connected"
- [ ] **Commands working** - `!square` spawns a shape
- [ ] **Performance good** - No lag or frame drops in OBS preview
- [ ] **Audio working** - If game has sound (optional)

---

## Resources

### Related Documentation

- 📖 [README.md](../README.md) - Platform overview
- 📖 [QUICKSTART.md](QUICKSTART.md) - Installation and setup
- 📖 [FILE_LOCATIONS.md](FILE_LOCATIONS.md) - Project structure
- 📖 [PHASER_GAME_TEMPLATE.md](PHASER_GAME_TEMPLATE.md) - Creating custom games

### External Resources

- [OBS Studio Documentation](https://obsproject.com/wiki/)
- [OBS Browser Source Guide](https://obsproject.com/wiki/Sources-Guide#browser-source)
- [Twitch Streaming Best Practices](https://help.twitch.tv/s/article/broadcasting-guidelines)

---

**Happy streaming!** 🎮📡

> **Pro Tip:** Test your setup with `!square`, `!circle`, and `!boost` commands before going live. Make sure shapes appear and physics work correctly!

> **Need help?** Join the community or open an issue on GitHub with OBS version, OS, and error messages from browser console (F12 in Interact mode).
