from textual.app import App, ComposeResult
from textual.widgets import Header, Footer, Static
from textual.widget import Widget
from textual.containers import Container, Horizontal, Vertical
from textual.reactive import reactive
from rich.console import RenderResult
from rich.text import Text
from rich.console import Group
import random
from enum import Enum
from typing import List, Tuple

N_ROWS = 14
N_COLS = 20

class State(Enum):
    PLAY = 0
    PAUSE = 1
    STOP = 2

class Direction(Enum):
    UP = (-1, 0)
    DOWN = (1, 0)
    LEFT = (0, -1)
    RIGHT = (0, 1)

class Snake:
    def __init__(self) -> None:
        self.body = [(N_ROWS // 2 - 1, N_COLS // 2 - 2)]
        self.direction = Direction.RIGHT
        self.next_direction = Direction.RIGHT
        self.grow_pending = False
    
    def move(self):
        self.direction = self.next_direction
        
        head_x, head_y = self.body[0]
        dx, dy = self.direction.value
        new_head = (head_x + dx, head_y + dy)
        
        self.body.insert(0, new_head)
        
        if not self.grow_pending:
            self.body.pop()
        else:
            self.grow_pending = False 
    
    def grow(self):
        self.grow_pending = True

    def change_direction(self, new_direction: Direction):
        if len(self.body) > 1:
            current_dx, current_dy = self.direction.value
            new_dx, new_dy = new_direction.value
            if (current_dx, current_dy) != (-new_dx, -new_dy):
                self.next_direction = new_direction
        else:
            self.next_direction = new_direction
    
    def check_self_collision(self) -> bool:
        head = self.body[0]
        return head in self.body[1:]
    
class Food:
    def __init__(self):
        self.position = (N_ROWS // 2 - 1, N_COLS // 2 + 1)
    
    def generate_position(self, snake_body: List[Tuple[int, int]] = None) -> Tuple[int, int]:
        if snake_body is None:
            snake_body = []
        
        while True:
            x = random.randint(0, N_ROWS - 1)
            y = random.randint(0, N_COLS - 1)
            if (x, y) not in snake_body:
                return (x, y)
    
    def respawn(self, snake_body: List[Tuple[int, int]]):
        self.position = self.generate_position(snake_body)

class GameBoard(Static):

    def __init__(self) -> None:
        super().__init__()
        self.snake = Snake()
        self.food = Food()
    
    def render(self) -> RenderResult:
        lines = []

        for row in range(N_ROWS):
            line = Text()
            for col in range(N_COLS):
                if (row, col) == self.snake.body[0]:
                    line.append("██", style="red")
                elif (row, col) in self.snake.body:
                    line.append("██", style="dim red")
                elif (row, col) == self.food.position:
                    line.append("██", style="bright_green")
                elif (row + col) % 2 == 0:
                    line.append("██", style="white")
                else:
                    line.append("██", style="bright_black")
            lines.append(line)

        return Group(*lines)

    def is_valid_position(self, x: int, y: int) -> bool:
        return 0 <= x < N_ROWS and 0 <= y < N_COLS

class TopBar(Widget):
    score = reactive(0)
    game_state = reactive(State.PLAY)

    def __init__(self, score: int = 0, game_state: State = State.PLAY):
        super().__init__()
        self.score = score
        self.game_state = game_state

    def watch_score(self, score: int) -> None:
        self.refresh()
    
    def watch_game_state(self, game_state: State) -> None:
        self.refresh()

    def compose(self) -> ComposeResult:
        yield Static(self.get_display_text(), id="score_display")
    
    def get_display_text(self) -> str:
        if self.game_state == State.STOP:
            return f"GAME OVER! Final Score: {self.score}"
        else:
            return f"Score: {self.score}"
    
    def on_mount(self) -> None:
        self.refresh()
    
    def refresh_display(self) -> None:
        """Manually refresh the display text"""
        score_widget = self.query_one("#score_display", Static)
        score_widget.update(self.get_display_text())

class SnakeApp(App):

    CSS_PATH = "snake.tcss"

    BINDINGS = [
        ("d", "toggle_dark", "Toggle dark mode"),
        ("up", "move_up", "Up"),
        ("down", "move_down", "Down"),
        ("left", "move_left", "Left"),
        ("right", "move_right", "Right"),
        ("r", "restart", "Restart"),
    ]

    def __init__(self):
        super().__init__()
        self.game_state = State.PLAY
        self.score = 0
        self.game_speed = 0.2
        self.game_timer = None

    def compose(self) -> ComposeResult:
        yield Header()
        yield Vertical(
            Horizontal(
                TopBar(score=self.score, game_state=self.game_state),
                Static("Use WASD or Arrow Keys to move | R to restart", id="instructions"),
            ),
            Container(
                GameBoard(),
                id="game_container"
            )
        )
        yield Footer()

    def on_mount(self):
        self.game_timer = self.set_interval(self.game_speed, self.game_tick)
        self.title = 'Snake'

    def game_tick(self):
        if self.game_state != State.PLAY:
            return
            
        board = self.query_one(GameBoard)
        
        board.snake.move()
        head_x, head_y = board.snake.body[0]

        if not board.is_valid_position(head_x, head_y):
            self.game_over()
            return

        if board.snake.check_self_collision():
            self.game_over()
            return
            
        if (head_x, head_y) == board.food.position:
            board.snake.grow()
            board.food.respawn(board.snake.body)
            self.score += 10
            
            top_bar = self.query_one(TopBar)
            top_bar.score = self.score
            top_bar.refresh_display()
            
            if self.score % 50 == 0:
                self.game_speed = max(0.05, self.game_speed - 0.01)
                if self.game_timer:
                    self.game_timer.pause()
                self.game_timer = self.set_interval(self.game_speed, self.game_tick)

        board.refresh()

    def game_over(self):
        """Handle game over state"""
        self.game_state = State.STOP
        
        top_bar = self.query_one(TopBar)
        top_bar.game_state = State.STOP
        top_bar.refresh_display()
        
        if self.game_timer:
            self.game_timer.pause()
    
    def action_restart(self):
        self.restart_game()
    
    def restart_game(self):
        self.game_state = State.PLAY
        self.score = 0
        self.game_speed = 0.2
        
        top_bar = self.query_one(TopBar)
        top_bar.score = 0
        top_bar.game_state = State.PLAY
        top_bar.refresh_display()
        
        board = self.query_one(GameBoard)
        board.snake = Snake()
        board.food = Food()
        board.refresh()
        
        if self.game_timer:
            self.game_timer.pause()
        self.game_timer = self.set_interval(self.game_speed, self.game_tick)

    def action_toggle_dark(self) -> None:
        self.theme = (
            "textual-dark" if self.theme == "textual-light" else "textual-light"
        )

    def action_move_up(self):
        if self.game_state == State.PLAY:
            board = self.query_one(GameBoard)
            board.snake.change_direction(Direction.UP)
    
    def action_move_down(self):
        if self.game_state == State.PLAY:
            board = self.query_one(GameBoard)
            board.snake.change_direction(Direction.DOWN)
    
    def action_move_left(self):
        if self.game_state == State.PLAY:
            board = self.query_one(GameBoard)
            board.snake.change_direction(Direction.LEFT)
    
    def action_move_right(self):
        if self.game_state == State.PLAY:
            board = self.query_one(GameBoard)
            board.snake.change_direction(Direction.RIGHT)

if __name__ == '__main__':
    SnakeApp().run()