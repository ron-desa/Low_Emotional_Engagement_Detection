import serial
import sys
import time
from datetime import datetime
import pytz

if len(sys.argv) != 2:
    print("  Usage: python signals.py <COMXX>\n  Example: python signals.py COM3\n")
    exit(-1)

currtime = time.time()
buff = ""
file_prefix = str(currtime)

file1 = open("signals_data.csv", "w")
file2 = open("signals_data.txt", "w")

ser = serial.Serial(sys.argv[1], 9600)

start_time = time.time()
save_interval = 5  # seconds

while True:
    ist_timezone = pytz.timezone('Asia/Kolkata')
    date = datetime.now(ist_timezone)

    latency_in_seconds = 0.1
    time.sleep(latency_in_seconds)

    milliseconds = int(time.time() * 1000)
    # cc = ser.readline().decode().strip()
    cc = ser.readline().decode('utf-8', errors='ignore').strip()

    print(milliseconds)

    buff = buff + cc + "," + str(milliseconds) + "," + str(date) + "\n"

    elapsed_time = time.time() - start_time
    print(buff)
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
