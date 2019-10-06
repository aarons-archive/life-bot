def get_time(second):

    minute, second = divmod(second, 60)
    hour, minute = divmod(minute, 60)
    day, hour = divmod(hour, 24)
    days = round(day)
    hours = round(hour)
    minutes = round(minute)
    seconds = round(second)
    if minutes == 0:
        return f"{seconds}s"
    if hours == 0:
        return "%02d:%02d" % (minutes, seconds)
    if days == 0:
        return "%02d:%02d:%02d" % (hours, minutes, seconds)
    return "%02d:%02d:%02d:%02d" % (days, hours, minutes, seconds)


def get_time_friendly(second):

    minute, second = divmod(second, 60)
    hour, minute = divmod(minute, 60)
    day, hour = divmod(hour, 24)
    days = round(day)
    hours = round(hour)
    minutes = round(minute)
    seconds = round(second)
    if minutes == 0:
        return f"%02ds" % seconds
    if hours == 0:
        return "%02dm %02ds" % (minutes, seconds)
    if days == 0:
        return "%02dh %02dm %02ds" % (hours, minutes, seconds)
    return "%02dd %02dh %02dm %02ds" % (days, hours, minutes, seconds)
