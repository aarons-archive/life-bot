
function skip(guild_id) {
    const url = `http://192.168.0.10:8080/dashboard/${guild_id}/skip`
    axios.post(url)
        .then( function (response) {
            console.log(response)
        })
        .catch( function (error) {
            console.log(error)
        })
}
