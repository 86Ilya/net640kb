window.onload = main;

function main() {
  let write_message__button = document.getElementsByClassName('write_message__button')[0];
  let write_message__form = document.getElementsByClassName('write_message__form')[0];

  write_message__button.onclick = function () {
    let write_message__form_text = document.getElementsByClassName('write_message__form_text')[0];
    // console.log(write_message__form_text.value.trim().length);
    if(write_message__form_text.value.trim().length > 0){
      write_message__form.submit();
    }
  }


}
