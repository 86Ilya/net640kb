import { EventBus, bus_name } from '/static/js/bus.js';

window.addEventListener('load', update_flow_func);

function update_flow_func() {
    var vue_app = new Vue({
        el: '#vue_base_app',
        delimiters: ['[[', ']]'],
        data: {
            user_page_size_formatted: '',
            user_page_size_bytes: '',
        },
        watch: {
            user_page_size_bytes: (new_size, old_size) => {
                if (new_size < 0) {
                    EventBus.$emit(bus_name, [
                        {
                            app_name: 'user_profile',
                            message: {
                                action: 'get_user_page_size',
                            },
                        },
                    ]);
                }
            },
        },

        methods: {
            new_friend_request: new_friend_request,
        },
    });

    let initial_page_size = document.getElementById('initial_user_page_size').innerText;
    vue_app.user_page_size_bytes = parseInt(initial_page_size);
    vue_app.user_page_size_formatted = beautify_page_size(vue_app.user_page_size_bytes);

    let action_map = {
        user_page_size: (message) => {
            vue_app.user_page_size_bytes = parseInt(message['size']);
            vue_app.user_page_size_formatted = beautify_page_size(vue_app.user_page_size_bytes);
        },

        upd_user_page_size: (message) => {
            vue_app.user_page_size_bytes += parseInt(message['delta']);
            vue_app.user_page_size_formatted = beautify_page_size(vue_app.user_page_size_bytes);
        },
        upd_relationship_waiting_for_accept: (message) => {
            vue_app.new_friend_request(
                message['upd_relationship_waiting_for_accept']['person'],
                message['upd_relationship_waiting_for_accept']['ignore_page']
            );
            vue_app.user_page_size_bytes += parseInt(message['upd_user_page_size']);
        },
    };

    EventBus.$on('user_profile', (message) => {
        let result = message['result'];
        if (!result) {
            return;
        }

        let action = message['action'];
        action_map[action](message);
    });
}

function beautify_page_size(size) {
    if (size < 1024) {
        return size + 'b';
    } else {
        return (size / 1024).toFixed(1) + 'Kb';
    }
}

function new_friend_request(person, ignore_page) {
    let cur_loc = window.location.pathname;
    if (ignore_page === cur_loc) {
        return;
    }
    // get main menu friends button
    let btn = document.getElementById('friends_main_menu_button');
    // add style to friends button
    let classes = btn.getAttribute('class');
    if (classes) {
        classes = classes.concat(' menu__item_blink');
        btn.setAttribute('class', classes);
    }
}
