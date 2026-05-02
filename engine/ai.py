import chess
import random

# Piece values
piece_values = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 20000
}

# Simplified piece square tables (PST) for positional evaluation
# Values are centered for white, reverse for black
pawn_pst = [
    0,  0,  0,  0,  0,  0,  0,  0,
    50, 50, 50, 50, 50, 50, 50, 50,
    10, 10, 20, 30, 30, 20, 10, 10,
    5,  5, 10, 25, 25, 10,  5,  5,
    0,  0,  0, 20, 20,  0,  0,  0,
    5, -5,-10,  0,  0,-10, -5,  5,
    5, 10, 10,-20,-20, 10, 10,  5,
    0,  0,  0,  0,  0,  0,  0,  0
]

knight_pst = [
    -50,-40,-30,-30,-30,-30,-40,-50,
    -40,-20,  0,  0,  0,  0,-20,-40,
    -30,  0, 10, 15, 15, 10,  0,-30,
    -30,  5, 15, 20, 20, 15,  5,-30,
    -30,  0, 15, 20, 20, 15,  0,-30,
    -30,  5, 10, 15, 15, 10,  5,-30,
    -40,-20,  0,  5,  5,  0,-20,-40,
    -50,-40,-30,-30,-30,-30,-40,-50
]

def evaluate_board(board: chess.Board):
    if board.is_checkmate():
        return -99999 if board.turn else 99999
    if board.is_stalemate() or board.is_insufficient_material():
        return 0
        
    score = 0
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece is not None:
            val = piece_values[piece.piece_type]
            
            # Add positional bonus
            if piece.piece_type == chess.PAWN:
                pst_val = pawn_pst[square] if piece.color == chess.WHITE else pawn_pst[chess.square_mirror(square)]
            elif piece.piece_type == chess.KNIGHT:
                pst_val = knight_pst[square] if piece.color == chess.WHITE else knight_pst[chess.square_mirror(square)]
            else:
                pst_val = 0 # Simplify other pieces positioning for now
                
            val += pst_val
            
            if piece.color == chess.WHITE:
                score += val
            else:
                score -= val
                
    return score

def minimax(board: chess.Board, depth: int, alpha: float, beta: float, maximizing_player: bool):
    if depth == 0 or board.is_game_over():
        return evaluate_board(board), None

    best_move = None
    legal_moves = list(board.legal_moves)
    
    # Simple move ordering (checks/captures first)
    legal_moves.sort(key=lambda m: board.is_capture(m) or board.gives_check(m), reverse=True)

    if maximizing_player:
        max_eval = float('-inf')
        for move in legal_moves:
            board.push(move)
            eval_score, _ = minimax(board, depth - 1, alpha, beta, False)
            board.pop()
            
            if eval_score > max_eval:
                max_eval = eval_score
                best_move = move
                
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        return max_eval, best_move
    else:
        min_eval = float('inf')
        for move in legal_moves:
            board.push(move)
            eval_score, _ = minimax(board, depth - 1, alpha, beta, True)
            board.pop()
            
            if eval_score < min_eval:
                min_eval = eval_score
                best_move = move
                
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        return min_eval, best_move

def get_best_move(board: chess.Board, difficulty: str = "Medium"):
    # depth mapping
    depths = {
        "Easy": 1,
        "Medium": 2,
        "Hard": 3,
        "Expert": 4
    }
    depth = depths.get(difficulty, 2)
    
    # Slight randomization for Easy so it doesn't play the exact same move
    if difficulty == "Easy" and random.random() < 0.3:
        return random.choice(list(board.legal_moves)).uci()
        
    _, move = minimax(board, depth, float('-inf'), float('inf'), board.turn == chess.WHITE)
    return move.uci() if move else None
