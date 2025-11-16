"""
Base game class for the new Flask + TypeScript architecture.
All games must inherit from this class.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Callable, Optional
import logging

logger = logging.getLogger(__name__)


class BaseGame(ABC):
    """Abstract base class for all games in the new architecture"""

    def __init__(self, socketio=None):
        """
        Initialize the game with optional socketio instance

        Args:
            socketio: Flask-SocketIO instance for emitting events
        """
        self.socketio = socketio

        # IMPORTANT: game_state accumulates ALL state updates since game start.
        # - Use emit_state(update) to send incremental updates to frontend
        # - Use get_initial_state() for reconnections to avoid sending stale events
        # See STATE_MANAGEMENT.md for details
        self.game_state = {}

        self.room_id = 'main_room'  # Default room for broadcasts
        self._manifest = None  # Populated by GameLoader

    # === METADATA ===

    @abstractmethod
    def get_title(self) -> str:
        """
        Return the game's display title.

        Returns:
            str: The name of the game to display
        """
        pass

    @abstractmethod
    def get_game_id(self) -> str:
        """
        Return unique game identifier (used for routing).

        Returns:
            str: Game ID (e.g., 'shape_smash')
        """
        pass

    # === COMMANDS ===

    @abstractmethod
    def get_commands(self) -> Dict[str, Callable]:
        """
        Return chat commands for this game.
        Handlers receive (message) and should call emit_state() after state changes.

        Returns:
            dict: Command name -> callback function mapping
                  Example: {'square': self.spawn_square, 'boost': self.boost_shapes}
        """
        pass

    # === STATE MANAGEMENT ===

    @abstractmethod
    def get_initial_state(self) -> Dict[str, Any]:
        """
        Return the initial game state as a JSON-serializable dict.
        This is sent to frontend when game loads or when a client reconnects.

        CRITICAL: This should return FRESH state, NOT self.game_state.

        Why? self.game_state accumulates ALL updates including transient events.
        If a client reconnects after someone used !boost, self.game_state might
        contain {event: 'boost'}, causing the reconnecting client to see the
        boost effect trigger inappropriately.

        See STATE_MANAGEMENT.md § "Bug #2: Sending Accumulated State on Reconnection"

        Returns:
            dict: Initial state (e.g., {'shapes': [], 'score': 0})
        """
        pass

    def update_state(self, updates: Dict[str, Any], emit: bool = True):
        """
        Update game state and optionally emit to frontend.

        Args:
            updates: Partial state updates to merge
            emit: Whether to emit the update to frontend (default: True)
        """
        self.game_state.update(updates)
        if emit:
            self.emit_state(updates)

    def emit_state(self, state_update: Optional[Dict[str, Any]] = None):
        """
        Emit state update to frontend via SocketIO.

        IMPORTANT: This method sends incremental updates, not full state snapshots.

        Best Practice:
          - Send minimal updates: emit_state({'shape_added': shape})
          - NOT full state: emit_state(self.game_state)

        Why? Smaller payloads are faster and make debugging easier (you can see
        exactly what changed). Frontend GameManager will pass these incremental
        updates to game components without merging old events in.

        Note: state_update is also merged into self.game_state for tracking, but
        this accumulated state should NOT be used for reconnections (use
        get_initial_state() instead).

        See STATE_MANAGEMENT.md § "Best Practices: Emitting State Updates"

        Args:
            state_update: Partial state to send (or full state if None)
        """
        if self.socketio and self.room_id:
            data = state_update if state_update else self.game_state
            # Merge update into accumulated state for tracking
            if state_update:
                self.game_state.update(state_update)

            self.socketio.emit(
                'game_state_update',
                data,
                room=self.room_id
            )
            logger.debug(f"Emitted state update: {list(data.keys())}")

    def emit_event(self, event_name: str, data: Optional[Dict[str, Any]] = None):
        """
        Emit a transient event to frontend WITHOUT storing it in game_state.

        Use this for one-time actions/effects that should NOT persist:
          - Visual effects (boost, explode, shake)
          - Notifications (player joined, achievement unlocked)
          - Scene transitions

        Example:
            self.emit_event('boost', {'username': 'Alice'})
            # Frontend receives: {event: 'boost', username: 'Alice'}
            # Frontend processes it once, then clears it
            # Future reconnections will NOT see this event

        Why separate from emit_state()?
          - Makes intent explicit: "this is transient"
          - Prevents events from accumulating in game_state
          - Safer for reconnections (won't replay old events)

        See STATE_MANAGEMENT.md § "Backend: Transient Events"

        Args:
            event_name: Name of the event (e.g., 'boost', 'explode', 'clear')
            data: Optional additional data to send with the event
        """
        if self.socketio and self.room_id:
            event_data = {'event': event_name}
            if data:
                event_data.update(data)

            # CRITICAL: Do NOT merge into game_state - events are transient
            self.socketio.emit(
                'game_state_update',
                event_data,
                room=self.room_id
            )
            logger.debug(f"Emitted transient event: {event_name}")

    # === LIFECYCLE ===

    def reset(self):
        """
        Reset game to initial state.
        Called when switching to this game or restarting.
        """
        self.game_state = self.get_initial_state()
        self.emit_state()
        logger.info(f"{self.get_title()} reset")

    def on_game_start(self):
        """
        Called when game becomes active.
        Override for initialization logic.
        """
        pass

    def on_game_end(self):
        """
        Called when game is being switched away from.
        Override for cleanup logic.
        """
        pass

    # === SERVER-SIDE GAME LOOP (optional) ===

    def update(self, delta_time: float):
        """
        Optional server-side game tick for physics/AI.
        Override if game needs server-side updates.

        Args:
            delta_time: Time since last update in seconds
        """
        pass

    def finish(self) -> bool:
        """
        Signal that the game has ended and should transition to next game.
        Optional method - games can call this to self-initiate transitions.

        Returns:
            bool: True if game is finished, False otherwise
        """
        return False

    # === FRONTEND INFO ===

    @abstractmethod
    def get_frontend_config(self) -> Dict[str, Any]:
        """
        Return frontend configuration.

        Returns:
            dict: Frontend config
                Example:
                {
                    'component': 'ShapeSmash',  # TypeScript component name
                    'assets': ['shapes.png'],
                    'canvas_width': 1920,
                    'canvas_height': 1080
                }
        """
        pass
