
from tools.datetime_tool import get_current_datetime


result = get_current_datetime()

print("Current Date:", result["date"])
print("Current Time:", result["time"])
print("Day of the Week:", result["day"])
