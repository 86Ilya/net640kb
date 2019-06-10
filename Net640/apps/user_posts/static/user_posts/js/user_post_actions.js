window.addEventListener("load", user_post_actions_func);


function user_post_actions_func(){

    let csrftoken = document.querySelector('input[name=csrfmiddlewaretoken]').value;

    let action_elem = document.querySelectorAll(".fa-heart, .fa-trash-alt");
    action_elem.forEach(function(elem){
        elem.onclick = action_on_user_post;
    });

    function action_on_user_post(event){
      let cur = event.currentTarget;
      let action = cur.getAttribute('data-action');
      let path = cur.getAttribute('data-action-url');
      let post_id = cur.getAttribute('data-post-id');
      let data = {
        csrfmiddlewaretoken: csrftoken,
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



}
