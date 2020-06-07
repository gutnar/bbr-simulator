import numpy as np
import pymunk


class Robot(pymunk.Body):
  def __init__(self, game, id, x, y, z, angle):
    super().__init__(game.ROBOT_MASS, pymunk.moment_for_circle(game.ROBOT_MASS, 0, game.ROBOT_RADIUS))

    self.id = id
    self.z = z
    self.target_velocity = 0, 0
    self.target_angular_velocity = 0

    self.thrower = 0
    self.angle = angle
    self.position = x, y
    self.velocity = 0, 0
    self.angular_velocity = 0
    self.ball_in_thrower = False

    shape = pymunk.Circle(self, game.ROBOT_RADIUS)
    shape.collision_type = game.COLLISION_TYPE_ROBOT

    game.add(self, shape)

    def constant_velocity(body, gravity, damping, dt):
      body.damping = 0
      body.velocity = np.array((
        (np.cos(self.angle), -np.sin(self.angle)),
        (np.sin(self.angle), np.cos(self.angle)),
      )) @ self.target_velocity
      body.angular_velocity = self.target_angular_velocity

    self.velocity_func = constant_velocity

  def get_state(self):
    return {
      "id": self.id,
      "x": self.position[0],
      "y": self.position[1],
      "z": self.z,
      "r": self.angle
    }

  def get_vision_state(self, game):
    state = { "baskets": {}, "balls": [], "ball_in_thrower": self.ball_in_thrower }
    projection_matrix = game.camera.get_projection_matrix(self)

    # Get basket locations on screen
    for basket, side in (("magenta", -1), ("blue", 1)):
      center = projection_matrix @ np.array((
        side * (game.COMPETITION_AREA_WIDTH/2 - game.BASKET_OUTER_RADIUS),
        0, 0, 1
      ))

      center = center[:2] / center[3] / 2

      if np.max(np.abs(center)) < 0.5:
        state["baskets"][basket] = center

    # Get ball locations on screen
    for ball in game.balls:
      if ball.launched or ball.in_basket:
        continue

      if abs(ball.position[0]) + game.BALL_RADIUS > game.COMPETITION_AREA_WIDTH/2:
        continue

      if abs(ball.position[1]) + game.BALL_RADIUS > game.COMPETITION_AREA_HEIGHT/2:
        continue

      center = projection_matrix @ np.array((
        ball.position[0],
        ball.position[1],
        ball.z,
        1
      ))

      center = center[:2] / center[3] / 2

      if np.max(np.abs(center)) < 0.5:
        state["balls"].append(center)
    
    if self.ball_in_thrower:
      self.ball_in_thrower = False

    return state

  def send_action(self, action):
    self.thrower = action["thrower"]
    self.target_velocity = action["velocity"]
    self.target_angular_velocity = action["angular_velocity"]
