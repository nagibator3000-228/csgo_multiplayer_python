from ursina import *
from ursina.prefabs.first_person_controller import FirstPersonController
from ursina.shaders import *
from direct.actor.Actor import Actor
from colorama import init, Fore
import socketio
import threading
import json

app = Ursina()

sio = socketio.Client()

init()

window.vsync = False
window.fullscreen = False

flag = False
data_flag = False

phantom_x = 0
phantom_y = 0
phantom_z = 0
rot = 0

weapon = None

data = {
   "socket": {
      "id": "",
      "count": 0
   },
   "player": {
      "name": "",
      "team": ""
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

player_data = {
   "nikname": "user"
}

def input(key):
   pass

def update():
   global phantom_x
   global phantom_y
   global phantom_z
   global rot

   send_data()

   arab.position = Vec3(phantom_x, phantom_y, phantom_z)
   arab.rotation = (-90, rot, 0)

   # print(phantom_x, phantom_y, phantom_z)

def start_client():
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

   decoded_data = json.loads(data)

   phantom_x = decoded_data["data"]["cord"]["x"]
   phantom_y = decoded_data["data"]["cord"]["y"]
   phantom_z = decoded_data["data"]["cord"]["z"]

   rot = decoded_data["data"]["dir"]

   print(Fore.GREEN + "GET", Fore.WHITE)

@sio.on("players")
def new_player(data):
   decoded_data = json.loads(data)
   if decoded_data["count"] >= 1:
      id = decoded_data["id"]
      arab = Entity(scale=.028, rotation=(-90, 0, 0))
      actor = Actor("assets/models/t.glb")
      actor.reparentTo(arab)
      arab.name = str(id)

@sio.on('new')
def new_conn(player_count):
   arab.show()

@sio.on('del')
def dis_conn(player_count):
   arab.hide()

def send_data():
   global weapon

   data["socket"]["id"] = sio.sid
   data["player"]["name"] = player_data["nikname"]

   data["data"]["dir"] = player.rotation_y + 180
   data["data"]["cord"]["x"] = player.x
   data["data"]["cord"]["y"] = player.y
   data["data"]["cord"]["z"] = player.z
   data["data"]["weapon"] = weapon

   sio.emit('client_data', json.dumps(data))
   print("POST")

if __name__ == '__main__':
   player = FirstPersonController()

   start_thread = threading.Thread(target=start_client)
   get_thread = threading.Thread(target=get_data)
   update_thread = threading.Thread(target=update)
   start_thread.start()
   get_thread.start()
   update_thread.start()
   Sky()

   ground = Entity(scale=100, model='plane', texture='grass', collider='box')
   arab = Entity(scale=.028, rotation=(-90, 0, 0))
   actor = Actor("assets/models/t.glb")
   actor.reparentTo(arab)
   map = Entity(scale=1, collider='mesh', position=Vec3(0, -10, 0))
   arab.hide()

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