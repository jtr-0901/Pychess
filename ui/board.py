from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.widget import Widget
from kivy.uix.image import Image
from kivy.graphics import Color, Rectangle, RoundedRectangle, Ellipse
from kivy.animation import Animation
from kivy.core.window import Window
from engine.chess_logic import GameLogic
from kivy.properties import ObjectProperty, NumericProperty, StringProperty, BooleanProperty
from kivy.clock import Clock
import chess
import os

class ChessPiece(Image):
    piece_type = StringProperty('')
    color_type = StringProperty('')
    square_name = StringProperty('')
    
    def __init__(self, piece_char, square_name, **kwargs):
        super().__init__(**kwargs)
        self.piece_char = piece_char
        self.square_name = square_name
        self.allow_stretch = True
        self.keep_ratio = True
        
        color_prefix = 'w' if piece_char.isupper() else 'b'
        filename = f"{color_prefix}{piece_char.lower()}.png"
        assets_dir = os.path.join(os.path.dirname(__file__), '..', 'assets', 'pieces')
        self.source = os.path.join(assets_dir, filename)


class ChessBoardUI(RelativeLayout):
    game_logic = ObjectProperty(None)
    
    def __init__(self, game_logic, on_move_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.game_logic = game_logic
        self.on_move_callback = on_move_callback
        self.pieces = {} # dict mapping square_name -> ChessPiece
        self.selected_square = None
        self.legal_moves_for_selected = []
        
        self.bind(size=self.draw_board, pos=self.draw_board)

    def draw_board(self, *args):
        self.canvas.clear()
        
        # Make board perfectly square based on the smaller dimension
        board_size = min(self.width, self.height)
        self.square_size = board_size / 8
        
        # Center the board
        self.start_x = (self.width - board_size) / 2
        self.start_y = (self.height - board_size) / 2
        
        with self.canvas:
            for row in range(8):
                for col in range(8):
                    is_light = (row + col) % 2 != 0
                    
                    if is_light:
                        Color(0.93, 0.93, 0.82, 1) # Modern cream
                    else:
                        Color(0.46, 0.59, 0.34, 1) # Modern green
                        
                    rect_pos = (self.start_x + col * self.square_size, self.start_y + row * self.square_size)
                    Rectangle(pos=rect_pos, size=(self.square_size, self.square_size))
                    
                    # Highlight selected square
                    square_name = chess.square_name(chess.square(col, row))
                    if square_name == self.selected_square:
                        Color(0.96, 0.96, 0.41, 0.7) # Premium Yellow
                        Rectangle(pos=rect_pos, size=(self.square_size, self.square_size))
                        
                    # Highlight legal moves
                    if square_name in self.legal_moves_for_selected:
                        Color(0, 0, 0, 0.15) # Subtle dark dot
                        dot_size = self.square_size * 0.3
                        offset = (self.square_size - dot_size) / 2
                        Ellipse(pos=(rect_pos[0] + offset, rect_pos[1] + offset), size=(dot_size, dot_size))

        self.update_pieces()
        
    def _get_coords_from_square(self, square_name):
        square_int = chess.parse_square(square_name)
        col = chess.square_file(square_int)
        row = chess.square_rank(square_int)
        x = self.start_x + col * self.square_size
        y = self.start_y + row * self.square_size
        return x, y

    def update_pieces(self):
        # Remove old pieces
        for child in list(self.children):
            if isinstance(child, ChessPiece):
                self.remove_widget(child)
                
        self.pieces.clear()
        
        board_layout = self.game_logic.get_board_2d()
        for square_name, piece_char in board_layout.items():
            piece = ChessPiece(piece_char=piece_char, square_name=square_name)
            piece.size_hint = (None, None)
            piece.size = (self.square_size, self.square_size)
            x, y = self._get_coords_from_square(square_name)
            piece.pos = (x, y)
            
            self.add_widget(piece)
            self.pieces[square_name] = piece
            
    def on_touch_down(self, touch):
        # Convert touch to board coordinates
        if not self.collide_point(*touch.pos):
            return super().on_touch_down(touch)
            
        local_x, local_y = self.to_local(touch.x, touch.y)
        board_size = min(self.width, self.height)
        if local_x < self.start_x or local_x > self.start_x + board_size or \
           local_y < self.start_y or local_y > self.start_y + board_size:
            return super().on_touch_down(touch)
            
        col = int((local_x - self.start_x) / self.square_size)
        row = int((local_y - self.start_y) / self.square_size)
        
        # Ensure within bounds
        col = max(0, min(7, col))
        row = max(0, min(7, row))
        
        clicked_square = chess.square_name(chess.square(col, row))
        
        if self.selected_square:
            if clicked_square in self.legal_moves_for_selected:
                # Attempt to move
                move_uci = self.selected_square + clicked_square
                # Handle promotion (auto queen for simplicity)
                move_obj = chess.Move.from_uci(move_uci)
                if move_obj not in self.game_logic.board.legal_moves:
                    move_uci += 'q' # try promotion
                    
                self._animate_move(self.selected_square, clicked_square, move_uci)
                self.selected_square = None
                self.legal_moves_for_selected = []
                self.draw_board()
                return True
            else:
                # Reset selection if clicking elsewhere
                self.selected_square = None
                self.legal_moves_for_selected = []
                # Fall through to possibly select another piece

        piece = self.game_logic.board.piece_at(chess.parse_square(clicked_square))
        if piece and piece.color == self.game_logic.board.turn:
            self.selected_square = clicked_square
            self.legal_moves_for_selected = self.game_logic.get_legal_moves(clicked_square)
            
        self.draw_board()
        return True

    def _animate_move(self, start_sq, end_sq, move_uci):
        if start_sq in self.pieces:
            piece = self.pieces[start_sq]
            target_x, target_y = self._get_coords_from_square(end_sq)
            
            anim = Animation(x=target_x, y=target_y, duration=0.2, t='in_out_quad')
            
            def finalize_move(*args):
                self.game_logic.push_move(move_uci)
                self.update_pieces() # Redraw board logic
                if self.on_move_callback:
                    self.on_move_callback()
                    
            anim.bind(on_complete=finalize_move)
            anim.start(piece)
        else:
            self.game_logic.push_move(move_uci)
            self.update_pieces()
            if self.on_move_callback:
                self.on_move_callback()

    def process_bot_move(self, move_uci):
        if not move_uci:
            return
        start_sq = move_uci[:2]
        end_sq = move_uci[2:4]
        self._animate_move(start_sq, end_sq, move_uci)
