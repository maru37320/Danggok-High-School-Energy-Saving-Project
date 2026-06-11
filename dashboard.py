# 수정 완료 했습니다!! 사용가능! 6월 12일 업데이트!

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, time as dtime, timedelta
import concurrent.futures

# 스프레드시트 ID (export URL의 공통 부분)
SHEET_ID = "1upDHGAi-83NMU4Mo_BuE3E6MeeBoonaemNNWhLZ0i8E"

# 16개 반의 gid
CLASS_GIDS = {
    "1-1": 0,
    "1-2": 1017758904,
    "1-3": 973826408,
    "1-4": 183323741,
    "1-5": 994373221,
    "1-6": 1411836865,
    "1-7": 1000209340,
    "1-8": 1363114437,
    "2-1": 687597777,
    "2-2": 1292185876,
    "2-3": 87037480,
    "2-4": 1451071089,
    "2-5": 1396217133,
    "2-6": 183824350,
    "2-7": 402481128,
    "2-8": 296245463,
}

def csv_url(gid):
    return f"https://docs.google.com/spreadsheets/d/{SHEET_ID}/export?format=csv&gid={gid}"

st.set_page_config(page_title="교실 에너지 모니터링", page_icon="🌍", layout="wide")

try:
    from streamlit_autorefresh import st_autorefresh
    st_autorefresh(interval=15 * 1000, key="refresh")   # 15초
except ImportError:
    pass


# ========================================
# 일정 정의
# ========================================
SCHEDULE_6 = [
    ("조회", dtime(8,10), dtime(8,20), "homeroom"),
    ("1교시", dtime(8,20), dtime(9,10), "class"),
    ("쉬는시간", dtime(9,10), dtime(9,20), "break"),
    ("2교시", dtime(9,20), dtime(10,10), "class"),
    ("쉬는시간", dtime(10,10), dtime(10,20), "break"),
    ("3교시", dtime(10,20), dtime(11,10), "class"),
    ("쉬는시간", dtime(11,10), dtime(11,20), "break"),
    ("4교시", dtime(11,20), dtime(12,10), "class"),
    ("점심시간", dtime(12,10), dtime(13,10), "lunch"),
    ("5교시", dtime(13,10), dtime(14,0), "class"),
    ("쉬는시간", dtime(14,0), dtime(14,10), "break"),
    ("6교시", dtime(14,10), dtime(15,0), "class"),
    ("종례", dtime(15,0), dtime(15,10), "homeroom"),
]
SCHEDULE_7 = [
    ("조회", dtime(8,10), dtime(8,20), "homeroom"),
    ("1교시", dtime(8,20), dtime(9,10), "class"),
    ("쉬는시간", dtime(9,10), dtime(9,20), "break"),
    ("2교시", dtime(9,20), dtime(10,10), "class"),
    ("쉬는시간", dtime(10,10), dtime(10,20), "break"),
    ("3교시", dtime(10,20), dtime(11,10), "class"),
    ("쉬는시간", dtime(11,10), dtime(11,20), "break"),
    ("4교시", dtime(11,20), dtime(12,10), "class"),
    ("점심시간", dtime(12,10), dtime(13,10), "lunch"),
    ("5교시", dtime(13,10), dtime(14,0), "class"),
    ("쉬는시간", dtime(14,0), dtime(14,10), "break"),
    ("6교시", dtime(14,10), dtime(15,0), "class"),
    ("쉬는시간", dtime(15,0), dtime(15,10), "break"),
    ("7교시", dtime(15,10), dtime(16,0), "class"),
    ("종례", dtime(16,0), dtime(16,10), "homeroom"),
]
DAY_SCHEDULE = {0: SCHEDULE_6, 1: SCHEDULE_7, 2: SCHEDULE_6, 3: SCHEDULE_7, 4: SCHEDULE_6}
WEEKDAY_KR = ["월","화","수","목","금","토","일"]


TIMETABLE = {
    # ===================== 1학년 =====================
    "1-1": {
        "월": {"1교시":"과탐실","2교시":"수학","3교시":"미술","4교시":"미술","5교시":"체육B","6교시":"통과C"},
        "화": {"1교시":"국어A","2교시":"수학","3교시":"한국사","4교시":"영어B","5교시":"통사C","6교시":"영어A","7교시":"통과A"},
        "수": {"1교시":"한국사","2교시":"체육A","3교시":"영어A","4교시":"음악","5교시":"수학","6교시":"통사A"},
        "목": {"1교시":"통사D","2교시":"통과B","3교시":"국어B","4교시":"진로","5교시":"한국사","6교시":"수학","7교시":"통과D"},
        "금": {"1교시":"국어C","2교시":"통사B","3교시":"음악","4교시":"영어C","5교시":"자율","6교시":"자율"},
    },
    "1-2": {
        "월": {"1교시":"미술","2교시":"미술","3교시":"한국사","4교시":"영어A","5교시":"통사A","6교시":"국어C"},
        "화": {"1교시":"통사D","2교시":"음악","3교시":"통과B","4교시":"수학","5교시":"통과A","6교시":"한국사","7교시":"과탐실"},
        "수": {"1교시":"통사C","2교시":"수학","3교시":"체육A","4교시":"국어A","5교시":"음악","6교시":"영어C"},
        "목": {"1교시":"수학","2교시":"통과D","3교시":"진로","4교시":"국어B","5교시":"통사B","6교시":"영어A","7교시":"한국사"},
        "금": {"1교시":"영어B","2교시":"통과C","3교시":"체육B","4교시":"수학","5교시":"자율","6교시":"자율"},
    },
    "1-3": {
        "월": {"1교시":"통사C","2교시":"체육A","3교시":"국어B","4교시":"영어C","5교시":"영어C","6교시":"통과C"},
        "화": {"1교시":"영어A","2교시":"한국사","3교시":"음악","4교시":"진로","5교시":"국어C","6교시":"통사B","7교시":"수학"},
        "수": {"1교시":"수학","2교시":"수학","3교시":"통사D","4교시":"한국사","5교시":"과탐실","6교시":"음악"},
        "목": {"1교시":"통과C","2교시":"미술","3교시":"미술","4교시":"체육B","5교시":"수학","6교시":"국어A","7교시":"영어A"},
        "금": {"1교시":"통사A","2교시":"통과B","3교시":"수학","4교시":"한국사","5교시":"자율","6교시":"자율"},
    },
    "1-4": {
        "월": {"1교시":"영어C","2교시":"수학","3교시":"통과C","4교시":"체육B","5교시":"국어A","6교시":"국어B"},
        "화": {"1교시":"통과D","2교시":"통과B","3교시":"통사D","4교시":"통사C","5교시":"음악","6교시":"체육A","7교시":"영어B"},
        "수": {"1교시":"수학","2교시":"국어A","3교시":"진로","4교시":"영어A","5교시":"한국사","6교시":"과탐실"},
        "목": {"1교시":"통과A","2교시":"한국사","3교시":"통사B","4교시":"영어A","5교시":"미술","6교시":"미술","7교시":"수학"},
        "금": {"1교시":"한국사","2교시":"통사A","3교시":"수학","4교시":"음악","5교시":"자율","6교시":"자율"},
    },
    "1-5": {
        "월": {"1교시":"한국사","2교시":"통사B","3교시":"영어A","4교시":"국어B","5교시":"수학","6교시":"정보B"},
        "화": {"1교시":"과탐실","2교시":"통과D","3교시":"통과C","4교시":"정보A","5교시":"한국사","6교시":"영어B","7교시":"통사A"},
        "수": {"1교시":"체육B","2교시":"통과A","3교시":"정보B","4교시":"진로","5교시":"영어A","6교시":"수학"},
        "목": {"1교시":"통사C","2교시":"수학","3교시":"한국사","4교시":"국어C","5교시":"체육A","6교시":"통과B","7교시":"영어C"},
        "금": {"1교시":"수학","2교시":"국어A","3교시":"통사D","4교시":"정보A","5교시":"자율","6교시":"자율"},
    },
    "1-6": {
        "월": {"1교시":"영어B","2교시":"국어C","3교시":"진로","4교시":"통과B","5교시":"수학","6교시":"한국사"},
        "화": {"1교시":"통사B","2교시":"통과C","3교시":"체육A","4교시":"통사D","5교시":"수학","6교시":"통사C","7교시":"정보B"},
        "수": {"1교시":"영어A","2교시":"한국사","3교시":"국어B","4교시":"영어C","5교시":"정보B","6교시":"수학"},
        "목": {"1교시":"정보A","2교시":"수학","3교시":"통과D","4교시":"국어A","5교시":"영어A","6교시":"체육B","7교시":"통사A"},
        "금": {"1교시":"과탐실","2교시":"정보A","3교시":"통과A","4교시":"한국사","5교시":"자율","6교시":"자율"},
    },
    "1-7": {
        "월": {"1교시":"통사D","2교시":"미술","3교시":"영어C","4교시":"통과C","5교시":"통사B","6교시":"영어A"},
        "화": {"1교시":"정보A","2교시":"진로","3교시":"국어B","4교시":"수학","5교시":"통과D","6교시":"통과B","7교시":"영어A"},
        "수": {"1교시":"통사C","2교시":"국어C","3교시":"수학","4교시":"체육B","5교시":"한국사","6교시":"정보A"},
        "목": {"1교시":"통사A","2교시":"한국사","3교시":"영어A","4교시":"통과A","5교시":"과탐실","6교시":"수학","7교시":"체육A"},
        "금": {"1교시":"영어B","2교시":"한국사","3교시":"정보B","4교시":"수학","5교시":"자율","6교시":"자율"},
    },
    "1-8": {
        "월": {"1교시":"수학","2교시":"영어C","3교시":"국어C","4교시":"진로","5교시":"한국사","6교시":"통사A"},
        "화": {"1교시":"수학","2교시":"과탐실","3교시":"통사B","4교시":"영어A","5교시":"국어A","6교시":"통과D","7교시":"한국사"},
        "수": {"1교시":"통과C","2교시":"체육A","3교시":"정보A","4교시":"통사D","5교시":"통과B","6교시":"정보B"},
        "목": {"1교시":"정보B","2교시":"영어A","3교시":"체육A","4교시":"통사C","5교시":"수학","6교시":"한국사","7교시":"통과A"},
        "금": {"1교시":"정보A","2교시":"수학","3교시":"영어B","4교시":"국어B","5교시":"자율","6교시":"자율"},
    },

    # ===================== 2학년 =====================
    "2-1": {
        "월": {"1교시":"영어1A","2교시":"스생B","3교시":"선택 과목","4교시":"선택 과목","5교시":"영어1B","6교시":"선택 과목"},
        "화": {"1교시":"선택 과목","2교시":"합주","3교시":"대수","4교시":"선택 과목","5교시":"영어1A","6교시":"문학B","7교시":"선택 과목"},
        "수": {"1교시":"문학C","2교시":"선택 과목","3교시":"선택 과목","4교시":"대수","5교시":"선택 과목","6교시":"문학D"},
        "목": {"1교시":"선택 과목","2교시":"대수","3교시":"선택 과목","4교시":"선택 과목","5교시":"영어1C","6교시":"선택 과목","7교시":"문학A"},
        "금": {"1교시":"선택 과목","2교시":"선택 과목","3교시":"대수","4교시":"스생A","5교시":"자율","6교시":"자율"},
    },
    "2-2": {
        "월": {"1교시":"스생B","2교시":"대수","3교시":"선택 과목","4교시":"선택 과목","5교시":"문학B","6교시":"선택 과목"},
        "화": {"1교시":"선택 과목","2교시":"대수","3교시":"문학C","4교시":"선택 과목","5교시":"영어1B","6교시":"합주","7교시":"선택 과목"},
        "수": {"1교시":"대수","2교시":"선택 과목","3교시":"선택 과목","4교시":"스생A","5교시":"선택 과목","6교시":"문학A"},
        "목": {"1교시":"선택 과목","2교시":"문학C","3교시":"선택 과목","4교시":"선택 과목","5교시":"대수","6교시":"선택 과목","7교시":"문학D"},
        "금": {"1교시":"선택 과목","2교시":"선택 과목","3교시":"영어1A","4교시":"영어1C","5교시":"자율","6교시":"자율"},
    },
    "2-3": {
        "월": {"1교시":"문학A","2교시":"영어1B","3교시":"선택 과목","4교시":"선택 과목","5교시":"대수","6교시":"선택 과목"},
        "화": {"1교시":"선택 과목","2교시":"문학C","3교시":"합주","4교시":"선택 과목","5교시":"대수","6교시":"스생A","7교시":"선택 과목"},
        "수": {"1교시":"영어1A","2교시":"선택 과목","3교시":"선택 과목","4교시":"문학B","5교시":"선택 과목","6교시":"대수"},
        "목": {"1교시":"선택 과목","2교시":"스생A","3교시":"선택 과목","4교시":"선택 과목","5교시":"영어1A","6교시":"선택 과목","7교시":"대수"},
        "금": {"1교시":"선택 과목","2교시":"선택 과목","3교시":"영어1C","4교시":"문학D","5교시":"자율","6교시":"자율"},
    },
    "2-4": {
        "월": {"1교시":"영어1B","2교시":"합주","3교시":"선택 과목","4교시":"선택 과목","5교시":"대수","6교시":"선택 과목"},
        "화": {"1교시":"선택 과목","2교시":"스생B","3교시":"문학D","4교시":"선택 과목","5교시":"영어1C","6교시":"대수","7교시":"선택 과목"},
        "수": {"1교시":"영어1A","2교시":"선택 과목","3교시":"선택 과목","4교시":"대수","5교시":"선택 과목","6교시":"스생A"},
        "목": {"1교시":"선택 과목","2교시":"문학A","3교시":"선택 과목","4교시":"선택 과목","5교시":"영어1A","6교시":"선택 과목","7교시":"문학C"},
        "금": {"1교시":"선택 과목","2교시":"선택 과목","3교시":"문학B","4교시":"대수","5교시":"자율","6교시":"자율"},
    },
    "2-5": {
        "월": {"1교시":"영어1A","2교시":"대수","3교시":"선택 과목","4교시":"선택 과목","5교시":"스생A","6교시":"선택 과목"},
        "화": {"1교시":"선택 과목","2교시":"대수","3교시":"스생B","4교시":"선택 과목","5교시":"영어1A","6교시":"문학A","7교시":"선택 과목"},
        "수": {"1교시":"대수","2교시":"선택 과목","3교시":"선택 과목","4교시":"합주","5교시":"선택 과목","6교시":"문학B"},
        "목": {"1교시":"선택 과목","2교시":"대수","3교시":"선택 과목","4교시":"선택 과목","5교시":"문학D","6교시":"선택 과목","7교시":"영어1C"},
        "금": {"1교시":"선택 과목","2교시":"선택 과목","3교시":"문학C","4교시":"영어1B","5교시":"자율","6교시":"자율"},
    },
    "2-6": {
        "월": {"1교시":"영어1B","2교시":"문학A","3교시":"선택 과목","4교시":"선택 과목","5교시":"문학D","6교시":"선택 과목"},
        "화": {"1교시":"선택 과목","2교시":"영어1A","3교시":"문학C","4교시":"선택 과목","5교시":"문학B","6교시":"대수","7교시":"선택 과목"},
        "수": {"1교시":"영어1C","2교시":"선택 과목","3교시":"선택 과목","4교시":"대수","5교시":"선택 과목","6교시":"합주"},
        "목": {"1교시":"선택 과목","2교시":"영어1A","3교시":"선택 과목","4교시":"선택 과목","5교시":"대수","6교시":"선택 과목","7교시":"스생B"},
        "금": {"1교시":"선택 과목","2교시":"선택 과목","3교시":"스생A","4교시":"대수","5교시":"자율","6교시":"자율"},
    },
    "2-7": {
        "월": {"1교시":"합주","2교시":"대수","3교시":"선택 과목","4교시":"선택 과목","5교시":"영어1A","6교시":"선택 과목"},
        "화": {"1교시":"선택 과목","2교시":"영어1B","3교시":"대수","4교시":"선택 과목","5교시":"스생A","6교시":"문학D","7교시":"선택 과목"},
        "수": {"1교시":"문학A","2교시":"선택 과목","3교시":"선택 과목","4교시":"영어1C","5교시":"선택 과목","6교시":"스생B"},
        "목": {"1교시":"선택 과목","2교시":"대수","3교시":"선택 과목","4교시":"선택 과목","5교시":"문학C","6교시":"선택 과목","7교시":"문학B"},
        "금": {"1교시":"선택 과목","2교시":"선택 과목","3교시":"대수","4교시":"영어1A","5교시":"자율","6교시":"자율"},
    },
    "2-8": {
        "월": {"1교시":"스생A","2교시":"영어1C","3교시":"선택 과목","4교시":"선택 과목","5교시":"대수","6교시":"선택 과목"},
        "화": {"1교시":"선택 과목","2교시":"대수","3교시":"문학A","4교시":"선택 과목","5교시":"합주","6교시":"영어1A","7교시":"선택 과목"},
        "수": {"1교시":"대수","2교시":"선택 과목","3교시":"선택 과목","4교시":"문학C","5교시":"선택 과목","6교시":"영어1A"},
        "목": {"1교시":"선택 과목","2교시":"영어1B","3교시":"선택 과목","4교시":"선택 과목","5교시":"문학B","6교시":"선택 과목","7교시":"대수"},
        "금": {"1교시":"선택 과목","2교시":"선택 과목","3교시":"문학D","4교시":"스생B","5교시":"자율","6교시":"자율"},
    },
}
MOVING_SUBJECTS = ["스생A", "스생B", "합주", "과탐실","미술","체육A","체육B","음악","통과D","정보A","정보B"]


# ========================================
# 시간 파싱 (2026. 6. 8 오전 11:10:26 형식)
# ========================================
def parse_time(t_str):
    if not isinstance(t_str, str):
        return None
    try:
        s = t_str.strip()
        if "오전" in s:
            ampm = "AM"; date_part, time_part = s.split("오전")
        elif "오후" in s:
            ampm = "PM"; date_part, time_part = s.split("오후")
        else:
            return None
        y, mo, d = [int(x) for x in date_part.replace(".", " ").split()]
        hh, mm, ss = [int(x) for x in time_part.strip().split(":")]
        if ampm == "PM" and hh != 12:
            hh += 12
        if ampm == "AM" and hh == 12:
            hh = 0
        return datetime(y, mo, d, hh, mm, ss)
    except Exception:
        return None


def get_current_slot(now):
    weekday = now.weekday()
    if weekday >= 5:
        return "주말", "weekend"
    now_t = now.time()
    schedule = DAY_SCHEDULE[weekday]
    if now_t < schedule[0][1]:
        return "등교 전", "before"
    for name, start, end, kind in schedule:
        if start <= now_t < end:
            return name, kind
    return "방과후", "after"


def get_subject(class_id, now, slot_name):
    if "교시" not in slot_name:
        return None
    weekday = now.weekday()
    if weekday >= 5:
        return None
    day = WEEKDAY_KR[weekday]
    return TIMETABLE.get(class_id, {}).get(day, {}).get(slot_name, None)

@st.cache_data(ttl=15)   # 짧게
def load_data():
    def read_one(item):
        class_id, gid = item
        try:
            sheet = pd.read_csv(csv_url(gid))
            if len(sheet) == 0:
                return None
            sheet.columns = ["시간", "반", "온도", "습도", "조도", "상태"]
            return sheet
        except Exception:
            return None

    all_dfs = []
    with concurrent.futures.ThreadPoolExecutor(max_workers=16) as ex:
        results = ex.map(read_one, CLASS_GIDS.items())
        for r in results:
            if r is not None:
                all_dfs.append(r)

    if not all_dfs:
        return pd.DataFrame(columns=["시간","반","온도","습도","조도","상태","datetime"])

    df = pd.concat(all_dfs, ignore_index=True)
    for col in ["온도", "습도", "조도"]:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["datetime"] = df["시간"].apply(parse_time)
    df = df[df["상태"] == "정상"]
    return df

df = load_data()

def is_active(last_time_str, now, threshold_min=3):
    t = parse_time(last_time_str)
    if t is None:
        return None
    diff = abs((now - t).total_seconds()) / 60
    return diff <= threshold_min


# ===== 상태 판단 기준값 =====
LIGHT_ON = 20  # 조도 ≥ 20
TEMP_COLD = 23 # 온도 < 23
TEMP_HOT = 29  # 온도 ≥ 29


def check_status(temp, light, class_id, now):
    """온도 + 조도 + 시간표로 상태 판단."""
    if temp is None or pd.isna(temp):
        return "❓ 측정실패", "데이터 없음", "gray"

    people = (light is not None) and (not pd.isna(light)) and (light >= LIGHT_ON)

    slot_name, kind = get_current_slot(now)
    subject = get_subject(class_id, now, slot_name)

    # ===== 이동수업일 때 (교실 비어야 정상) =====
    if subject in MOVING_SUBJECTS:
        # 1) 이동수업인데 불 켜짐 → 조명 낭비! (NEW)
        if people:
            return "🔴 이동수업 조명 낭비!", f"{subject} 시간인데 불 켜둠", "red"
        # 2) 이동수업인데 냉방 켜둠 → 냉방 낭비
        if temp < TEMP_COLD:
            return "🔴 이동수업 냉방 낭비!", f"{subject} 시간인데 냉방 켜둠", "red"

    # 온도 높음 → 냉방 안 함
    if temp >= TEMP_HOT:
        return "⚪ 냉방 안 함", "온도 높음", "orange"

    # 온도 낮음
    elif temp < TEMP_COLD:
        if not people:
            return "🟡 빈 교실 냉방 의심", "불 꺼졌는데 냉방 중", "gold"
        else:
            return "🔴 과냉방 (낭비!)", "온도 너무 낮음", "red"

    # 적정
    else:
        return "🟢 정상", "적정 온도", "green"

COLOR_HEX = {"green":"#2e7d32","red":"#c62828","gold":"#f9a825","orange":"#ef6c00","gray":"#757575"}


# ========================================
# 에너지 점수 로직 (체계적, 등급 없음)
# ========================================
def energy_score_today(class_id, df_class_today, now):
    """
    [배점 1000점] 온도적정(300)+이동수업(250)+빈교실(250)+안정성(200)
    """
    detail = {}
    if df_class_today["온도"].notna().sum() == 0:
        return 0, {"데이터없음": 0}

    temps = df_class_today["온도"].dropna()
    avg_temp = temps.mean()

    # 1) 온도 적정성 (300점)
    if 24 <= avg_temp <= 26:
        t_score = 300
    elif avg_temp < 24:
        t_score = max(0, 300 - (24 - avg_temp) * 70)   # 과냉방 감점
    else:
        t_score = max(0, 300 - (avg_temp - 26) * 40)
    t_score = round(t_score, 1)
    detail["🌡️온도적정"] = t_score

    # 2) 이동수업 절약 (250점) — 이동수업인데 냉방 켜둠 감점
    move_score = 250
    move_total = 0; move_waste = 0
    weekday = now.weekday()
    if weekday < 5:
        day = WEEKDAY_KR[weekday]
        schedule = DAY_SCHEDULE[weekday]
        for _, drow in df_class_today.iterrows():
            dt = drow["datetime"]
            if dt is None or pd.isna(drow["온도"]):
                continue
            for name, start, end, kind in schedule:
                if start <= dt.time() < end and "교시" in name:
                    subj = TIMETABLE.get(class_id, {}).get(day, {}).get(name)
                    if subj in MOVING_SUBJECTS:
                        move_total += 1
                        if drow["온도"] < TEMP_COLD:   # 추운데 냉방 켜둠
                            move_waste += 1
                    break
        if move_total > 0:
            move_score = round(250 * (1 - move_waste / move_total), 1)
    detail["🚶이동수업"] = move_score

    # 3) 빈 교실 절약 (250점) — 불 꺼졌는데(조도 낮음) 냉방 중이면 감점
    empty_total = 0; empty_waste = 0
    for _, drow in df_class_today.iterrows():
        if pd.isna(drow["온도"]) or pd.isna(drow["조도"]):
            continue
        if drow["조도"] < LIGHT_ON:   # 불 꺼짐 = 빈 교실 추정
            empty_total += 1
            if drow["온도"] < TEMP_COLD:   # 빈 교실인데 추움(냉방 중)
                empty_waste += 1
    empty_score = round(250 * (1 - empty_waste / empty_total), 1) if empty_total > 0 else 250
    detail["🪑빈교실"] = empty_score

    # 4) 온도 안정성 (200점)
    if len(temps) >= 3:
        std = temps.std()
        if std <= 1: s_score = 200
        elif std <= 2: s_score = 140
        elif std <= 3: s_score = 80
        else: s_score = 0
    else:
        s_score = 200
    detail["📉안정성"] = round(s_score, 1)

    total = round(max(0, min(1000, t_score + move_score + empty_score + s_score)), 1)
    return total, detail


# ========================================
# CSS (배경)
# ========================================
st.markdown("""
<style>
.stApp {
    background: linear-gradient(180deg,#9fd9ff 0%,#bfe9ff 35%,#ddf4ff 65%,#eefaff 100%);
    background-attachment: fixed;
}
h1,h2,h3,h4,h5,p,span,label,li,td,th,
.stMarkdown,.stCaption,
div[data-testid="stMetricValue"],div[data-testid="stMetricLabel"],
.stSelectbox label,.stRadio label {
    color:#fff !important;
    text-shadow:-1.5px -1.5px 0 #000,1.5px -1.5px 0 #000,-1.5px 1.5px 0 #000,1.5px 1.5px 0 #000,
        -1.5px 0 0 #000,1.5px 0 0 #000,0 -1.5px 0 #000,0 1.5px 0 #000 !important;
}
.main .block-container { position:relative; z-index:10; }
[data-testid="stSidebar"] { background:linear-gradient(180deg,#1565c0,#0d47a1); z-index:20; }

.sun-wrap { position:fixed; top:30px; right:40px; width:200px; height:200px; z-index:0; pointer-events:none; }
.sun-rays { position:absolute; top:50%; left:50%; width:200px; height:200px;
    margin:-100px 0 0 -100px; animation:spinRay 30s linear infinite; }
.ray { position:absolute; top:50%; left:50%; width:30px; height:55px; margin:-100px 0 0 -15px;
    background:#ffd23f; border:4px solid #1a1a1a; border-radius:50% 50% 0 0; transform-origin: 50% 100px; }
.sun-core { position:absolute; top:50%; left:50%; width:130px; height:130px; margin:-65px 0 0 -65px; border-radius:50%;
    background:radial-gradient(circle at 38% 35%,#fff6a0 0%,#ffd23f 45%,#ffb300 100%);
    border:5px solid #1a1a1a; z-index:2; }
.sun-core::before { content:''; position:absolute; top:42px; left:34px; width:13px; height:19px;
    background:#1a1a1a; border-radius:50%; box-shadow:42px 0 0 #1a1a1a; }
.sun-core::after { content:''; position:absolute; top:72px; left:44px; width:42px; height:22px;
    border:5px solid #1a1a1a; border-top:none; border-radius:0 0 50px 50px; }
@keyframes spinRay { from { transform:rotate(0); } to { transform:rotate(360deg); } }

.earth-wrap { position:fixed; bottom:-400px; left:50%; width:760px; height:760px; margin-left:-380px; z-index:0; pointer-events:none; }
.earth { width:100%; height:100%; border-radius:50%;
    background:radial-gradient(circle at 38% 32%,#aee1ff 0%,#4ea8ec 45%,#1f78c4 100%);
    border:7px solid #0d3b66; position:relative; overflow:hidden;
    box-shadow:inset -40px -40px 90px rgba(0,0,30,0.35),0 0 70px rgba(78,168,236,0.6);
    animation:spinEarth 50s linear infinite; }
.continent { position:absolute; background:#5cc26b; border:5px solid #2e7d32; }
.c1 { top:14%; left:18%; width:160px; height:130px; border-radius:55% 45% 60% 40%/50% 55% 45% 50%; }
.c2 { top:42%; left:50%; width:200px; height:150px; border-radius:45% 55% 40% 60%/55% 45% 60% 40%; }
.c3 { top:60%; left:14%; width:130px; height:110px; border-radius:60% 40% 50% 50%; }
.c4 { top:8%; left:58%; width:110px; height:90px; border-radius:50% 50% 45% 55%; }
@keyframes spinEarth { from{transform:rotate(0);} to{transform:rotate(360deg);} }

.cloud { position:fixed; z-index:0; pointer-events:none; background:#fff; border-radius:100px; opacity:0.85; border:3px solid #cfe8ff; }
.cloud::before,.cloud::after { content:''; position:absolute; background:#fff; border-radius:50%; }
.cloud::before { width:60%; height:160%; top:-55%; left:12%; }
.cloud::after { width:45%; height:130%; top:-35%; right:12%; }
@keyframes drift { from{transform:translateX(-220px);} to{transform:translateX(calc(100vw + 250px));} }
</style>

<div class="sun-wrap"><div class="sun-rays">
    <div class="ray" style="transform:rotate(0deg);"></div><div class="ray" style="transform:rotate(45deg);"></div>
    <div class="ray" style="transform:rotate(90deg);"></div><div class="ray" style="transform:rotate(135deg);"></div>
    <div class="ray" style="transform:rotate(180deg);"></div><div class="ray" style="transform:rotate(225deg);"></div>
    <div class="ray" style="transform:rotate(270deg);"></div><div class="ray" style="transform:rotate(315deg);"></div>
</div><div class="sun-core"></div></div>

<div class="earth-wrap"><div class="earth">
    <div class="continent c1"></div><div class="continent c2"></div>
    <div class="continent c3"></div><div class="continent c4"></div>
</div></div>

<div class="cloud" style="width:130px;height:42px;top:10%;animation:drift 50s linear infinite;"></div>
<div class="cloud" style="width:90px;height:32px;top:20%;animation:drift 65s linear infinite;animation-delay:-10s;"></div>
<div class="cloud" style="width:150px;height:48px;top:30%;animation:drift 75s linear infinite;animation-delay:-25s;"></div>
<div class="cloud" style="width:100px;height:34px;top:42%;animation:drift 58s linear infinite;animation-delay:-5s;"></div>
<div class="cloud" style="width:120px;height:40px;top:55%;animation:drift 70s linear infinite;animation-delay:-35s;"></div>
<div class="cloud" style="width:80px;height:28px;top:15%;animation:drift 62s linear infinite;animation-delay:-45s;"></div>
<div class="cloud" style="width:140px;height:46px;top:65%;animation:drift 80s linear infinite;animation-delay:-15s;"></div>
""", unsafe_allow_html=True)


now = datetime.now()
slot_name, slot_kind = get_current_slot(now)

st.sidebar.title("🌍 에너지 모니터링")
page = st.sidebar.radio("페이지 선택",
    ["🏠 대시보드 홈","📊 반별 상세","🏆 에너지 랭킹","📅 오늘의 시간표","💡 에너지 리포트","🎯 프로젝트 목표"])


# ========================================
# CSS (컴포넌트)
# ========================================
st.markdown("""
<style>
.clock-wrap{display:flex;align-items:center;gap:30px;
    background:linear-gradient(135deg,#42a5f5,#1976d2);border-radius:30px;
    padding:24px 36px;margin-bottom:24px;border:3px solid #0d3b66;
    box-shadow:0 12px 35px rgba(25,118,210,0.45);position:relative;z-index:10;}
.analog{width:110px;height:110px;border-radius:50%;
    background:radial-gradient(circle,#fff,#e3f2fd);border:6px solid #0d3b66;position:relative;flex-shrink:0;}
.analog .center{position:absolute;top:50%;left:50%;width:12px;height:12px;
    background:#0d47a1;border-radius:50%;transform:translate(-50%,-50%);z-index:5;border:2px solid #fff;}
.hand{position:absolute;bottom:50%;left:50%;transform-origin:bottom center;border-radius:10px;}
.hour{width:6px;height:28px;background:#0d47a1;margin-left:-3px;animation:spinH 43200s linear infinite;}
.minute{width:4px;height:40px;background:#1976d2;margin-left:-2px;animation:spinM 3600s linear infinite;}
.second{width:2px;height:45px;background:#e53935;margin-left:-1px;animation:spinS 60s linear infinite;}
@keyframes spinS{from{transform:rotate(0);}to{transform:rotate(360deg);}}
@keyframes spinM{from{transform:rotate(0);}to{transform:rotate(360deg);}}
@keyframes spinH{from{transform:rotate(0);}to{transform:rotate(360deg);}}
.tick{position:absolute;width:3px;height:9px;background:#90caf9;left:50%;top:5px;margin-left:-1.5px;transform-origin:50% 50px;}
.clock-time{font-size:48px;font-weight:900;margin:0;letter-spacing:2px;}
.clock-date{font-size:17px;margin:2px 0 0 0;}
.clock-slot{display:inline-block;margin-top:10px;padding:7px 20px;
    background:rgba(255,255,255,0.95);border-radius:30px;font-size:18px;font-weight:800;}
.clock-slot span{color:#0d47a1 !important;text-shadow:none !important;}

.class-card{border-radius:22px;padding:20px;margin-bottom:14px;
    box-shadow:0 8px 24px rgba(0,0,0,0.25);border:4px solid #0d3b66;
    position:relative;overflow:hidden;z-index:10;transition:transform 0.3s,box-shadow 0.3s;}
.class-card:hover{transform:translateY(-12px) scale(1.03);box-shadow:0 20px 45px rgba(0,0,0,0.4);}
.class-card::before{content:'';position:absolute;top:-30px;right:-30px;width:110px;height:110px;border-radius:50%;background:rgba(255,255,255,0.12);}
.cc-name{font-size:26px;font-weight:900;margin:0;}
.cc-subject{font-size:15px;margin:2px 0 8px 0;}
.cc-active{display:inline-block;padding:3px 12px;border-radius:20px;font-size:13px;font-weight:800;margin-bottom:8px;}
.cc-status{font-size:19px;font-weight:800;margin:6px 0;}
.cc-reason{font-size:13px;margin-bottom:10px;}
.cc-data{font-size:15px;font-weight:600;background:rgba(0,0,0,0.25);border-radius:12px;padding:8px 10px;}

.tt-table{width:100%;border-collapse:separate;border-spacing:0 8px;}
.tt-table th{background:#6d4c41;
    padding:16px;font-size:19px;font-weight:900;border:none;border-radius:12px;}
.tt-row td{background:#f5ece3;
    color:#4e342e !important;text-shadow:none !important;
    padding:16px 20px;font-size:20px;font-weight:800;
    border:none;vertical-align:middle;}
.tt-row td:first-child{border-radius:12px 0 0 12px;}
.tt-row td:last-child{border-radius:0 12px 12px 0;text-align:right;
    font-size:15px;font-weight:700;color:#8d6e63 !important;}
.tt-subject{font-size:22px;font-weight:900;}
.tt-period-label{font-size:14px;opacity:0.65;font-weight:700;}

/* 쉬는시간 - 더 연하게 */
.tt-break td{background:#efebe9 !important;
    color:#795548 !important;font-size:16px;padding:10px 20px;}
/* 점심 - 살짝 진하게 */
.tt-lunch td{background:#e0c9a6 !important;
    color:#4e342e !important;font-size:20px;}
/* 조종례 - 중간 톤 */
.tt-home td{background:#e8dcc8 !important;
    color:#4e342e !important;}
/* 현재 교시 - 같은 계열 진한 톤 + 부드러운 그림자 */
.tt-now td{background:#a1887f !important;
    color:#ffffff !important;box-shadow:0 4px 14px rgba(109,76,65,0.45);}
/* 이동수업 - 같은 계열 + 왼쪽 띠로만 잔잔히 강조 */
.tt-move td{background:#e0c9a6 !important;color:#4e342e !important;}
.tt-move td:first-child{border-left:6px solid #8d6e63;border-radius:12px 0 0 12px;}

/* ===== 프로젝트 목표 페이지 ===== */
.goal-main{background:linear-gradient(135deg,#1565c0,#42a5f5,#26c6da);
    border-radius:32px;padding:55px 40px;text-align:center;margin-bottom:30px;
    border:5px solid #0d3b66;box-shadow:0 16px 50px rgba(0,0,0,0.35);position:relative;overflow:hidden;}
.goal-main::before{content:'🌍';position:absolute;font-size:260px;opacity:0.13;top:-60px;right:-40px;
    animation:spinEarth 60s linear infinite;}
.goal-main .badge{display:inline-block;background:#ffd23f;color:#0d3b66 !important;
    padding:6px 24px;border-radius:30px;font-size:18px;font-weight:900;
    border:3px solid #0d3b66;margin-bottom:18px;text-shadow:none !important;}
.goal-main h1{font-size:46px;margin:0;line-height:1.3;}
.goal-main p{font-size:20px;margin-top:18px;}
.goal-sub-title{text-align:center;font-size:26px;margin:10px 0 18px 0;}
.goal-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(220px,1fr));gap:18px;margin-bottom:26px;}
.goal-item{border-radius:22px;padding:26px 20px;border:4px solid #0d3b66;text-align:center;
    box-shadow:0 8px 24px rgba(0,0,0,0.25);transition:transform 0.3s,box-shadow 0.3s;position:relative;overflow:hidden;}
.goal-item:hover{transform:translateY(-12px) scale(1.04);box-shadow:0 22px 48px rgba(0,0,0,0.4);}
.goal-item .gicon{font-size:54px;margin-bottom:8px;}
.goal-item h3{font-size:20px;margin:6px 0;}
.goal-item p{font-size:14px;line-height:1.6;}
.flow-box{background:linear-gradient(135deg,#0d47a1,#1565c0);border-radius:26px;
    padding:32px;border:4px solid #0d3b66;box-shadow:0 10px 30px rgba(0,0,0,0.3);}
.flow-steps{display:flex;justify-content:space-around;align-items:center;flex-wrap:wrap;gap:10px;margin-top:18px;}
.flow-step{text-align:center;flex:1;min-width:110px;}
.flow-step .fi{font-size:46px;}
.flow-arrow{font-size:38px;}
.chart-box {
    background: rgba(13, 71, 161, 0.55);
    border-radius: 22px;
    padding: 14px;
    margin-bottom: 18px;
    box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    border: 1px solid rgba(255,255,255,0.15);
}
</style>
""", unsafe_allow_html=True)


def render_clock(now, slot_name, slot_kind):
    slot_icons={"class":"📚","break":"☕","lunch":"🍱","homeroom":"📢","after":"🏠","before":"🌅","weekend":"🌴"}
    icon=slot_icons.get(slot_kind,"🕐")
    wd=WEEKDAY_KR[now.weekday()]
    h=now.hour%12;m=now.minute;s=now.second
    sec_deg=s*6;min_deg=m*6+s*0.1;hour_deg=h*30+m*0.5
    ticks="".join(f'<div class="tick" style="transform:rotate({i*30}deg);"></div>' for i in range(12))
    return f"""<div class="clock-wrap"><div class="analog">{ticks}
        <div class="hand hour" style="animation-delay:-{hour_deg/360*43200}s;"></div>
        <div class="hand minute" style="animation-delay:-{min_deg/360*3600}s;"></div>
        <div class="hand second" style="animation-delay:-{sec_deg/360*60}s;"></div>
        <div class="center"></div></div>
        <div><p class="clock-time">{now.strftime('%H:%M:%S')}</p>
        <p class="clock-date">{now.strftime('%Y년 %m월 %d일')} ({wd}요일)</p>
        <span class="clock-slot"><span>{icon} {slot_name}</span></span></div></div>"""


def date_range_picker(df_source, key_prefix):
    """데이트피커 + 시간 입력으로 범위 선택. (필터된 df, 시작, 종료) 반환."""
    valid = df_source[df_source["datetime"].notna()]
    if len(valid) == 0:
        return df_source.iloc[0:0], None, None
    min_dt = valid["datetime"].min()
    max_dt = valid["datetime"].max()
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        sd = st.date_input("시작 날짜", min_dt.date(),
            min_value=min_dt.date(), max_value=max_dt.date(), key=key_prefix+"sd")
    with c2:
        stime = st.time_input("시작 시각", min_dt.time(), key=key_prefix+"st")
    with c3:
        ed = st.date_input("종료 날짜", max_dt.date(),
            min_value=min_dt.date(), max_value=max_dt.date(), key=key_prefix+"ed")
    with c4:
        etime = st.time_input("종료 시각", max_dt.time(), key=key_prefix+"et")
    start_dt = datetime.combine(sd, stime)
    end_dt = datetime.combine(ed, etime)
    filtered = valid[(valid["datetime"] >= start_dt) & (valid["datetime"] <= end_dt)]
    return filtered, start_dt, end_dt


# ========================================
# 페이지 1: 홈
# ========================================
if page == "🏠 대시보드 홈":
    st.markdown(render_clock(now, slot_name, slot_kind), unsafe_allow_html=True)
    st.title("🏠 전체 교실 현황")

    if len(df) == 0:
        st.warning("아직 수집된 데이터가 없어요. (정상 데이터 기준)")
    else:
        latest = df.groupby("반").last().reset_index()
        total = len(latest)
        waste = sum(1 for _, r in latest.iterrows()
                    if check_status(r["온도"], r["조도"], r["반"], now)[2] in ["red", "gold"])
        normal = sum(1 for _, r in latest.iterrows()
                     if check_status(r["온도"], r["조도"], r["반"], now)[2] == "green")
        c1, c2, c3 = st.columns(3)
        c1.metric("📊 측정 중인 반", f"{total}개")
        c2.metric("🟢 정상", f"{normal}개")
        c3.metric("🔴 낭비 의심", f"{waste}개")
        st.divider()
        st.subheader("⚡ 반별 상태")
        rows = [latest[i:i+4] for i in range(0, len(latest), 4)]
        for rg in rows:
            cols = st.columns(4)
            for idx, (_, row) in enumerate(rg.iterrows()):
                status, reason, color = check_status(row["온도"], row["조도"], row["반"], now)
                subject = get_subject(row["반"], now, slot_name)
                subject_text = f"📖 {subject} · {slot_name}" if subject else f"🕐 {slot_name}"
                bg = COLOR_HEX.get(color, "#757575")
                active = is_active(row["시간"], now)
                if active is True:
                    ah = '<span class="cc-active" style="background:#43a047;">🟢 작동함</span>'
                elif active is False:
                    ah = '<span class="cc-active" style="background:#c62828;">🔴 작동 안함</span>'
                else:
                    ah = '<span class="cc-active" style="background:#757575;">⚪ 알수없음</span>'
                # 조도로 불 켜짐/꺼짐 표시
                light_val = row["조도"]
                if pd.notna(light_val) and light_val >= LIGHT_ON:
                    light_text = f"💡 {light_val} (켜짐)"
                else:
                    light_text = f"🌑 {light_val} (꺼짐)"
                with cols[idx]:
                    st.markdown(f"""<div class="class-card" style="background:{bg};">
                    <p class="cc-name">{row['반']}</p>
                    <p class="cc-subject">{subject_text}</p>{ah}
                    <p class="cc-status">{status}</p>
                    <p class="cc-reason">{reason}</p>
                    <div class="cc-data">🌡️ {row['온도']}°C &nbsp; 💧 {row['습도']}%<br>
                    {light_text}</div></div>""", unsafe_allow_html=True)


# ========================================
# 페이지 2: 반별 상세 (날짜/시각 범위 선택)
# ========================================
elif page == "📊 반별 상세":
    st.title("📊 반별 상세 그래프")
    if len(df) == 0:
        st.warning("아직 수집된 데이터가 없어요.")
    else:
        class_list = sorted(df["반"].unique().tolist())
        selected = st.selectbox("반을 선택하세요", class_list, key="detail_class")

        class_all = df[df["반"] == selected].copy()
        class_df, sdt, edt = date_range_picker(class_all, "detail_")
        class_df = class_df.sort_values("datetime")

        if len(class_df) == 0:
            st.warning("선택한 범위에 데이터가 없어요. 범위를 조정해보세요.")
        else:
            latest_row = class_df.iloc[-1]
            status, reason, color = check_status(latest_row["온도"], latest_row["조도"], selected, now)
            subject = get_subject(selected, now, slot_name)
            st.markdown(f"## {selected}반 — {status}")
            st.caption(f"{reason} · 현재: {subject or slot_name} · "
                       f"{sdt.strftime('%m/%d %H:%M')} ~ {edt.strftime('%m/%d %H:%M')} / {len(class_df)}개")

            # 불 켜짐/꺼짐
            light_val = latest_row["조도"]
            light_state = "💡 켜짐" if (pd.notna(light_val) and light_val >= LIGHT_ON) else "🌑 꺼짐"

            c1, c2, c3 = st.columns(3)
            c1.metric("🌡️ 온도", f"{latest_row['온도']} °C")
            c2.metric("💧 습도", f"{latest_row['습도']} %")
            c3.metric("💡 조도", f"{latest_row['조도']} ({light_state})")
            st.divider()
            
            # 그래프 공통 스타일 적용 함수
            def _style_chart(fig, title, color):
                fig.update_layout(
                    plot_bgcolor="rgba(255,255,255,0.97)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#ffffff", size=15, family="Arial Black, Arial, sans-serif"),
                    title=dict(text=title, font=dict(color="#ffffff", size=22,
                               family="Arial Black, Arial, sans-serif",
                               shadow="2px 2px 3px black, -2px -2px 3px black, 2px -2px 3px black, -2px 2px 3px black")),
                    xaxis_title="시각", margin=dict(l=20, r=20, t=55, b=20), height=320,
                    hoverlabel=dict(bgcolor="white",
                                    font=dict(color="black", size=15, family="Arial, sans-serif"),
                                    bordercolor=color))
                shadow4 = "1px 1px 2px black, -1px -1px 2px black, 1px -1px 2px black, -1px 1px 2px black"
                fig.update_xaxes(gridcolor="rgba(13,59,94,0.18)", color="#ffffff",
                    tickfont=dict(color="#ffffff", size=13, shadow=shadow4),
                    title_font=dict(color="#ffffff", size=15, shadow=shadow4),
                    linecolor="#ffffff", linewidth=2)
                fig.update_yaxes(gridcolor="rgba(13,59,94,0.18)", color="#ffffff",
                    tickfont=dict(color="#ffffff", size=13, shadow=shadow4),
                    title_font=dict(color="#ffffff", size=15, shadow=shadow4),
                    linecolor="#ffffff", linewidth=2)
                return fig

            def make_chart(y_col, title, color):
                fig = px.line(class_df, x="datetime", y=y_col, title=title, markers=True)
                # 선 굵게 + 마커 크게
                fig.update_traces(
                    line_color=color,
                    line_width=5,   # ← 선 굵기 (3 → 5)
                    marker=dict(size=10, color=color,
                                line=dict(width=2.5, color="white")),  # 마커 테두리 흰색
                    hovertemplate="<b>%{x|%m/%d %H:%M:%S}</b><br>" + y_col + ": <b>%{y}</b><extra></extra>"
                )
                fig.update_layout(
                    plot_bgcolor="rgba(255,255,255,0.97)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(color="#ffffff", size=15,
                              family="Arial Black, Arial, sans-serif"),
                    title=dict(
                        text=title,
                        font=dict(color="#ffffff", size=22,
                                  family="Arial Black, Arial, sans-serif",
                                  shadow="2px 2px 3px black, -2px -2px 3px black, 2px -2px 3px black, -2px 2px 3px black")  # ★ 제목 사방 그림자
                    ),
                    xaxis_title="시각",
                    margin=dict(l=20, r=20, t=55, b=20),
                    height=320,
                    hoverlabel=dict(
                        bgcolor="white",
                        font=dict(color="black", size=15,
                                  family="Arial, sans-serif"),  # ★ Arial Black → Arial
                        bordercolor=color
                    )
                )
                # 축 글씨 — 사방 그림자로 진하게
                fig.update_xaxes(
                    gridcolor="rgba(13,59,94,0.18)",
                    color="#ffffff",
                    tickfont=dict(color="#ffffff", size=13,
                                  shadow="1px 1px 2px black, -1px -1px 2px black, 1px -1px 2px black, -1px 1px 2px black"),  # ★
                    title_font=dict(color="#ffffff", size=15,
                                    shadow="1px 1px 2px black, -1px -1px 2px black, 1px -1px 2px black, -1px 1px 2px black"),  # ★
                    linecolor="#ffffff", linewidth=2
                )
                fig.update_yaxes(
                    gridcolor="rgba(13,59,94,0.18)",
                    color="#ffffff",
                    tickfont=dict(color="#ffffff", size=13,
                                  shadow="1px 1px 2px black, -1px -1px 2px black, 1px -1px 2px black, -1px 1px 2px black"),  # ★
                    title_font=dict(color="#ffffff", size=15,
                                    shadow="1px 1px 2px black, -1px -1px 2px black, 1px -1px 2px black, -1px 1px 2px black"),  # ★
                    linecolor="#ffffff", linewidth=2
                )
                return fig

            # 그래프를 둥근 카드 안에 넣기
            def chart_card(fig):
                st.markdown('<div class="chart-box">', unsafe_allow_html=True)
                st.plotly_chart(fig, use_container_width=True)
                st.markdown('</div>', unsafe_allow_html=True)

            # ===== 온도 그래프 (낭비 시점 빨강으로 색칠) =====
            import plotly.graph_objects as go

            # 각 점의 낭비 여부 판단 → 색 결정
            temp_colors = []
            for _, r in class_df.iterrows():
                pt_time = r["datetime"]
                _, _, c = check_status(r["온도"], r["조도"], selected, pt_time)
                temp_colors.append("#e53935" if c in ["red", "gold"] else "#00897b")

            fig_temp = go.Figure()
            fig_temp.add_trace(go.Scatter(
                x=class_df["datetime"], y=class_df["온도"],
                mode="lines+markers",
                line=dict(color="#00897b", width=5),
                marker=dict(size=11, color=temp_colors, line=dict(width=2.5, color="white")),
                hovertemplate="<b>%{x|%m/%d %H:%M:%S}</b><br>온도: <b>%{y}</b>°C<extra></extra>"
            ))
            _style_chart(fig_temp, "🌡️ 온도 변화 (🔴=낭비 의심)", "#00897b")

            # ===== 조도 그래프 (이동수업 중 불 켜진 시점 빨강으로) =====
            light_colors = []
            for _, r in class_df.iterrows():
                pt_time = r["datetime"]
                _, _, c = check_status(r["온도"], r["조도"], selected, pt_time)
                # 조명 낭비(이동수업+불켜짐)일 때만 빨강
                slot_n, _ = get_current_slot(pt_time)
                subj = get_subject(selected, pt_time, slot_n)
                is_light_waste = (subj in MOVING_SUBJECTS) and pd.notna(r["조도"]) and (r["조도"] >= LIGHT_ON)
                light_colors.append("#e53935" if is_light_waste else "#fbc02d")

            fig_light = go.Figure()
            fig_light.add_trace(go.Scatter(
                x=class_df["datetime"], y=class_df["조도"],
                mode="lines+markers",
                line=dict(color="#fbc02d", width=5),
                marker=dict(size=11, color=light_colors, line=dict(width=2.5, color="white")),
                hovertemplate="<b>%{x|%m/%d %H:%M:%S}</b><br>조도: <b>%{y}</b><extra></extra>"
            ))
            _style_chart(fig_light, "💡 조도 변화 (🔴=이동수업 중 불 켜짐)", "#fbc02d")

            # 그래프 출력 (온도 → 습도 → 조도)
            chart_card(fig_temp)
            chart_card(make_chart("습도", "💧 습도 변화", "#1e88e5"))
            chart_card(fig_light)
# ========================================
# 페이지 3: 에너지 랭킹 (오늘 하루, 등급 없음)
# ========================================
elif page == "🏆 에너지 랭킹":
    st.title("🏆 오늘의 에너지 절약 랭킹")
    st.caption(f"📅 {now.strftime('%Y년 %m월 %d일')} 집계 (매일 0시 초기화)")
    st.caption("온도적정(300)+이동수업(250)+빈교실(250)+안정성(200) = 1000점")

    today = now.date()
    df_today = df[df["datetime"].notna()].copy()
    df_today = df_today[df_today["datetime"].apply(lambda d: d.date()==today)]

    if len(df_today)==0:
        st.warning("오늘 수집된 데이터가 아직 없어요.")
    else:
        results=[]
        for class_id in df_today["반"].unique():
            dc=df_today[df_today["반"]==class_id].reset_index(drop=True)
            sc, detail = energy_score_today(class_id, dc, now)
            latest=dc.iloc[-1]
            results.append((class_id, sc, detail, latest))
        results.sort(key=lambda x:x[1], reverse=True)

        for idx,(class_id,sc,detail,latest) in enumerate(results):
            medal=["🥇","🥈","🥉"][idx] if idx<3 else f"{idx+1}위"
            status,reason,color=check_status(latest["온도"],latest["조도"],class_id,now)
            bg=COLOR_HEX.get(color,"#757575")
            detail_str=" · ".join(f"{k} {v}" for k,v in detail.items())
            # 불 켜짐/꺼짐
            light_val = latest["조도"]
            light_txt = "💡켜짐" if (pd.notna(light_val) and light_val >= LIGHT_ON) else "🌑꺼짐"
            st.markdown(f"""<div class="class-card" style="background:{bg};">
                <div style="display:flex;align-items:center;">
                <div style="font-size:44px;margin-right:20px;">{medal}</div>
                <div style="flex:1;">
                <p class="cc-name">{class_id} — {sc}점</p>
                <p class="cc-status">{status}</p>
                <p class="cc-reason">🌡️ 현재 {latest['온도']}°C · {light_txt}</p>
                <div class="cc-data">{detail_str}</div>
                </div></div></div>""", unsafe_allow_html=True)

# ========================================
# 페이지 4: 시간표
# ========================================
elif page == "📅 오늘의 시간표":
    st.title("📅 오늘의 시간표")
    selected = st.selectbox("반 선택", sorted(TIMETABLE.keys()))
    weekday = now.weekday()
    if weekday >= 5:
        st.info("🌴 주말입니다! 시간표가 없어요.")
    else:
        day = WEEKDAY_KR[weekday]
        st.subheader(f"{selected}반 · {day}요일")
        schedule = DAY_SCHEDULE[weekday]
        html = '<table class="tt-table"><tr><th>교시 / 과목</th><th>시간</th></tr>'
        for name, start, end, kind in schedule:
            subject = TIMETABLE.get(selected, {}).get(day, {}).get(name, "")
            time_str = f"{start.strftime('%H:%M')} ~ {end.strftime('%H:%M')}"
            is_now = (start <= now.time() < end)
            is_move = subject in MOVING_SUBJECTS

            # 행 클래스 결정
            rc = "tt-row"
            if kind == "break": rc += " tt-break"
            elif kind == "lunch": rc += " tt-lunch"
            elif kind == "homeroom": rc += " tt-home"
            elif is_move: rc += " tt-move"
            if is_now: rc += " tt-now"

            # 교시 + 과목 묶어서 표시
            if "교시" in name:
                move_icon = " 🏃" if is_move else ""
                now_icon = " 🔴" if is_now else ""
                cell = (f'<span class="tt-period-label">{name}</span><br>'
                        f'<span class="tt-subject">{subject or "-"}{move_icon}</span>{now_icon}')
            else:
                # 쉬는시간/점심/조종례는 이름만
                now_icon = " 🔴" if is_now else ""
                cell = f'<span class="tt-subject">{name}</span>{now_icon}'

            html += f'<tr class="{rc}"><td>{cell}</td><td>{time_str}</td></tr>'
        html += '</table>'
        st.markdown(html, unsafe_allow_html=True)

# ========================================
# 페이지 5: 에너지 리포트 (범위 선택)
# ========================================
elif page == "💡 에너지 리포트":
    st.title("💡 에너지 절약 리포트")
    df_all = df[df["datetime"].notna() & df["온도"].notna()].copy()
    df_valid, sdt, edt = date_range_picker(df_all, "report_")

    if len(df_valid) == 0:
        st.warning("선택한 범위에 데이터가 없어요.")
    else:
        st.caption(f"📅 {sdt.strftime('%m/%d %H:%M')} ~ {edt.strftime('%m/%d %H:%M')} / {len(df_valid)}개 분석")
        c1, c2, c3 = st.columns(3)
        c1.metric("🌡️ 평균 온도", f"{df_valid['온도'].mean():.1f} °C")
        c2.metric("💡 평균 조도", f"{df_valid['조도'].mean():.0f}")
        c3.metric("💧 평균 습도", f"{df_valid['습도'].mean():.1f} %")
        st.divider()

        # 그래프 글씨 그림자 (재사용)
        shadow4 = "1px 1px 2px black, -1px -1px 2px black, 1px -1px 2px black, -1px 1px 2px black"
        layout = dict(plot_bgcolor="rgba(255,255,255,0.95)",
            paper_bgcolor="rgba(13,71,161,0.55)",
            font=dict(color="#fff", shadow=shadow4),
            margin=dict(l=20, r=20, t=60, b=20))

        # ===== ① 시간대별 평균 온도 =====
        st.subheader("⏰ 시간대별 평균 온도")
        df_valid = df_valid.copy()
        df_valid["시각"] = df_valid["datetime"].dt.hour
        hourly = df_valid.groupby("시각")["온도"].mean().reset_index()
        fig = px.bar(hourly, x="시각", y="온도", text_auto=".1f",
            color="온도", color_continuous_scale="RdBu_r",
            labels={"시각": "시간 (시)", "온도": "평균 온도(°C)"})
        fig.update_traces(marker_line_width=2, marker_line_color="#0d3b66", textposition="outside",
            textfont=dict(color="#fff"))
        fig.add_hline(y=24, line_dash="dash", line_color="lime",
            annotation_text="적정 하한 24도", annotation_font_color="white")
        fig.add_hline(y=26, line_dash="dash", line_color="orange",
            annotation_text="적정 상한 26도", annotation_font_color="white")
        fig.update_layout(height=380, title="", **layout)   # ★ 제목 비움
        fig.update_xaxes(color="#fff", title_font_color="#fff", dtick=1,
            tickfont=dict(color="#fff", shadow=shadow4), title_font=dict(shadow=shadow4))
        fig.update_yaxes(color="#fff", title_font_color="#fff",
            tickfont=dict(color="#fff", shadow=shadow4), title_font=dict(shadow=shadow4))
        st.plotly_chart(fig, use_container_width=True)

        # ===== ② 온도 상태 비율 / ③ 조도 상태 비율 =====
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("🌡️ 온도 상태 비율")
            def temp_cat(t):
                if t < 22: return "너무 추움(낭비)"
                elif t <= 28: return "적정"
                else: return "너무 더움"
            df_valid["상태분류"] = df_valid["온도"].apply(temp_cat)
            cat = df_valid["상태분류"].value_counts().reset_index()
            cat.columns = ["상태", "개수"]
            fig2 = px.pie(cat, names="상태", values="개수", hole=0.5,
                color="상태", color_discrete_map={
                    "적정": "#2e7d32", "너무 추움(낭비)": "#1e88e5", "너무 더움": "#e53935"})
            fig2.update_traces(textinfo="percent+label",
                textfont=dict(color="white", shadow=shadow4),   # ★ 그림자
                marker=dict(line=dict(color="#0d3b66", width=3)))
            fig2.update_layout(height=350, title="", **layout)   # ★ 제목 비움
            st.plotly_chart(fig2, use_container_width=True)
        with col2:
            st.subheader("💡 조명 상태 비율")
            def light_cat(l):
                return "불 켜짐" if l >= LIGHT_ON else "불 꺼짐"
            df_valid["조명분류"] = df_valid["조도"].apply(light_cat)
            cat3 = df_valid["조명분류"].value_counts().reset_index()
            cat3.columns = ["상태", "개수"]
            fig3 = px.pie(cat3, names="상태", values="개수", hole=0.5,
                color="상태", color_discrete_map={
                    "불 켜짐": "#fbc02d", "불 꺼짐": "#37474f"})
            fig3.update_traces(textinfo="percent+label",
                textfont=dict(color="white", shadow=shadow4),   # ★ 그림자
                marker=dict(line=dict(color="#0d3b66", width=3)))
            fig3.update_layout(height=350, title="", **layout)   # ★ 제목 비움
            st.plotly_chart(fig3, use_container_width=True)

        st.divider()

        # ===== ④ 이동수업 낭비 분석 =====
        st.subheader("🚶 이동수업 중 에너지 낭비 분석")
        st.caption("이동수업(교실 비움)인데 불을 켜뒀거나 냉방을 켜둔 비율")

        move_ok = 0; move_light = 0; move_cool = 0
        for _, r in df_valid.iterrows():
            dt = r["datetime"]
            slot_n, _ = get_current_slot(dt)
            subj = get_subject(r["반"], dt, slot_n)
            if subj in MOVING_SUBJECTS:
                light_on = pd.notna(r["조도"]) and r["조도"] >= LIGHT_ON
                cool_on = pd.notna(r["온도"]) and r["온도"] < TEMP_COLD
                if light_on:
                    move_light += 1
                elif cool_on:
                    move_cool += 1
                else:
                    move_ok += 1

        total_move = move_ok + move_light + move_cool
        if total_move == 0:
            st.info("분석 범위에 이동수업 시간 데이터가 없어요.")
        else:
            mdf = pd.DataFrame({
                "상태": ["✅ 잘 껐음", "🔴 불 켜둠(낭비)", "🔴 냉방 켜둠(낭비)"],
                "개수": [move_ok, move_light, move_cool]
            })
            mdf = mdf[mdf["개수"] > 0]
            fig4 = px.pie(mdf, names="상태", values="개수", hole=0.5,
                color="상태", color_discrete_map={
                    "✅ 잘 껐음": "#2e7d32",
                    "🔴 불 켜둠(낭비)": "#e53935",
                    "🔴 냉방 켜둠(낭비)": "#ef6c00"})
            fig4.update_traces(textinfo="percent+label",
                textfont=dict(color="white", shadow=shadow4),   # ★ 그림자
                marker=dict(line=dict(color="#0d3b66", width=3)))
            fig4.update_layout(height=400, title="", **layout)   # ★ 제목 비움
            st.plotly_chart(fig4, use_container_width=True)

            waste_cnt = move_light + move_cool
            waste_pct = waste_cnt / total_move * 100
            if waste_pct == 0:
                st.success(f"🎉 훌륭해요! 이동수업 {total_move}회 모두 에너지를 잘 절약했어요!")
            else:
                st.warning(f"⚠️ 이동수업 {total_move}회 중 {waste_cnt}회({waste_pct:.0f}%)에서 "
                           f"에너지 낭비가 있었어요. 이동수업 때 불·냉방을 꼭 끕시다!")

# ========================================
# 페이지 6: 프로젝트 목표 (계층적 디자인)
# ========================================
elif page == "🎯 프로젝트 목표":
    st.title("🎯 프로젝트 목표")

    # 가장 큰 핵심 목표 (제일 크게!)
    st.markdown("""
    <div class="goal-main">
        <span class="badge">⭐ 핵심 목표</span>
        <h1>학교 교실의 에너지 낭비를<br>실시간으로 잡아낸다! 🔋</h1>
        <p>센서로 교실 환경을 측정하고, 낭비를 한눈에 보여줘<br>
        <b>모두가 함께 에너지를 절약하는 문화</b>를 만듭니다.</p>
    </div>
    """, unsafe_allow_html=True)

    # 세부 목표 (작게, 그리드로)
    st.markdown('<h2 class="goal-sub-title">📌 이를 위한 세부 목표</h2>', unsafe_allow_html=True)
    goals=[
        ("🚶","이동수업 낭비 감지","체육 등 빈 교실에 냉방·조명 켜둔 걸 자동 감지","#e53935"),
        ("💡","조명 낭비 감지","조도 센서로 이동수업 중 불 켜둠을 포착","#fbc02d"),
        ("📊","데이터 기반 관리","감이 아닌 실제 데이터로 냉방·조명 관리","#1e88e5"),
        ("🏆","절약 동기부여","반별 랭킹으로 자발적 절약 유도","#f9a825"),
        ("🌱","환경 보호","탄소 배출을 줄여 지구를 지킴","#43a047"),
    ]
    cards_html='<div class="goal-grid">'
    for icon,title,desc,col in goals:
        cards_html+=f"""<div class="goal-item" style="background:{col};">
            <div class="gicon">{icon}</div><h3>{title}</h3><p>{desc}</p></div>"""
    cards_html+='</div>'
    st.markdown(cards_html, unsafe_allow_html=True)

        # 작동 원리 (흐름도)
    st.markdown("""
    <div class="flow-box">
        <h2 style="text-align:center;">📡 어떻게 작동하나요?</h2>
        <div class="flow-steps">
            <div class="flow-step"><div class="fi">🔌</div><p><b>피코 + 센서</b><br>교실 환경 측정</p></div>
            <div class="flow-arrow">➡️</div>
            <div class="flow-step"><div class="fi">📊</div><p><b>구글 시트</b><br>데이터 저장</p></div>
            <div class="flow-arrow">➡️</div>
            <div class="flow-step"><div class="fi">💻</div><p><b>대시보드</b><br>실시간 분석</p></div>
        </div>
        <p style="text-align:center;margin-top:18px;">⏱️ 30초마다 자동으로 갱신됩니다!</p>
    </div>
    """, unsafe_allow_html=True)
