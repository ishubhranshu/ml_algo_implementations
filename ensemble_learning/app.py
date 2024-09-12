import socket
from flask import Flask, render_template_string, request, jsonify, session
import random
import numpy as np

app = Flask(__name__)

# HTML Template
TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>2048 Game</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            display: flex;
            flex-direction: column;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
            background-color: #faf8ef;
        }
        .board {
            display: grid;
            grid-template-columns: repeat(4, 100px);
            grid-template-rows: repeat(4, 100px);
            gap: 10px;
            margin-bottom: 20px;
        }
        .tile {
            background-color: #cdc1b4;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 24px;
            font-weight: bold;
            color: #776e65;
            border-radius: 3px;
        }
        .tile[data-value="2"] { background-color: #eee4da; }
        .tile[data-value="4"] { background-color: #ede0c8; }
        .tile[data-value="8"] { background-color: #f2b179; color: #f9f6f2; }
        .tile[data-value="16"] { background-color: #f59563; color: #f9f6f2; }
        .tile[data-value="32"] { background-color: #f67c5f; color: #f9f6f2; }
        .tile[data-value="64"] { background-color: #f65e3b; color: #f9f6f2; }
        .tile[data-value="128"] { background-color: #edcf72; color: #f9f6f2; }
        .tile[data-value="256"] { background-color: #edcc61; color: #f9f6f2; }
        .tile[data-value="512"] { background-color: #edc850; color: #f9f6f2; }
        .tile[data-value="1024"] { background-color: #edc53f; color: #f9f6f2; }
        .tile[data-value="2048"] { background-color: #edc22e; color: #f9f6f2; }
        .controls {
            margin-top: 10px;
        }
        .controls button {
            padding: 10px 20px;
            font-size: 18px;
            margin: 5px;
            cursor: pointer;
        }
    </style>
</head>
<body>
    <h1>2048 Game</h1>
    <h2>Score: {{ score }}</h2>
    <div class="board">
        {% for row in board %}
            {% for tile in row %}
                <div class="tile" data-value="{{ tile }}">{{ tile if tile != 0 else '' }}</div>
            {% endfor %}
        {% endfor %}
    </div>
    <div class="controls">
        <button onclick="move('up')">⬆️ Up</button>
        <button onclick="move('left')">⬅️ Left</button>
        <button onclick="move('down')">⬇️ Down</button>
        <button onclick="move('right')">➡️ Right</button>
    </div>
    <form method="POST" action="/">
        <button type="submit">Restart Game</button>
    </form>
    <script>
        function move(direction) {
            fetch('/move', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ direction: direction }),
            })
            .then(response => response.json())
            .then(data => {
                if (data.game_over) {
                    alert('Game Over!');
                }
                location.reload();
            });
        }
    </script>
</body>
</html>
"""

# 2048 Game Logic
def init_board():
    board = np.zeros((4, 4), dtype=int)
    add_random_tile(board)
    add_random_tile(board)
    return board

def add_random_tile(board):
    empty_cells = list(zip(*np.where(board == 0)))
    if empty_cells:
        r, c = random.choice(empty_cells)
        board[r, c] = random.choice([2, 4])

def merge_left(row):
    new_row = [tile for tile in row if tile != 0]
    for i in range(len(new_row) - 1):
        if new_row[i] == new_row[i + 1]:
            new_row[i] *= 2
            new_row[i + 1] = 0
    new_row = [tile for tile in new_row if tile != 0]
    return new_row + [0] * (4 - len(new_row))

def move_left(board):
    return np.array([merge_left(row) for row in board])

def rotate_board(board):
    return np.rot90(board, -1)

def move_right(board):
    rotated = rotate_board(rotate_board(board))
    moved = move_left(rotated)
    return rotate_board(rotate_board(moved))

def move_up(board):
    rotated = rotate_board(rotate_board(rotate_board(board)))
    moved = move_left(rotated)
    return rotate_board(moved)

def move_down(board):
    rotated = rotate_board(board)
    moved = move_left(rotated)
    return rotate_board(rotate_board(rotate_board(moved)))

def check_game_over(board):
    if 0 in board:
        return False
    for r in range(4):
        for c in range(3):
            if board[r, c] == board[r, c + 1]:
                return False
            if board[c, r] == board[c + 1, r]:
                return False
    return True

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        board = init_board()
        score = 0
    else:
        board = np.array(session.get('board', init_board()))
        score = session.get('score', 0)

    session['board'] = board.tolist()
    session['score'] = score
    return render_template_string(TEMPLATE, board=board, score=score)

@app.route("/move", methods=["POST"])
def move():
    board = np.array(session.get('board'))
    direction = request.json['direction']
    
    if direction == "up":
        new_board = move_up(board)
    elif direction == "left":
        new_board = move_left(board)
    elif direction == "down":
        new_board = move_down(board)
    elif direction == "right":
        new_board = move_right(board)
    
    if not np.array_equal(new_board, board):
        add_random_tile(new_board)
        session['board'] = new_board.tolist()
        session['score'] += np.sum(new_board) - np.sum(board)

    game_over = check_game_over(new_board)
    
    return jsonify({"game_over": game_over})

def check_port(port):
    """Check if the port is available."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) != 0

if __name__ == "__main__":
    app.secret_key = 'secret!'
    
    # Default port
    port = 5555
    
    # Check if the default port is available
    if not check_port(port):
        print(f"Port {port} is in use. Trying another port...")
        while not check_port(port):
            port += 1
        print(f"Using port {port} instead.")
    
    app.run(debug=True, port=port)
