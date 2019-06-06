window.addEventListener("load", submit_form_func);

function submit_form_func(){

  let submit_button = document.getElementById("submit_button");
  submit_button.onclick = submit_data;

}

function fail(elem){
  setTimeout(()=>{
    elem.innerText = '';
    elem.removeAttribute("class");
  }, 3000);
  elem.setAttribute("class", "failed_animation");
}

function submit_data(event){
  let password1 = document.getElementById("id_password").value;
  let password2 = document.getElementById("id_password_again").value;
  let result = document.getElementById("pre_submit");
  let form = document.querySelector('form[enctype="multipart/form-data"]');
  if(password1 === password2 && password1.length >= 8){
      result.innerText = "Ok";
      form.submit();
  }
  else if(password1 === password2 && password1.length <= 8){
      result.innerText = "Password length must be at least 8 symbol";
      fail(result);
  }
  else {
      result.innerText = "New passwords mismatch";
      fail(result);
    }
}
