window.addEventListener("load", preview_avatar_func);

function preview_avatar_func(){

    document.getElementById("id_avatar").onchange = function () {
        var reader = new FileReader();

        reader.onload = function (e) {
            // get loaded data and render thumbnail.
            document.getElementById("avatar_image").src = e.target.result;
        };

        // read the image file as a data URL.
        reader.readAsDataURL(this.files[0]);
    };

}
