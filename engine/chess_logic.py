import chess
import chess.pgn
import io

class GameLogic:
    def __init__(self):
        self.board = chess.Board()
        self.white_player = "Player"
        self.black_player = "Bot"
        self.mode = "PvB" # "PvB" or "PvP"
        
    def reset_game(self):
        self.board.reset()

    def load_fen(self, fen):
        self.board.set_fen(fen)

    def is_legal_move(self, uci_move: str) -> bool:
        try:
            move = chess.Move.from_uci(uci_move)
            return move in self.board.legal_moves
        except:
            return False

    def push_move(self, uci_move: str) -> bool:
        if self.is_legal_move(uci_move):
            self.board.push(chess.Move.from_uci(uci_move))
            return True
        return False
        
    def get_legal_moves(self, square: str):
        # square is like 'e2'
        square_int = chess.parse_square(square)
        moves = []
        for move in self.board.legal_moves:
            if move.from_square == square_int:
                moves.append(chess.square_name(move.to_square))
        return moves

    def is_game_over(self):
        return self.board.is_game_over()
        
    def get_game_result(self):
        return self.board.result()
        
    def undo_move(self):
        if len(self.board.move_stack) > 0:
            self.board.pop()
            # If playing against bot, pop twice to undo both
            if self.mode == "PvB" and len(self.board.move_stack) > 0:
                self.board.pop()

    def get_pgn(self) -> str:
        game = chess.pgn.Game.from_board(self.board)
        game.headers["White"] = self.white_player
        game.headers["Black"] = self.black_player
        exporter = chess.pgn.StringExporter(headers=True, variations=False, comments=False)
        return game.accept(exporter)

    def get_board_2d(self):
        # Returns dict of square -> piece (e.g. 'e2' -> 'P', 'd1' -> 'Q')
        board_layout = {}
        for square in chess.SQUARES:
            piece = self.board.piece_at(square)
            if piece:
                board_layout[chess.square_name(square)] = piece.symbol()
        return board_layout
        
    def is_check(self):
        return self.board.is_check()

    def is_checkmate(self):
        return self.board.is_checkmate()
