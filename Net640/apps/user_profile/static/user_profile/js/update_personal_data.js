window.onload = update_personal_data_func;

function update_personal_data_func(){


  let submit_button = document.getElementById("submit_button");

  submit_button.onclick = submit_data;




}

function submit_data(event){
  let old_password = document.getElementById("old_password").value;
  let new_password1 = document.getElementById("new_password1").value;
  let new_password2 = document.getElementById("new_password2").value;
  let result = document.getElementById("result");

  if(new_password1.length > 0 && new_password2.length > 0){
    if(new_password1 === new_password2){
      result.innerText = "Ok";
    } else {
      result.innerText = "New passwords mismatch";
      event.preventDefault();

    }
  }


}