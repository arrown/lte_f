import serial
import time
import re

# === 소티 조건 입력 (테스트별로 다르게 설정) ===
v = "3mps"     # 속도
h = "50m"      # 고도
INTERVAL = 1  # 측정 주기 (초)

# === 설정 ===
PORT = "/dev/ttyUSB2"      
BAUDRATE = 115200
LOG_FILE = f"lte_log_{v}_{h}.txt"

def send_at_command(ser, command, timeout=2):
    ser.write((command + "\r").encode())
    time.sleep(timeout)
    return ser.read_all().decode(errors='ignore')

def parse_csq(response):
    match = re.search(r'\+CSQ: (\d+),(\d+)', response)
    if match:
        rssi = int(match.group(1))
        ber = match.group(2)
        dbm = -113 + 2 * rssi if rssi < 32 else "Unknown"
        return rssi, ber, dbm
    return None

def parse_servingcell(response):
    match = re.search(r'servingcell","(\w+)",\s*"LTE","\w+",(\d+),\s*(\d+),.*?,.*?,.*?,.*?,.*?,.*?,.*?,(-?\d+),(-?\d+)', response)
    if match:
        conn_state = match.group(1)
        earfcn = match.group(2)
        pci = match.group(3)
        rsrp = match.group(4)
        rsrq = match.group(5)
        return conn_state, earfcn, pci, rsrp, rsrq
    return None

def log_signal_data(log_path, message):
    with open(log_path, "a") as f:
        f.write(message + "\n")

def main():
    try:
        ser = serial.Serial(PORT, BAUDRATE, timeout=1)
        print(f"[INFO] 포트 {PORT} 연결 성공")
        print(f"[INFO] 로그 파일: {LOG_FILE}")

        while True:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
            print(f"\n[INFO] {timestamp} - 신호 정보 조회 중...")

            log_entry = f"[{timestamp}]"

            # RSSI
            csq_resp = send_at_command(ser, "AT+CSQ")
            csq_result = parse_csq(csq_resp)
            if csq_result:
                rssi, ber, dbm = csq_result
                log_entry += f" RSSI: {rssi} ({dbm} dBm), BER: {ber}"
            else:
                rssi, ber, dbm = "N/A", "N/A", "N/A"
                log_entry += " RSSI: N/A"

            # RSRP, RSRQ
            qeng_resp = send_at_command(ser, 'AT+QENG="servingcell"')
            qeng_result = parse_servingcell(qeng_resp)
            if qeng_result:
                conn, earfcn, pci, rsrp, rsrq = qeng_result
                log_entry += f", RSRP: {rsrp} dBm, RSRQ: {rsrq} dB"
            else:
                conn, earfcn, pci, rsrp, rsrq = "N/A", "N/A", "N/A", "N/A", "N/A"
                log_entry += ", RSRP/RSRQ: N/A"

            # 한 줄로 출력
            print(f"  ▶ RSSI: {rssi} ({dbm} dBm), RSRP: {rsrp} dBm, RSRQ: {rsrq} dB")

            # 로그 저장
            log_signal_data(LOG_FILE, log_entry)
            time.sleep(INTERVAL)

    except serial.SerialException as e:
        print(f"[ERROR] 포트 연결 실패: {e}")
    except KeyboardInterrupt:
        print("\n[INFO] 종료됨.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()

if __name__ == "__main__":
    main()
