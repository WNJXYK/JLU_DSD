var HARDWARE_ADD = "/interface/add_hardware";
var HARDWARE_BIND = "/interface/bind_hardware";
var HARDWARE_ALL = "/interface/allHardware";
var HARDWARE_DEL = "/interface/del_hardware";

// 增加房间对话框
function addHardwareDialog(){
  mdui.dialog({
    title: 'Add Hardware Room',
    content: '<div class="mdui-textfield">\
                <label class="mdui-textfield-label">Hardware ID</label>\
                <input class="mdui-textfield-input" type="text" id="hardware-hid"/>\
              </div>\
              <div class="mdui-textfield">\
                <label class="mdui-textfield-label">Hardware Nickname</label>\
                <input class="mdui-textfield-input" type="text" id="hardware-nickname"/>\
              </div>\
              <div class="mdui-textfield">\
                <label class="mdui-textfield-label">Hardware Type</label>\
                <select class="mdui-select" id="hardware-type">\
                  <option value="Light" selected>Light</option>\
                  <option value="PresenceSensor">Presence Sensor</option>\
                  <option value="LightSensor">Light Sensor</option>\
                  <option value="ButtonSensor">Button</option>\
                </select>\
              </div>',
    buttons: [
      { text: 'Cancel'},
      {
        text: 'Confirm',
        onClick: function(inst){
          let obj = document.getElementById('hardware-type');
          let type = obj.options[obj.selectedIndex].value;
          let hid = $$("#hardware-hid").val();
          let nick = $$("#hardware-nickname").val();
          addHardware(hid, nick, type);
        }
      }
    ]
  });
}

// 增加房间函数
function addHardware(hid, nick, type){
  $$.ajax({
    method: 'POST',
    url: SERVER + HARDWARE_ADD,
    data: {
      SID: SID,
      UID: UID,
      HID: hid,
      Nickname: nick,
      Type: type
    },
    success: function (data) {
      var objs = JSON.parse(data);
      if (objs["status"]==0){
        mdui.snackbar({message: "Hardware Added"});
      }else mdui.snackbar({message: objs["msg"]});
    }
  });
}

// 绑定房间与硬件对话框
function bindHardwareDialog(){
  mdui.dialog({
    title: 'Bind/Unbind Hardware With Room',
    content: '<div class="mdui-textfield">\
                <label class="mdui-textfield-label">Hardware ID</label>\
                <input class="mdui-textfield-input" type="text" id="bhardware-hid"/>\
              </div>\
              <div class="mdui-textfield">\
                <label class="mdui-textfield-label">Room ID</label>\
                <input class="mdui-textfield-input" type="text" id="bhardware-rid"/>\
              </div>',
    buttons: [
      { text:"Cancel" },
      { text: 'Unbind',
        onClick: function(inst){
          let hid = $$("#bhardware-hid").val();
          let rid = $$("#bhardware-rid").val();
          bindHardware(hid, rid, 0);
        }
      },
      {
        text: 'Bind',
        onClick: function(inst){
          let hid = $$("#bhardware-hid").val();
          let rid = $$("#bhardware-rid").val();
          bindHardware(hid, rid, 1);
        }
      }
    ]
  });
}

// 绑定房间与硬件
function bindHardware(hid, rid, bind){
  $$.ajax({
    method: 'POST',
    url: SERVER + HARDWARE_BIND,
    data: {
      SID: SID,
      UID: UID,
      HID: hid,
      RID: rid,
      Bind: bind
    },
    success: function (data) {
      var objs = JSON.parse(data);
      if (objs["status"]==0){
        mdui.snackbar({message: "Hardware Operated"});
      }else mdui.snackbar({message: objs["msg"]});
    }
  });
}

// 增加房间对话框
function allHardwareDialog(){
  $$.ajax({
    method: 'POST',
    url: SERVER + HARDWARE_ALL,
    data: {
      SID: SID,
      UID: UID
    },
    success: function (data) {
      var objs = JSON.parse(data);
      if (objs["status"]==0){
        let arr = objs["info"];
        // 生成硬件列表
        let list = $$('<ul class="mdui-list" id="hardware-list"></ul>');
        for (var i=0; i<arr.length; ++i){
           list.append($$('<li class="mdui-list-item mdui-ripple"><div class="mdui-list-item-content" onclick="deleteHardware(\''+arr[i]["HID"] +'\');">' + arr[i]["Nickname"] +' ('+arr[i]["HID"] + ') - ' + arr[i]["Type"] + '</div></li>'));
        }
        // 生成对话框
        mdui.dialog({
          title: 'All Hardware (Click to delete)',
          content: $$('<p></p>').append(list).html(),
          buttons:[{text:"OK"}]
        });
      }else mdui.snackbar({message: objs["msg"]});
    }
  });
}

function refreshAllHardware(){
  $$.ajax({
    method: 'POST',
    url: SERVER + HARDWARE_ALL,
    data: {
      SID: SID,
      UID: UID
    },
    success: function (data) {
      var objs = JSON.parse(data);
      if (objs["status"]==0){
        let arr = objs["info"];
        // 生成硬件列表
        let list = $$('#hardware-list');
        list.html("");
        for (var i=0; i<arr.length; ++i){
           list.append($$('<li class="mdui-list-item mdui-ripple"><div class="mdui-list-item-content" onclick="deleteHardware(\''+arr[i]["HID"] +'\');">' + arr[i]["Nickname"] +' ('+arr[i]["HID"] + ') - ' + arr[i]["Type"] + '</div></li>'));
        }
      }
    }
  });
}

// 增加房间函数
function deleteHardware(hid){
  mdui.snackbar({
    message: 'Are you sure to delete Hardware ' + hid,
    buttonText: 'Delete it!',
    onClick: function(){},
    onButtonClick: function(){
      $$.ajax({
        method: 'POST',
        url: SERVER + HARDWARE_DEL,
        data: {
          SID: SID,
          UID: UID,
          HID: hid
        },
        success: function (data) {
          var objs = JSON.parse(data);
          if (objs["status"]==0){
            mdui.snackbar({message: "Hardware Deleted"});
            refreshAllHardware();
          }else mdui.snackbar({message: objs["msg"]});
        }
      });
    },
    onClose: function(){}
  });
}