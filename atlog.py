import serial
import time
import re
import os
from datetime import datetime

# === 측정 설정 ===
NUM_MEASUREMENTS = 20       # 측정 횟수
INTERVAL = 1                # 측정 간격 (초)
PORT = "/dev/ttyUSB2"
BAUDRATE = 115200
DELAY = 0.2                 # 명령 후 대기 시간
v = "3mps"
h = "50m"

# === 로그 파일 설정 ===
log_dir = "atlogs"
os.makedirs(log_dir, exist_ok=True)
log_path = os.path.join(log_dir, f"lte_log_{v}_{h}.txt")

# AT 명령 송신 및 응답 수신
def send_at_command(ser, command):
    ser.reset_input_buffer()
    ser.write((command + "\r").encode())
    time.sleep(DELAY)

    lines = []
    end_time = time.time() + 1.0
    while time.time() < end_time:
        line = ser.readline().decode(errors='ignore').strip()
        if line:
            lines.append(line)
        if "OK" in line or "ERROR" in line:
            break
    return lines

# RSSI 파싱
def parse_csq(lines):
    for line in lines:
        match = re.search(r'\+CSQ: (\d+),(\d+)', line)
        if match:
            rssi = int(match.group(1))
            dbm = -113 + 2 * rssi if rssi < 32 else "Unknown"
            return rssi, dbm
    return None, None

# RSRP/RSRQ 파싱
def parse_qeng(lines):
    for line in lines:
        if '+QENG:' in line and 'LTE' in line:
            parts = line.split(',')
            try:
                rsrp = int(parts[-9])
                rsrq = int(parts[-8])
                return rsrp, rsrq
            except (ValueError, IndexError):
                return None, None
    return None, None
# 메인 실행
def main():
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=1) as ser, open(log_path, "a") as f:
            print(f"[INFO] Logging to → {log_path}")
            for i in range(NUM_MEASUREMENTS):
                timestamp_str = time.strftime("%Y-%m-%d %H:%M:%S")
                log_line = f"[#{i+1}] {timestamp_str}"

                # RSSI
                csq_lines = send_at_command(ser, "AT+CSQ")
                rssi, dbm = parse_csq(csq_lines)
                if rssi is not None:
                    log_line += f" | RSSI: {rssi} ({dbm} dBm)"
                else:
                    log_line += " | RSSI: N/A"

                # RSRP/RSRQ
                qeng_lines = send_at_command(ser, 'AT+QENG="servingcell"')
                rsrp, rsrq = parse_qeng(qeng_lines)
                if rsrp is not None:
                    log_line += f" | RSRP: {rsrp} dBm, RSRQ: {rsrq} dB"
                else:
                    log_line += " | RSRP/RSRQ: N/A"

                print(log_line)

                # 💾 안전하게 매번 저장
                with open(log_path, "a") as f:
                    f.write(log_line + "\n")
                    f.flush()  # flush는 OS 버퍼에 안 쌓이고 바로 기록되게 함

                time.sleep(INTERVAL)

            print("[INFO] 측정 완료")
    except serial.SerialException as e:
        print(f"[ERROR] 포트 연결 실패: {e}")
    except KeyboardInterrupt:
        print("[INFO] 사용자 중단")

if __name__ == "__main__":
    main()
