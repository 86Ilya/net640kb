import { EventBus, bus_name } from '/static/js/bus.js';

window.addEventListener('load', user_image_actions_func);

function user_image_actions_func() {
    let app_name = 'image_processing';

    let get_image_elem_by_id_and_action = (id, action) => {
        let img_elem = document.querySelector(`[data-image-id="${id}"][data-action="${action}"]`);
        return img_elem;
    };

    let action_map = {
        remove: (message) => {
            let elem = get_image_elem_by_id_and_action(message['image_id'], 'remove');
            elem.parentNode.parentNode.remove();
        },

        like: (message) => {
            let elem = get_image_elem_by_id_and_action(message['image_id'], 'like');
            elem.setAttribute('class', 'fas fa-heart');
            elem.setAttribute('data-action', 'dislike');
            elem.parentNode.getElementsByClassName('badge')[0].innerText = message['likes'].toFixed(1);
        },
        dislike: (message) => {
            let elem = get_image_elem_by_id_and_action(message['image_id'], 'dislike');
            elem.setAttribute('class', 'far fa-heart');
            elem.setAttribute('data-action', 'like');
            elem.parentNode.getElementsByClassName('badge')[0].innerText = message['likes'].toFixed(1);
        },
    };

    EventBus.$on(app_name, (message) => {
        let result = message['result'];
        if (!result) {
            return;
        }

        let action = message['action'];
        action_map[action](message);
        console.log('image processing from bus:' + message);
    });

    let action_elem = document.querySelectorAll('.fa-heart, .fa-trash-alt');
    action_elem.forEach(function (elem) {
        elem.onclick = action_on_user_image;
    });

    function action_on_user_image(event) {
        let cur = event.currentTarget;
        let action = cur.getAttribute('data-action');
        let image_id = cur.getAttribute('data-image-id');
        EventBus.$emit(bus_name, [
            {
                app_name: app_name,
                message: {
                    action: action,
                    image_id: image_id,
                },
            },
        ]);
    }
}
