window.addEventListener("load", user_image_actions_func);


function user_image_actions_func(){

    let csrftoken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
    let action_elem = document.querySelectorAll(".fa-heart, .fa-trash-alt");
    action_elem.forEach(function(elem){
        elem.onclick = action_on_user_image;
    });

    function action_on_user_image(event){

      let cur = event.currentTarget;
      let action = cur.getAttribute('data-action');
      let path = cur.getAttribute('data-action-url');
      let image_id = cur.getAttribute('data-image-id');

      let data = {
        csrfmiddlewaretoken: csrftoken,
        action: action,
        image_id: image_id
        };
        
      post_request(data, path).then(function(response){
        response = JSON.parse(response);

        if(response['result'] == true){
          if(action == 'remove'){
            // TODO looks bad
            cur.parentNode.parentNode.remove();
          } 
          else if(action == 'like'){
            cur.setAttribute('class', 'fas fa-heart');
            cur.setAttribute('data-action', 'dislike');
            cur.parentNode.getElementsByClassName("badge")[0].innerText = response["likes"].toFixed(1);
          }
          else if(action == 'dislike'){
            cur.setAttribute('class', 'far fa-heart');
            cur.setAttribute('data-action', 'like');
            cur.parentNode.getElementsByClassName("badge")[0].innerText = response["likes"].toFixed(1);
          }
          
        }

      });
    }



}
