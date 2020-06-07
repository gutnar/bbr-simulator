import asyncio
from threading import Thread
from queue import Queue

from bbr_simulator.server import start_server
from bbr_simulator.game import Game


req_queue = Queue()
res_queue = Queue(1)


async def game_interval(game):
  while True:
    while not req_queue.empty():
      action = req_queue.get()
      if action[0] == "state":
        res_queue.put(game.get_state(action[1]))
      elif action[0] == "action":
        game.send_action(action[1], action[2])
      req_queue.task_done()

    game.update()
    await asyncio.sleep(1.0/60)


def start_background_loop(loop, game):
  asyncio.set_event_loop(loop)

  game_task = loop.create_task(game_interval(game))

  loop.run_until_complete(start_server(game))
  loop.run_until_complete(game_task)

  loop.run_forever()


class Simulation:
  def __init__(self, **kwargs):
    self.game = Game(**kwargs)
  
  def run(self):
    loop = asyncio.new_event_loop()
    thread = Thread(target=start_background_loop, args=(loop, self.game), daemon=True)
    thread.start()
  
  def get_state(self, robot_index=0):
    req_queue.put(["state", robot_index])
    state = res_queue.get()
    res_queue.task_done()

    return state
  
  def send(self, action, robot_index=0):
    req_queue.put(["action", robot_index, action])
