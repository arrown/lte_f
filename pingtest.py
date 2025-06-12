import subprocess
import time
import re
import threading

# 소티 구분 (속도, 고도 등)
v = "3mps"
h = "50m"

# 로그 파일 이름 설정
log_file = f"ping_{v}_{h}_log.txt"
target_ip = "8.8.8.8"
ping_cmd = ["ping", "-c", "1", target_ip]
rtt_pattern = re.compile(r"time[=<]([\d.]+)\s*ms")

# 루프 제어용 플래그
running = True

def ping_loop():
    global running
    print(f"[INFO] Start logging RTT to {target_ip} using ping - File: {log_file}")
    while running:
        try:
            result = subprocess.run(ping_cmd, capture_output=True, text=True)
            output = result.stdout
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S")

            match = rtt_pattern.search(output)
            if match:
                rtt = float(match.group(1))
                one_way_delay = round(rtt / 2, 2)
                log_entry = f"{timestamp} - Latency: {one_way_delay} ms (RTT: {rtt} ms)"
            else:
                log_entry = f"{timestamp} - Latency: TIMEOUT or no response"

            with open(log_file, "a") as f:
                f.write(log_entry + "\n")

            print(log_entry)
        except Exception as e:
            print(f"[ERROR] {e}")
        time.sleep(1)

# 별도 스레드로 핑 측정 실행
thread = threading.Thread(target=ping_loop)
thread.start()

# 사용자 입력 대기
while True:
    user_input = input("종료하려면 'q' 입력: ").strip().lower()
    if user_input == "q":
        running = False
        thread.join()
        print("[INFO] Ping logging stopped by user.")
        break

