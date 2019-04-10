var device_list = []
var SUPER_SERVER = "http://127.0.0.1:443"
var HARDWARE_INFO = "/api/hardware";
function updateHardware(HID, ID){
  $$.ajax({
    method: 'GET',
    url: SUPER_SERVER + HARDWARE_INFO,
    data: {
      HID: HID,
      SID: SID,
      UID: UID
    },
    success: function (data) {
      var objs = JSON.parse(data);
      console.log(objs);
    }
  });
}

// 定时更新硬件信息
function updateHardwareTimer(){
  var t1=window.setInterval(refreshCount, 5000);
  function refreshCount() {
    console.log(device_list);
    var list = device_list.slice(0);
    device_list = []
    for (var i=0; i<list.length; i++){
      if ($$("#"+list[i]["ID"]).length>0){
        device_list.push(list[i]);
        updateHardware(list[i]["HID"], "#"+list[i]["ID"], list[i]["Type"]);
      }
    }
  }
}

function openHardwarePage(RID){
  $$.ajax({
    method: 'POST',
    url: SERVER + HARDWARE,
    data: {
      SID: SID,
      UID: UID,
      RID: RID
    },
    success: function (data) {
      var objs = JSON.parse(data);
      console.log(objs);
      if (objs["status"]==0){
        let arr = objs["info"];
        // 生成硬件列表
        let list = $$('<ul class="mdui-list"></ul>');
        for (var i=0; i<arr.length; ++i){
          if (arr[i]["Ctrl"]==1){
              list.append($$('<li class="mdui-list-item mdui-ripple">\
                    <div class="mdui-list-item-content">' + arr[i]["Nickname"] + ' (' + arr[i]["HID"] + ') - ' + arr[i]["Type"] + '</div>\
                    <label class="mdui-switch">\
                      <input type="checkbox" checked id="HC-' + arr[i]["HID"] + '"/>\
                      <i class="mdui-switch-icon"></i>\
                    </label>\
                  </li>'));
              device_list.push({"HID": arr[i]["HID"], "ID": "HC-" + arr[i]["HID"], "Type" : 1});
          }else{
            list.append($$('<li class="mdui-list-item mdui-ripple">\
                 <div class="mdui-list-item-content" id="HV-' + arr[i]["HID"] + '">' + arr[i]["Nickname"] +' ('+arr[i]["HID"] + ') - ' + arr[i]["Type"] + '</div>\
               </li>'));
            device_list.push({"HID": arr[i]["HID"], "ID": "HV-" + arr[i]["HID"], "Type" : 0});
          }
        }
        // 生成对话框
        mdui.dialog({
          title: 'Hardware List',
          content: list.html()
        });
      }else mdui.snackbar({message: objs["msg"]});
    }
  });
}