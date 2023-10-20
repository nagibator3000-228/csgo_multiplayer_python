from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import *
from direct.actor.Actor import Actor
from panda3d.core import DirectionalLight
from colorama import init, Fore
import socketio
import threading
import json
import random
import hashlib
import sys
import time

app = Ursina()

sio = socketio.Client()

window.cog_menu = False

init()

players = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14]

class SunLight(Entity):
   def __init__(self, direction, resolution, player):
      super().__init__()
      self.player = player
      self.resolution = resolution

      self.dlight = DirectionalLight("sun")
      self.dlight.setShadowCaster(True, self.resolution, self.resolution)

      lens = self.dlight.getLens()
      lens.setNearFar(-80, 200)
      lens.setFilmSize((100, 100))

      self.dlnp = render.attachNewNode(self.dlight)
      self.dlnp.lookAt(direction)
      render.setLight(self.dlnp)

   def update(self):
      self.dlnp.setPos(self.player.world_position)

   def update_resolution(self):
      self.dlight.setShadowCaster(True, self.resolution, self.resolution)

ip = ""

flag = False
data_flag = False
sit_flag = False
join_flag = False

shoot_tmr = 0
shoot_interval = 0.26

render_sit_flag = False

conn_counter = 0

resolution = 3955

solo = False

phantom_x = 0
phantom_y = 0
phantom_z = 0
rot = 0

weapon = None

data = {
   "socket": {
      "id": "",
      "room": "",
      "hash": "",
      "num": 0
   },
   "player": {
      "team": "",
      "nickname": "",
      "color": "",
      "health": 100,
      "oponent_health": 100
   },
   "data": {
      "dir": 0,
      "cord": {
         "x": 0,
         "y": 0,
         "z": 0
      }
   },
   "game": {
      "death": False,
   }
}

kill = {
   "who": "",
   "when": "",
   "with": "",
   "room": ""
}

def calculate_file_hash(file_path):
   with open(file_path, 'rb') as file:
      data = file.read()
      file_hash = hashlib.sha256(data).hexdigest()
      return file_hash


def update():
   global phantom_x
   global phantom_y
   global phantom_z
   global rot
   global render_sit_flag
   global solo
   global shoot_interval
   global shoot_tmr

   print(players)

   if held_keys['left arrow']:
      window.position = Vec2(0, 100)
   elif held_keys['right arrow']:
      window.position = Vec2(1000, 100)

   if (data["player"]["health"] <= 0 or data["player"]["health"] > 100):
      data["game"]["death"] = True
      send_data()
      sio.disconnect()
      application.quit()
      sys.exit()

   if (not solo):
      whats_my_number()
      send_data()

      # arab.position = Vec3(phantom_x, phantom_y, phantom_z)
      # arab.rotation = (-90, rot, 0)

   if held_keys['left control'] and sit_flag == False:
      sit()
      render_sit_flag = False
   else:
      stay()

   if held_keys['left shift'] and render_sit_flag:
      player.speed = 3.5

   if (mouse.left):
      current_time = time.time()
      if (current_time - shoot_tmr >= shoot_interval):
         ray = raycast(origin=camera.world_position, direction=camera.forward,
                       distance=500, ignore=[camera, player, ground, text], debug=False)
         bullet = Entity(parent=camera, model='cube',
                         scale=.1, color=color.black)
         bullet.world_parent = scene
         bullet.animate_position(
             bullet.position+(bullet.forward*1000)*time.dt*900, curve=curve.linear, duration=10)
         destroy(bullet, delay=7)
         deagle_sound = Audio("assets/sounds/deagle.mp3", autoplay=True, volume=0.55)
         if (ray.hit and ray.entity != wall):
            data["player"]["oponent_health"] -= 20
            destroy(bullet, delay=0.1)
         if (ray.entity == wall):
            destroy(bullet, delay=0.1)
         shoot_tmr = current_time

   # print(phantom_x, phantom_y, phantom_z)

def sit():
   player.camera_pivot.y = 2 - held_keys['left control']
   player.height = 2 - held_keys['left control']
   player.speed = 1.9

   ray = raycast(origin=camera.world_position, direction=Vec3(0, 1, 0), distance=1, ignore=[camera, player])
   if (ray.hit):
      player.jump_height = 0
   else:
      player.jump_height = 1.5


def stay():
   global render_sit_flag

   ray = raycast(origin=camera.world_position, direction=Vec3(0, 1, 0), distance=1, ignore=[camera, player])

   if (not ray.hit):
      player.camera_pivot.y = 2 - held_keys['left control']
      player.height = 2 - held_keys['left control']
      player.speed = 5
      render_sit_flag = True
      player.jump_height = 1.5

def start_client():
   global solo

   if (not solo):
      sio.connect('http://192.168.178.50:3000')
      sio.wait()

# @sio.on('status')
# def status(status_code):
#    status = json.loads(status_code)

@sio.on('disconnect')
def on_disconnect():
   print(Fore.RED + 'Disconnected.')

@sio.on('new')
def new_conn(data):
   parsed_data = json.loads(data)
   # e = Entity(scale=.028, rotation=(-90, 0, 0))
   # actor = Actor("assets/models/t.glb")
   # actor.reparentTo(e)
   # e.position = Vec3(9999, 9999, 9999)
   # players[parsed_data] = e
   print(Fore.GREEN + "NEW!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!" + Fore.WHITE)

@sio.on('joined')
def joined(player_count):
   print(Fore.GREEN + "joined!!" + Fore.WHITE)
   print(Fore.GREEN + str(player_count) + Fore.WHITE)
   print(Fore.GREEN + str(data["socket"]["num"]) + Fore.WHITE)
   print(Fore.GREEN + str(players) + Fore.WHITE)

# @sio.on('del')
# def dis_conn(player_count):

def whats_my_number():
   global solo
   num_flag = False

   if (not num_flag and not solo):
      sio.emit('wmn')
      num_flag = True

@sio.on("ynmi")
def num_response(num):
   data["socket"]["num"] = int(num)
   join_room()

def join_room():
   global join_flag
   global solo

   if (not join_flag and not solo):
      sio.emit("join", json.dumps(data))
      join_flag = True

def conn_counter_reset():
   global conn_counter

   conn_counter = 0

@sio.on("server_res")
def get_data(res):
   global phantom_x
   global phantom_y
   global phantom_z
   global rot
   global solo
   global conn_counter

   if (not solo):
      decoded_data = json.loads(res)

      # print(Fore.GREEN + str(players) + Fore.WHITE)
      # print(Fore.GREEN + str(decoded_data["socket"]["num"]) + Fore.WHITE)

      phantom_x = decoded_data["data"]["cord"]["x"]
      phantom_y = decoded_data["data"]["cord"]["y"]
      phantom_z = decoded_data["data"]["cord"]["z"]

      rot = decoded_data["data"]["dir"]

      data["player"]["health"] = decoded_data["player"]["oponent_health"]
      fantom_number = decoded_data["socket"]["num"]

      if (type(players[decoded_data["socket"]["num"]]) == int and conn_counter == 0):
         conn_counter += 1
         e = Entity(scale=.028, rotation=(-90, 0, 0))
         actor = Actor("assets/models/t.glb")
         actor.reparentTo(e)
         e.hide()
         players[decoded_data["socket"]["num"]] = e
         print("NOT ENTITY", conn_counter)
         invoke(conn_counter_reset, delay=10)
      else:
         e = players[fantom_number]
         
         e.show()

         # print(Fore.GREEN + str(e) + Fore.WHITE)

         e.position = Vec3(phantom_x, phantom_y, phantom_z)
         e.rotation_y = rot

      if decoded_data["game"]["death"] == True:
         ez.play()
         send_kill(decoded_data["player"]["nickname"])
         print("death")

      # if decoded_data["player"]["color"] == 'green': 
      #    if text.color != color.green:
      #       text.color = color.green
      #       text.text = decoded_data["player"]["nickname"]
      # elif decoded_data["player"]["color"] == 'red': 
      #    if text.color != color.red:
      #       text.color = color.red
      #       text.text = decoded_data["player"]["nickname"]
      # elif decoded_data["player"]["color"] == 'orange': 
      #    if text.color != color.orange:
      #       text.color = color.orange
      #       text.text = decoded_data["player"]["nickname"]
      # elif decoded_data["player"]["color"] == 'yellow': 
      #    if text.color != color.yellow:
      #       text.color = color.yellow
      #       text.text = decoded_data["player"]["nickname"]
      # elif decoded_data["player"]["color"] == 'blue': 
      #    if text.color != color.blue:
      #       text.color = color.blue
      #       text.text = decoded_data["player"]["nickname"]
      # elif decoded_data["player"]["color"] == 'purple': 
      #    if text.color != color.pink:
      #       text.color = color.pink
      #       text.text = decoded_data["player"]["nickname"]
      # else: 
      #    if text.color != color.white:
      #       text.color = color.white
      #       text.text = decoded_data["player"]["nickname"]

      # text.position = Vec3(phantom_x, phantom_y + 2.25, phantom_z)

      # print(Fore.GREEN + "GET", Fore.WHITE)

def send_data():
   global weapon
   global render_sit_flag
   global solo

   if (not solo):
      data["socket"]["id"] = sio.sid

      data["data"]["dir"] = player.rotation_y + 180

      if (player.rotation_y > 360 or player.rotation_y < -360):
         player.rotation_y = 0

      if (render_sit_flag):
         data["data"]["cord"]["y"] = player.y
      else:
         data["data"]["cord"]["y"] = player.y - 1

      data["data"]["cord"]["x"] = player.x
      data["data"]["cord"]["z"] = player.z

      data["data"]["weapon"] = weapon

      sio.emit('client_data', json.dumps(data))
      # print("POST")

@sio.on("chat")
def log(chat_log):
   decoded_chat = json.loads(chat_log)
   chat_text = decoded_chat["who"] + " was killed by " + decoded_chat["when"] + " with " + decoded_chat["with"]
   chat.text = chat_text
   invoke(clear_chat, delay=5)

def clear_chat():
   chat.text = ""

def send_kill(nickname):
   if (not solo):
      kill["who"] = data["player"]["nickname"]
      kill["when"] = nickname
      kill["with"] = "desert eagle"
      kill["room"] = data["socket"]["room"]

      sio.emit("kill", json.dumps(kill))
 
def generate_id():
   id_number = random.randint(100000, 999999)
   id_string = "{:06d}".format(id_number)
   return id_string

if __name__ == '__main__':
   player = FirstPersonController(speed=6, jump_height=1.5)
   player.cursor.model = 'sphere'
   player.cursor.rotation_z = 0
   player.cursor.color = color.black
   player.cursor.size = .05
   player.gravity = 0.9

   Sky()

   print("\n\n\n\n 1. create room | 2. join room \n print 1 or 2 and play.")
   mode = input()

   if mode == '1':
      room_id = generate_id()
      print(Fore.GREEN + "\nyour room id:", room_id, "| send it to your friends (if you have :D) and play" + Fore.WHITE)
      data["socket"]["room"] = room_id
   elif mode == '2':
      room_id = input("\nwrite a room id to join: ")
      data["socket"]["room"] = room_id.replace(" ", "")
   else:
      print(Fore.RED + "tf you write here? \n !solo mode!" + Fore.WHITE)
      solo = True

   start_thread = threading.Thread(target=start_client)
   get_thread = threading.Thread(target=get_data)
   update_thread = threading.Thread(target=update)
   send_thread = threading.Thread(target=send_data)

   start_thread.start()
   get_thread.start()
   update_thread.start()
   send_thread.start()

   ez = Audio("assets/sounds/IZIFORENZ.mp3", autoplay=False)

   with open("settings.json", "r") as file:
      parsed_data = json.load(file)
      data["player"]["team"] = parsed_data["settings"]["team"]
      data["player"]["nickname"] = parsed_data["settings"]["nickname"]
      data["player"]["color"] = parsed_data["settings"]["color"]

      resolution = parsed_data["_game_"][2]["graphic"]["graphic-resolution"]
      ip = parsed_data["_game_"][1]["connect-addr"]

      window.vsync = bool(parsed_data["_game_"][2]["graphic"]["VSync"])
      window.fullscreen = bool(parsed_data["_game_"][2]["graphic"]["Fullscreen"])
      window.fps_counter.enabled = bool(parsed_data["_game_"][2]["graphic"]["show-FPS"])

      if (parsed_data["settings"]["crosshair"]["size"] != None):
         player.cursor.scale = float(parsed_data["settings"]["crosshair"]["size"])

      if (parsed_data["settings"]["crosshair"]["type"] != None):
         player.cursor.model = 'quad'
         if parsed_data["settings"]["crosshair"]["type"] == 0:
            player.cursor.model = 'sphere'
         else:
            cursor_path = str("assets/models/cursor/{!r}").format(parsed_data["global"]["crosshair_paths"][int(parsed_data["settings"]["crosshair"]["type"])])
            cursor_path = cursor_path.replace("'", "")
            player.cursor.texture = cursor_path

   text = Text(parrent=scene, origin=(0, -0.5), billboard=True, scale=2.3)
   chat = Text(parrent=camera, scale=1, color=color.red, origin=(-0.6, -16.3))

   ground = Entity(scale=100, model='plane', texture='grass', collider='box')
   block = Entity(scale=1, model='cube', collider='box', position=Vec3(5, 2, 5))
   wall = Entity(scale=7, scale_x=1, model='cube', collider='box', position=Vec3(7, 2, 5))

   sun = SunLight(direction=(-0.7, -0.9, 0.5), resolution=resolution, player=player)
   ambient = AmbientLight(color=Vec4(0.485, 0.5, 0.63, 0) * 1.5)

   render.setShaderAuto()

   file_path = sys.argv[0]
   file_hash = calculate_file_hash(file_path)
   data["socket"]["hash"] = file_hash

   app.run()

   # global flag

   # print(player.position)


   # if h == False:
   #    data["data"]["dir"] = player.rotation_y + 180
   # else:
   #    data["data"]["dir"] = data["data"]["dir"] + 10 * time.dt * 10 * 500