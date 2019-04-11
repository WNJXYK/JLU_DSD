var device_list = []
var HARDWARE_INFO = "/api/hardware";
var HARDWARE_CMD = "/api/command";

// 处理CheckBox
function solveCheckbox(HID, ID, type){
  var cmd = "";
  switch(type){
    case "Light":
      if ($$(ID).get(0).checked){
        cmd = "on";
      }else cmd = "off";
      break;
  }
  $$.ajax({
      method: 'GET',
      url: SERVER + HARDWARE_CMD,
      data: {
        HID: HID,
        SID: SID,
        UID: UID,
        CMD: cmd
      },
      success: function (data) {
        var objs = JSON.parse(data);
        if (objs["status"]==0){
          mdui.snackbar({message: "Command Sent"});
        }else {
          mdui.snackbar({message: objs["msg"]});
          refreshHardwareDialog();
        }
      }
    });
}

// 处理传感器显示
function parseSensor(type, online, data, ID){
  var str = "<br>&nbsp;*&nbsp;&nbsp;";
  if (online==0) {
    str = str + "Sensor is Offline."
  }else{
    switch(type){
      case "LightSensor":
        str = str + "Light Intensity : " + data;
        break;
      case "PresenceSensor":
        if (data == "False") {
          str = str + "Object Detect : Nothing";
        }else{
          str = str + "Object Detect : Find";
        }
        break;
      case "ButtonSensor":
        str = str + "Button is Online";
        break;
    }
  }
  $$(ID).html(str);
}

// 处理设备显示
function parseDevice(type, online, data, ID){
  if (online == 0) {
    $$(ID).get(0).checked = false;
    $$(ID+"-DIV").hide();
  }else{
    switch(type){
      case "Light":
        if (data == "True"){
          $$(ID).get(0).checked = true;
        }else $$(ID).get(0).checked = false;
        break;
    }
    $$(ID+"-DIV").show();
  }
}

// 更新硬件信息
function updateHardware(HID, ID, type){
  $$.ajax({
    method: 'GET',
    url: SERVER + HARDWARE_INFO,
    data: {
      HID: HID,
      SID: SID,
      UID: UID
    },
    success: function (data) {
      var objs = JSON.parse(data);
      if (type==0) parseSensor(objs["type"], objs["online"], objs["data"], ID);
      if (type==1) parseDevice(objs["type"], objs["online"], objs["data"], ID);
    }
  });
}

// 立即请求所有硬件信息
function refreshHardwareDialog() {
  // console.log(device_list);
  var list = device_list.slice(0);
  device_list = [];
  for (var i=0; i<list.length; i++){
    if ($$("#"+list[i]["ID"]).length>0){
      device_list.push(list[i]);
      updateHardware(list[i]["HID"], "#"+list[i]["ID"], list[i]["Type"]);
    }
  }
}

// 定时更新硬件信息
function updateHardwareTimer(){
  var t1=window.setInterval(refreshHardwareDialog, 1000);
}

// 打开硬件页
function viewHardwareDialog(RID){
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
      // console.log(objs);
      if (objs["status"]==0){
        let arr = objs["info"];
        // 生成硬件列表
        let list = $$('<ul class="mdui-list"></ul>');
        for (var i=0; i<arr.length; ++i){
          if (arr[i]["Ctrl"]==1){
              list.append($$('<li class="mdui-list-item mdui-ripple">\
                    <div class="mdui-list-item-content">' + arr[i]["Nickname"] + ' (' + arr[i]["HID"] + ') - ' + arr[i]["Type"] + '</div>\
                    <div id="HC-' + arr[i]["HID"] + '-DIV">\
                      <label class="mdui-switch">\
                        <input type="checkbox" id="HC-' + arr[i]["HID"] + '" onclick="solveCheckbox(\''+ arr[i]["HID"] + '\',\'#HC-' + arr[i]["HID"] + '\',\'' + arr[i]["Type"] + '\');" checked/>\
                        <i class="mdui-switch-icon"></i>\
                      </label>\
                    </div>\
                  </li>'));
              device_list.push({"HID": arr[i]["HID"], "ID": "HC-" + arr[i]["HID"], "Type" : 1});
          }else{
            list.append($$('<li class="mdui-list-item mdui-ripple">\
                 <div class="mdui-list-item-content">' + arr[i]["Nickname"] +' ('+arr[i]["HID"] + ') - ' + arr[i]["Type"] + '<span id="HV-' + arr[i]["HID"] + '"></span></div>\
               </li>'));
            device_list.push({"HID": arr[i]["HID"], "ID": "HV-" + arr[i]["HID"], "Type" : 0});
          }
        }
        // 生成对话框
        mdui.dialog({
          title: '<div class="mdui-row-xs-1">\
                      <div class="mdui-col">\
                        <button class="mdui-btn mdui-btn-block mdui-color-theme-accent mdui-ripple" onclick="refreshHardwareDialog();">Hardware List (Refresh)</button>\
                      </div>\
                    </div>',
          content: $$('<p></p>').append(list).html()
        });
        refreshHardwareDialog();
      }else mdui.snackbar({message: objs["msg"]});
    }
  });
}