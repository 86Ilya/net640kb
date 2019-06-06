window.addEventListener("load", chat_func);

function chat_func() {
  var room_name = document.getElementById('room_name').getAttribute('value');
  var master_id = document.getElementById('master_id').getAttribute('value');
  var master = document.getElementById('master_name').getAttribute('value');

  let send_message_btn = document.getElementById('send_message_btn');
  let send_message_form = document.getElementById('send_message_form');
  let chat_table = document.getElementById('chat_table');
  let chat_window = document.getElementById('chat_window');
  let ws_scheme = window.location.protocol == "https:" ? "wss://" : "ws://";
  let path = ws_scheme + window.location.host + '/ws/chat/' + room_name + '/';
  //var path = 'ws://127.0.0.1:8000/'+'ws/chat/' + room_name + '/';
  let chatsock = new ReconnectingWebSocket(path);
  //let chatsock = new WebSocket(path);

  // var chatsock = new WebSocket(ws_scheme + '://' + window.location.hostname + '/' + group_id + ':8000');
  // chat__table.setAttribute('style','.written_by_${ownerName} {background-color: white;}');
  chat_window.scrollTop = chat_window.scrollHeight;


  chatsock.onmessage = function(event) {
      let message = JSON.parse(event.data)['message'];
      //debugger
      let ele = document.createElement("tr");
      // var ele = $('<tr></tr>')
      let td_time = document.createElement("td");
      td_time.innerText = message.timestamp;
      td_time.setAttribute("class", "chat__table_message_time");
      ele.appendChild(td_time);

      let td_content = document.createElement("td");
      td_content.innerText = message.content;
      // console.log(data.author == ownerName);
      if(message.author == master){
        td_content.setAttribute("class", "chat__table_message_content chat__table_message_written_by_owner");
      }
      else{
        td_content.setAttribute("class", "chat__table_message_content");
      }
      
      ele.appendChild(td_content);


      chat_table.appendChild(ele)

      chat_window.scrollTop = chat_window.scrollHeight;
      //chat_table.scrollTop = chat_table.scrollHeight;

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
}
