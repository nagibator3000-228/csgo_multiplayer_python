const express = require("express");
const app = express();
const http = require("http").createServer(app);
const io = require("socket.io")(http);
const cors = require("cors");
const { exec } = require('child_process');
const path = require('path');

app.use(cors());

"use strict";

var save_to_cloud = true

var sockets = {
   sockets: [],
   count_of_sockets: 0
};

setInterval(() => {
   let date = new Date();
   let month = date.getMonth() + 1;
   console.log(`\nauto log [${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')} : ${date.getMinutes().toString().padStart(2, '0')} : ${date.getSeconds().toString().padStart(2, '0')}]` + " " + "sockets.sockets: ", sockets.sockets, "\nauto log " + `[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')} : ${date.getMinutes().toString().padStart(2, '0')} : ${date.getSeconds().toString().padStart(2, '0')}]` + " " + "players online: ", " ", sockets.count_of_sockets);
}, 60 * 1 * 1000);

const back_up_file = path.join('../auto-back-up.bat');
if (save_to_cloud) {
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

io.on("connection", (socket) => {
   var date = new Date();
   var month = date.getMonth() + 1;
   console.log(`[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')} : ${date.getMinutes().toString().padStart(2, '0')} : ${date.getSeconds().toString().padStart(2, '0')}]` + " " + "\u001b[32mPlayer connected.\u001b[0m");

   sockets.sockets.push(socket.id);
   let connectionsCount = io.sockets.server.engine.clientsCount;
   sockets.count_of_sockets = connectionsCount;
   console.log(`[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')} : ${date.getMinutes().toString().padStart(2, '0')} : ${date.getSeconds().toString().padStart(2, '0')}]` + " " + "sockets.sockets: ", sockets.sockets, "\n" + `[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')} : ${date.getMinutes().toString().padStart(2, '0')} : ${date.getSeconds().toString().padStart(2, '0')}]` + " " + "players online: ", " ", sockets.count_of_sockets);

   setTimeout(() => {
      if (sockets.count_of_sockets >= 2) {
         try {
            io.emit("new", sockets.count_of_sockets)
         } catch (e) {
            console.error(new Error(`Error 502 | ${e}`));
         }
      }
   }, 1200);

   socket.on("client_data", async (data) => {
      if (sockets.count_of_sockets >= 2) {
         try {
            socket.broadcast.emit("server_res", data);
         } catch (e) {
            console.error(new Error(`Error 502 | ${e}`));
         }
      }
   });

   socket.on("disconnect", () => {
      var date = new Date();
      console.log(`[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')} : ${date.getMinutes().toString().padStart(2, '0')} : ${date.getSeconds().toString().padStart(2, '0')}]` + " " + "\u001b[31mPlayer disconnected.\u001b[0m");

      sockets.count_of_sockets--;
      let index = sockets.sockets.indexOf(socket.id);
      if (index !== -1) {
         sockets.sockets.splice(index, 1);
      }
      try {
         socket.emit("del", sockets.count_of_sockets);
      } catch (e) {
         console.error(new Error(`Error 502 | ${e}`));
      }

      console.log(`[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')} : ${date.getMinutes().toString().padStart(2, '0')} : ${date.getSeconds().toString().padStart(2, '0')}]` + " " + "sockets.sockets: ", sockets.sockets, "\n" + `[${date.getDate().toString().padStart(2, '0')}.${month.toString().padStart(2, '0')}.${date.getFullYear()} | ${date.getHours().toString().padStart(2, '0')} : ${date.getMinutes().toString().padStart(2, '0')} : ${date.getSeconds().toString().padStart(2, '0')}]` + " " + "players online: ", " ", sockets.count_of_sockets);
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
   }
});
