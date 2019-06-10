window.addEventListener("load", user_view_func);

function user_view_func(){
    const NO_RELATIONSHIP= -1;
    const RELATIONSHIP_REQUEST = 0;
    const RELATIONSHIP_WAITING_FOR_ACCEPT = 1;
    const RELATIONSHIP_FRIENDS = 2;
    const RELATIONSHIP_BLOCKED = 3;
    let RELATIONSHIP_STATUSES = {
      "0": 'Request has sent',
      "1": 'Waiting for accept',
      "2": 'Friends',
      "3": 'Blocked',
      "-1": 'Not a friend',
    };
      
    let default_values = document.getElementById("default_values")
    let relationship_status = default_values.getAttribute("data-relationship_status");
    let page_owner_username = default_values.getAttribute("data-page_owner_username");
    let page_owner_id = default_values.getAttribute("data-page_owner_id");
    let page_owner_size = default_values.getAttribute("data-page_owner_size");
    let post_action_url = default_values.getAttribute('data-action-url');

    // TODO -> to function
    page_owner_size = (parseInt(page_owner_size) / 1024).toFixed(1) + "Kb";

    let friend = false;
    if(parseInt(relationship_status) ===  RELATIONSHIP_FRIENDS){
      friend = true;
    } 

    let doc_path = window.location.pathname;
    let csrftoken = document.querySelectorAll('input[name=csrfmiddlewaretoken]')[0].value;
    let relationship_descr = RELATIONSHIP_STATUSES[parseInt(relationship_status)];

    var vue_app = new Vue({
      el: '#vue_user_view_app',
      delimiters: ['[[', ']]'],
      data: {
        friend: friend,
        relationship_status: relationship_status,
        relationship_descr: relationship_descr,
        doc_path: doc_path,
        csrftoken: csrftoken,
        posts: '',
        page_owner_username: page_owner_username,
        page_owner_id: page_owner_id,
        page_owner_size: page_owner_size,
        RELATIONSHIP_STATUSES: RELATIONSHIP_STATUSES,
        RELATIONSHIP_FRIENDS: RELATIONSHIP_FRIENDS,
        post_action_url: post_action_url,
      },
      methods: {
        get_user_info: get_user_info,
        update_relationship_descr: update_relationship_descr,
        action_on_user_post: action_on_user_post,
      }
    });
    
    vue_app.get_user_info();

    var interval_id;
    var running = false;
    window.onfocus = ()=>{
      if(running) return;
      vue_app.get_user_info();
      interval_id = setInterval(vue_app.get_user_info, 10000);
    };

    window.onblur = ()=>{
      running = false;
      clearInterval(interval_id);
    };

}

function update_relationship_descr(){
  this.relationship_descr=this.RELATIONSHIP_STATUSES[this.relationship_status];

  if(parseInt(this.relationship_status) ===  this.RELATIONSHIP_FRIENDS){
    this.friend = true;
  }
  else{
    this.friend = false;
  } 
}

function get_user_info(){
  
  let data = {
    csrfmiddlewaretoken: this.csrftoken,
    action: "get_user_info",
    };
  
    post_request(data, this.doc_path).then((response)=>{
      let json_resp = JSON.parse(response);
      this.posts = json_resp.posts;
      this.relationship_status = parseInt(json_resp.relationship_status);
      this.update_relationship_descr();

      //TODO alert -> useful
    }, alert);
}

function action_on_user_post(event){
      let cur = event.currentTarget;
      let action = cur.getAttribute('data-action');
      let path = cur.getAttribute('data-action-url');
      let post_id = cur.getAttribute('data-post-id');
      let data = {
        csrfmiddlewaretoken: this.csrftoken,
        action: action,
        post_id: post_id
        };
      post_request(data, path).then(function(response){
        response = JSON.parse(response);

        if(response['result'] == true){

          if(action == 'remove'){
            // TODO looks bad
            cur.parentNode.parentNode.parentNode.parentNode.remove();
          } 
          else if(action == 'like'){
            cur.setAttribute('class', 'fas fa-heart');
            cur.setAttribute('data-action', 'dislike');
            cur.parentNode.parentNode.getElementsByClassName("badge")[0].innerText = response["likes"].toFixed(1);
            
          }
          else if(action == 'dislike'){
            cur.setAttribute('class', 'far fa-heart');
            cur.setAttribute('data-action', 'like');
            cur.parentNode.parentNode.getElementsByClassName("badge")[0].innerText = response["likes"].toFixed(1);
            
          }
 
              
        }

      });
    }
