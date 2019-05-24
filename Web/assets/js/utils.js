function isEmpty(value){
  if(value == null || value == "" || value == "undefined" || value == undefined || value == "null"){
      return true;
  }else{
    value = value.replace(/\s/g,"");
    if(value == "") return true;
    return false;
  }
}

function loadConfig(){
  var server = $.cookie('global_server');
  if (isEmpty(server)){
    server = "http://0.0.0.0:443";
    $.cookie('global_server', server);
  }
}

function notLogin(){
  if (isEmpty($.cookie('global_uid')) || isEmpty($.cookie('global_token'))) {
    return true;
  }
  return false;
}

function checkLogin(){
  if (isEmpty($.cookie('global_uid')) || isEmpty($.cookie('global_token'))) {
    window.location.href="./login.html";
  }
}

function disabledButtons(){
  permission = $.cookie('global_permission');
  let admin_flag=false;
  let build_flag=false;
  let force_flag=false;
  permission = permission.toString().split(",");
  for (let i=0; i<permission.length; i++){
    if (permission[i]=="admin") admin_flag=true;
    if (permission[i]=="build") build_flag=true;
    if (permission[i]=="force") force_flag=true;
  }

  if (admin_flag==false){
    $('#nav-user').hide();
    $('#nav-raspi').hide();
    $('.admin-permission').hide();
  }

  if (build_flag==false){
    $('.build-permission').hide();
  }

  if (notLogin()){
    $('#nav-role').hide();
    $('#nav-hardware').hide();
    $("#user-info").html("");
    $("#login").html("Login");
  }
}

function isForce(){
  permission = $.cookie('global_permission');
  permission = permission.toString().split(",");
  for (let i=0; i<permission.length; i++){
    if (permission[i]=="force") return true;
  }
  return false;
}

function logout(){
  $.cookie('global_uid', "");
  $.cookie('global_token', "");
  $.cookie('global_permission', "");
  $.cookie('global_role', "");
  $.cookie('global_name', "");
  window.location.href="./login.html";
}