import datetime

start_time_system = 1747033587.924104  # System Time at recording start
start_time_synced = 1116530.305898629      # Pupil Time at recording start

# Calculate the fixed offset between System and Pupil Time
offset = start_time_system - start_time_synced

# Choose a Pupil timestamp that you want to convert to System Time
# (this can be any or all timestamps of interest)
pupil_timestamp = 1116530.25  # This is a random example of a Pupil timestamp

# Add the fixed offset to the timestamp(s) we wish to convert
pupiltime_in_systemtime = pupil_timestamp + offset

# Using the datetime python module, we can convert timestamps 
# stored as seconds represented by floating point values to a 
# more readable datetime format.
pupil_datetime = datetime.datetime.fromtimestamp(pupiltime_in_systemtime).strftime("%Y-%m-%d %H:%M:%S.%f")

print(pupil_datetime)
# example output: '2018-08-02 15:16:08.199800'

# Hint: you can also copy and paste timestamps into various websites that convert them
# to the readable date time format!