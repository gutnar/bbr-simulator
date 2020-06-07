from random import random
from math import pi
import numpy as np
import pymunk

from bbr_simulator.camera import Camera
from bbr_simulator.robot import Robot
from bbr_simulator.ball import Ball
from bbr_simulator.collisions import *


class Game(pymunk.Space):
  # Constants
  ROBOTS = 1
  BALLS = 11

  AREA_WIDTH = 8.100
  AREA_HEIGHT = 6.000
  PLAY_AREA_WIDTH = 6.100
  PLAY_AREA_HEIGHT = 4.000
  COMPETITION_AREA_WIDTH = 4.600
  COMPETITION_AREA_HEIGHT = 3.100
  LINE_WIDTH = 0.050

  BACKBOARD_WIDTH = 0.660
  BACKBOARD_HEIGHT = 0.800
  BACKBOARD_DEPTH = 0.01
  BASKET_HEIGHT = 0.500
  BASKET_OUTER_RADIUS = 0.160 / 2
  BASKET_INNER_RADIUS = 0.148 / 2

  BALL_MASS = 0.024
  BALL_RADIUS = 0.040 / 2
  BALL_FREE_PADDING = 0.9

  ROBOT_MASS = 4
  ROBOT_RADIUS = 0.350 / 2
  ROBOT_HEIGHT = 0.15

  ROBOT_CAMERA_X = 0
  ROBOT_CAMERA_Y = 0
  ROBOT_CAMERA_Z = 0.3
  ROBOT_CAMERA_R = pi / 2.6
  ROBOT_CAMERA_FOV = 45
  ROBOT_CAMERA_ASPECT = 16.0 / 9.0
  ROBOT_CAMERA_NEAR = 0.2
  ROBOT_CAMERA_FAR = 5

  # Physics
  COLLISION_TYPE_ROBOT = 1
  COLLISION_TYPE_BALL = 2
  COLLISION_TYPE_BASKET = 3
  COLLISION_TYPE_WALL = 4

  # State
  balls = []
  robots = []
  camera = None

  def __init__(self, **kwargs):
    super().__init__()

    self.__dict__.update(kwargs)
    self.camera = Camera(self)

    self.damping = 0.75
    self.setup_geometry()

    if isinstance(self.ROBOTS, int):
      self.setup_robots(self.ROBOTS)
    else:
      self.robots = [Robot(self, "r" + str(i), p[0], p[1], 0, p[2]) for i, p in enumerate(self.ROBOTS)]

    if isinstance(self.BALLS, int):
      self.setup_balls(self.BALLS)
    else:
      self.balls = [
        Ball(self, "b" + str(i), p[0], p[1], self.BALL_RADIUS) for i, p in enumerate(self.BALLS)
      ]

    # Collision handlers
    self.add_collision_handler(
      self.COLLISION_TYPE_ROBOT, self.COLLISION_TYPE_BALL
    ).begin = handle_robot_ball_collision

    self.add_collision_handler(
      self.COLLISION_TYPE_BALL, self.COLLISION_TYPE_BALL
    ).begin = handle_ball_ball_collision

    self.add_collision_handler(
      self.COLLISION_TYPE_BALL, self.COLLISION_TYPE_BASKET
    ).begin = handle_ball_basket_collision

    self.add_collision_handler(
      self.COLLISION_TYPE_BALL, self.COLLISION_TYPE_WALL
    ).begin = handle_ball_wall_collision

  def setup_geometry(self):
    walls = (
      # Outer walls
      pymunk.Segment(
        self.static_body,
        (-self.AREA_WIDTH/2, -self.AREA_HEIGHT/2),
        (self.AREA_WIDTH/2, -self.AREA_HEIGHT/2),
        0.01
      ),
      pymunk.Segment(
        self.static_body,
        (-self.AREA_WIDTH/2, self.AREA_HEIGHT/2),
        (self.AREA_WIDTH/2, self.AREA_HEIGHT/2),
        0.01
      ),
      pymunk.Segment(
        self.static_body,
        (-self.AREA_WIDTH/2, -self.AREA_HEIGHT/2),
        (-self.AREA_WIDTH/2, self.AREA_HEIGHT/2),
        0.01
      ),
      pymunk.Segment(
        self.static_body,
        (self.AREA_WIDTH/2, -self.AREA_HEIGHT/2),
        (self.AREA_WIDTH/2, self.AREA_HEIGHT/2),
        0.01
      ),
      # Basket backboards
      pymunk.Segment(
        self.static_body,
        (-self.COMPETITION_AREA_WIDTH/2, -self.BACKBOARD_WIDTH/2),
        (-self.COMPETITION_AREA_WIDTH/2, self.BACKBOARD_WIDTH/2),
        self.BACKBOARD_DEPTH * 2
      ),
      pymunk.Segment(
        self.static_body,
        (self.COMPETITION_AREA_WIDTH/2, -self.BACKBOARD_WIDTH/2),
        (self.COMPETITION_AREA_WIDTH/2, self.BACKBOARD_WIDTH/2),
        self.BACKBOARD_DEPTH * 2
      )
    )

    tubes = (
      # Basket tubes
      pymunk.Circle(
        self.static_body,
        self.BASKET_OUTER_RADIUS,
        (-self.COMPETITION_AREA_WIDTH/2 + self.BASKET_OUTER_RADIUS, 0)
      ),
      pymunk.Circle(
        self.static_body,
        self.BASKET_OUTER_RADIUS,
        (self.COMPETITION_AREA_WIDTH/2 - self.BASKET_OUTER_RADIUS, 0)
      )
    )

    for wall in walls:
      wall.elasticity = 0.3
      wall.collision_type = self.COLLISION_TYPE_WALL

    for tube in tubes:
      tube.elasticity = 0.3
      tube.collision_type = self.COLLISION_TYPE_BASKET

    self.add(walls)
    self.add(tubes)

  def setup_robots(self, n):
    if n > 0:
      self.robots.append(Robot(
        self,
        "r0",
        -self.COMPETITION_AREA_WIDTH/2 + self.ROBOT_RADIUS + self.LINE_WIDTH,
        -self.COMPETITION_AREA_HEIGHT/2 + self.ROBOT_RADIUS + self.LINE_WIDTH,
        0,
        -pi/4
      ))
    
    if n > 1:
      self.robots.append(Robot(
        self,
        "r1",
        self.COMPETITION_AREA_WIDTH/2 - self.ROBOT_RADIUS - self.LINE_WIDTH,
        self.COMPETITION_AREA_HEIGHT/2 - self.ROBOT_RADIUS - self.LINE_WIDTH,
        0,
        pi*3/4
      ))

  def setup_balls(self, n):
    if n > 0:
      self.balls = [Ball(self, "b0", 0, 0, self.BALL_RADIUS)]

    if n > 1:
      for i in range((n - 1) // 2):
        ball = Ball(
          self,
          "b" + str(i+1),
          (random() - 0.5) * (self.COMPETITION_AREA_WIDTH - self.BALL_FREE_PADDING),
          (random() - 0.5) * (self.COMPETITION_AREA_HEIGHT - self.BALL_FREE_PADDING),
          self.BALL_RADIUS
        )

        self.balls.append(ball)
        self.balls.append(Ball(
          self,
          "b" + str(i+1+(n - 1) // 2),
          -ball.position[0],
          -ball.position[1],
          ball.z
        ))
  
  def send_action(self, robot_index, action):
    self.robots[robot_index].send_action(action)

  def update(self, dt=1.0/60):
    self.step(dt)

  def get_constants(self):
    return {
      "AREA_WIDTH": self.AREA_WIDTH,
      "AREA_HEIGHT": self.AREA_HEIGHT,
      "PLAY_AREA_WIDTH": self.PLAY_AREA_WIDTH,
      "PLAY_AREA_HEIGHT": self.PLAY_AREA_HEIGHT,
      "COMPETITION_AREA_WIDTH": self.COMPETITION_AREA_WIDTH,
      "COMPETITION_AREA_HEIGHT": self.COMPETITION_AREA_HEIGHT,
      "LINE_WIDTH": self.LINE_WIDTH,
      "BACKBOARD_WIDTH": self.BACKBOARD_WIDTH,
      "BACKBOARD_HEIGHT": self.BACKBOARD_HEIGHT,
      "BACKBOARD_DEPTH": self.BACKBOARD_DEPTH,
      "BASKET_HEIGHT": self.BASKET_HEIGHT,
      "BASKET_OUTER_RADIUS": self.BASKET_OUTER_RADIUS,
      "BASKET_INNER_RADIUS": self.BASKET_INNER_RADIUS,
      "BALL_RADIUS": self.BALL_RADIUS,
      "BALL_FREE_PADDING": self.BALL_FREE_PADDING,
      "ROBOT_RADIUS": self.ROBOT_RADIUS,
      "ROBOT_HEIGHT": self.ROBOT_HEIGHT,
      "ROBOT_CAMERA_X": self.ROBOT_CAMERA_X,
      "ROBOT_CAMERA_Y": self.ROBOT_CAMERA_Y,
      "ROBOT_CAMERA_Z": self.ROBOT_CAMERA_Z,
      "ROBOT_CAMERA_R": self.ROBOT_CAMERA_R,
      "ROBOT_CAMERA_FOV": self.ROBOT_CAMERA_FOV,
      "ROBOT_CAMERA_ASPECT": self.ROBOT_CAMERA_ASPECT,
      "ROBOT_CAMERA_NEAR": self.ROBOT_CAMERA_NEAR,
      "ROBOT_CAMERA_FAR": self.ROBOT_CAMERA_FAR,
    }

  def get_state(self, robot_index=None):
    if robot_index is None:
      return {
        "robots": [robot.get_state() for robot in self.robots],
        "balls": [ball.get_state() for ball in self.balls]
      }
    
    return self.robots[robot_index].get_vision_state(self)
