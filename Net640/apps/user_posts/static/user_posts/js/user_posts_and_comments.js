window.addEventListener("load", user_posts_and_comments_func);

function user_posts_and_comments_func(){
    let app_el = document.querySelector('#vue_postscomments_app');
    let default_values = app_el.querySelector('[data-application-variables]');
    let doc_path = window.location.pathname;
    let post_processing_url = default_values.getAttribute('data-userpost-processing-url');
    let page_owner_id = doc_path.match(/(\d*)\/$/gm);

    if(page_owner_id.length > 1){
      post_processing_url = post_processing_url + page_owner_id + '/';
    }

    let comment_processing_url = default_values.getAttribute('data-usercomment-processing-url');

    let csrftoken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

    var vue_app = new Vue({
      el: '#vue_postscomments_app',
      delimiters: ['[[', ']]'],
      data: {
        doc_path: doc_path,
        csrftoken: csrftoken,
        posts: '',
        post_processing_url: post_processing_url,
        commented_post_id: '', // this variable will contain the post id, which is currently commented
        comment_processing_url: comment_processing_url,
      },
      methods: {
        action_on_user_message: action_on_user_message,
        get_posts: get_posts,
        show_modal_add_comment: show_modal_add_comment,
        close_modal_add_comment: close_modal_add_comment,
        add_comment: add_comment,
        remove_user_post: remove_user_post,
        remove_user_comment: remove_user_comment,
        remove_user_message: remove_user_message,
      }

    });

    vue_app.get_posts();

    function remove_user_message(message_id, message_type){
      if(message_type === 'post'){
        vue_app.remove_user_post(message_id);
      }
      else if(message_type === 'comment'){
        vue_app.remove_user_comment(message_id);
      }
    }

    function remove_user_post(id){
      let cur_post = this.$data.posts.find((elem) => elem.id == parseInt(id));
      if(cur_post){
        let index = vue_app.$data.posts.indexOf(cur_post);
        vue_app.$data.posts.splice(index, 1);
        return
      }

    }

    function remove_user_comment(id){
    // find comment in the array and remove it
    for(let i=0; i<vue_app.$data.posts.length; i++){
      let cur_comment = vue_app.$data.posts[i].comments.find((elem) => elem.id == parseInt(id));
      if(cur_comment){
        let index = vue_app.$data.posts[i].comments.indexOf(cur_comment);
        vue_app.$data.posts[i].comments.splice(index, 1);
        return
        }
      }

    }

    function show_modal_add_comment(event){
      let modal = document.getElementById("modal_add_comment"); // TODO replace by var in the module
      let post_id = event.currentTarget.getAttribute('data-message-id');
      this.$data.commented_post_id = post_id;
      modal.style.display = "block";

    }

    function close_modal_add_comment(){
      let modal = document.getElementById("modal_add_comment"); // TODO replace by var in the module
      this.$data.commented_post_id = '';
      modal.style.display = "none";
    }

    function add_comment(event){
      event.preventDefault();
      let form = event.currentTarget.parentNode;
      let content_elem = form.querySelector('[name=content]');
      content_elem.focus();
      let content = content_elem.value;
      let csrfmiddlewaretoken = form.querySelector('[name=csrfmiddlewaretoken]').value;
      let post_id = this.$data.commented_post_id;

      let data = {
        csrfmiddlewaretoken: csrfmiddlewaretoken,
        post_id: post_id,
        content: content,

      };

      post_request(data, this.$data.comment_processing_url).then((response)=>{
        let json_resp = JSON.parse(response);
        this.close_modal_add_comment(event);
        if(json_resp.errors){
          alert('Internal server error');
          return
        }

        if(json_resp.result === true){
          let cur_post = this.$data.posts.find((elem) => elem.id == parseInt(post_id));
          let comment_meta = json_resp["comment_meta_data"];
          comment_meta.content = content;
          cur_post.comments.unshift(comment_meta);
        }
        //TODO alert -> useful
      }, alert);

      }


  function action_on_user_message(event){
        let cur = event.currentTarget;
        let action = cur.getAttribute('data-action');
        let path = cur.getAttribute('data-action-url');
        let message_id = cur.getAttribute('data-message-id');
        let message_type_elem = get_closest_upper(cur, '[data-message-type]');
        let message_type = message_type_elem.getAttribute('data-message-type');

        let data = {
          csrfmiddlewaretoken: vue_app.$data.csrftoken,
          action: action,
          id: message_id
          };

        post_request(data, path).then(function(response){
          response = JSON.parse(response);

          if(response['result'] === true){

            if(action == 'remove'){
              vue_app.remove_user_message(message_id, message_type);
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


  function get_posts(){

    let data = {
      csrfmiddlewaretoken: this.csrftoken,
      action: "get_posts",
      };

      post_request(data, this.$data.post_processing_url).then((response)=>{
        let json_resp = JSON.parse(response);
        this.posts = json_resp.posts;

        //TODO alert -> useful
      }, alert);
  }

}

