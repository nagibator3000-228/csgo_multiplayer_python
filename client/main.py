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

# window.position = Vec2(0, 100)

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
      "room": "", 
      "password": ""
   },
   "player": {
      "team": "",
      "nickname": "",
      "color": "", 
      "health": 100
   },
   "data": {
      "dir": 0,
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

   if (data["player"]["health"] <= 0):
      application.quit()

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

   if held_keys['left shift'] and render_sit_flag:
      player.speed = 3.5

   if (mouse.left):
      ray = raycast(origin=camera.world_position, direction=camera.forward, distance=500, ignore=[camera, player, ground, text], debug=True)
      if ray.hit:
         print("hit")

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

      if decoded_data["player"]["color"] == 'green': 
         if text.color != color.green:
            text.color = color.green
            text.text = decoded_data["player"]["nickname"]
      elif decoded_data["player"]["color"] == 'red': 
         if text.color != color.red:
            text.color = color.red
            text.text = decoded_data["player"]["nickname"]
      elif decoded_data["player"]["color"] == 'orange': 
         if text.color != color.orange:
            text.color = color.orange
            text.text = decoded_data["player"]["nickname"]
      elif decoded_data["player"]["color"] == 'yellow': 
         if text.color != color.yellow:
            text.color = color.yellow
            text.text = decoded_data["player"]["nickname"]
      elif decoded_data["player"]["color"] == 'blue': 
         if text.color != color.blue:
            text.color = color.blue
            text.text = decoded_data["player"]["nickname"]
      elif decoded_data["player"]["color"] == 'purple': 
         if text.color != color.pink:
            text.color = color.pink
            text.text = decoded_data["player"]["nickname"]
      else: 
         if text.color != color.white:
            text.color = color.white
            text.text = decoded_data["player"]["nickname"]

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
         data["data"]["cord"]["y"] = player.y - 1

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
   player = FirstPersonController(speed=6, jump_height=1.5)
   player.cursor.model = 'sphere'
   player.cursor.rotation_z = 0
   player.cursor.color = color.black
   player.cursor.size = .05

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

      data["socket"]["password"] = parsed_data["global"]["connection"]["room_password"]

      if (parsed_data["settings"]["crosshair"]["size"] != None):
         player.cursor.scale = float(parsed_data["settings"]["crosshair"]["size"])

      if (parsed_data["settings"]["crosshair"]["type"] != None):
         player.cursor.model = 'quad'
         if parsed_data["settings"]["crosshair"]["type"] == 0:
            player.cursor.model = 'sphere'
         else:
            cursor_path = str("assets/models/cursor/{!r}").format(parsed_data["global"]["crosshair_types"][int(parsed_data["settings"]["crosshair"]["type"])])
            cursor_path = cursor_path.replace("'", "")
            # print(Fore.RED, cursor_path, Fore.WHITE)
            player.cursor.texture = cursor_path

   text = Text(parent=scene, origin=(0, -0.5), billboard=True, scale=3.2)

   ground = Entity(scale=100, model='plane', texture='grass', collider='box')
   block = Entity(scale=1, model='cube', collider='box', position=Vec3(5, 2, 5))
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
