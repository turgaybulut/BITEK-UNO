# BI-TEK UNO

A real-time multiplayer implementation of the classic UNO card game with modern networking features and a graphical user interface.

## Features

- Real-time multiplayer gameplay supporting 2-4 players per game
- Multiple simultaneous game rooms
- Built-in chat system for player communication
- Room creation and joining system with invite functionality
- Clean and intuitive graphical user interface
- Automatic game state synchronization
- Player disconnect/reconnect handling
- Complete UNO rule implementation including:
  - All card types (Number, Skip, Reverse, Draw Two, Wild, Wild Draw Four)
  - Color selection for wild cards
  - Turn management
  - Card draw and play validation
  - Win condition detection

## Technology Stack

- **Backend**
  - Python 3.11+
  - WebSocket server for real-time communication
  - Event-driven architecture
  - Asynchronous I/O with `asyncio`

- **Frontend**
  - Tkinter for GUI
  - WebSocket client for real-time updates
  - Event-based UI updates

## Project Structure

```plaintext
project/
├── scripts/
│   ├── run_client.py                     # Client application entry point
│   └── run_server.py                     # Server application entry point
├── src/
│   ├── client/
│   │   ├── ui/
│   │   │   ├── chat_box.py               # Chat interface component
│   │   │   ├── game_board.py             # Game board visualization
│   │   │   ├── game_room_section.py      # Game room UI
│   │   │   ├── game_ui.py                # Main UI coordination
│   │   │   ├── player_hand.py            # Player's card display
│   │   │   └── room_selection_section.py # Room list UI
│   │   ├── game_client.py                # Client-side game logic
│   │   ├── logger.py                     # Client logging utilities
│   │   ├── ui_coordinator.py             # UI-Game logic coordination
│   │   └── websocket_client.py           # Client networking
│   ├── common/
│   │   ├── card.py                       # Card representation
│   │   ├── card_enums.py                 # Card types and colors
│   │   ├── deck.py                       # Deck management
│   │   ├── game.py                       # Core game logic
│   │   ├── game_room.py                  # Game room management
│   │   ├── network_protocol.py           # Network message types
│   │   └── player.py                     # Player management
│   └── server/
│       ├── event_manager.py              # Event handling system
│       ├── game_server.py                # Game server logic
│       ├── logger.py                     # Server logging utilities
│       └── websocket_server.py           # Server networking 
├── Procfile                              # Heroku deployment config    
└── setup.py                              # Project packaging
```

## Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/turgaybulut/BITEK-UNO.git
   cd BITEK-UNO
   ```

2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1
   ```

3. Install dependencies:

   ```bash
   pip install -e .
   ```

## Running the Application

1. Start the server:

   ```bash
   python scripts/run_server.py
   ```

2. Launch client instances:

   ```bash
   python scripts/run_client.py
   ```

## Game Rules

1. Each player starts with 7 cards
2. Players must match the top card on the discard pile by:
   - Number
   - Color
   - Action (Skip, Reverse, Draw Two)
   - Or play a Wild card

3. Special cards:
   - **Skip**: Next player loses their turn
   - **Reverse**: Changes direction of play
   - **Draw Two**: Next player draws 2 cards and loses their turn
   - **Wild**: Change color of play
   - **Wild Draw Four**: Change color and next player draws 4 cards

4. Win condition: First player to play all their cards wins

## Network Protocol

The game uses a WebSocket-based protocol with JSON messages for all communication. Message types include:

- Authentication
- Room management (create, join, leave)
- Game actions (play card, draw card)
- Chat messages
- Game state updates

## Development

### Architecture Overview

The project follows a client-server architecture with:

1. **Server Components**
   - WebSocket server for client connections
   - Game rooms for multiple concurrent games
   - Event manager for handling game events

2. **Client Components**
   - WebSocket client for server communication
   - UI coordinator for managing game interface
   - Event handling for real-time updates

3. **Common Components**
   - Shared game logic
   - Network protocol definitions
   - Card and player management

## Credits

Created by:

- Turgay Bulut (S025007)
- İpek Motorcu (S029101)
- Burcu Kurnazoğlu (S029445)
- Başak Kadakal (S024336)
- Emin Şahin Mektepli (S025026)

Course: CS 447 - Computer Networks  
Instructor: Prof. Mehmet Reha Civanlar
