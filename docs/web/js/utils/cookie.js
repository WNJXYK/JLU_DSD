// 扩展 Cookie 操作功能
// Extend Cookie Function
mdui.JQ.extend({
    setCookie: function setCookie(name, value, days){
      var exp = new Date();
      exp.setTime(exp.getTime() + days*24*60*60*1000);
      document.cookie = name + "="+ escape (value) + ";expires=" + exp.toGMTString();
    },
    getCookie: function getCookie(name){
      var arr, reg = new RegExp("(^| )"+name+"=([^;]*)(;|$)");
      if(arr=document.cookie.match(reg)){
        return unescape(arr[2]);
      }else return null;
    }
});