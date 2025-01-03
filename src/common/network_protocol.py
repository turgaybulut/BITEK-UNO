from enum import Enum, auto
from typing import TypedDict, Union, Optional, List, Dict, Any


class MessageType(Enum):
    # Authentication
    AUTHENTICATE = auto()  # Client -> Server: Player authentication
    AUTHENTICATED = auto()  # Server -> Client: Authentication successful

    # Room Management
    CREATE_ROOM = auto()  # Client -> Server: Create new room
    ROOM_CREATED = auto()  # Server -> Client: Room creation successful
    JOIN_ROOM = auto()  # Client -> Server: Join existing room
    ROOM_JOINED = auto()  # Server -> Client: Room join successful
    LEAVE_ROOM = auto()  # Client -> Server: Leave current room
    ROOM_LEFT = auto()  # Server -> Client: Room leave successful
    ROOM_CLOSED = auto()  # Server -> Client: Room has been closed

    # Game Actions
    START_GAME = auto()  # Client -> Server: Request to start game
    GAME_STARTED = auto()  # Server -> Client: Game has started
    GAME_STATE = auto()  # Server -> Client: Current game state
    PLAY_CARD = auto()  # Client -> Server: Play a card
    DRAW_CARD = auto()  # Client -> Server: Draw a card
    COLOR_SELECTION = auto()  # Client -> Server: Select color for wild card
    GAME_END = auto()  # Server -> Client: Game has ended

    # Chat
    CHAT_MESSAGE = auto()  # Bi-directional: Chat message

    # Connection Management
    PLAYER_DISCONNECTED = auto()  # Server -> Client: Player disconnected
    PLAYER_RECONNECTED = auto()  # Server -> Client: Player reconnected

    # Error Handling
    ERROR = auto()  # Server -> Client: Error message

    # Room listing
    LIST_ROOMS = auto()  # Client -> Server: Request room list
    ROOM_LIST = auto()  # Server -> Client: Room list response


class PlayerState(TypedDict):
    player_id: str
    name: str
    card_count: int
    is_connected: bool


class GameState(TypedDict):
    game_id: str  # Unique game identifier
    state: str  # "WAITING" | "PLAYING" | "FINISHED"
    current_player_index: int  # Index of current player in players list
    current_player_id: str  # ID of player whose turn it is
    direction_clockwise: bool  # Direction of play
    current_color: Optional[str]  # Current valid color
    top_card: Optional[Dict]  # Currently faced up card
    deck_count: int  # Number of cards remaining in deck
    players: List[PlayerState]  # List of all players
    your_hand: Optional[List[Dict]]  # Current player's cards (if applicable)


class RoomInfo(TypedDict):
    room_id: str
    player_count: int
    max_players: int
    state: str


# Authentication Messages
class AuthenticateMessage(TypedDict):
    type: str  # MessageType.AUTHENTICATE
    player_id: str  # Unique identifier for the player
    name: str  # Display name of the player


class AuthenticatedMessage(TypedDict):
    type: str  # MessageType.AUTHENTICATED
    player_id: str  # Confirmed player ID


# Room Management Messages
class CreateRoomMessage(TypedDict):
    type: str  # MessageType.CREATE_ROOM
    player_id: str  # ID of player creating the room


class RoomCreatedMessage(TypedDict):
    type: str  # MessageType.ROOM_CREATED
    room_id: str  # ID of the created room
    state: GameState  # Initial room state


class JoinRoomMessage(TypedDict):
    type: str  # MessageType.JOIN_ROOM
    room_id: str  # Room to join
    player_id: str  # Player requesting to join


class RoomJoinedMessage(TypedDict):
    type: str  # MessageType.ROOM_JOINED
    room_id: str  # Joined room ID
    state: GameState  # Current room state


class LeaveRoomMessage(TypedDict):
    type: str  # MessageType.LEAVE_ROOM
    room_id: str  # Room to leave
    player_id: str  # Player leaving


class RoomLeftMessage(TypedDict):
    type: str  # MessageType.ROOM_LEFT
    room_id: str  # Left room ID


class RoomClosedMessage(TypedDict):
    type: str  # MessageType.ROOM_CLOSED
    room_id: str  # Closed room ID


# Game Action Messages
class StartGameMessage(TypedDict):
    type: str  # MessageType.START_GAME
    room_id: str  # Room to start game in


class GameStartedMessage(TypedDict):
    type: str  # MessageType.GAME_STARTED
    room_id: str  # Room ID
    state: GameState  # Initial game state


class GameStateMessage(TypedDict):
    type: str  # MessageType.GAME_STATE
    room_id: str  # Room ID
    state: GameState  # Current game state


class PlayCardMessage(TypedDict):
    type: str  # MessageType.PLAY_CARD
    room_id: str  # Room ID
    player_id: str  # Player playing the card
    card: Dict[str, Any]  # Card being played
    chosen_color: Optional[str]  # For wild cards


class DrawCardMessage(TypedDict):
    type: str  # MessageType.DRAW_CARD
    room_id: str  # Room ID
    player_id: str  # Player drawing


class ColorSelectionMessage(TypedDict):
    type: str  # MessageType.COLOR_SELECTION
    room_id: str  # Room ID
    player_id: str  # Player selecting
    color: str  # Selected color


class GameEndMessage(TypedDict):
    type: str  # MessageType.GAME_END
    room_id: str  # Room ID
    winner_id: str  # ID of winning player
    state: GameState  # Final game state


# Chat Messages
class ChatMessage(TypedDict):
    type: str  # MessageType.CHAT_MESSAGE
    room_id: str  # Room ID
    player_id: str  # Player sending message
    player_name: str  # Name of player sending message
    content: str  # Message content
    timestamp: float  # Message timestamp


# Connection Messages
class PlayerConnectionMessage(TypedDict):
    type: str  # MessageType.PLAYER_DISCONNECTED or PLAYER_RECONNECTED
    room_id: str  # Room ID
    player_id: str  # Player who disconnected/reconnected


# Error Messages
class ErrorMessage(TypedDict):
    type: str  # MessageType.ERROR
    message: str  # Error description


class ListRoomsMessage(TypedDict):
    type: str  # MessageType.LIST_ROOMS


class RoomListMessage(TypedDict):
    type: str  # MessageType.ROOM_LIST
    rooms: List[RoomInfo]


# Union type for all possible messages
NetworkMessage = Union[
    AuthenticateMessage,
    AuthenticatedMessage,
    CreateRoomMessage,
    RoomCreatedMessage,
    JoinRoomMessage,
    RoomJoinedMessage,
    LeaveRoomMessage,
    RoomLeftMessage,
    RoomClosedMessage,
    StartGameMessage,
    GameStartedMessage,
    GameStateMessage,
    PlayCardMessage,
    DrawCardMessage,
    ColorSelectionMessage,
    GameEndMessage,
    ChatMessage,
    PlayerConnectionMessage,
    ErrorMessage,
    ListRoomsMessage,
    RoomListMessage,
]
