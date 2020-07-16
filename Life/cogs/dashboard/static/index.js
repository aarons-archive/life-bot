function parseTime(milliseconds) {
    let seconds = milliseconds / 1000;
    const hours = parseInt(seconds / 3600);
    seconds = seconds % 3600;
    const minutes = parseInt(seconds / 60);
    seconds = Math.round(seconds % 60)

    if (hours > 0)
        return hours+'h '+minutes+'m '+seconds+'s '
    else if (minutes > 0)
        return minutes+'m '+seconds+'s '
    else if (seconds > 0)
        return seconds+'s '
}

