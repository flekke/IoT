import serial
import time
import os

PORT = 'COM9'         # 포트 번호를 환경에 맞게 수정
BAUD_RATE = 9600

DATA_FILE = "data/data.txt"
os.makedirs("data", exist_ok=True)

try:
    ser = serial.Serial(PORT, BAUD_RATE)
    time.sleep(2)
    print(f"{PORT} connected. loading...")
except serial.SerialException:
    print(f"{PORT} cannot be connected.")
    exit()

while True:
    try:
        line = ser.readline().decode('utf-8').strip()

        if ',' not in line:
            continue

        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        log_line = f"{timestamp},{line}\n"

        with open(DATA_FILE, "a") as f:
            f.write(log_line)

        print("saved:", log_line.strip())

    except Exception as e:
        print("error:", e)
        time.sleep(2)

