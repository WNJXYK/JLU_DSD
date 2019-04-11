var LOGIN_LOCATION = "/interface/login";
var VERIFY_LOCATION = "/interface/verify";

// 账户欢迎处理
// Welcome for User Account
function loginWelcome(){
  loginVerify();
  if (UID!=null && SID!=null){
    mdui.snackbar({message: 'Welcome ' + Nickname});
    updateUserTab();
  }//else loginDialog();
}

// 检验用户登陆状态
// Verify User Account State
function loginVerify(){
  // Get Info from Cookie
  UID = $$.getCookie("UID");
  SID = $$.getCookie("SID");
  Authority = $$.getCookie("Authority");
  Email = $$.getCookie("Email");
  Nickname = $$.getCookie("Nickname");

  if (UID!=null && SID!=null){
    // Verify User Account
    $$.ajax({
      method: 'POST',
      url: SERVER + VERIFY_LOCATION,
      data: {
        SID: SID,
        UID: UID
      },
      async: false,
      success: function (data) {
        let objs = JSON.parse(data);
        if (objs["status"]==0){
          // Verified
          $$.setCookie("Authority", objs["info"]["Authority"], 7);
          $$.setCookie("Nickname", objs["info"]["Nickname"], 7);
          $$.setCookie("Admin", objs["info"]["Admin"], 7);
        }else UID=SID=null;
      }
    });
  }else UID=SID=null;
}

function setServerDialog(){
  mdui.dialog({
    title: "Set Server",
    content: '<div class="mdui-textfield">\
              <label class="mdui-textfield-label">Server</label>\
              <input class="mdui-textfield-input" type="text" id="Server-Input" value="' + SERVER + '"/>\
            </div>',
    buttons: [
      { text: 'Cancel'},
      {
        text: 'Confirm',
        onClick: function(inst){
          SERVER = $$("#Server-Input").val();
          $$.setCookie("SERVER", SERVER, 365*100);
        }
      }
    ]
  });
}

// 呼出登陆窗口
// Call Login Dialog
function loginDialog(){
  mdui.dialog({
    title: 'Login',
    content: '<div class="mdui-textfield">\
                <label class="mdui-textfield-label">E-Mail</label>\
                <input class="mdui-textfield-input" type="text" id="login_email"/>\
              </div>\
              <br>\
              <div class="mdui-textfield">\
                <label class="mdui-textfield-label">Password</label>\
                <input class="mdui-textfield-input" type="password" id="login_password"/>\
              </div>',
    buttons: [
      { text: 'Cancel'},
      {
        text: 'Login',
        onClick: function(inst){
          $$.ajax({
            method: 'POST',
            url: SERVER + LOGIN_LOCATION,
            data: {
              email: $$("#login_email").val(),
              password: hex_md5($$("#login_password").val())
            },
            success: function (data) {
              let objs = JSON.parse(data);
              console.log(objs);
              if (objs["status"]==0){
                  $$.setCookie("Email", $$("#login_email").val(), 7);
                  $$.setCookie("UID", objs["info"]["UID"], 7);
                  $$.setCookie("SID", objs["info"]["SID"], 7);
                  $$.setCookie("Authority", objs["info"]["Authority"], 7);
                  $$.setCookie("Nickname", objs["info"]["Nickname"], 7);
                  self.location.reload();
              }else{
                  mdui.snackbar({message: 'Login Failed : ' + objs["msg"]});
              }
            }
          });
        }
      }
    ]
  });
}

// 用户登出
// User logout
function logout(){
	$$.setCookie("SID", null, 0);
	self.location.reload();
}

// 更新用户板块
// Upate User Tab
function updateUserTab(){
	let authority_name = ["Hardware", "Hardware", "Student", "Teacher", "Administrator"];
  
  let user_tab = $$('\
	  <div class="mdui-card">\
	  	<!-- 用户昵称、ID、权限 -->\
		  <!-- User Nickname & UID & Authority -->\
		  <div class="mdui-card-media">\
		    <img src="./imgs/card.jpg"/>\
		    <div class="mdui-card-media-covered">\
		      <div class="mdui-card-primary">\
		        <div class="mdui-card-primary-title">' + Nickname + '</div>\
		        <div class="mdui-card-primary-subtitle">' + authority_name[Authority] + ' (UID:' + UID + ')</div>\
		      </div>\
		    </div>\
		    <!-- 用户登出操作 -->\
		  	<!-- Logout -->\
			  <div class="mdui-card-menu" mdui-tooltip="{content: \'Logout\'}">\
			    <button class="mdui-btn mdui-btn-icon mdui-text-color-white" onclick="logout();"><i class="mdui-icon material-icons">&#xe14c;</i></button>\
			  </div>\
		  </div>\
		  \
		  <!-- 卡片的标题和副标题 -->\
		  <div id="Admin-Tool">\
        <div class="mdui-card-primary">\
          <div class="mdui-card-primary-title">Admin Menu</div>\
          <!--div class="mdui-card-primary-subtitle">Subtitle</div-->\
        </div>\
        <!-- 卡片的内容 -->\
        <!--div class="mdui-card-content">子曰：「学而时习之，不亦说乎？有朋自远方来，不亦乐乎？人不知，而不愠，不亦君子乎？」</div-->\
        <!-- 卡片的按钮 -->\
        <div class="mdui-card-actions">\
          <button class="mdui-btn mdui-ripple" onclick="addHardwareDialog();" >Register Hardware</button>\
          <button class="mdui-btn mdui-ripple" onclick="bindHardwareDialog();" >Bind Hardware</button>\
          <button class="mdui-btn mdui-ripple" onclick="allHardwareDialog();" >View & Delete Hardware</button>\
        </div>\
		  </div>\
		</div>\
	');
	$$("#tab-user").html("");
	$$("#tab-user").append(user_tab);
	if ($$.getCookie("Admin")==1) $$("#Admin-Tool").show(); else $$("#Admin-Tool").hide();
}