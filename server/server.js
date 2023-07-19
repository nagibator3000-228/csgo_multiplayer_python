const express = require('express');
const app = express();
const http = require('http').createServer(app);
const io = require('socket.io')(http);
const cors = require('cors');
const { exec } = require('child_process');
const path = require('path');
const fs = require('fs');
const crypto = require('crypto');

"use strict";

app.use(cors({origin: '*'}));

var anti_cheat = true;

var save_to_cloud = true;

var sockets = {
   sockets: [],
   count_of_sockets: 0
};

setInterval(() => {
   let date = new Date();
   let month = date.getMonth() + 1;
   console.log(`\nauto log [${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')} : ${date.getMinutes().toString().padStart(2, '0')} : ${date.getSeconds().toString().padStart(2, '0')}]` + " " + "sockets: ", sockets.sockets, "\nauto log " + `[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')} : ${date.getMinutes().toString().padStart(2, '0')} : ${date.getSeconds().toString().padStart(2, '0')}]` + " " + "players online: ", " ", sockets.count_of_sockets, '\n');
}, 1 * 60 * 1000);

const back_up_file = path.join('auto-back-up.bat');
if (save_to_cloud === true) {
   setInterval(() => {
      exec(back_up_file, (error, stdout, stderr) => {
         var date = new Date();
         var month = date.getMonth() + 1;
         if (error) {
            console.error(`[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')} : ${date.getMinutes().toString().padStart(2, '0')} : ${date.getSeconds().toString().padStart(2, '0')}]` + " " + `\u001b[31mError to back up | ${error} | \u001b[0m`);
            return;
         }
         console.log(`[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')} : ${date.getMinutes().toString().padStart(2, '0')} : ${date.getSeconds().toString().padStart(2, '0')}]` + " " + "\u001b[32msuccesfull loaded data in back-up\u001b[0m");
      });
   }, 60 * 60 * 1 * 1000);
}

const main_path = 'anti_cheat/main.py';
const readStream = fs.createReadStream(main_path);
const hash = crypto.createHash('sha256');

let main_hash;

readStream.on('data', (data) => {
   hash.update(data);
});

readStream.on('end', () => {
   const fileHash = hash.digest('hex');
   main_hash = fileHash;
   console.log(`crypto main hash: ${fileHash}`);
});

readStream.on('error', (err) => {
   console.error('Error :', err);
});

io.on("connection", (socket) => {
   var date = new Date();
   var month = date.getMonth() + 1;
   console.log(`[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')} : ${date.getMinutes().toString().padStart(2, '0')} : ${date.getSeconds().toString().padStart(2, '0')}]` + " " + "\u001b[32mPlayer connected.\u001b[0m");

   sockets.sockets.push(socket.id);
   let connectionsCount = io.sockets.server.engine.clientsCount;
   sockets.count_of_sockets = connectionsCount;
   console.log(`[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')} : ${date.getMinutes().toString().padStart(2, '0')} : ${date.getSeconds().toString().padStart(2, '0')}]` + " " + "sockets: ", sockets.sockets, "\n" + `[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')} : ${date.getMinutes().toString().padStart(2, '0')} : ${date.getSeconds().toString().padStart(2, '0')}]` + " " + "players online: ", " ", sockets.count_of_sockets);

   socket.on("join", (data) => {
      try {
         let parsed_data = JSON.parse(data);
         if (parsed_data.socket.hash != main_hash && anti_cheat) {
            socket.disconnect();
            return;
         }
         socket.join(parsed_data.socket.room);
         const room = io.sockets.adapter.rooms.get(parsed_data.socket.room);
         const playerCount = room ? room.size : 0;
         if (playerCount >= 2) {
            io.in(parsed_data.socket.room).emit('new', sockets.count_of_sockets);
         }
      } catch (e) {
         console.error(new Error(`Error 502 | ${e}`));
      } finally {
         var date = new Date();
         var month = date.getMonth() + 1;
         const logString = `\n[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}] sockets: ${JSON.stringify(sockets.sockets)}\n[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}] players online: ${sockets.count_of_sockets}\n`;
         fs.writeFile('logs.txt', logString, {flag: 'a', encoding: 'utf-8'}, (err) => {
            if (err) throw err;
         });
      }
   });

   socket.on("client_data", async (data) => {
      if (sockets.count_of_sockets >= 2) {
         try {
            let parsed_data = JSON.parse(data);
            if (parsed_data.socket.hash != main_hash && anti_cheat) {
               socket.disconnect();
               return;
            }
            socket.broadcast.to(parsed_data.socket.room).emit('server_res', JSON.stringify(parsed_data));
         } catch (e) {
            console.error(new Error(`Error 502 | ${e}`));
         }
      }
   });

   socket.on("disconnect", () => {
      var date = new Date();
      var month = date.getMonth() + 1;
      console.log(`[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')} : ${date.getMinutes().toString().padStart(2, '0')} : ${date.getSeconds().toString().padStart(2, '0')}]` + " " + "\u001b[31mPlayer disconnected.\u001b[0m");

      sockets.count_of_sockets--;
      let index = sockets.sockets.indexOf(socket.id);
      if (index !== -1) {
         sockets.sockets.splice(index, 1);
      }

      try {
         io.emit("del", sockets.count_of_sockets);
      } catch (e) {
         console.error(new Error(`Error 502 | ${e}`));
      } finally {
         var date = new Date();
         var month = date.getMonth() + 1;
         console.log(`[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')} : ${date.getMinutes().toString().padStart(2, '0')} : ${date.getSeconds().toString().padStart(2, '0')}]` + " " + "sockets: ", sockets.sockets, "\n" + `[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')} : ${date.getMinutes().toString().padStart(2, '0')} : ${date.getSeconds().toString().padStart(2, '0')}]` + " " + "players online: ", " ", sockets.count_of_sockets);
         const logString = `\n[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}] sockets: ${JSON.stringify(sockets.sockets)}\n[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}] players online: ${sockets.count_of_sockets}\n`;
         fs.writeFile('logs.txt', logString, {flag: 'a', encoding: 'utf-8'}, (err) => {
            if (err) throw err;
         });
      }
   });
});

http.listen(3000, '192.168.178.50', () => {
   console.log("starting...");
   try {
      let date = new Date();
      let month = date.getMonth() + 1;
      console.log(`\n[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')} : ${date.getMinutes().toString().padStart(2, '0')} : ${date.getSeconds().toString().padStart(2, '0')}]` + " " + "\u001b[32mServer started on port 3000\u001b[0m\n");
   } catch (e) {
      console.error(new Error(`Error 503 | ${e}`));
   } finally {
      var date = new Date();
      var month = date.getMonth() + 1;
      const logString = `\n[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}:${date.getSeconds().toString().padStart(2, '0')}] Server started on port 3000\n`;
      fs.writeFile('logs.txt', logString, {flag: 'a', encoding: 'utf-8'}, (err) => {
         if (err) throw err;
      });
   }
});
