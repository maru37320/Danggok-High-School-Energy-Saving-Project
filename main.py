import time
import gc
import json
import network
from machine import I2C, Pin, ADC, WDT, reset
import wifi_config
time.sleep(5)

def feed():
    """와치독이 켜져 있을 때만 feed."""
    global wdt
    if wdt is not None:
        wdt.feed()
        
try:
    import usocket as socket
except ImportError:
    import socket
try:
    import ussl as ssl
except ImportError:
    import ssl


print(">>> ===== 부팅! 코드 시작 =====")

# ===== 와치독 (일단 만들지 말고, 변수만 준비) =====
wdt = None   # ← 처음엔 None! 아직 시작 안 함


# ===== 버퍼 설정 =====
BUFFER_FILE = "buffer.jsonl"
BUFFER_MAX = 200

# ===== 측정 간격 =====
INTERVAL_SEC = 30


# ===== 하드웨어: SHT40 (I2C) =====
i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=100000)
SHT40_ADDR = 0x44
print(">>> I2C 스캔:", [hex(x) for x in i2c.scan()])

# ===== 하드웨어: 조도 센서 (아날로그, GP26) =====
light_sensor = ADC(Pin(26))


def read_sht40():
    """SHT40에서 온도(°C), 습도(%) 읽기."""
    # 고정밀 측정 명령 0xFD
    i2c.writeto(SHT40_ADDR, b'\xFD')
    time.sleep_ms(10)
    data = i2c.readfrom(SHT40_ADDR, 6)
    # 온도 계산
    t_ticks = data[0] * 256 + data[1]
    temp = -45 + 175 * t_ticks / 65535
    # 습도 계산
    rh_ticks = data[3] * 256 + data[4]
    hum = -6 + 125 * rh_ticks / 65535
    hum = max(0, min(100, hum))  # 0~100 범위 제한
    return temp, hum


def read_light():
    """조도 센서 읽기 (0~100% 정도로 변환)."""
    raw = light_sensor.read_u16()  # 0~65535
    light_pct = raw / 65535 * 100
    return light_pct


def measure():
    """센서 1회 측정. 실패 항목은 None."""
    temp, hum, light = None, None, None
    try:
        t, rh = read_sht40()
        temp = round(t, 2)
        hum = round(rh, 2)
    except Exception as e:
        print(">>> SHT40 오류:", e)
    try:
        light = round(read_light(), 1)
    except Exception as e:
        print(">>> 조도 센서 오류:", e)
    return temp, hum, light


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    time.sleep(5)   # 워밍업 더 길게

    if wlan.isconnected():
        return wlan

    for attempt in range(5):
        feed()
        print(">>> WiFi 연결 시도", attempt + 1, "/5")
        try:
            scan_result = wlan.scan()
            available = [w[0].decode() for w in scan_result]
            print(">>> 주변 WiFi 개수:", len(available))
            print(">>> 주변 WiFi 목록:", available)
        except Exception as e:
            print(">>> 스캔 에러:", e)
            time.sleep(2)
            continue

        # wifi_config에 있는 WiFi 찾기
        print(">>> 내가 찾는 WiFi:", list(wifi_config.WIFI_NETWORKS.keys()))
        for ssid, pw in wifi_config.WIFI_NETWORKS.items():
            if ssid in available:
                print(">>> 발견! 연결 시도:", ssid)
                wlan.connect(ssid, pw)
                for _ in range(15):
                    feed()
                    if wlan.isconnected():
                        print(">>> 연결 성공! IP:", wlan.ifconfig()[0])
                        return wlan
                    time.sleep(1)
                print(">>>", ssid, "연결 실패")
                wlan.disconnect()
            else:
                print(">>>", ssid, "는 주변에 없음")

        print(">>> 이번 시도 실패, 3초 후 재시도")
        for _ in range(3):
            feed()
            time.sleep(1)
    print(">>> WiFi 최종 실패")
    return None


# ===== URL 분해 =====
def parse_url(url):
    url = url.split("://", 1)[1]
    if "/" in url:
        host, path = url.split("/", 1)
        return host, "/" + path
    return url, "/"


# ===== HTTPS GET (리다이렉트 처리, 구글 시트용) =====
def https_get(url):
    host, path = parse_url(url)
    s = None
    try:
        addr = socket.getaddrinfo(host, 443)[0][-1]
        s = socket.socket()
        s.settimeout(15)
        s.connect(addr)
        s = ssl.wrap_socket(s, server_hostname=host)
        request = ("GET " + path + " HTTP/1.1\r\n"
                   "Host: " + host + "\r\n"
                   "Connection: close\r\n\r\n")
        s.write(request.encode())
        response = b""
        while True:
            chunk = s.read(512)
            if not chunk:
                break
            response += chunk
        return response.decode("utf-8", "ignore")
    finally:
        if s:
            try:
                s.close()
            except:
                pass


# ===== 시트로 전송 (한 건) =====
def send_once(temp, hum, light):
    try:
        params = "class={}&temp={}&hum={}&light={}".format(
            wifi_config.CLASS_ID, temp, hum, light)
        full_url = wifi_config.SHEET_URL + "?" + params
        print(">>> 전송 URL:", full_url)   # ← URL 확인

        response = https_get(full_url)
        status_line = response.split("\r\n", 1)[0]
        print(">>> 1차 응답:", status_line)

        if "302" in status_line or "301" in status_line or "307" in status_line:
            new_url = None
            for line in response.split("\r\n"):
                if line.lower().startswith("location:"):
                    new_url = line.split(":", 1)[1].strip()
                    break
            print(">>> 리다이렉트 주소:", new_url)   # ← 새 주소 확인!

            if new_url:
                response2 = https_get(new_url)
                status_line2 = response2.split("\r\n", 1)[0]
                print(">>> 2차 응답:", status_line2)
                # ★ 응답 본문 확인!
                body2 = response2.split("\r\n\r\n", 1)[-1]
                print(">>> 2차 본문:", body2[-200:])   # ← 핵심!
                return "200" in status_line2
            return False
        body = response.split("\r\n\r\n", 1)[-1]
        print(">>> 본문:", body[-200:])
        return "200" in status_line
    except Exception as e:
        print(">>> 전송 실패:", e)
        return False


# ===== 버퍼링 (전송 실패 시 저장) =====
def buffer_append(temp, hum, light):
    try:
        try:
            with open(BUFFER_FILE, "r") as f:
                lines = f.readlines()
        except OSError:
            lines = []
        payload = {"temp": temp, "hum": hum, "light": light}
        lines.append(json.dumps(payload) + "\n")
        if len(lines) > BUFFER_MAX:
            lines = lines[-BUFFER_MAX:]
        with open(BUFFER_FILE, "w") as f:
            f.writelines(lines)
        print(">>> 버퍼에 저장 (총", len(lines), "건)")
    except OSError as e:
        print(">>> 버퍼 쓰기 실패:", e)


def buffer_flush():
    """버퍼에 쌓인 것 재전송. 성공한 건 제거."""
    try:
        with open(BUFFER_FILE, "r") as f:
            lines = f.readlines()
    except OSError:
        return
    if not lines:
        return
    print(">>> 버퍼", len(lines), "건 재전송 시도")
    survivors = []
    for line in lines:
        feed()
        try:
            p = json.loads(line)
            if not send_once(p["temp"], p["hum"], p["light"]):
                survivors.append(line)
        except ValueError:
            pass  # 깨진 줄 버림
    try:
        with open(BUFFER_FILE, "w") as f:
            f.writelines(survivors)
    except OSError:
        pass


# ===== 메인 =====
print(">>> WiFi 연결 시도")
wlan = connect_wifi()
if not wlan:
    print(">>> WiFi 연결 실패! reset")
    time.sleep(2)
    reset()

# ★ WiFi 연결 성공 후에 와치독 시작! (8초 → 넉넉하게 늘림)
from machine import WDT
# ★ WiFi 연결 성공 후에 와치독 시작!
wdt = WDT(timeout=8388)  # 피코 최대값 약 8.3초
print(">>> 와치독 시작!")

print(">>> 측정+전송 루프 시작")
loop_count = 0

while True:
    loop_count += 1
    try:
        feed()
        print(">>> ===== 루프 #" + str(loop_count) + " =====")

        if not wlan.isconnected():
            print(">>> WiFi 끊김! 재연결")
            wlan = connect_wifi()
            if not wlan:
                reset()

        temp, hum, light = measure()
        print("온도:", temp, "습도:", hum, "조도:", light)

        if temp is not None and send_once(temp, hum, light):
            buffer_flush()  # 그동안 쌓인 것도 전송
        else:
            buffer_append(temp, hum, light)

    except Exception as e:
        print(">>> 루프 에러:", e)

    gc.collect()

    # INTERVAL 대기 (와치독 feed 하면서!)
    print(">>>", INTERVAL_SEC, "초 대기...")
    elapsed = 0
    while elapsed < INTERVAL_SEC:
        feed()
        time.sleep(1)
        elapsed += 1
