window.addEventListener("load", update_flow_func);

function update_flow_func(){
    var vue_app = new Vue({
      el: '#vue_base_app',
      delimiters: ['[[', ']]'],
      data: {
        user_page_size_formatted: '',
        user_page_size_bytes: ''
      }
    });
 

    let ws_scheme = window.location.protocol == "https:" ? "wss://" : "ws://";
    let path = ws_scheme + window.location.host + '/ws/update_flow/';
    //var path = 'ws://127.0.0.1:8000/update_flow/';

    //let chatsock = new WebSocket(path);
    let chatsock = new ReconnectingWebSocket(path);
    let initial_page_size = document.getElementById("initial_user_page_size").innerText;
    vue_app.user_page_size_bytes = parseInt(initial_page_size);
    vue_app.user_page_size_formatted = beautify_page_size(vue_app.user_page_size_bytes);  

    chatsock.onmessage = function(e) {
        let data = JSON.parse(e.data);
        let message = data['message'];
        if(!message['error']){
          let size = vue_app.user_page_size;
          if(message['user_page_size']){
            vue_app.user_page_size_bytes = parseInt(message['user_page_size']);
          } 
          else if(message['inc_user_page_size']){
            vue_app.user_page_size_bytes += parseInt(message['inc_user_page_size']);
          }
          else if(message['dec_user_page_size']){
            vue_app.user_page_size_bytes -= parseInt(message['dec_user_page_size']);
          }
          vue_app.user_page_size_formatted = beautify_page_size(vue_app.user_page_size_bytes);
        }
        else{
          console.log(message['error_reason']);

        }
    };

    chatsock.onclose = function(e) {
      //console.error('Update flow socket closed unexpectedly', e);
    };
}

function beautify_page_size(size){
  return (size / 1024).toFixed(1);
};

