# OBS Browser Source Setup Guide

How to add your Twitch Chat Games to OBS as a browser source.

## Prerequisites

- OBS Studio installed
- Chat Games running on `localhost:5000`
- Games loaded and working in browser

## Step-by-Step Setup

### 1. Start the Application

```bash
cd chat-games/backend
python app.py
```

Verify it's working by opening `http://localhost:5000` in your browser.

### 2. Add Browser Source in OBS

1. In OBS, click the **+** button in the **Sources** panel
2. Select **Browser**
3. Name it "Twitch Chat Games" (or whatever you prefer)
4. Click **OK**

### 3. Configure Browser Source

In the **Properties** dialog:

**URL:**
```
http://localhost:5000
```

**Width:**
```
1920
```

**Height:**
```
1080
```

**Custom CSS** (optional, for transparency):
```css
body {
  background-color: rgba(0, 0, 0, 0);
  margin: 0px auto;
  overflow: hidden;
}
```

**Additional Settings:**
- ✅ **Control audio via OBS** (if your games have sound)
- ✅ **Shutdown source when not visible** (saves resources)
- ✅ **Refresh browser when scene becomes active** (keeps it fresh)

### 4. Position and Resize

- Use the red bounding box to position/resize the game on your stream
- Right-click → Transform → Edit Transform for precise control
- Recommended: Full screen or bottom overlay

### 5. Test It!

1. Make sure your Twitch bot is connected
2. Send a command in chat: `!square`
3. Watch the shape appear in OBS!

## Tips & Tricks

### Transparent Background

To make the dark background transparent:

1. **Remove the background from CSS** in the game (if needed)
2. **Add to Custom CSS**:
   ```css
   body { background-color: transparent !important; }
   #app { background-color: transparent !important; }
   ```

### Performance Optimization

For better performance:

1. **Set FPS** in OBS Browser Source properties:
   - Set **FPS** to `60` for smooth animations

2. **Hardware Acceleration**:
   - OBS Settings → Advanced → Browser Source Hardware Acceleration: **Enabled**

3. **Resolution**:
   - Match the canvas resolution (1920x1080 default)
   - Lower if experiencing lag

### Interaction

To interact with the game from OBS (for testing):

1. Right-click the browser source
2. Select **Interact**
3. Opens a window where you can click/interact with the page

### Refresh the Source

If the game gets stuck or stops updating:

1. Right-click the browser source
2. Select **Refresh**

Or enable "Refresh browser when scene becomes active" to auto-refresh.

### Multiple Games

To show different games:

**Option A: One Browser Source**
- Use `!nextgame` command to cycle games
- Game will automatically switch in OBS

**Option B: Multiple Browser Sources**
- Create separate sources for each game (not recommended yet)
- Future: Direct game URLs like `http://localhost:5000/game/shape_smash`

## Common Issues

### Game not showing in OBS

1. **Check the URL**: Must be exactly `http://localhost:5000`
2. **Check Flask is running**: Open URL in regular browser first
3. **Check OBS version**: Requires OBS 28.0+ for best compatibility

### Game appears but doesn't update

1. **Refresh the browser source**
2. **Check backend console** for errors
3. **Verify Twitch bot is connected**
4. **Check browser console** (right-click → Interact, then press F12)

### Performance issues / lag

1. **Lower resolution**: Try 1280x720 instead of 1920x1080
2. **Enable hardware acceleration** in OBS settings
3. **Close other browser sources** to free up resources
4. **Reduce max shapes** in game config

### Twitch commands not working

1. **Verify bot is connected**: Check backend console logs
2. **Check OAuth tokens**: Make sure `.env` is configured
3. **Test in browser first**: Open `http://localhost:5000` and watch console

## Advanced: Custom Resolution

To use a custom resolution:

1. **Update game manifest** (`games/builtin/shape_smash/game_manifest.json`):
   ```json
   "config": {
     "canvas_width": 1280,
     "canvas_height": 720
   }
   ```

2. **Match OBS browser source** width/height to the same values

3. **Restart Flask** to reload the config

## Production Setup (Optional)

For running on a dedicated streaming PC:

1. **Change Flask host** in `backend/app.py`:
   ```python
   socketio.run(app, host='0.0.0.0', port=5000)
   ```

2. **Update OBS URL** to your PC's IP:
   ```
   http://192.168.1.100:5000
   ```

3. **Configure firewall** to allow port 5000

## Troubleshooting Checklist

- [ ] Flask server running on port 5000
- [ ] Game loads in regular browser
- [ ] Twitch bot connected (check console)
- [ ] OBS browser source URL is correct
- [ ] Resolution matches game config
- [ ] Hardware acceleration enabled
- [ ] No console errors (F12 in Interact mode)

## Next Steps

- Customize your games!
- Add sound effects
- Create overlays and animations
- Share your setup with the community

Happy streaming! 🎮📡
