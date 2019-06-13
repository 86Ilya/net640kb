window.addEventListener("load", preview_avatar_func);

function preview_avatar_func(){
   let preview = document.getElementById("avatar_image");

    document.getElementById("id_avatar").onchange = function () {
        var reader = new FileReader();

        reader.onload = function (e) {
            // get loaded data and render thumbnail.
            preview.src = e.target.result;
            preview.setAttribute("class", "w-50 mx-auto");
        };

        // read the image file as a data URL.
        reader.readAsDataURL(this.files[0]);
    };

}
