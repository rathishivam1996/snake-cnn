# pylint: disable=invalid-name
import random
from enum import Enum
from collections import namedtuple
import numpy as np
import pygame

np.set_printoptions(threshold=np.inf)
pygame.init()
font = pygame.font.Font("arial.ttf", 25)
# font = pygame.font.SysFont('arial', 25)


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


Point = namedtuple("Point", "r, c")

# rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN1 = (34, 139, 34)
GREEN2 = (50, 205, 50)
BLACK = (0, 0, 0)

BLOCK_SIZE = 40
SPEED = 2


class SnakeGame:
    def __init__(self, r=10, c=10):
        self.r = r
        self.c = c
        # init display
        self.display = pygame.display.set_mode(
            (self.c * BLOCK_SIZE, self.r * BLOCK_SIZE)
        )

        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        # init game state
        self.direction = Direction.RIGHT
        self.score = 0
        self.head = None
        self.tail = None
        self.food = None
        self.board = np.zeros(shape=[self.r, self.c, 4], dtype=np.uint8)
        self._init_snake()
        self._place_food()

    def _init_snake(self):
        self.head = Point(self.r // 2, self.c // 2)
        b1 = Point(self.head.r, self.head.c - 1)
        self.tail = Point(self.head.r, self.head.c - (2 * 1))

        self.board[self.head.r, self.head.c, 0] = 1
        self.board[b1.r, b1.c, 1] = 1
        self.board[self.tail.r, self.tail.c, 1] = 1

        # init snake old
        self.snake = [
            self.head,
            b1,
            self.tail,
        ]

        print("init snake")
        for snake in self.snake:
            print(snake.r, snake.c, self.board[snake.r, snake.c])

    def _place_food(self):
        r = random.randint(0, (self.r - 1))
        c = random.randint(0, (self.c - 1))
        temp = Point(r=r, c=c)
        if temp in self.snake:
            self._place_food()
        else:
            self._set_board_food(self.food, temp)
            self.food = temp

    def _set_board_food(self, old_food, new_food):
        if old_food is not None:
            self.board[old_food.r, old_food.c, 2] = 0
        self.board[new_food.r, new_food.c, 2] = 1

        print("food")
        if old_food is not None:
            print(
                "old food: ",
                old_food.r,
                " ",
                old_food.c,
                self.board[old_food.r, old_food.c],
            )
        print(
            "old food: ",
            new_food.r,
            " ",
            new_food.c,
            self.board[new_food.r, new_food.c],
        )

    def play_step(self):
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN:
                    self.direction = Direction.DOWN

        # 2. move
        temp = self.head  # save old head
        self._move(self.direction)  # update the head pos
        self.snake.insert(0, self.head)  # inset new head => increase size

        # 3. check if game over
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score

        self._set_board_head(
            temp, self.head
        )  # update head on board, after checking collision

        # 4. place new food or just move
        if self.head == self.food:
            print("increase length")
            print("init snake")
            for snake in self.snake:
                print(snake.r, snake.c, self.board[snake.r, snake.c])
            self.score += 1
            self._place_food()
        else:
            temp = self.tail
            self.snake.pop()
            self.tail = self.snake[-1]
            self._set_board_tail(temp, self.tail)

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return game_over, self.score

    def _set_board_head(self, old_head: Point, new_head: Point):
        self.board[old_head.r, old_head.c, 0] = 0  # prev head 0
        self.board[old_head.r, old_head.c, 1] = 1  # make prev head = body
        self.board[new_head.r, new_head.c, 0] = 1  # set new head

        print("head")
        print(
            "old head: ",
            old_head.r,
            " ",
            old_head.c,
            " ",
            self.board[old_head.r, old_head.c],
        )
        print(
            "new head: ",
            new_head.r,
            " ",
            new_head.c,
            " ",
            self.board[new_head.r, new_head.c],
        )

    def _set_board_tail(self, old_tail, new_tail):
        self.board[old_tail.r, old_tail.c, 1] = 0

        print("tail")
        print(
            "old tail: ",
            old_tail.r,
            " ",
            old_tail.c,
            " ",
            self.board[old_tail.r, old_tail.c],
        )
        print(
            "new tail: ",
            new_tail.r,
            " ",
            new_tail.c,
            " ",
            self.board[new_tail.r, new_tail.c],
        )

    def _is_collision(self):
        print("_is_collision")
        # hits boundary
        if (
            self.head.c > self.c - 1
            or self.head.c < 0
            or self.head.r > self.r - 1
            or self.head.r < 0
        ):
            print("collision")
            return True
        # hits itself
        if self.head in self.snake[1:]:
            return True
        return False

    def _update_ui(self):
        # fill board
        self.display.fill(BLACK)
        # draw head
        pygame.draw.rect(
            self.display,
            GREEN1,
            pygame.Rect(
                self.head.c * BLOCK_SIZE,
                self.head.r * BLOCK_SIZE,
                BLOCK_SIZE,
                BLOCK_SIZE,
            ),
        )
        # draw body
        for pt in self.snake[1:]:
            pygame.draw.rect(
                self.display,
                GREEN2,
                pygame.Rect(
                    (pt.c * BLOCK_SIZE), (pt.r * BLOCK_SIZE), BLOCK_SIZE, BLOCK_SIZE
                ),
            )
        # draw food
        pygame.draw.rect(
            self.display,
            RED,
            pygame.Rect(
                self.food.c * BLOCK_SIZE,
                self.food.r * BLOCK_SIZE,
                BLOCK_SIZE,
                BLOCK_SIZE,
            ),
        )
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _move(self, direction):
        print("_move")
        r = self.head.r
        c = self.head.c
        if direction == Direction.RIGHT:
            c += 1
        elif direction == Direction.LEFT:
            c -= 1
        elif direction == Direction.DOWN:
            r += 1
        elif direction == Direction.UP:
            r -= 1

        self.head = Point(r, c)


if __name__ == "__main__":
    game = SnakeGame()

    # game loop
    while True:
        game_over, score = game.play_step()

        if game_over is True:
            break

    print("Final Score", score)

    pygame.quit()
