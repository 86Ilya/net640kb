window.onload = my_images_func;

function my_images_func(){
    let form = document.getElementsByClassName("my_images_upload_image__form")[0];
    let button = document.getElementsByClassName("my_images_upload_image__button")[0];
    button.onclick = ()=>form.submit(); // TODO проверки всякие
    let input_file = document.querySelector(".my_images_upload_image__form input[type=file]");
    filename_field = document.getElementById("filename");

    input_file.onchange = (event)=>{
        let filename = event.target.value.replace(/.*\\/, "");
        filename_field.innerText = filename;
        // console.log(filename);
    };


}