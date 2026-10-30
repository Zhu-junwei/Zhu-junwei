#!/usr/bin/env python3
"""
生命监测系统 - Life Monitor System

每次运行本脚本 = 一次「手动打卡」，记录当前时间。
如果距上次打卡超过 7 天，则在 README 中发布「讣告」。
定时任务每天 23:00 北京时间自动运行，用于检测系统是否停滞。
"""

import os
import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATE_FILE = os.path.join(BASE_DIR, ".last_run")
README_PATH = os.path.join(BASE_DIR, "README.md")

MAX_DAYS = 7  # 最大间隔天数
BIRTH_DATE = datetime.date(1995, 4, 16)  # 出生日期


def read_last_run():
    """读取上次运行时间"""
    if not os.path.exists(STATE_FILE):
        return None
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            raw = f.read().strip()
        return datetime.datetime.fromisoformat(raw)
    except Exception:
        return None


def write_last_run(dt):
    """写入当前运行时间"""
    with open(STATE_FILE, "w", encoding="utf-8") as f:
        f.write(dt.isoformat())


BJ = datetime.timezone(datetime.timedelta(hours=8))  # 北京时间 UTC+8


def now():
    return datetime.datetime.now(BJ)


def generate_alive_content(last_run, days, scan_time):
    """生成正常状态下的 README 内容"""
    lines = []
    lines.append(f"🟢 上次存活时间: {last_run.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)")
    lines.append("")
    lines.append(f"更新时间: {scan_time} (UTC+8)")
    return "\n".join(lines)


def generate_obituary_content(last_run, days, scan_time):
    """生成正式讣告内容"""
    death_date = (last_run + datetime.timedelta(days=MAX_DAYS)).date()
    birth = BIRTH_DATE
    age = death_date.year - birth.year - ((death_date.month, death_date.day) < (birth.month, birth.day))

    lines = []
    lines.append("## ⚫ 讣告")
    lines.append("")
    lines.append("```")
    lines.append("        🪦")
    lines.append("")
    lines.append("        R  I  P")
    lines.append("")
    lines.append(f"    {birth.strftime('%Y-%m-%d')} — {death_date.strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append(f"    享年 {age} 岁")
    lines.append("```")
    lines.append("")
    lines.append(f"> **出生日期**: {birth.strftime('%Y-%m-%d')}")
    lines.append("")
    lines.append(f"> **死亡日期**: {death_date.strftime('%Y-%m-%d')}（最后手动执行后第 {MAX_DAYS} 天）")
    lines.append("")
    lines.append(f"> **最后存活时间**: {last_run.strftime('%Y-%m-%d %H:%M:%S')} (UTC+8)")
    lines.append("")
    lines.append(f"> **距上次执行**: {days} 天")
    lines.append("")
    lines.append("超过 7 天未检测到生命体征，按协议发布讣告。")
    lines.append("")
    lines.append(f"更新时间: {scan_time} (UTC+8)")
    return "\n".join(lines)


def run():
    import sys
    auto_mode = "--auto" in sys.argv

    scan_time = now()
    last_run = read_last_run()

    # 手动模式：先打卡更新时间戳，再判断（间隔为0，刚复活）
    # 自动模式：不更新时间戳，基于旧时间判断
    if not auto_mode:
        write_last_run(scan_time)
        # 手动打卡后，last_run 就是现在，间隔为 0
        last_run = scan_time

    if last_run is None:
        # 首次运行
        days = 0
        content = generate_alive_content(scan_time, days, scan_time.strftime('%Y-%m-%d %H:%M:%S'))
    else:
        days = (scan_time - last_run).days
        if days > MAX_DAYS:
            print(f"⚠️  距上次手动执行已过去 {days} 天，超过 {MAX_DAYS} 天阈值！")
            content = generate_obituary_content(last_run, days, scan_time.strftime('%Y-%m-%d %H:%M:%S'))
        else:
            print(f"✅ 距上次手动执行 {days} 天，在 {MAX_DAYS} 天阈值内。")
            content = generate_alive_content(last_run, days, scan_time.strftime('%Y-%m-%d %H:%M:%S'))

    with open(README_PATH, "w", encoding="utf-8") as f:
        f.write(content)

    print(f"📝 README.md 已更新: {README_PATH}")
    print(f"   上次执行: {last_run.strftime('%Y-%m-%d %H:%M:%S') if last_run else '首次'}")
    print(f"   间隔: {days} 天 | 阈值: {MAX_DAYS} 天")
    print(f"   模式: {'自动检查' if auto_mode else '手动打卡'}")
    print(f"   状态: {'讣告' if last_run and days > MAX_DAYS else '正常'}")


if __name__ == "__main__":
    run()