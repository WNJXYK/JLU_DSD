var ROOM_LOCATION = "/interface/user/room";
var ROOM_MODIFY = "/interface/user/modify_room";
var room_fab = new mdui.Fab('#fab-room');

// 分页功能
var room_offset = 0, room_delta = 1, room_count = 0, room_page=0, room_total_page = 0;

function changeTabForRoom(idx){
  if (idx==0) {
    room_fab.show(); 
    updateRoomPage();
  }else room_fab.hide();
}

function modifyRoomDelta(){
  mdui.dialog({
    title: 'How many rooms in one page?',
    content: '<div class="mdui-textfield">\
                <input class="mdui-textfield-input" type="text" id="room-delta"/>\
              </div>',
    buttons: [
      { text: 'Cancel'
      },
      {
        text: 'Confirm',
        onClick: function(inst){
         room_delta = parseInt($$("#room-delta").val());
         room_offset = room_page = 0;
         $$.setCookie("room-delta", room_delta, 1048576);
         updateRoomPage();
        }
      }
    ]
  });
}

function nextRoomPage(){
  var pages = room_total_page;
  if (room_page + 1 < pages){
    ++room_page;
    room_offset = room_page * room_delta;
    updateRoomPage();
  }else mdui.snackbar({message: 'This is the last page.'});
}

function prevRoomPage(){
  var pages = room_total_page;
  if (room_page - 1 >= 0){
    --room_page;
    room_offset = room_page * room_delta;
    updateRoomPage();
  }else mdui.snackbar({message: 'This is the first page.'});
}

function modifyRoom(RID, des, del){
  data_pack = {
    SID: SID,
    UID: UID,
    RID: RID
  };
  if (des != null) data_pack["Details"] = des;
  if (del == 1) data_pack["Delete"] = 1;

  // 发送请求
  $$.ajax({
    method: 'POST',
    url: SERVER + ROOM_MODIFY,
    data: data_pack,
    success: function (data) {
      var objs = JSON.parse(data);
      if (objs["status"]==0){
        mdui.snackbar({message: "Room Updated");
      }else mdui.snackbar({message: objs["msg"]});
    }
  });
}

function updateRoomPage(){
  // 等待特效
  $$("#room-list").html('<div class="mdui-progress"><div class="mdui-progress-indeterminate"></div></div>');
  $$("#room-info").html('...');

  // 读取保存分页信息
  if ($$.getCookie("room-delta")==null){
    $$.setCookie("room-delta", room_delta = 10, 1048576);
  }else room_delta = parseInt($$.getCookie("room-delta"));
  
  // 发送请求
  $$.ajax({
    method: 'POST',
    url: SERVER + ROOM_LOCATION,
    data: {
      SID: SID,
      UID: UID,
      Offset: room_offset,
      Delta: room_delta
    },
    success: function (data) {
      var objs = JSON.parse(data);
      if (objs["status"]==0){
        // 更新房间总数
        room_count = objs["info"]["cnt"];
        room_total_page = parseInt((room_count+room_delta-1)/room_delta);
        // 更新房间标签
        $$("#room-info").html('Page: '+(room_page+1)+'/' + room_total_page);
        // 更新显示房间信息
        arr = objs["info"]["arr"];
        $$("#room-list").html("");
        for (var i=0; i<arr.length; ++i){
          let item = $$('<li class="mdui-list-item mdui-ripple">\
                <div class="mdui-list-item-content">\
                  <div class="mdui-list-item-title">' + arr[i]["Nickname"]+ '</div>\
                  <div class="mdui-list-item-text mdui-list-item-one-line">' + 'Room ID: ' + arr[i]['RID'] + ' | Device: ' + arr[i]['dCNT'] + ' | Sensor: ' + arr[i]['sCNT'] + '</div>\
                  <div class="mdui-list-item-text mdui-list-item-one-line">' + (arr[i]["Details"]==null?"No Description":arr[i]["Details"])+ '</div>\
                </div>\
              </li>\
              <li class="mdui-divider-inset mdui-m-y-0"></li>');
          let itemEx = $$('<li class="mdui-collapse-item">\
                <div class="mdui-collapse-item-header mdui-list-item mdui-ripple">\
                  <div class="mdui-list-item-content">' + arr[i]["Nickname"]+ '</div>\
                  <i class="mdui-collapse-item-arrow mdui-icon material-icons">keyboard_arrow_down</i>\
                </div>\
                <ul class="mdui-collapse-item-body mdui-list mdui-list-dense">\
                <li class="mdui-list-item mdui-ripple mdui-list-item-text ">' + 'Room ID: ' + arr[i]['RID'] + '</li>\
                  <li class="mdui-list-item mdui-ripple mdui-list-item-text ">' + 'Device: ' + arr[i]['dCNT'] + ' | Sensor: ' + arr[i]['sCNT'] + '</li>\
                  <li class="mdui-list-item mdui-ripple mdui-list-item-text ">' + (arr[i]["Details"]==null?"No Description":arr[i]["Details"])+ '</li>\
                  <li class="mdui-list-item mdui-ripple">View & Modify Hardwares</li>\
                  <li class="mdui-list-item mdui-ripple">Modify Description</li>\
                  <li class="mdui-list-item mdui-ripple">Delete Room</li>\
                </ul>\
              </li>');
          if (objs["info"]["allow"]) $$("#room-list").append(itemEx); else $$("#room-list").append(item);
        }
      }else console.log(objs["msg"]);
    }
  });
}