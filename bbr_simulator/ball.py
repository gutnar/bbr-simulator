import numpy as np
import pymunk


class Ball(pymunk.Body):
  def __init__(self, game, id, x, y, z):
    super().__init__(game.BALL_MASS, pymunk.moment_for_circle(game.BALL_MASS, 0, game.BALL_RADIUS))

    self.game = game
    self.id = id
    self.z = z
    self.launched = False
    self.flight_time = 0

    self.position = x, y
    self.in_basket = False

    shape = pymunk.Circle(self, game.BALL_RADIUS)
    shape.elasticity = 0.8
    shape.collision_type = game.COLLISION_TYPE_BALL

    game.add(self, shape)

    def velocity_func(body, gravity, damping, dt):
      if self.in_basket:
        pymunk.Body.update_velocity(body, gravity, 0, dt)
      elif self.launched:
        self.z = self.game.BASKET_HEIGHT + self.game.BALL_RADIUS * 2
        pymunk.Body.update_velocity(body, gravity, 1, dt)
      else:
        self.z = self.game.BALL_RADIUS
        pymunk.Body.update_velocity(body, gravity, damping, dt)

    self.velocity_func = velocity_func

  def get_state(self):
    return {
      "id": self.id,
      "x": self.position[0],
      "y": self.position[1],
      "z": self.z
    }
  
  def launch(self, robot):
    rotation = np.array((
      (np.cos(robot.angle), -np.sin(robot.angle)),
      (np.sin(robot.angle), np.cos(robot.angle)),
    ))

    self.position = np.array((
      robot.position[0],
      robot.position[1]
    )) + rotation @ (0, self.game.ROBOT_RADIUS)
    self.velocity = rotation @ (0, 4)

    self.launched = True
    #self.flight_time = 0

    """
    self.launch_space = pymunk.Space()
    self.launch_space.gravity = 0, -9.81
    ground = pymunk.Segment(
      self.launch_space.static_body,
      (-1, -1),
      (1, -1),
      1
    )
    ground.elasticity = 0.5
    self.launch_space.add(ground)

    self.launch_body = pymunk.Body(self.mass, self.moment)
    self.launch_body.position = (0, 0)
    self.launch_body.velocity = 0, 4

    shape = pymunk.Circle(self.launch_body, self.game.BALL_RADIUS)
    shape.elasticity = 0.8
    self.launch_space.add(self.launch_body, shape)
    """
  
  def go_in_basket(self, basket):
    self.in_basket = True
    self.position = basket.offset[0], basket.offset[1]
    self.z = 0
