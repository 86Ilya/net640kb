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
      
    let relationship_status = document.getElementById("default_values").getAttribute("data-relationship_status");
    let page_owner_username = document.getElementById("default_values").getAttribute("data-page_owner_username");
    let page_owner_id = document.getElementById("default_values").getAttribute("data-page_owner_id");
    let page_owner_size = document.getElementById("default_values").getAttribute("data-page_owner_size");
    let friend = false;
    if(parseInt(relationship_status) ===  RELATIONSHIP_FRIENDS){
      friend = true;
    } 

    let doc_path = window.location.pathname;
    let csrftoken = document.querySelectorAll('input[name=csrfmiddlewaretoken]')[0].value;
    let relationship_descr = RELATIONSHIP_STATUSES[parseInt(relationship_status)];
     console.log("relationship_status",relationship_status, RELATIONSHIP_STATUSES);
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
        RELATIONSHIP_FRIENDS: RELATIONSHIP_FRIENDS
      },
      methods: {
        send_request_for_friends: send_request_for_friends,
        remove_from_friends: remove_from_friends,
        get_user_info: get_user_info,
        update_relationship_descr: update_relationship_descr,
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
  // console.log("update_relationship_descr");
  this.relationship_descr=this.RELATIONSHIP_STATUSES[this.relationship_status];
  console.log("this.$data.relationship_status", this.relationship_status);

  if(parseInt(this.relationship_status) ===  this.RELATIONSHIP_FRIENDS){
    this.friend = true;
  }
  else{
    this.friend = false;
  } 
}

function get_user_info(){
  console.log("in get_user_info");
  
  let data = {
    csrfmiddlewaretoken: this.csrftoken,
    action: "get_user_info",
    };
  
    post_request(data, this.doc_path).then((response)=>{
      let json_resp = JSON.parse(response);
      this.posts = json_resp.posts;
      this.relationship_status = parseInt(json_resp.relationship_status);
      console.log("r.relationship_status", json_resp.relationship_status);
      this.update_relationship_descr();

      //TODO alert -> useful
    }, alert);
}

function send_request_for_friends(){
  let data = {
    csrfmiddlewaretoken: this.csrftoken,
    action: "add",
    };
    
  post_request(data, this.doc_path).then((response)=>{
    let r = JSON.parse(response);
    if(r.status && r.status == true) {
      this.relationship_status = parseInt(r.relationship_status);
      console.log("r.relationship_status", r.relationship_status);
      this.update_relationship_descr();

    }
  }, alert);

}

function remove_from_friends(event){
  // let relationship = event.target.dataset.relationship;
  console.log("this.relationship",this.relationship_status);
  let data = {
    csrfmiddlewaretoken: this.csrftoken,
    action: "remove",
    relationship: this.relationship_status
    };
    
  post_request(data, this.doc_path).then((response)=>{
    let r = JSON.parse(response);
    if(r.status && r.status == true) {
      this.relationship_status = parseInt(r.relationship_status);
      console.log("r.relationship_status", r.relationship_status);
      this.update_relationship_descr();

    }
  }, alert);

}
