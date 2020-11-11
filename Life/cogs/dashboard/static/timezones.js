/*
 * Life
 * Copyright (C) 2020 Axel#3456
 *
 * Life is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software
 * Foundation, either version 3 of the License, or (at your option) any later version.
 *
 * Life is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
 * PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.
 *
 * You should have received a copy of the GNU Affero General Public License along with Life. If not, see https://www.gnu.org/licenses/.
 *
 */

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

