window.addEventListener("load", chat_func);

function chat_func() {
  var room_name = document.getElementById('room_name').getAttribute('value');
  var master_id = document.getElementById('master_id').getAttribute('value');
  var master = document.getElementById('master_name').getAttribute('value');

  let send_message_btn = document.getElementById('send_message_btn');
  let send_message_form = document.getElementById('send_message_form');
  let chat_table = document.getElementById('chat_table');
  let chat_table_body = document.getElementById('chat_table_body');
  let chat_window = document.getElementById('chat_window');
  let ws_scheme = window.location.protocol == "https:" ? "wss://" : "ws://";
  let path = ws_scheme + window.location.host + '/ws/chat/' + room_name + '/';
  let chatsock = new ReconnectingWebSocket(path);

  chat_window.scrollTop = chat_window.scrollHeight;


  chatsock.onmessage = function(event) {
      let message = JSON.parse(event.data)['message'];
      let tr = document.createElement("tr");
      tr.setAttribute("class", "chat__table_message");
      let td_time = document.createElement("td");
      td_time.innerText = message.timestamp;
      td_time.setAttribute("class", "chat__table_message_time");
      tr.appendChild(td_time);

      let td_content = document.createElement("td");
      td_content.innerText = message.content;
      let td_trash = document.createElement("td");
      if(message.author == master){
        td_content.setAttribute("class", "chat__table_message_content chat__table_message_written_by_owner");
        let i_elem = document.createElement("i");
        i_elem.setAttribute("class", "far fa-trash-alt");
        i_elem.setAttribute("data-action-url", "/message_action/");
        i_elem.setAttribute("data-message-id", message.message_id);
        i_elem.setAttribute("data-action", "remove");
        i_elem.onclick = action_on_user_message;
        td_trash.appendChild(i_elem);

      }
      else{
        td_content.setAttribute("class", "chat__table_message_content");
      }
      
      tr.appendChild(td_content);
      tr.appendChild(td_trash);


      chat_table_body.appendChild(tr)

      chat_window.scrollTop = chat_window.scrollHeight;

  };


  send_message_btn.onclick = function () {

    let send_message_form_text = document.getElementById('send_message_form_text');
    let message_content = send_message_form_text.value.trim()
    if(message_content.length > 0){
      let message = {
          message: message_content,
      }
      chatsock.send(JSON.stringify(message));
      send_message_form_text.value = "";
      send_message_form_text.focus();

      // $("#message").val('').focus();
      // return false;
    }
  }
  // console.log(send_message_form);
  send_message_form.onkeypress = function(e) {
    // if(e.which == 13 && e.ctrlKey) {
    //   send_message_btn.onclick();
    // }

    if(e.which == 13) {
      send_message_btn.onclick();
    }
  }


  let csrftoken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

  let action_elem = document.querySelectorAll(".fa-trash-alt");
  action_elem.forEach(function(elem){
      elem.onclick = action_on_user_message;
  });

  function action_on_user_message(event){
    let cur = event.currentTarget;
    let action = cur.getAttribute('data-action');
    let path = cur.getAttribute('data-action-url');
    let message_id = cur.getAttribute('data-message-id');

    let data = {
      csrfmiddlewaretoken: csrftoken,
      action: action,
      message_id: message_id
      };
      
    post_request(data, path).then(function(response){
      response = JSON.parse(response);
      if(response['result'] == true){
        if(action == 'remove'){
          // TODO looks bad
          cur.parentNode.parentNode.remove();
        } 
      }

    });
  }
}
