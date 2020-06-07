import numpy as np


class Camera:
  def __init__(self, game):
    aspect = game.ROBOT_CAMERA_ASPECT
    fov = game.ROBOT_CAMERA_FOV / 180 * np.pi
    f = np.tan(fov / 2)
    z_near = game.ROBOT_CAMERA_NEAR
    z_far = game.ROBOT_CAMERA_FAR

    self.projection_matrix = np.array((
      (1/(aspect*f), 0, 0, 0),
      (0, 1/f, 0, 0),
      (0, 0, -(z_far + z_near) / (z_far - z_near), -(2 * z_far * z_near) / (z_far - z_near)),
      (0, 0, -1, 0)
    ))

    self.local_matrix = np.array((
      (1, 0, 0, game.ROBOT_CAMERA_X),
      (0, 1, 0, game.ROBOT_CAMERA_Y),
      (0, 0, 1, game.ROBOT_CAMERA_Z),
      (0, 0, 0, 1)
    )) @ np.array((
      (1, 0, 0, 0),
      (0, np.cos(game.ROBOT_CAMERA_R), -np.sin(game.ROBOT_CAMERA_R), 0),
      (0, np.sin(game.ROBOT_CAMERA_R), np.cos(game.ROBOT_CAMERA_R), 0),
      (0, 0, 0, 1)
    ))

  def get_projection_matrix(self, robot):
    view_matrix = np.array((
      (1, 0, 0, robot.position[0]),
      (0, 1, 0, robot.position[1]),
      (0, 0, 1, robot.z),
      (0, 0, 0, 1)
    )) @ np.array((
      (np.cos(robot.angle), -np.sin(robot.angle), 0, 0),
      (np.sin(robot.angle), np.cos(robot.angle), 0, 0),
      (0, 0, 1, 0),
      (0, 0, 0, 1)
    )) @ self.local_matrix

    return self.projection_matrix @ np.linalg.inv(view_matrix)
