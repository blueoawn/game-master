"""
Flask application entry point with SocketIO support.
Serves the frontend and provides real-time communication with games.
"""
from flask import Flask, render_template, jsonify, request
from flask_socketio import SocketIO, join_room, emit
from flask_cors import CORS
import threading
import logging

from game_manager import GameManager
from twitch_bot import Bot, setup_database
import asqlite
import twitchio

# Setup logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)s:%(name)s:%(message)s')
logger = logging.getLogger(__name__)

# Initialize Flask
app = Flask(__name__,
            static_folder='../frontend/dist',
            static_url_path='',  # Serve static files from root URL
            template_folder='../frontend/dist')
app.config['SECRET_KEY'] = 'your-secret-key-change-this'

# Enable CORS for development
CORS(app)

# Initialize SocketIO
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='threading')

# Initialize GameManager
game_manager = GameManager(socketio)

# Request logging for debugging
@app.before_request
def log_request_info():
    """Log all incoming requests for debugging"""
    logger.debug(f"🌐 Request: {request.method} {request.path}")
    if request.path.startswith('/assets/'):
        logger.debug(f"   Static asset request detected")

# Twitch bot instance
bot_instance = None

# === HTTP Routes ===

@app.route('/')
def index():
    """Serve the frontend"""
    return render_template('index.html')

@app.route('/api/games')
def list_games():
    """API endpoint to list available games"""
    return jsonify({
        'games': [
            {
                'id': gid,
                'name': manifest['name'],
                'description': manifest['description'],
                'commands': manifest.get('commands', [])
            }
            for gid, manifest in game_manager.games.items()
        ]
    })

@app.route('/api/games/<game_id>/config')
def get_game_config(game_id):
    """Get frontend config for a specific game"""
    try:
        config = game_manager.loader.get_frontend_config(game_id)
        return jsonify(config)
    except ValueError as e:
        return jsonify({'error': str(e)}), 404

@app.route('/api/active-game')
def get_active_game():
    """Get the currently active game info"""
    if game_manager.active_game:
        return jsonify({
            'gameId': game_manager.active_game_id,
            'title': game_manager.active_game.get_title(),
            'state': game_manager.active_game.game_state
        })
    return jsonify({'error': 'No active game'}), 404

# Catch-all route for SPA - must be last!
@app.route('/<path:path>')
def catch_all(path):
    """Catch-all route to serve SPA or 404"""
    logger.debug(f"📥 Catch-all handling: {path}")

    # If it's an API route that doesn't exist, return 404
    if path.startswith('api/'):
        logger.debug(f"  → 404 (API not found)")
        return jsonify({'error': 'Not found'}), 404

    # Explicitly serve static assets (fixes MIME type issue)
    if path.startswith('assets/'):
        logger.debug(f"  → Serving static file")
        return app.send_static_file(path)

    # Otherwise serve index.html for SPA routing
    logger.debug(f"  → Serving index.html (SPA route)")
    return render_template('index.html')

# === SocketIO Events ===

@socketio.on('connect')
def handle_connect():
    """Client connected"""
    join_room('main_room')
    logger.info(f"Client connected: {request.sid}")

    # Send current game state if game is active
    if game_manager.active_game:
        emit('game_loaded', {
            'gameId': game_manager.active_game_id,
            'title': game_manager.active_game.get_title(),
            # Use get_initial_state() not game_state to avoid sending accumulated events
            'initialState': game_manager.active_game.get_initial_state(),
            'config': game_manager.loader.get_frontend_config(
                game_manager.active_game_id
            )
        })

@socketio.on('disconnect')
def handle_disconnect():
    """Client disconnected"""
    logger.info(f"Client disconnected: {request.sid}")

@socketio.on('load_game')
def handle_load_game(data):
    """Load a specific game"""
    game_id = data.get('gameId')
    try:
        game_manager.load_game(game_id)
        # Refresh bot commands
        if bot_instance:
            # The bot will automatically pick up new commands via game_manager
            logger.info(f"Loaded game: {game_id}")
    except Exception as e:
        logger.error(f"Error loading game: {e}")
        emit('error', {'message': str(e)})

@socketio.on('add_score')
def handle_add_score(data):
    """Add score for a player"""
    username = data.get('username')
    points = data.get('points', 1)
    game_name = data.get('game_name', 'ShapeSmash')

    if not username:
        return

    import sqlite3

    try:
        conn = sqlite3.connect('tokens.db')
        cursor = conn.cursor()

        # Check if player exists
        cursor.execute('SELECT score FROM player_scores WHERE username = ?', (username,))
        row = cursor.fetchone()

        if row:
            # Update existing score
            new_score = row[0] + points
            cursor.execute(
                'UPDATE player_scores SET score = ?, last_updated = CURRENT_TIMESTAMP WHERE username = ?',
                (new_score, username)
            )
        else:
            # Insert new player
            cursor.execute(
                'INSERT INTO player_scores (username, score, game_name) VALUES (?, ?, ?)',
                (username, points, game_name)
            )

        conn.commit()
        logger.info(f"✅ Added {points} points for {username} in {game_name}")

        # Emit updated leaderboard to all clients
        cursor.execute('SELECT username, score FROM player_scores ORDER BY score DESC LIMIT 10')
        leaderboard = [{'username': row[0], 'score': row[1]} for row in cursor.fetchall()]
        socketio.emit('leaderboard_update', {'leaderboard': leaderboard}, room='main_room')

        conn.close()
    except Exception as e:
        logger.error(f"❌ Error updating score: {e}")

@socketio.on('get_leaderboard')
def handle_get_leaderboard(data=None):
    """Get current leaderboard"""
    import sqlite3

    try:
        conn = sqlite3.connect('tokens.db')
        cursor = conn.cursor()
        cursor.execute('SELECT username, score FROM player_scores ORDER BY score DESC LIMIT 10')
        leaderboard = [{'username': row[0], 'score': row[1]} for row in cursor.fetchall()]
        conn.close()

        emit('leaderboard_update', {'leaderboard': leaderboard})
        logger.info(f"📊 Sent leaderboard with {len(leaderboard)} players")
    except Exception as e:
        logger.error(f"❌ Error fetching leaderboard: {e}")
        emit('leaderboard_update', {'leaderboard': []})

# === Twitch Bot Startup ===

async def start_twitch_bot():
    """Start Twitch bot (async)"""
    global bot_instance

    # Import bot setup
    from twitch_bot import CLIENT_ID, CLIENT_SECRET, BOT_ID, OWNER_ID

    async with asqlite.create_pool("tokens.db") as tdb:
        tokens, subs = await setup_database(tdb)

        async with Bot(game_manager=game_manager, token_database=tdb, subs=subs) as bot:
            bot_instance = bot
            for pair in tokens:
                await bot.add_token(*pair)

            await bot.start(load_tokens=False)

def run_twitch_bot():
    """Wrapper to run async bot in thread"""
    import asyncio
    try:
        asyncio.run(start_twitch_bot())
    except KeyboardInterrupt:
        logger.warning("Twitch bot shutting down")

# === Startup ===

if __name__ == '__main__':
    # Discover and load games
    game_manager.discover_games()

    # Load first game if available
    if game_manager.games:
        first_game_id = list(game_manager.games.keys())[0]
        game_manager.load_game(first_game_id)
        logger.info(f"Loaded initial game: {first_game_id}")

    # Start Twitch bot in separate thread
    bot_thread = threading.Thread(target=run_twitch_bot, daemon=True)
    bot_thread.start()

    # Start Flask-SocketIO server
    logger.info("Starting Flask server on http://localhost:5000")
    socketio.run(app, host='0.0.0.0', port=5000, debug=True, use_reloader=False)
