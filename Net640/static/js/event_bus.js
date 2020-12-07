import { EventBus, bus_name } from '/static/js/bus.js';

window.addEventListener('load', event_bus);

function event_bus() {
    let ws_scheme = window.location.protocol == 'https:' ? 'wss://' : 'ws://';
    let path = ws_scheme + window.location.host + '/ws/event_bus/';

    let event_bus_socket = new ReconnectingWebSocket(path);

    /*
        Event Bus request message example:

        [{
            "app_name": "image_processing",
            "message": {
                "action": "like",
                "image_id": 8,
            },
        }, ...]

        There are two required paremeter for Python backend: "app_name" and "message"
        "app_name" is used for routing message, "message" is used for processing inside app.


        Event Bus response message example:

        [{
            "app_name": "image_processing",
            "message": {
                "result": true
                "action": "like",
                "image_id": 8,
            },
        }, ...]
    */

    // process messages from vue applications
    EventBus.$on(bus_name, (data) => {
        event_bus_socket.send(JSON.stringify(data));
    });

    // process messages from python backend
    event_bus_socket.onmessage = function (e) {
        let data = JSON.parse(e.data);
        for (let i = 0; i < data.length; i++) {
            let app_name = data[i]['app_name'];
            let message = data[i]['message'];
            EventBus.$emit(app_name, message);
        }
    };
}
