#!/usr/bin/env python3
"""生命监测系统"""

import os
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, ".last_run")
README_PATH = os.path.join(BASE_DIR, "README.md")

MAX_DAYS = 7
BIRTH_DATE = datetime.date(1995, 4, 23)
BJ = datetime.timezone(datetime.timedelta(hours=8))


def read_last_run():
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            raw = f.read().strip()
        dt = datetime.datetime.fromisoformat(raw)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=BJ)
        return dt
    except Exception:
        return None


def write_last_run(dt):
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(dt.isoformat())


def now():
    return datetime.datetime.now(BJ)


def generate_alive_content(last_run, days, scan_time):
    lines = [
        f"🟢 上次存活时间: {last_run.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)",
        "",
        f"更新时间: {scan_time.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)",
    ]
    return "\n".join(lines)


def generate_obituary_content(last_run, days, scan_time, force_death=False):
    birth = BIRTH_DATE
    if force_death:
        death_date = scan_time.date()
        death_detail = ""
        death_reason = "手动确认死亡。"
    else:
        death_date = (last_run + datetime.timedelta(days=MAX_DAYS)).date()
        death_detail = f"（最后手动执行后第 {MAX_DAYS} 天（估算））"
        death_reason = f"超过 {MAX_DAYS} 天未检测到生命体征，按协议发布讣告。"
    age = death_date.year - birth.year - ((death_date.month, death_date.day) < (birth.month, birth.day))

    with open(os.path.join(BASE_DIR, "obituary.md"), "r", encoding="utf-8") as f:
        content = f.read()

    replacements = {
        "{{BIRTH_DATE}}": birth.strftime('%Y-%m-%d'),
        "{{BIRTH_LUNAR}}": "农历一九九五年三月廿四",
        "{{DEATH_DATE}}": death_date.strftime('%Y-%m-%d'),
        "{{AGE}}": str(age),
        "{{MAX_DAYS}}": str(MAX_DAYS),
        "{{LAST_RUN}}": last_run.strftime('%Y-%m-%d %H:%M:%S'),
        "{{DAYS}}": str(days),
        "{{SCAN_TIME}}": scan_time.strftime('%Y-%m-%d %H:%M:%S'),
        "{{DEATH_DETAIL}}": death_detail,
        "{{DEATH_REASON}}": death_reason,
    }

    for key, value in replacements.items():
        content = content.replace(key, value)

    return content


def run():
    import sys
    auto_mode = "--auto" in sys.argv
    force_death = "--force-death" in sys.argv

    scan_time = now()
    last_run = read_last_run()

    if force_death:
        fake_past = scan_time - datetime.timedelta(days=MAX_DAYS + 1)
        write_last_run(fake_past)
        last_run = fake_past
    elif not auto_mode:
        write_last_run(scan_time)
        last_run = scan_time

    if last_run is None:
        days = 0
        content = generate_alive_content(scan_time, days, scan_time)
    else:
        days = (scan_time - last_run).days
        if days > MAX_DAYS:
            print(f"⚠️  距上次手动执行已过去 {days} 天，超过 {MAX_DAYS} 天阈值！")
            content = generate_obituary_content(last_run, days, scan_time, force_death)
        else:
            print(f"✅ 距上次手动执行 {days} 天，在 {MAX_DAYS} 天阈值内。")
            content = generate_alive_content(last_run, days, scan_time)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"📝 README.md 已更新")
    print(f"   间隔: {days} 天 | 模式: {'自动检查' if auto_mode else ('强制死亡' if force_death else '手动打卡')}")
    print(f"   状态: {'讣告' if last_run and days > MAX_DAYS else '正常'}")


if __name__ == "__main__":
    run()
