import re

MS_TO_SECONDS = 1000
MS_TO_MINUTE = 1000 * 60
MS_TO_HOUR = 1000 * 60 * 60
MS_TO_DAY = 1000 * 60 * 60 * 24
MS_TO_WEEK = 1000 * 60 * 60 * 24 * 7
MS_TO_YEAR = 1000 * 60 * 60 * 24 * 7 * 52.143


def ms(time: str | int | float, decimal:bool=True) -> str | int | float:
    """Input a string to get it parsed in ms

    Input int or float to get it back in a readable string format

        Parameters:
                time (str | int | float) value to parse

                decimal (bool) if set to false will return string dates rounded to the nearest whole number
    """
    if isinstance(time, str):
        if not len(time) > 0:
            raise Exception("'time' must not be a non empty string")

        num_value = re.search(
            r'^(-?(?:\d+)?\.?\d+) *(ms|msec|msecs|milli|millis|msecond|mseconds|min|mins|m|minute|minutes|h|hr|hrs|hour|hours|d|day|days|w|wk|wks|week|weeks|y|yr|yrs|year|years)',
            time)

        if num_value is None:
            raise Exception("No Valid Time Unit Or Number Found")

        if num_value.group(1).find(".") == -1:
            time = int(num_value.group(1))
        else:
            time = float(num_value.group(1))
        time_unit = num_value.group(2)


        match time_unit:
            case "ms" | "msec" | "msecs" | "milli" | "millis" | "msecond" | "mseconds":
                return time
            case "min" | "mins" | "m|""minute" | "minutes":
                return time * MS_TO_MINUTE
            case "h" | "hr" | "hrs" | "hour" | "hours":
                return time * MS_TO_HOUR
            case "d"|"day"|"days":
                return time * MS_TO_DAY
            case "w" | "wk" | "wks" | "week" | "weeks":
                return time * MS_TO_WEEK
            case "y" | "yr" | "yrs" | "year" | "years":
                return time * MS_TO_YEAR
            case _:
                raise Exception("No Valid Time Unit")
    elif isinstance(time, int) or isinstance(time, float):
        abs_time = abs(time)
        round_dp = 2 if decimal else None

        if abs_time > MS_TO_YEAR:
            return f"{round(time/MS_TO_YEAR, round_dp)} Year{'' if (1.0 >= round(time/MS_TO_YEAR, round_dp) >= -1.0) else 's'}"
        elif abs_time > MS_TO_WEEK:
            return f"{round(time/MS_TO_WEEK, round_dp)} Week{'' if (1.0 >= round(time/MS_TO_WEEK, round_dp) >= -1.0) else 's'}"
        elif abs_time > MS_TO_DAY:
            return f"{round(time / MS_TO_DAY, round_dp)} Day{'' if (1.0 >= round(time / MS_TO_DAY, round_dp) >= -1.0) else 's'}"
        elif abs_time > MS_TO_HOUR:
            return f"{round(time / MS_TO_HOUR, round_dp)} Hour{'' if (1.0 >= round(time / MS_TO_HOUR, round_dp) >= -1.0) else 's'}"
        elif abs_time > MS_TO_MINUTE:
            return f"{round(time / MS_TO_MINUTE, round_dp)} Minute{'' if (1.0 >= round(time / MS_TO_MINUTE, round_dp) >= -1.0) else 's'}"
        elif abs_time > MS_TO_SECONDS:
            return f"{round(time / MS_TO_SECONDS, round_dp)} Second{'' if (1.0 >= round(time / MS_TO_SECONDS, round_dp) >= -1.0) else 's'}"
        else:
            return f"{round(time, round_dp)} Millisecond{'' if (1.0 >= round(time, round_dp) >= -1.0) else 's'}"
    else:
        raise Exception("No Valid Time Unit Or Number Found")

print(ms("1d"))