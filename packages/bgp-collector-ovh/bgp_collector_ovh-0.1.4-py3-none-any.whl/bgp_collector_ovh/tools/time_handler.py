from datetime import datetime


def datetime_to_unix_timestamp(time):
    timestamp = datetime.strptime(time, "%Y-%m-%d %H:%M:%S.%f").timestamp()
    return timestamp


def unix_timestamp_to_datetime(timestamp):
    formatted_time = datetime.utcfromtimestamp(float(timestamp)).strftime(
        "%Y-%m-%d %H:%M:%S.%f"
    )
    return formatted_time
