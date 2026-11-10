#!/usr/bin/env python3
"""生命监测系统"""

import os
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, ".last_run")
README_PATH = os.path.join(BASE_DIR, "README.md")
DEATH_CONFIRMED_FILE = os.path.join(BASE_DIR, ".death_confirmed")

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


def confirm_death(death_date, manual=True):
    """写入死亡确认标记，manual=True 表示手动强制死亡"""
    with open(DEATH_CONFIRMED_FILE, "w", encoding="utf-8") as f:
        f.write(f"{'manual' if manual else 'auto'}\n{death_date.isoformat()}")


def clear_death_confirmation():
    """清除死亡确认标记（复活）"""
    if os.path.exists(DEATH_CONFIRMED_FILE):
        os.remove(DEATH_CONFIRMED_FILE)


def get_death_info():
    """读取死亡确认信息，返回 (类型, 死亡日期) 或 None"""
    if not os.path.exists(DEATH_CONFIRMED_FILE):
        return None
    try:
        with open(DEATH_CONFIRMED_FILE, "r", encoding="utf-8") as f:
            lines = f.read().strip().split("\n")
        if len(lines) == 2:
            death_type = lines[0]
            death_date = datetime.date.fromisoformat(lines[1])
            return (death_type, death_date)
    except Exception:
        pass
    return None


def now():
    return datetime.datetime.now(BJ)


def generate_alive_content(last_run, days, scan_time):
    lines = [
        f"🟢 上次存活时间: {last_run.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)",
        "",
        f"更新时间: {scan_time.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)",
    ]
    return "\n".join(lines)


def generate_obituary_content(last_run, days, scan_time, force_death=False, death_info=None):
    birth = BIRTH_DATE
    if death_info is not None:
        # 死亡已通过标记确认（手动强制死亡后由自动任务读取）
        death_type, death_date = death_info
        death_detail = ""
        death_reason = "手动确认死亡。" if death_type == "manual" else f"超过 {MAX_DAYS} 天未检测到生命体征，按协议发布讣告。"
    elif force_death:
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


def run():
    import sys
    auto_mode = "--auto" in sys.argv
    force_death = "--force-death" in sys.argv

    scan_time = now()
    last_run = read_last_run()
    death_info = get_death_info()
    current_state = read_current_state()

    if force_death:
        # 死亡模式：不修改 .last_run，保留真实的上次存活时间
        if last_run is None:
            last_run = scan_time
        death_date = scan_time.date()
        confirm_death(death_date, manual=True)
        death_info = ("manual", death_date)
    elif not auto_mode:
        # 手动签到：更新 .last_run 为当前时间，清除死亡标记（复活）
        write_last_run(scan_time)
        clear_death_confirmation()
        last_run = scan_time
        death_info = None

    death_confirmed = death_info is not None

    if last_run is None:
        days = 0
        if death_confirmed:
            content = generate_obituary_content(scan_time, days, scan_time, death_info=death_info)
        elif force_death:
            content = generate_obituary_content(scan_time, days, scan_time, force_death)
        else:
            content = generate_alive_content(scan_time, days, scan_time)
    else:
        days = (scan_time - last_run).days
        if death_confirmed:
            if auto_mode and current_state == "alive":
                # GitHub 手动签到后 README 已是存活，信任 README 内容
                print(f"✅ README 已是存活状态，跳过死亡标记覆盖。")
                content = generate_alive_content(last_run, days, scan_time)
            else:
                print(f"💀 死亡已确认。最后存活时间: {last_run.strftime('%Y-%m-%d %H:%M:%S')}")
                content = generate_obituary_content(last_run, days, scan_time, death_info=death_info)
        elif force_death:
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
        else:
            print(f"✅ 距上次手动执行 {days} 天，在 {MAX_DAYS} 天阈值内。")
            content = generate_alive_content(last_run, days, scan_time)

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"📝 README.md 已更新")
    mode_str = '自动检查' if auto_mode else ('强制死亡' if force_death else '手动打卡')
    print(f"   间隔: {days} 天 | 模式: {mode_str}")
    is_dead = (death_confirmed and not (auto_mode and current_state == "alive")) or (last_run is not None and days > MAX_DAYS)
    print(f"   状态: {'讣告' if is_dead else '正常'}")


if __name__ == "__main__":
    run()