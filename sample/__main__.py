import numpy as np
from time import sleep
from bbr_simulator import Simulation

simulation = Simulation(BALLS=11)
simulation.run()

target_basket = "blue"
ball_was_in_thrower = False

action = {
  "velocity": [0, 0],
  "angular_velocity": 0,
  "thrower": 0
}

while True:
  simulation.send(action)
  state = simulation.get_state()

  if ball_was_in_thrower and not state["ball_in_thrower"]:
    action["thrower"] = 0

  ball_was_in_thrower = state["ball_in_thrower"]

  if action["thrower"] > 0:
    if not target_basket in state["baskets"]:
      action["thrower"] = 0
      continue

    action["velocity"] = [
      -state["baskets"][target_basket][0]/2,
      0.2
    ]
    continue

  closest_ball = None

  if len(state["balls"]) > 0:
    closest_ball = sorted(state["balls"], key=lambda ball: ball[1])[0]

  if closest_ball is None:
    action["velocity"] = [0, 0]
    action["angular_velocity"] = 0.5
    continue

  action["velocity"] = [0, closest_ball[1] + 0.35]
  action["angular_velocity"] = -closest_ball[0]*2

  if abs(action["angular_velocity"]) < 0.2:
    if target_basket in state["baskets"]:
      action["velocity"][0] = -state["baskets"][target_basket][0]/2
    else:
      action["velocity"][0] = -0.25
  
  if np.max(np.abs(action["velocity"])) < 0.01 and action["angular_velocity"] < 0.005:
    action["velocity"] = [0, 0]
    action["angular_velocity"] = 0
    action["thrower"] = 100
