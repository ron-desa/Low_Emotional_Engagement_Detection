import serial
import sys
import time
from datetime import datetime
import pytz
import os

if len(sys.argv) != 2:
    print("  Usage: python signals.py <COMXX>\n  Example: python signals.py COM3\n")
    exit(-1)

currtime = time.time()
buff = ""
file_prefix = str(currtime)

# file1 = open("signals_data.csv", "w")
# file2 = open("signals_data.txt", "w")

filename1 = "signals_data.csv"
filename2 = "signals_data.txt"  # Now it's writing to a .txt file

# Open both files in append mode
file1 = open(filename1, "w")
file2 = open(filename2, "w")

# Add headers if files are new or empty
if os.stat(filename1).st_size == 0:
    file1.write("ArduinoTime(ms),GSR,Pulse,SystemTime(ms),Datetime(Asia/Kolkata)\n")

if os.stat(filename2).st_size == 0:
    file2.write("ArduinoTime(ms),GSR,Pulse,SystemTime(ms),Datetime(Asia/Kolkata)\n")

ser = serial.Serial(sys.argv[1], 9600)

start_time = time.time()
save_interval = 5  # seconds

while True:
    ist_timezone = pytz.timezone('Asia/Kolkata')
    date = datetime.now(ist_timezone)

    latency_in_seconds = 0.1
    time.sleep(latency_in_seconds)

    milliseconds = int(time.time() * 1000)
    cc = ser.readline().decode().strip()
    print(milliseconds)

    buff = buff + cc + "," + str(milliseconds) + "," + str(date) + "\n"

    elapsed_time = time.time() - start_time

    if elapsed_time >= save_interval:
        file1.write(buff)
        file2.write(buff)
        buff = ""
        start_time = time.time()
        file1.close()
        file2.close()
        file1 = open("signals_data.csv", "a")
        file2 = open("signals_data.txt", "a")
        # file1 = open(file_prefix + "_data.csv", "a")
        # file2 = open(file_prefix + "_data.txt", "a")
