from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.core.window import Window
import os
import sys

# Ensure imports work from correct paths when packaged via buildozer
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database.history import init_db
from ui.screens import MenuScreen, DifficultyScreen, GameScreen, HistoryScreen, TimeSelectionScreen

class ChessApp(App):
    def build(self):
        # Initialize SQLite Database
        init_db()
        
        # Set a premium dark theme background color globally
        Window.clearcolor = (0.086, 0.082, 0.07, 1)
        
        sm = ScreenManager(transition=FadeTransition())
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(DifficultyScreen(name='difficulty'))
        sm.add_widget(TimeSelectionScreen(name='time_select'))
        sm.add_widget(GameScreen(name='game'))
        sm.add_widget(HistoryScreen(name='history'))
        
        return sm

if __name__ == '__main__':
    # For desktop testing simulate mobile size
    Window.size = (400, 700)
    ChessApp().run()
