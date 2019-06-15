window.addEventListener("load", preview_image);

function preview_image(){
   let preview = document.getElementById("preview_image");
   let id_input_image = preview.getAttribute("data-id-input-image");

    document.getElementById(id_input_image).onchange = function () {
        var reader = new FileReader();

        reader.onload = function (e) {
            // get loaded data and render thumbnail.
            preview.src = e.target.result;
            let preview_class = preview.getAttribute("class");
            preview_class = preview_class.replace(/d-none/i, '').trim();
            preview.setAttribute("class", preview_class);
        };

        // read the image file as a data URL.
        reader.readAsDataURL(this.files[0]);
    };

}
