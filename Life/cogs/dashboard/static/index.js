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

function getCookie(cookie) {
    const name = cookie + "=";
    const decodedCookie = decodeURIComponent(document.cookie);
    const ca = decodedCookie.split(';');
    for(let i = 0; i <ca.length; i++) {
        let c = ca[i];
        while (c.charAt(0) === ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) === 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function parseTime(milliseconds) {
    return moment.utc(milliseconds).format('HH:mm:ss')}

function getWebsocketUrl() {
    if (window.location.protocol === 'http:') { return `ws://${window.location.host}/websocket` }
    else if (window.location.protocol === 'https:') { return `wss://${window.location.host}/websocket` }
}

function set_current_track(track_data) {
    document.getElementById('CurrentThumbnail').src = track_data.thumbnail
    document.getElementById('CurrentTitle').innerHTML = track_data.title
    document.getElementById('CurrentTitle').href = track_data.uri
    document.getElementById('CurrentAuthor').innerHTML = `Author: ${track_data.author}`
    document.getElementById('CurrentLength').innerHTML = `Length: ${parseTime(track_data.length)}`
    document.getElementById('CurrentRequester').innerHTML = `Requester: ${track_data.requester_name}`
}

function reset_current_track() {
    document.getElementById('CurrentThumbnail').src = 'https://media.mrrandom.xyz/no_image320x180.png'
    document.getElementById('CurrentTitle').innerHTML = 'No current track'
    document.getElementById('CurrentTitle').href = '#'
    document.getElementById('CurrentAuthor').innerHTML = ''
    document.getElementById('CurrentLength').innerHTML = ''
    document.getElementById('CurrentRequester').innerHTML = ''
}

function set_position(position_data) {
    document.getElementById('CurrentPosition').innerHTML = `Position: ${parseTime(position_data.position)}`
    document.getElementById('CurrentProgress').style.width = `${(100 / (Math.round(position_data.length) / 1000)) * (Math.round(position_data.position) / 1000)}%`
    document.getElementById('CurrentProgressBar').classList.remove('invisible')
}

function reset_position() {
    document.getElementById('CurrentPosition').innerHTML = ''
    document.getElementById('CurrentProgress').style.width = '0'
    document.getElementById('CurrentProgressBar').classList.add('invisible')
}

function set_queue(position, track_data) {
    document.getElementById(`QueueThumbnail${position}`).src = track_data.thumbnail
    document.getElementById(`QueueTitle${position}`).innerHTML = track_data.title
    document.getElementById(`QueueTitle${position}`).href = track_data.uri
    document.getElementById(`QueueAuthor${position}`).innerHTML = `Author: ${track_data.author}`
    document.getElementById(`QueueLength${position}`).innerHTML = `Length: ${parseTime(track_data.length)}`
    document.getElementById(`QueueRequester${position}`).innerHTML = `Requester: ${track_data.requester_name}`
}

function reset_queue(position) {
    document.getElementById(`QueueThumbnail${position}`).src = 'https://media.mrrandom.xyz/no_image320x180.png'
    document.getElementById(`QueueTitle${position}`).innerHTML = 'Empty queue slot'
    document.getElementById(`QueueTitle${position}`).href = '#'
    document.getElementById(`QueueAuthor${position}`).innerHTML = ''
    document.getElementById(`QueueLength${position}`).innerHTML = ''
    document.getElementById(`QueueRequester${position}`).innerHTML = ''
}


const websocket = new WebSocket(getWebsocketUrl())

websocket.onmessage = function(event) {
    const data = JSON.parse(event.data)

    if (data.op === 1) {
        let guild_id = window.location.pathname.replace('/dashboard/', '')
        websocket.send(JSON.stringify({op: 2, data: {guild_id: guild_id, identifier: getCookie('identifier')}}))
    }

    if (data.op === 0) {
        const event_data = data.data

        if (data.event === 'CONNECTED' || data.event === "READY") {

            const current = JSON.parse(event_data.current)
            if (current !== null) {
                set_current_track(current)
            } else {
                reset_current_track()
            }

            const queue = JSON.parse(event_data.queue)
            if (queue.queue !== null) {
                for (let index = 0; index < 4; index++) {
                    if (queue.queue[index] !== undefined) {
                        set_queue(index, JSON.parse(queue.queue[index]))
                    } else {
                        reset_queue(index)
                    }
                }
            } else {
                for (let index = 0; index < 4; index++) {
                    reset_queue(index)
                }
            }
        }

        if (data.event === 'DISCONNECTED') {
            reset_current_track()
            reset_position()
            for (let index = 0; index < 4; index++) {
                reset_queue(index)
            }
        }

        if (data.event === 'TRACK_START') { set_current_track(JSON.parse(event_data.current)) }
        if (data.event === 'TRACK_END') { reset_current_track() }

        if (data.event === 'POSITION') {
            if (event_data.position !== 0) {
                set_position(event_data)
            } else {
                reset_position()
            }
        }

        if (data.event === 'QUEUE_UPDATE') {
            const queue = JSON.parse(event_data.queue)
            if (queue.queue !== null) {
                for (let index = 0; index < 4; index++) {
                    if (queue.queue[index] !== undefined) {
                        set_queue(index, JSON.parse(queue.queue[index]))
                    } else {
                        reset_queue(index)
                    }
                }
            } else {
                for (let index = 0; index < 4; index++) {
                    reset_queue(index)
                }
            }
        }

    }
}