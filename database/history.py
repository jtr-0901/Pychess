import sqlite3
import os
import datetime

DB_PATH = os.path.join(os.path.dirname(__file__), '..', 'chess_history.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS games (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            white_player TEXT NOT NULL,
            black_player TEXT NOT NULL,
            result TEXT NOT NULL,
            pgn TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

def save_game(white: str, black: str, result: str, pgn: str):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO games (white_player, black_player, result, pgn, timestamp)
        VALUES (?, ?, ?, ?, ?)
    ''', (white, black, result, pgn, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def get_all_games():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, white_player, black_player, result, pgn, timestamp FROM games ORDER BY id DESC')
    rows = cursor.fetchall()
    conn.close()
    
    games = []
    for row in rows:
        games.append({
            'id': row[0],
            'white': row[1],
            'black': row[2],
            'result': row[3],
            'pgn': row[4],
            'timestamp': row[5]
        })
    return games
