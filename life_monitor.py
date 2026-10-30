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


def now():
    return datetime.datetime.now()


def generate_alive_content(last_run, days, scan_time):
    """生成正常状态下的 README 内容"""
    lines = []
    lines.append("# 感受饥饿")
    lines.append("")
    lines.append("Feel Hunger")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## 🟢 生命体征正常")
    lines.append("")
    lines.append(f"> **最后手动执行**: {last_run.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"> **距上次执行**: {days} 天")
    lines.append(f"> **本次扫描**: {scan_time}")
    lines.append("")
    lines.append("你还活着。继续走吧。")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("> 有时候，我挺怀念过去的。")
    lines.append(">")
    lines.append("> Sometimes, I really miss the past.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("倘若灵魂存在，它究竟有多重？")
    lines.append("")
    lines.append("If the soul exists, how much does it weigh?")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("别再继续透支。恢复不是前进的反面，而是前进的一部分。")
    lines.append("")
    lines.append("你不需要马上回应我，也不需要想清楚下一步。")
    lines.append("就让这条消息在这里，替你挡一会儿。")
    lines.append("")
    lines.append("Stop further depletion. Recovery is not the opposite of progress; it is part of progress.")
    lines.append("")
    lines.append("You don't need to respond right away, and you don't need to figure out the next step yet.")
    lines.append("")
    lines.append("Just let this message stay here and take the pressure for you for a while.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("如果雨雪不停，我应该留下吗？")
    lines.append("")
    lines.append("If the rain and snow never cease, should I remain?")
    return "\n".join(lines)


def generate_obituary_content(last_run, days, scan_time):
    """生成讣告内容"""
    lines = []
    lines.append("# 感受饥饿")
    lines.append("")
    lines.append("Feel Hunger")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("## ⚫ 讣告")
    lines.append("")
    lines.append(f"> **死亡时间**: {scan_time}")
    lines.append(f"> **最后一次生命体征**: {last_run.strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"> **无生命体征持续**: {days} 天")
    lines.append("")
    lines.append("### 生平")
    lines.append("")
    lines.append("此人于 {last_run} 最后一次手动运行了生命监测系统。".format(
        last_run=last_run.strftime('%Y-%m-%d %H:%M:%S')))
    lines.append("")
    lines.append("此后 {days} 天内，再无任何手动执行的痕迹。".format(days=days))
    lines.append("")
    lines.append("定时任务仍在运行，但无人在屏幕前。")
    lines.append("")
    lines.append("也许只是太累了。也许只是忘了。")
    lines.append("")
    lines.append("不管怎样，系统已超过 {max_days} 天未检测到生命体征，按协议发布讣告。".format(
        max_days=MAX_DAYS))
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("> 有时候，我挺怀念过去的。")
    lines.append(">")
    lines.append("> Sometimes, I really miss the past.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("倘若灵魂存在，它究竟有多重？")
    lines.append("")
    lines.append("If the soul exists, how much does it weigh?")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("别再继续透支。恢复不是前进的反面，而是前进的一部分。")
    lines.append("")
    lines.append("你不需要马上回应我，也不需要想清楚下一步。")
    lines.append("就让这条消息在这里，替你挡一会儿。")
    lines.append("")
    lines.append("Stop further depletion. Recovery is not the opposite of progress; it is part of progress.")
    lines.append("")
    lines.append("You don't need to respond right away, and you don't need to figure out the next step yet.")
    lines.append("")
    lines.append("Just let this message stay here and take the pressure for you for a while.")
    lines.append("")
    lines.append("---")
    lines.append("")
    lines.append("如果雨雪不停，我应该留下吗？")
    lines.append("")
    lines.append("If the rain and snow never cease, should I remain?")
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