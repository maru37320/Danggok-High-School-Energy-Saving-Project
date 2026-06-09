import time
import gc
import network
from machine import I2C, Pin, ADC
from neopixel import NeoPixel
from scd30 import SCD30
import wifi_config
time.sleep(5)

try:
    import usocket as socket
except ImportError:
    import socket
try:
    import ussl as ssl
except ImportError:
    import ssl


print(">>> ===== 부팅! 코드 시작 =====")

# ===== 하드웨어 =====
i2c = I2C(0, sda=Pin(8), scl=Pin(9), freq=50000)
print(">>> SCD30 검색 중...")
try:
    scd = SCD30(i2c, addr=0x61)
    scd.start_cont_measure()
    print(">>> SCD30 연결 성공!")
except Exception as e:
    print(">>> SCD30 에러:", e)
    while True:
        time.sleep(1)

gas_sensor = ADC(Pin(26))
print(">>> MQ-2 준비 완료")

# ===== LED (WS2813, GP16, 10개) =====
NUM_LEDS = 10
TIMING = (280, 515, 515, 745)
led = NeoPixel(Pin(16), NUM_LEDS, timing=TIMING)


def set_led(r, g, b):
    """모든 LED를 같은 색으로"""
    for i in range(NUM_LEDS):
        led[i] = (r, g, b)
    led.write()


def led_for_status(status):
    if status == "정상":
        set_led(0, 12, 0)
    elif status in ("과냉방", "이동수업낭비"):
        set_led(15, 0, 0)
    elif status == "빈교실냉방의심":
        set_led(10, 0, 15)
    elif status == "냉방안함":
        set_led(15, 6, 0)
    else:
        set_led(6, 6, 6)

set_led(0, 0, 40)
time.sleep(1)
set_led(0, 0, 0)


def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    time.sleep(3)
    if wlan.isconnected():
        return wlan
    for attempt in range(5):
        print(">>> WiFi 연결 시도", attempt + 1, "/5")
        try:
            available = [w[0].decode() for w in wlan.scan()]
        except Exception as e:
            print(">>> 스캔 에러:", e)
            time.sleep(2)
            continue
        for ssid, pw in wifi_config.WIFI_NETWORKS.items():
            if ssid in available:
                print(">>> 연결 시도:", ssid)
                wlan.connect(ssid, pw)
                for _ in range(15):
                    if wlan.isconnected():
                        print(">>> 연결 성공! IP:", wlan.ifconfig()[0])
                        return wlan
                    time.sleep(1)
                print(">>>", ssid, "연결 실패, 다음 시도")
                wlan.disconnect()
        print(">>> 이번 시도 실패, 3초 후 재시도")
        time.sleep(3)
    print(">>> WiFi 최종 실패")
    return None


def parse_url(url):
    url = url.split("://", 1)[1]
    if "/" in url:
        host, path = url.split("/", 1)
        return host, "/" + path
    return url, "/"


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


def send_to_sheet(co2, temp, hum, gas, status):
    try:
        params = "class={}&co2={}&temp={}&hum={}&gas={}&status={}".format(
            wifi_config.CLASS_ID, co2, temp, hum, gas, status)
        full_url = wifi_config.SHEET_URL + "?" + params
        print(">>> 1차 GET 전송...")
        response = https_get(full_url)
        status_line = response.split("\r\n", 1)[0]
        print(">>> 1차 응답:", status_line)
        if "302" in status_line or "301" in status_line or "307" in status_line:
            new_url = None
            for line in response.split("\r\n"):
                if line.lower().startswith("location:"):
                    new_url = line.split(":", 1)[1].strip()
                    break
            if new_url:
                print(">>> 리다이렉트! 2차 GET")
                response2 = https_get(new_url)
                print(">>> 2차 응답:", response2.split("\r\n", 1)[0])
    except Exception as e:
        print(">>> 전송 중 에러:", e)


def read_sensors():
    gas_value = gas_sensor.read_u16()
    for _ in range(10):
        try:
            if scd.get_status_ready():
                co2, temp, humi = scd.read_measurement()
                return co2, temp, humi, gas_value
        except Exception as e:
            print(">>> 센서 읽기 오류:", e)
        time.sleep(0.5)
    print(">>> SCD30 데이터 준비 안 됨")
    return None, None, None, gas_value


def get_status(temp, co2):
    if temp is None:
        return "측정실패"
    if temp >= 29:
        return "냉방안함"
    elif temp < 22:
        return "빈교실냉방의심" if co2 < 600 else "과냉방"
    else:
        return "정상"


print(">>> WiFi 연결 시도")
wlan = connect_wifi()
if not wlan:
    print(">>> WiFi 연결 실패! 종료")
    set_led(50, 0, 0)
    while True:
        time.sleep(1)

print(">>> 측정+전송 루프 시작")
loop_count = 0

while True:
    loop_count += 1
    try:
        print(">>> ===== 루프 #" + str(loop_count) + " =====")
        if not wlan.isconnected():
            print(">>> WiFi 끊김! 재연결")
            wlan = connect_wifi()

        co2, temp, hum, gas = read_sensors()
        if co2 is not None:
            co2 = round(co2, 1)
            temp = round(temp, 1)
            hum = round(hum, 1)
            print("CO2:", co2, "온도:", temp, "습도:", hum, "가스:", gas)
            status = get_status(temp, co2)
            print("상태:", status)
            
            led_for_status(status)

            set_led(0, 0, 40)
            send_to_sheet(co2, temp, hum, gas, status)

            led_for_status(status)
        else:
            print(">>> 센서 측정 실패")
            set_led(20, 20, 20)
    except Exception as e:
        print(">>> 루프 에러:", e)

    gc.collect()
    print(">>> 30초 대기...")
    time.sleep(30)
