function post_request(data, path) {
    let data_str = '';
    for (const key in data) {
        data_str += key + '=' + data[key] + '&';
    }

    return new Promise(function (resolve, reject) {
        let xhr = new XMLHttpRequest();
        xhr.open('POST', path, true);
        xhr.timeout = 10000; // 10 секунд (в миллисекундах)
        xhr.setRequestHeader('Content-Type', 'application/x-www-form-urlencoded');
        xhr.onreadystatechange = function () {
            if (this.status == 200) {
                if (this.readyState === 4) {
                    resolve(this.response);
                }
            } else {
                var error = new Error(this.statusText);
                error.code = this.status;
                reject(error);
            }
        };

        xhr.onerror = function () {
            reject(new Error('Network Error'));
        };

        xhr.send(data_str);
    });
}

/**
 * Get the closest matching element up the DOM tree.
 * @private
 * @param  {Element} elem     Starting element
 * @param  {String}  selector Selector to match against
 * @return {Boolean|Element}  Returns null if not match found
 */
function get_closest_upper(elem, selector) {
    let node_elem = elem.parentNode;
    while (node_elem !== document || !node_elem) {
        let found = node_elem.querySelector(selector);
        if (found) {
            return found;
        }
        node_elem = node_elem.parentNode;
    }
}
