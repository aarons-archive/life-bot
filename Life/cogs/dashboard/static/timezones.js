'use strict';

function timezoneSearchFunction() {
    const input = document.getElementById('timezoneSearch');
    const list = document.getElementById('timezoneList')
    const list_items = list.getElementsByClassName('col-6')

    let text;

    for (let index = 0; index < list_items.length; index++) {
        text = list_items[index].textContent || list_items[index].innerText;
        if (text.toUpperCase().indexOf(input.value.toUpperCase()) > -1) {
            list_items[index].style.display = "";
        } else {
            list_items[index].style.display = "none";
        }
    }
}

