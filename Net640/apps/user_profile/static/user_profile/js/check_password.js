window.addEventListener("load", submit_form_func);

function submit_form_func(){

  let result = document.getElementById("pre_submit");
  let form = document.querySelector('form[enctype="multipart/form-data"]');
  // submit form
  let submit_button = document.getElementById("submit_button");
  submit_button.onclick = submit_data;
  // check password strengh while user typing it
  let password_input_field = document.getElementById('id_password');
  password_input_field.oninput = check_password_strengh;


  function submit_data(event){
    let password1 = document.getElementById("id_password").value;
    let password2 = document.getElementById("id_password_again").value;

    // senf form only if password have enouth length or password is empty
    if(password1 === password2 && (password1.length >= 8 || password1.length == 0)){
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

  function check_password_strengh(event){
    let password1 = document.getElementById("id_password").value;
    let checked_pass = zxcvbn(password1);
    result.innerText = `Your password can be cracked in ${checked_pass.crack_times_display.offline_slow_hashing_1e4_per_second}`
  }

  function fail(elem){
    setTimeout(()=>{
      elem.innerText = '';
      elem.removeAttribute("class");
    }, 3000);
    elem.setAttribute("class", "failed_animation");
  }

}
