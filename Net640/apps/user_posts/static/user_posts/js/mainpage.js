window.addEventListener("load", mainpage_func);

function mainpage_func(){
    let default_values = document.getElementById("default_values")
    let post_action_url = default_values.getAttribute('data-action-url');

    let doc_path = window.location.pathname;
    let csrftoken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

    var vue_app = new Vue({
      el: '#vue_mainpage_app',
      delimiters: ['[[', ']]'],
      data: {
        doc_path: doc_path,
        csrftoken: csrftoken,
        posts: '',
        post_action_url: post_action_url,
      },
      methods: {
        action_on_user_post: action_on_user_post,
        get_own_posts: get_own_posts,
      }

    });

    vue_app.get_own_posts();
}

function get_own_posts(){

  let data = {
    csrfmiddlewaretoken: this.csrftoken,
    action: "get_own_posts",
    };

    post_request(data, this.doc_path).then((response)=>{
      let json_resp = JSON.parse(response);
      this.posts = json_resp.posts;

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
