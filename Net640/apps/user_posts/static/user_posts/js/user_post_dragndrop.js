window.addEventListener("load", user_post_dragndrop_func);


function user_post_dragndrop_func(){
  // TODO add drag n drop, and remove browse button in form
  let preview = document.getElementById("preview_image");
  document.getElementById("id_image").onchange = function () {
        var reader = new FileReader();
        reader.onload = function (e) {
            preview.src = e.target.result;
        };
        // read the image file as a data URL.
        reader.readAsDataURL(this.files[0]);
        preview.setAttribute('class', 'w-50 mx-auto');
    };
}
