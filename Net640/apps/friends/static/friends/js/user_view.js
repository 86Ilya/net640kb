window.addEventListener("load", user_view_func);

function user_view_func(){
    const NO_RELATIONSHIP= -1;
    const RELATIONSHIP_REQUEST_HAS_SENT = 0;
    const RELATIONSHIP_WAITING_FOR_ACCEPT = 1;
    const RELATIONSHIP_FRIENDS = 2;
    const RELATIONSHIP_BLOCKED = 3;

    let RELATIONSHIP_STATUSES = {};
    RELATIONSHIP_STATUSES[NO_RELATIONSHIP] = 'Not a friend'
    RELATIONSHIP_STATUSES[RELATIONSHIP_REQUEST_HAS_SENT] = 'Request has sent';
    RELATIONSHIP_STATUSES[RELATIONSHIP_WAITING_FOR_ACCEPT] = 'Waiting for accept'
    RELATIONSHIP_STATUSES[RELATIONSHIP_FRIENDS] = 'Friends'
    RELATIONSHIP_STATUSES[RELATIONSHIP_BLOCKED] = 'Blocked'

    let app_el = document.querySelector('#vue_user_view_app');
    let default_values = app_el.querySelector('[data-application-variables]');
    let relationship_status = default_values.getAttribute("data-relationship_status");
    let page_owner_username = default_values.getAttribute("data-page_owner_username");
    let page_owner_id = default_values.getAttribute("data-page_owner_id");
    let page_owner_size = default_values.getAttribute("data-page_owner_size");

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
        page_owner_username: page_owner_username,
        page_owner_id: page_owner_id,
        page_owner_size: page_owner_size,
        RELATIONSHIP_STATUSES: RELATIONSHIP_STATUSES,
        RELATIONSHIP_FRIENDS: RELATIONSHIP_FRIENDS,
      },
      methods: {
        get_user_info: get_user_info,
        update_relationship_descr: update_relationship_descr,
        send_request_for_friends: send_request_for_friends,
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
      this.relationship_status = parseInt(json_resp.relationship_status);
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
      this.update_relationship_descr();

    }
  }, alert);

}
