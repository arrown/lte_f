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

def send_qeng_command(ser):
    ser.reset_input_buffer()
    ser.write(b'AT+QENG="servingcell"\r')
    time.sleep(DELAY)

    lines = []
    end_time = time.time() + 1.0  # 1초 내 응답 수신 제한
    while time.time() < end_time:
        line = ser.readline().decode(errors='ignore').strip()
        if line:
            lines.append(line)
        if "OK" in line or "ERROR" in line:
            break
    return lines

def extract_rsrp_rsrq(qeng_lines):
    for line in qeng_lines:
        if "servingcell" in line and "LTE" in line:
            match = re.search(r'servingcell",".*?","LTE",".*?",\d+,\d+,\d+.*?,.*?,.*?,.*?,.*?,.*?,.*?,(-?\d+),(-?\d+)', line)
            if match:
                rsrp = int(match.group(1))
                rsrq = int(match.group(2))
                return rsrp, rsrq
    return None, None

def main():
    try:
        with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
            print("[INFO] LTE 신호 측정 시작...")
            for i in range(10):  # 10회 측정
                lines = send_qeng_command(ser)
                rsrp, rsrq = extract_rsrp_rsrq(lines)
                if rsrp is not None:
                    print(f"[#{i+1}] RSRP: {rsrp} dBm, RSRQ: {rsrq} dB")
                else:
                    print(f"[#{i+1}] 측정 실패")
                time.sleep(1)  # 주기적으로 측정
    except serial.SerialException as e:
        print(f"[ERROR] 포트 연결 실패: {e}")
    except KeyboardInterrupt:
        print("[INFO] 사용자 중단")

if __name__ == "__main__":
    main()

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
