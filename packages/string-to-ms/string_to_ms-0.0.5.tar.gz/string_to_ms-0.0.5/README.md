# String to Milliseconds Converter

This Python module provides functionality to convert between time strings and milliseconds, and vice versa.

## Main Function

### `ms(time: str | int | float, decimal: bool = True) -> str | int | float`

A versatile function that handles bidirectional conversion between time strings and milliseconds. Inspired by the `ms` [npm package](https://www.npmjs.com/package/ms), it allows for both parsing time strings into milliseconds and converting milliseconds into human-readable time strings.

#### Parameters

- `time` (str | int | float): The value to parse or convert
- `decimal` (bool, optional): If False, returns string dates rounded to whole numbers. Default is True.

#### Functionality

**String Input → Milliseconds Output:**

- Parses time strings with format: `"<number> <unit>"`
- Supported units:
- Milliseconds: `ms`, `msec`, `msecs`, `milli`, `millis`, `msecond`, `mseconds`
- Minutes: `min`, `mins`, `m`, `minute`, `minutes`
- Hours: `h`, `hr`, `hrs`, `hour`, `hours`
- Days: `d`, `day`, `days`
- Weeks: `w`, `wk`, `wks`, `week`, `weeks`
- Years: `y`, `yr`, `yrs`, `year`, `years`
- Years will return as floats as they use the average weeks in a year (52.143 weeks).

**Numeric Input → Human-readable String Output:**

- Converts milliseconds to the most appropriate time unit
- Automatically handles pluralization
- Returns formatted strings like "2.5 Hours" or "1 Day"

#### Examples

```python
ms("2.5 hours")  # Returns 9000000
ms("3mins")  # Returns 180000
ms(8280000)      # Returns "2.3 Hours"

ms(8280000, decimal=False)  # 2 Hours
```
[https://github.com/chickenman34234/StringToMilliseconds](https://github.com/chickenman34234/StringToMilliseconds)