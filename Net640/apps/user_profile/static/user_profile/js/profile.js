window.addEventListener("load", profile_func);

function profile_func(){
    let copy_link_btn = document.getElementById("copy_link")
    let default_values = document.querySelector('[data-application-variables]');
    let user_page_url = window.location.host + default_values.getAttribute('data-user_page_url');
    let doc_path = window.location.pathname;
    let csrftoken = document.querySelector('input[name=csrfmiddlewaretoken]').value;
    let avatar_trash_icon =document.querySelector(".fa-trash-alt");
    if (avatar_trash_icon){
      avatar_trash_icon.onclick = remove_avatar;
    }

    copy_link_btn.onclick = () => {
      copy_to_clipboard(user_page_url);
      alert("Link copied: " + user_page_url);
    }

    function remove_avatar(){

      let data = {
        csrfmiddlewaretoken: csrftoken,
        action: "remove_avatar",
        };

        post_request(data, doc_path).then((response)=>{
          let json_resp = JSON.parse(response);

          if(json_resp['result'] === true && json_resp['default_avatar_url']){
            let avatar = document.querySelector('#preview_image');
            avatar.src = json_resp['default_avatar_url'];
          }
          avatar_trash_icon.parentNode.remove();
        });
    }

    function copy_to_clipboard(text_to_copy){
      const el = document.createElement('textarea');
      el.value = text_to_copy;
      el.setAttribute('readonly', '');
      el.style.position = 'absolute';
      el.style.left = '-9999px';
      document.body.appendChild(el);
      el.select();
      document.execCommand('copy');
      document.body.removeChild(el);
    }

}
