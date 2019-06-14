var ROOM = "/interface/room";
var ROOM_MODIFY = "/interface/modify_room";
var ROOM_ADD = "/interface/add_room";
var HARDWARE = "/interface/hardware";
var room_fab = new mdui.Fab('#fab-room');

// 分页功能
var room_offset = 0, room_delta = 1, room_count = 0, room_page=0, room_total_page = 0;

function changeTabForRoom(idx){
  if (idx==0) {
    room_fab.show(); 
    updateRoomPage();
  }else room_fab.hide();
}

// 修改分页房间数量
function modifyRoomDeltaDialog(){
  mdui.dialog({
    title: 'How many rooms in one page?',
    content: '<div class="mdui-textfield">\
                <input class="mdui-textfield-input" type="text" id="room-delta"/>\
              </div>',
    buttons: [
      { text: 'Cancel'},
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

// 分页：下一页
function nextRoomPage(){
  var pages = room_total_page;
  if (room_page + 1 < pages){
    ++room_page;
    room_offset = room_page * room_delta;
    updateRoomPage();
  }else mdui.snackbar({message: 'This is the last page.'});
}

// 分页：上一页
function prevRoomPage(){
  var pages = room_total_page;
  if (room_page - 1 >= 0){
    --room_page;
    room_offset = room_page * room_delta;
    updateRoomPage();
  }else mdui.snackbar({message: 'This is the first page.'});
}

// 修改房间对话框
function modifyRoomDialog(RID, DES, BID){
  mdui.dialog({
    title: 'Modify Room ' + RID,
    content: '<div class="mdui-textfield">\
                <label class="mdui-textfield-label">Description</label>\
                <input class="mdui-textfield-input" type="text" id="room-description" value="' + DES + '"/>\
                <label class="mdui-textfield-label">Building it belongs</label>\
                <input class="mdui-textfield-input" type="text" id="room-building" value="' + BID + '"/>\
              </div>',
    buttons: [
      { text: 'Cancel'},
      {
        text: 'Confirm',
        onClick: function(inst){ modifyRoom(RID, $$("#room-description").val(), $$("#room-building").val(), 0); }
      }
    ]
  });
}

// 删除房间对话框
function deleteRoomDialog(RID){
  mdui.dialog({
    title: 'Are you sure to delete Room ' + RID,
    buttons: [
      { text: 'Cancel'},
      {
        text: 'Confirm',
        onClick: function(inst){ modifyRoom(RID, null, null, 1); }
      }
    ]
  });
}

// 修改房间函数
function modifyRoom(RID, des, buildings, del){
  data_pack = {
    SID: SID,
    UID: UID,
    RID: RID
  };
  if (des != null) data_pack["Details"] = des;
  if (buildings != null) data_pack["BID"] = parseInt(buildings);
  if (del == 1) data_pack["Delete"] = 1;
  console.log(data_pack)
  // 发送请求
  $$.ajax({
    method: 'POST',
    url: SERVER + ROOM_MODIFY,
    data: data_pack,
    success: function (data) {
      var objs = JSON.parse(data);
      if (objs["status"]==0){
        mdui.snackbar({message: "Room Updated"});
        updateRoomPage();
      }else mdui.snackbar({message: objs["msg"]});
    }
  });
}

// 增加房间对话框
function addRoomDialog(){
  mdui.dialog({
    title: 'Add New Room',
    content: '<div class="mdui-textfield">\
                <label class="mdui-textfield-label">Nickname</label>\
                <input class="mdui-textfield-input" type="text" id="room-nickname"/>\
              </div>\
              <div class="mdui-textfield">\
                <label class="mdui-textfield-label">Building ID</label>\
                <input class="mdui-textfield-input" type="text" id="room-bid"/>\
              </div>\
              <div class="mdui-textfield">\
                <label class="mdui-textfield-label">Description</label>\
                <input class="mdui-textfield-input" type="text" id="room-description"/>\
              </div>',
    buttons: [
      { text: 'Cancel'},
      {
        text: 'Confirm',
        onClick: function(inst){ addRoom($$("#room-nickname").val(), $$("#room-bid").val(), $$("#room-description").val()); }
      }
    ]
  });
}

// 增加房间函数
function addRoom(nick, bid, des){
  $$.ajax({
    method: 'POST',
    url: SERVER + ROOM_ADD,
    data: {
      SID: SID,
      UID: UID,
      BID: bid,
      Nickname: nick,
      Details: des
    },
    success: function (data) {
      var objs = JSON.parse(data);
      if (objs["status"]==0){
        mdui.snackbar({message: "Room Added"});
        updateRoomPage();
      }else mdui.snackbar({message: objs["msg"]});
    }
  });
}

// 更新房间页
function updateRoomPage(){
  //初始化
  $$("#add-room").hide();

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
    url: SERVER + ROOM,
    data: {
      SID: SID,
      UID: UID,
      Offset: room_offset,
      Delta: room_delta,
      BID: BuildingID
    },
    success: function (data) {
      var objs = JSON.parse(data);
      if (objs["status"]==0){
        // 更新房间总数
        room_count = objs["info"]["cnt"];
        room_total_page = parseInt((room_count+room_delta-1)/room_delta);
        // 更新房间标签
        $$("#building-info").html('Building: ' + BuildingName);
        $$("#room-info").html('Page: '+(room_page+1) + '/' + room_total_page);
        // 更新显示房间信息
        arr = objs["info"]["arr"];
        $$("#room-list").html("");
        for (var i=0; i<arr.length; ++i){
          let item = $$('<li class="mdui-list-item mdui-ripple">\
                <div class="mdui-list-item-content" onclick="viewHardwareDialog(' + arr[i]['RID'] + ');">\
                  <div class="mdui-list-item-title">' + arr[i]["Nickname"]+ '</div>\
                  <div class="mdui-list-item-text mdui-list-item-one-line">' + 'Room ID: ' + arr[i]['RID'] + ' | Belongs to Building: ' + arr[i]['BID'] + '</div>\
                  <div class="mdui-list-item-text mdui-list-item-one-line">' + 'Description: ' + (arr[i]["Details"]==null?"No Description":arr[i]["Details"])+ '</div>\
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
                <li class="mdui-list-item mdui-ripple mdui-list-item-text ">' + 'Belongs to Building: ' + arr[i]['BID'] + '</li>\
                  <!--li class="mdui-list-item mdui-ripple mdui-list-item-text ">' + 'Device: ' + arr[i]['dCNT'] + ' | Sensor: ' + arr[i]['sCNT'] + '</li-->\
                  <li class="mdui-list-item mdui-ripple mdui-list-item-text ">' + 'Description: ' + (arr[i]["Details"]==null?"No Description":arr[i]["Details"])+ '</li>\
                  <li class="mdui-list-item mdui-ripple" onclick="viewHardwareDialog(' + arr[i]['RID'] + ');">Hardwares</li>\
                  <li class="mdui-list-item mdui-ripple" onclick="modifyRoomDialog(' + arr[i]['RID'] + ',\'' + (arr[i]["Details"]==null?"No Description":arr[i]["Details"]) +'\',' + arr[i]['BID'] + ');">Modify Room</li>\
                  <li class="mdui-list-item mdui-ripple" onclick="deleteRoomDialog(' + arr[i]['RID'] + ');">Delete Room</li>\
                </ul>\
              </li>');
          if (objs["info"]["Modify"]) $$("#room-list").append(itemEx); else $$("#room-list").append(item);
        }
        if (objs["info"]["Modify"]) $$("#add-room").show();
      }else console.log(objs["msg"]);
    }
  });
}