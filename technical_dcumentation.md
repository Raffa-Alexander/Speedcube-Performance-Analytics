# Definitions
### Sub-X
A solution that take less than X time. Example: 8.00 and 8.93 are classified as sub-9, but 9.00 is sub-10.
### Session
A session is defined as a maximal sequence of consecutive solves in which the time difference between two adjacent solves does not exceed `SESSION_GAP_THRESHOLD_SEC`.

# Code

### Global Constants
- `COLOR_BARS` = "#3691E0"
- `COLOR_SCATTERS` = "#3691E0"
- `COLOR_LINES` = "#E17070"
### Functions
- `linear_regression(session_stats, x, y)`: Generates a line showing tendency with a slope according to density of points
- `parse_time_mmss(s)`: Converts strings mm:ss.xx to pd.Timedelta
- `load_data()`: Loads data from "data.csv" to variable "df".
