# pylint: disable=invalid-name
import math
import random
from collections import namedtuple
from enum import Enum
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


Point = namedtuple("Point", "r, c ")

# rgb colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
GREEN1 = (34, 139, 34)
GREEN2 = (50, 205, 50)
BLACK = (0, 0, 0)

BLOCK_SIZE = 64
SPEED = 40


class SnakeGameAI:
    def __init__(self, r=16, c=8):
        self.r = r
        self.c = c
        # init display
        self.display = pygame.display.set_mode(
            (self.c * BLOCK_SIZE, self.r * BLOCK_SIZE)
        )
        pygame.display.set_caption("Snake")
        self.clock = pygame.time.Clock()
        # init GAME state
        self.direction = None
        self.score = 0

        self.snake = None
        self.head = None
        self.tail = None
        self.food = None
        self.board = np.zeros(shape=[self.r, self.c, 4], dtype=np.uint8)
        self.reset()

    def reset(self):
        # init game state
        self.direction = Direction.RIGHT
        self.score = 0
        self.frame_iteration = 0

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

        # print("init snake")
        # for snake in self.snake:
        #     print(snake.r, snake.c, self.board[snake.r, snake.c])
        self._place_food()

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

        # print("food")
        # if old_food is not None:
        #     print(
        #         "old food: ",
        #         old_food.r,
        #         " ",
        #         old_food.c,
        #         self.board[old_food.r, old_food.c],
        #     )
        # print(
        #     "old food: ",
        #     new_food.r,
        #     " ",
        #     new_food.c,
        #     self.board[new_food.r, new_food.c],
        # )

    def play_step(self, action):
        # action = [1, 0, 0]
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    action = [0, 1, 0]
                elif event.key == pygame.K_RIGHT:
                    action = [0, 0, 1]

        # 2. move
        my_reward = 0
        temp_head = self.head  # save old head
        self._move(action)  # update the head pos
        self.snake.insert(0, self.head)  # inset new head => increase size

        my_reward = my_reward + self._get_dir_reward(self.food, temp_head, self.head)
        # 3. check if game over
        my_game_over = False
        if self.is_collision() or self.frame_iteration > 100 * len(self.snake):
            my_game_over = True
            my_reward = my_reward - 10
            return my_reward, my_game_over, self.score

        self._set_board_head(
            temp_head, self.head
        )  # update head on board, after checking collision

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            my_reward = my_reward + 50
            # print("increase length")
            # print("init snake")
            # for snake in self.snake:
            #     print(snake.r, snake.c, self.board[snake.r, snake.c])
            self._place_food()
        else:
            temp_head = self.tail
            self.snake.pop()
            self.tail = self.snake[-1]
            self._set_board_tail(temp_head, self.tail)

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)
        # 6. return game over and score
        return my_reward, my_game_over, self.score

    def _get_dir_reward(self, food, old_head, new_head):
        prev_dist = math.sqrt((old_head.r - food.r) ** 2 + (old_head.c - food.c) ** 2)

        new_dist = math.sqrt((new_head.r - food.r) ** 2 + (new_head.c - food.c) ** 2)

        if new_dist == prev_dist:
            return 0
        elif new_dist > prev_dist:
            return -1
        else:
            return +1

    def _set_board_head(self, old_head: Point, new_head: Point):
        self.board[old_head.r, old_head.c, 0] = 0  # prev head 0
        self.board[old_head.r, old_head.c, 1] = 1  # make prev head = body
        self.board[new_head.r, new_head.c, 0] = 1  # set new head

        # print("head")
        # print(
        #     "old head: ",
        #     old_head.r,
        #     " ",
        #     old_head.c,
        #     " ",
        #     self.board[old_head.r, old_head.c],
        # )
        # print(
        #     "new head: ",
        #     new_head.r,
        #     " ",
        #     new_head.c,
        #     " ",
        #     self.board[new_head.r, new_head.c],
        # )

    def _set_board_tail(self, old_tail, new_tail):
        self.board[old_tail.r, old_tail.c, 1] = 0
        # print("tail")
        # print(
        #     "old tail: ",
        #     old_tail.r,
        #     " ",
        #     old_tail.c,
        #     " ",
        #     self.board[old_tail.r, old_tail.c],
        # )
        # print(
        #     "new tail: ",
        #     new_tail.r,
        #     " ",
        #     new_tail.c,
        #     " ",
        #     self.board[new_tail.r, new_tail.c],
        # )

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # hits boundary
        if pt.r > self.r - 1 or pt.r < 0 or pt.c > self.c - 1 or pt.c < 0:
            return True
        # hits itself
        if pt in self.snake[1:]:
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

    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx]  # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]  # right turn r -> d -> l -> u
        else:  # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]  # left turn r -> u -> l -> d

        self.direction = new_dir

        r = self.head.r
        c = self.head.c
        if self.direction == Direction.RIGHT:
            c += 1
        elif self.direction == Direction.LEFT:
            c -= 1
        elif self.direction == Direction.DOWN:
            r += 1
        elif self.direction == Direction.UP:
            r -= 1

        self.head = Point(r, c)


# if __name__ == "__main__":
#     game = SnakeGameAI()

#     # game loop
#     while True:
#         reward, game_over, score = game.play_step()
#         print("Reward", reward)
#         print("Game over", game_over)
#         print("Score", score)
#         if game_over is True:
#             break
#     print("final Reward", reward)
#     print("final Game over", game_over)
#     print("Final Score", score)

#     pygame.quit()
