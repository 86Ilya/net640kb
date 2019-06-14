window.addEventListener("load", friends_func);


function friends_func(){
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


    let doc_path = window.location.pathname;
    let csrftoken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

    var vue_app = new Vue({
      el: '#vue_friends_lists_app',
      delimiters: ['[[', ']]'],
      data: {
        friends_list: '',
        friends_waiting_for_accept_list: '',
        friends_sent_requests_list: '',
        show: false,
        doc_path: doc_path,
        csrftoken: csrftoken
      },
      methods: {
        cancel: cancel,
        accept: accept,
      }
    });
    
    vue_app.doc_path = doc_path;
    vue_app.csrftoken = csrftoken;

    function update_friends_list(){
      get_friends_lists(doc_path, csrftoken).then(function(response){
        let json_resp = JSON.parse(response);
        vue_app.friends_list = json_resp.friends_list;
        vue_app.friends_waiting_for_accept_list = json_resp.friends_waiting_for_accept_list;
        vue_app.friends_sent_requests_list = json_resp.friends_sent_requests_list;
        // TODO change alert to something useful
      }, alert);
    }

    function cancel(event){
      let user_id = event.target.dataset.user_id;

      let data={
        csrfmiddlewaretoken:this.$data.csrftoken,
        action: "cancel",
        user_id: user_id,
        // Server must know the real relationship between users
        //relationship: relationship
        };

      post_request(data, this.$data.doc_path).then((response)=>{
        let json_resp = JSON.parse(response);
        if(json_resp.status && json_resp.status == true) {
          event.target.dataset.relationship = json_resp.relationship_status;
          // TODO update only one person status 
          update_friends_list();

        }
      }, alert);
    }

    function accept(event){
      let user_id = event.target.dataset.user_id;
      let relationship = event.target.dataset.relationship;

      let data={
        csrfmiddlewaretoken: this.$data.csrftoken,
        action: "accept",
        user_id: user_id,
        relationship: relationship
        };

      post_request(data, this.$data.doc_path).then((response)=>{
        let json_resp = JSON.parse(response);
        //console.log(r);
        if(json_resp.status && json_resp.status == true) {
          event.target.dataset.relationship = json_resp.relationship_status;
          // TODO update only one person status 
          update_friends_list();
        }
      }, alert);
    }

    update_friends_list();
}


function get_friends_lists(doc_path, csrftoken){
  let data = {
    csrfmiddlewaretoken: csrftoken,
    action: "get_friends_lists",
    };
    
  return post_request(data, doc_path);
}
