from datetime import timedelta, datetime, timezone


def isNowInTimePeriod(startTime, endTime, nowTime):
    if startTime < endTime:
        return nowTime >= startTime and nowTime <= endTime
    else:
        # Over midnight:
        return nowTime >= startTime or nowTime <= endTime


def dayText(event, today=datetime.now(timezone.utc)):

    weekday = ["Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag"]
    text = ""
    try:
        dt = datetime.fromisoformat(
            event["start"].get("dateTime", event["start"].get("date"))
        ).replace(tzinfo=timezone.utc)

        tomorrow = today + timedelta(1)
        delta = dt - today

        if dt.date() == today.date():
            text = text + "I dag: "
        elif dt.date() == tomorrow.date():
            text = text + "I morgen: "
        elif delta.days > 6:
            text = text + weekday[dt.weekday()] + " " + dt.strftime("%d/%m") + ": "
        else:
            text = text + weekday[dt.weekday()] + ": "

        text = text + event["summary"]

        if dt.hour > 0:
            text = text + dt.strftime(" kl. %H:%M")

    except ValueError:
        print(event)

    return text
