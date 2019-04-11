var BUILDING = "/interface/building";

function buildingList(){
  var ret = [];
  $$.ajax({
    method: 'POST',
    url: SERVER + BUILDING,
    data: {},
    async: false,
    success: function (data) {
      var objs = JSON.parse(data);
      if (objs["status"]==0){
        console.log(objs["info"]);
        ret=objs["info"];
      }else console.log(objs["msg"]);
    }
  });
  return ret;
}

function selectBuilding(){
  arr = buildingList();
  str = '<option value="0">All Buildings</option>';
  for (var i=0; i<arr.length; ++i) str+='<option value="' + arr[i]["BID"] + '">#' + arr[i]["BID"] + '.' + arr[i]["Nickname"] + '</option>';
  str='<select class="mdui-select" id="select-building">'+str+'</select>';

  mdui.dialog({
    title: "Select Building",
    content: str,
    buttons: [
      { text: 'Cancel'},
      {
        text: 'Confirm',
        onClick: function(inst){
          var obj = document.getElementById('select-building');
          var index = obj.selectedIndex;
          BuildingName = obj.options[index].text;
          BuildingID = obj.options[index].value;
          room_offset = room_page = 0;
          updateRoomPage();
          // console.log(index + "," + text + "," + value);
        }
      }
    ]
  });
  mdui.mutation();
}