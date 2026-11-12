#!/usr/bin/env python3
"""生命监测系统"""

import os
import json
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, ".last_run")
README_PATH = os.path.join(BASE_DIR, "README.md")
STATUS_PATH = os.path.join(BASE_DIR, "status.json")

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
        f"🟢 上次签到时间: {last_run.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)",
        "",
        f"更新时间: {scan_time.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)",
    ]
    return "\n".join(lines)


def generate_obituary_content(last_run, days, scan_time, force_death=False):
    birth = BIRTH_DATE
    if force_death:
        # 手动确认死亡：死亡日期为当前扫描日期，保留真实最后存活时间
        death_date = scan_time.date()
        death_detail = ""
        death_reason = "手动确认死亡。"
    else:
        # 自动判定死亡：超过阈值，估算死亡日期
        death_date = (last_run + datetime.timedelta(days=MAX_DAYS)).date()
        death_detail = f"（最后手动执行后第 {MAX_DAYS} 天（估算））"
        death_reason = f"超过 {MAX_DAYS} 天未检测到生命体征，按协议发布讣告。"
    days_line = f"> **距上次执行**: {days} 天"
    age = death_date.year - birth.year - ((death_date.month, death_date.day) < (birth.month, birth.day))

    with open(os.path.join(BASE_DIR, "obituary.md"), "r", encoding="utf-8") as f:
        content = f.read()

    replacements = {
        "{{BIRTH_DATE}}": birth.strftime('%Y-%m-%d'),
        "{{BIRTH_LUNAR}}": "农历一九九五年三月廿四",
        "{{NAME}}": "朱俊伟",
        "{{DEATH_DATE}}": death_date.strftime('%Y-%m-%d'),
        "{{AGE}}": str(age),
        "{{MAX_DAYS}}": str(MAX_DAYS),
        "{{LAST_RUN}}": last_run.strftime('%Y-%m-%d %H:%M:%S'),
        "{{SCAN_TIME}}": scan_time.strftime('%Y-%m-%d %H:%M:%S'),
        "{{DEATH_DETAIL}}": death_detail,
        "{{DEATH_REASON}}": death_reason,
        "{{DAYS_LINE}}": days_line,
    }

    for key, value in replacements.items():
        content = content.replace(key, value)

    return content


def read_current_state():
    """读取 README.md 当前状态，返回 'dead' / 'alive' / None（无法判断）"""
    if not os.path.exists(README_PATH):
        return None
    try:
        with open(README_PATH, "r", encoding="utf-8") as f:
            content = f.read()
    except Exception:
        return None
    if "🪦" in content or "R  I  P" in content:
        return "dead"
    if "🟢" in content:
        return "alive"
    return None


def write_status_json(status, last_checkin, updated_at, days, death_date=None, age_at_death=None, death_reason=None):
    data = {
        "name": "朱俊伟",
        "birth_date": BIRTH_DATE.strftime('%Y-%m-%d'),
        "birth_lunar": "农历一九九五年三月廿四",
        "status": status,
        "last_checkin": last_checkin.isoformat() if last_checkin else None,
        "updated_at": updated_at.isoformat(),
        "days_since_checkin": days,
        "max_days": MAX_DAYS,
        "death_date": death_date,
        "age_at_death": age_at_death,
        "death_reason": death_reason,
    }
    with open(STATUS_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def run():
    import sys
    auto_mode = "--auto" in sys.argv
    force_death = "--force-death" in sys.argv

    scan_time = now()
    last_run = read_last_run()
    current_state = read_current_state()

    if force_death:
        # 死亡模式：不修改 .last_run，保留真实的上次存活时间
        if last_run is None:
            last_run = scan_time
    elif not auto_mode:
        # 手动签到：更新 .last_run 为当前时间
        write_last_run(scan_time)
        last_run = scan_time

    if last_run is None:
        days = 0
        if force_death:
            content = generate_obituary_content(scan_time, days, scan_time, force_death)
        else:
            content = generate_alive_content(scan_time, days, scan_time)
    else:
        days = (scan_time - last_run).days
        if force_death:
            print(f"💀 手动确认死亡。最后存活时间: {last_run.strftime('%Y-%m-%d %H:%M:%S')}")
            content = generate_obituary_content(last_run, days, scan_time, force_death)
        elif days > MAX_DAYS:
            print(f"⚠️  距上次手动执行已过去 {days} 天，超过 {MAX_DAYS} 天阈值！")
            content = generate_obituary_content(last_run, days, scan_time, force_death)
        elif auto_mode and current_state == "dead":
            # 自动任务不覆盖已存在的讣告（可能是 GitHub 手动提交的）
            print(f"🔒 检测到 README 已有讣告，自动任务跳过覆盖。")
            with open(README_PATH, "r", encoding="utf-8") as f:
                content = f.read()
        elif auto_mode and current_state == "alive":
            # GitHub 手动签到后 README 已是存活，跳过覆盖
            print(f"✅ README 已是存活状态，跳过覆盖。")
            content = generate_alive_content(last_run, days, scan_time)
        else:
            print(f"✅ 距上次手动执行 {days} 天，在 {MAX_DAYS} 天阈值内。")
            content = generate_alive_content(last_run, days, scan_time)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    is_dead = "🪦" in content or "R  I  P" in content

    # 写入 status.json
    death_date_str = None
    age_at_death_val = None
    death_reason_str = None

    if is_dead:
        if force_death:
            death_date_str = scan_time.date().isoformat()
            death_reason_str = "手动确认死亡。"
        elif days > MAX_DAYS:
            death_date_str = (last_run + datetime.timedelta(days=MAX_DAYS)).date().isoformat()
            death_reason_str = f"超过 {MAX_DAYS} 天未检测到生命体征，按协议发布讣告。"

        if death_date_str:
            dd = datetime.date.fromisoformat(death_date_str)
            age_at_death_val = dd.year - BIRTH_DATE.year - ((dd.month, dd.day) < (BIRTH_DATE.month, BIRTH_DATE.day))

    write_status_json(
        "dead" if is_dead else "alive",
        last_run,
        scan_time,
        days,
        death_date_str,
        age_at_death_val,
        death_reason_str,
    )

    print(f"📝 README.md 已更新")
    mode_str = '自动检查' if auto_mode else ('强制死亡' if force_death else '手动打卡')
    print(f"   间隔: {days} 天 | 模式: {mode_str}")
    print(f"   状态: {'讣告' if is_dead else '正常'}")
    print(f"📊 status.json 已更新")


if __name__ == "__main__":
    run()