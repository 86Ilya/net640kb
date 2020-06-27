window.addEventListener("load", update_flow_func);

function update_flow_func(){
    var vue_app = new Vue({
      el: '#vue_base_app',
      delimiters: ['[[', ']]'],
      data: {
        user_page_size_formatted: '',
        user_page_size_bytes: ''
      },
      methods: {
        new_friend_request: new_friend_request,
      }
    });


    let ws_scheme = window.location.protocol == "https:" ? "wss://" : "ws://";
    let path = ws_scheme + window.location.host + '/ws/update_flow/';

    let chatsock = new ReconnectingWebSocket(path);
    let initial_page_size = document.getElementById("initial_user_page_size").innerText;
    vue_app.user_page_size_bytes = parseInt(initial_page_size);
    vue_app.user_page_size_formatted = beautify_page_size(vue_app.user_page_size_bytes);

    chatsock.onmessage = function(e) {
        let data = JSON.parse(e.data);
        let message = data['message'];
        if(!message['error']){
          if(message['user_page_size']){
            vue_app.user_page_size_bytes = parseInt(message['user_page_size']);
            vue_app.user_page_size_formatted = beautify_page_size(vue_app.user_page_size_bytes);
          }
          else if(message['upd_user_page_size']){
            vue_app.user_page_size_bytes += parseInt(message['upd_user_page_size']);
            vue_app.user_page_size_formatted = beautify_page_size(vue_app.user_page_size_bytes);
          }
          else if(message['upd_relationship_waiting_for_accept']){
            vue_app.new_friend_request(message['upd_relationship_waiting_for_accept']['person'],
                                       message['upd_relationship_waiting_for_accept']['ignore_page'])
            vue_app.user_page_size_bytes += parseInt(message['upd_user_page_size']);
          }
        }
        else{
          console.log(message['error_reason']);
        }
    };

    //chatsock.onclose = function(e) {
      //console.error('Update flow socket closed unexpectedly', e);
    //};
}

function beautify_page_size(size){
    if(size < 1024){
      return size + "b"
    }
    else{
      return ((size / 1024).toFixed(1)) + "Kb";
    }
}

function new_friend_request(person, ignore_page){
  let cur_loc = window.location.pathname;
  if(ignore_page === cur_loc){
    return;
  }
  // get main menu friends button
  let btn = document.getElementById('friends_main_menu_button');
  // add style to friends button
  let classes = btn.getAttribute('class');
  if(classes){
    classes = classes.concat(' menu__item_blink');
    btn.setAttribute('class', classes);
  }

}

