var ROOM_LOCATION = "/interface/user/room";
var room_fab = new mdui.Fab('#fab-room');

function changeTabForRoom(idx){
  if (idx==0) room_fab.show(); else room_fab.hide();
}

function getRoom(){
  $$.ajax({
    method: 'POST',
    url: SERVER + ROOM_LOCATION,
    data: {
      SID: SID,
      UID: UID
    },
    success: function (data) {
      let objs = JSON.parse(data);
      console.log(objs);
      if (objs["status"]==0){
          console.log(objs["info"]);
      }else{
          console.log(objs["msg"]);
      }
    }
  });
}