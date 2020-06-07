from random import random
from math import pi
import numpy as np
import pymunk


def handle_robot_ball_collision(arbiter, game, data):
  robot = arbiter.shapes[0].body
  ball = arbiter.shapes[1].body

  if robot.thrower == 0:
    return True

  ball.launch(robot)
  robot.ball_in_thrower = True

  return False


def handle_ball_ball_collision(arbiter, game, data):
  return not (arbiter.shapes[0].body.launched or arbiter.shapes[1].body.launched)


def handle_ball_basket_collision(arbiter, game, data):
  ball = arbiter.shapes[0].body

  if ball.launched and np.min(ball.position - arbiter.shapes[1].offset) < game.BASKET_INNER_RADIUS:
    ball.launched = False
    ball.go_in_basket(arbiter.shapes[1])

    return False

  return True


def handle_ball_wall_collision(arbiter, game, data):
  arbiter.shapes[0].body.launched = False
  return True
