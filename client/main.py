from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import *
from direct.actor.Actor import Actor
from colorama import init, Fore
import socketio
import threading
import json
import random

app = Ursina()

sio = socketio.Client()

init()

window.vsync = False
window.fullscreen = False

flag = False
data_flag = False
sit_flag = False
join_flag = False

render_sit_flag = False

solo = False

phantom_x = 0
phantom_y = 0
phantom_z = 0
rot = 0

weapon = None

players = []

data = {
   "socket": {
      "id": "",
      "room": ""
   },
   "player": {
      "team": "",
      "nickname": "",
      "color": ""
   },
   "data": {
      "dir": 0,
      "weapon": None,
      "cord": {
         "x": 0,
         "y": 0,
         "z": 0
      }
   }
}

def update():
   global phantom_x
   global phantom_y
   global phantom_z
   global rot
   global render_sit_flag
   global solo

   if (not solo):
      join_room()
      send_data()

      arab.position = Vec3(phantom_x, phantom_y, phantom_z)
      arab.rotation = (-90, rot, 0)

   if held_keys['left control'] and sit_flag == False:
      sit()
      render_sit_flag = False
   else:
      stay()

   # print(phantom_x, phantom_y, phantom_z)

def sit():
   player.camera_pivot.y = 2 - held_keys['left control']
   player.height = 2 - held_keys['left control']
   player.speed = 2

def stay():
   global render_sit_flag

   ray = raycast(origin=camera.world_position, direction=Vec3(0, 1, 0), distance=1, ignore=[camera, player])

   if (not ray.hit):
      player.camera_pivot.y = 2 - held_keys['left control']
      player.height = 2 - held_keys['left control']
      player.speed = 5
      render_sit_flag = True

def start_client():
   global solo

   if (not solo):
      sio.connect('http://192.168.178.50:3000')
      sio.wait()

@sio.on('disconnect')
def on_disconnect():
   print(Fore.RED + 'Disconnected.')

@sio.on("server_res")
def get_data(data):
   global phantom_x
   global phantom_y
   global phantom_z
   global rot
   global solo

   if (not solo):
      decoded_data = json.loads(data)

      phantom_x = decoded_data["data"]["cord"]["x"]
      phantom_y = decoded_data["data"]["cord"]["y"]
      phantom_z = decoded_data["data"]["cord"]["z"]

      rot = decoded_data["data"]["dir"]

      text.position = Vec3(phantom_x, phantom_y + 2.25, phantom_z)

      # print(Fore.GREEN + "GET", Fore.WHITE)

@sio.on('new')
def new_conn(player_count):
   arab.show()
   text.show()

@sio.on('del')
def dis_conn(player_count):
   arab.hide()
   text.hide()

def join_room():
   global join_flag
   global solo

   if (not join_flag and not solo):
      sio.emit("join", json.dumps(data))
      join_flag = True

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
         data["data"]["cord"]["y"] = player.y - 1.2

      data["data"]["cord"]["x"] = player.x
      data["data"]["cord"]["z"] = player.z
      data["data"]["weapon"] = weapon

      sio.emit('client_data', json.dumps(data))
      # print("POST")

def generate_id():
    id_number = random.randint(100000, 999999)
    id_string = "{:06d}".format(id_number)
    return id_string

if __name__ == '__main__':
   player = FirstPersonController()

   Sky()

   print("\n\n\n\n 1. create room | 2. join room \n print 1 or 2 and press enter to generate room id.")
   mode = input()

   if mode == '1':
      room_id = generate_id()
      print(Fore.GREEN + "\nyour room id:", room_id, "| send it to your friends (if you have :D) and play" + Fore.WHITE)
      data["socket"]["room"] = room_id
   elif mode == '2':
      room_id = input("\nwrite a room id to join: ")
      data["socket"]["room"] = room_id
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

   with open("settings.json", "r") as file:
      parsed_data = json.load(file)
      data["player"]["team"] = parsed_data["settings"]["team"]
      data["player"]["nickname"] = parsed_data["settings"]["nickname"]
      data["player"]["color"] = parsed_data["settings"]["color"]

      if data["player"]["color"] == 'green': text = Text(text=data["player"]["nickname"], parent=scene, origin=(0, -0.5), billboard=True, scale=3.2, color=color.green)
      elif data["player"]["color"] == 'red': text = Text(text=data["player"]["nickname"], parent=scene, origin=(0, -0.5), billboard=True, scale=3.2, color=color.red)
      elif data["player"]["color"] == 'yellow': text = Text(text=data["player"]["nickname"], parent=scene, origin=(0, -0.5), billboard=True, scale=3.2, color=color.yellow)
      elif data["player"]["color"] == 'orange': text = Text(text=data["player"]["nickname"], parent=scene, origin=(0, -0.5), billboard=True, scale=3.2, color=color.orange)
      elif data["player"]["color"] == 'blue': text = Text(text=data["player"]["nickname"], parent=scene, origin=(0, -0.5), billboard=True, scale=3.2, color=color.blue)
      else: text = Text(text=data["player"]["nickname"], parent=scene, origin=(0, -0.5), billboard=True, scale=3.2, color=color.white)

   ground = Entity(scale=100, model='plane', texture='grass', collider='box')
   arab = Entity(scale=.028, rotation=(-90, 0, 0))
   actor = Actor("assets/models/t.glb")
   actor.reparentTo(arab)
   arab.hide()
   text.hide()

   app.run()

   # global flag

   # print(player.position)

   # if flag:
   #    arab.rotation_x = arab.rotation_x - 4 * time.dt * 10
   #    print(arab.rotation_x)
   #    if (arab.rotation_x < -180):
   #       flag = False
   #       arab.hide()
   #       death = Audio("assets/sounds/death.mp3", autoplay=True)


   # global flag

   # if held_keys['q']:
   #    flag = True

   # if h == False:
   #    data["data"]["dir"] = player.rotation_y + 180
   # else:
   #    data["data"]["dir"] = data["data"]["dir"] + 10 * time.dt * 10 * 500
