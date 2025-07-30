#!/bin/python3
# Created by Jacobus Burger (2025-06-14)
# Info:
#   Play the game Pong in terminal!
# See:
#   https://en.wikipedia.org/wiki/Pong
from math import floor, ceil
import os
from random import choice
from sys import argv
from time import sleep
import argparse
import curses



# DONE:
# - add const variable for paddle height  (before 2025-06-25, added 2025-06-23)
# - add CLI controls for madness-mode and paddle_height among other things like refresh speed and more.  (before 2025-06-25, added 2025-06-23)
# - interestingly, logic lets paddles move on x too. Add as feature activated with "--madness" flag  (before 2025-06-25, added 2025-06-23) 
# - check it works on other platforms  (before 2025-06-30, done 2025-06-25)
# TODO:
# - create distributions  (before 2025-06-30)
#   - setup project so it's available through PyPI
#   - publish on itch.io
# - finished, move on to make ultrapong with pygame or something...


def pong(madness, paddle, speed):
    # initialize ncurses
    stdscr = curses.initscr()
    curses.curs_set(False)
    curses.noecho()
    curses.cbreak()
    curses.start_color()

    # set up colors
    blank_color = 1
    blank_char = " "
    ball_color = 2
    ball_char = "*"
    player_color = 3
    opponent_color = 4
    paddle_char = "I"
    curses.init_pair(blank_color, curses.COLOR_BLACK, curses.COLOR_BLACK)
    curses.init_pair(ball_color, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(player_color, curses.COLOR_RED, curses.COLOR_BLACK)
    curses.init_pair(opponent_color, curses.COLOR_BLUE, curses.COLOR_BLACK)

    # initialize game window
    height, width = stdscr.getmaxyx()
    win = curses.newwin(height, width, 0, 0)
    win.keypad(True)
    win.timeout(speed if speed else 100)
    win.border()

    try:
        # begin pong
        # set paddle size based on arg
        paddle_height = paddle if paddle else 5
        if paddle_height >= height // 4:
            paddle_height = height // 4
        # [player, opponent]
        scores = [0, 0]
        game = True
        while game:
            # set initial position and direction at start of each round
            x, y = width // 2, height // 2
            dx = choice([-1, 1])
            dy = choice([-1, 1])

            # y, x
            player_paddle = [height // 2, 2]
            opponent_paddle = [height // 2, width - 2]

            # each round
            while True:
                # get input
                key = win.getch()
                # quit on q key
                if key == ord('q'):
                    game = False
                    break
                # move paddle up or down based on input
                #   move player paddle up
                if key == ord('w'):
                    if player_paddle[0] > ceil(paddle_height / 2):
                        player_paddle[0] -= 1
                #   move player paddle down
                if key == ord('s'):
                    if player_paddle[0] < height - (ceil(paddle_height / 2) + 1):
                        player_paddle[0] += 1
                #   move opponent paddle up
                if key == ord('i'):
                    if opponent_paddle[0] > ceil(paddle_height / 2):
                        opponent_paddle[0] -= 1
                #   move opponent paddle down
                if key == ord('k'):
                    if opponent_paddle[0] < height - (ceil(paddle_height / 2) + 1):
                        opponent_paddle[0] += 1
                # madness mode: move paddles on x plane too!
                if madness:
                    # move player paddle left
                    if key == ord('a'):
                        if player_paddle[1] > 1:
                            player_paddle[1] -= 1
                    # move player paddle right
                    if key == ord('d'):
                        if player_paddle[1] < width - 1:
                            player_paddle[1] += 1
                    # move opponent paddle left
                    if key == ord('j'):
                        if opponent_paddle[1] > 1:
                            opponent_paddle[1] -= 1
                    # move opponent paddle right
                    if key == ord('l'):
                        if opponent_paddle[1] < width - 1:
                            opponent_paddle[1] += 1

                # update pong
                #   update ball position
                y = y + dy
                x = x + dx
                # bounce ball against floor and ceiling
                if y + dy <= 1 or y + dy >= height - 1:
                    dy = dy * -1
                # bounce against paddles
                #   bounce from player paddle
                if x + dx == player_paddle[1] and y in [*range(player_paddle[0] - floor(paddle_height / 2), player_paddle[0] + ceil(paddle_height / 2))]:
                    dx = dx * -1
                #   bounce from opponent paddle
                if x + dx == opponent_paddle[1] and y in [*range(opponent_paddle[0] - floor(paddle_height / 2), opponent_paddle[0] + ceil(paddle_height / 2))]:
                    dx = dx * -1

                # update scores and start next round when hitting walls
                #   bounce from player paddle
                #   bounce from opponent paddle
                #   if on left wall (player, score to opponent)
                if x <= 1:
                    scores[1] += 1
                    break
                #   if on right wall (opponent, score to player)
                if x >= width - 1:
                    scores[0] += 1
                    break

                # render
                #   clear and draw window
                win.clear()
                win.border()
                #   draw ball
                win.addch(int(y), int(x), ord(ball_char), curses.color_pair(ball_color))
                #   draw paddles
                for player_y in range(player_paddle[0] - floor(paddle_height / 2), player_paddle[0] + ceil(paddle_height / 2)):
                    win.addch(int(player_y), int(player_paddle[1]), ord(paddle_char), curses.color_pair(player_color))
                for opponent_y in range(opponent_paddle[0] - floor(paddle_height / 2), opponent_paddle[0] + ceil(paddle_height / 2)):
                    win.addch(int(opponent_y), int(opponent_paddle[1]), ord(paddle_char), curses.color_pair(opponent_color))
                #   write scores
                win.addstr(int(height // 2), int(width // 8), "player: {}".format(scores[0]), curses.color_pair(player_color))
                win.addstr(int(height // 2), int(width // 4 * 3), "opponent: {}".format(scores[1]), curses.color_pair(opponent_color))
                #   write instructions
                if madness:
                    win.addstr(int(2), int(2), "wasd = ^<v>", curses.color_pair(player_color))
                else:
                    win.addstr(int(2), int(2), "ws = ^v", curses.color_pair(player_color))
                if madness:
                    win.addstr(int(2), int(width - 13), "ijkl = ^<v>", curses.color_pair(opponent_color))
                else:
                    win.addstr(int(2), int(width - 9), "ik = ^v", curses.color_pair(opponent_color))
                #   show visuals
                win.refresh()
    except:
        pass
    # clean up and end
    curses.curs_set(True)
    curses.nocbreak()
    curses.echo()
    curses.endwin()
    os.system("clear") if os.name == "nt" else os.system("cls")



def main():
    # parse input of CLI
    parser = argparse.ArgumentParser(
        prog="PONG",
        description="An NCurses implementation of the classic game PONG.",
        epilog="Jacobus Burger (2025)"
    )
    parser.add_argument("-m", "--madness", action="store_true", help="madness mode")
    parser.add_argument("-p", "--paddle", type=int, help="paddle size")
    parser.add_argument("-s", "--speed", type=int, help="refresh rate")
    args = parser.parse_args()
    pong(args.madness, args.paddle, args.speed)


if __name__ == '__main__':
    main()
