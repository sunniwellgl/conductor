#!/usr/bin/env python3
# ==============================================================================
# 车载 Linux PC 桌面总线模拟注入与 GUI 靶向截图复合验证模板脚本
# (Composite Desktop Verification Harness Template)
#
# 遵循规范:
#   1. 30-Engineering/30.01-Architecture/Automated-Bus-Injection-And-Mocking-Standard-Principles.md
#   2. 30-Engineering/30.01-Architecture/Linux-Desktop-GUI-Targeted-Capture-And-Verification-Principles.md
#   3. Conductor 规范驱动开发: 验证脚本随轨归档铁律 (Track-Scoped Verification Scripts)
#
# 使用指南:
#   1. 新建验证任务时，将本模板复制到当前轨道的 scripts/ 目录下:
#      cp <conductor_templates>/scripts/verification_harness_template.py conductor/tracks/<track_id>/scripts/verify_<feature>.py
#   2. 修改下方 [配置区] CONFIG 字典以适配具体工程环境 (Qt版本、构建路径、启动进程名等);
#   3. 在 [业务测试场景工作流] 中定制你的多状态总线发包与截图步骤;
#   4. 运行脚本即可完成: 实体拉起 -> 总线刺激 -> 靶向截图 -> 像素级物理比对 -> 进程安全回收 的全闭环验证。
# ==============================================================================

import argparse
import hashlib
import json
import os
import re
import shutil
import signal
import subprocess
import sys
import time

def resolve_qt_root() -> str:
    """多级智能嗅探 Qt SDK 根目录，消除用户名硬编码，提供优雅自愈能力"""
    # 1. 优先读取显式环境变量 (QT_ROOT 或 QTDIR)
    env_root = os.environ.get("QT_ROOT") or os.environ.get("QTDIR")
    if env_root and os.path.exists(env_root):
        return os.path.abspath(env_root)

    # 2. 尝试从当前 PATH 中的 qmake 动态反查标准安装前缀
    qmake = shutil.which("qmake")
    if qmake:
        try:
            prefix = subprocess.check_output([qmake, "-query", "QT_INSTALL_PREFIX"], text=True).strip()
            if prefix and os.path.exists(prefix):
                return prefix
        except Exception:
            pass

    # 3. 常见标准候选路径嗅探 (支持 ~ 动态展开当前登录用户家目录，杜绝硬编码特定用户名)
    candidates = [
        os.path.expanduser("~/Qt5.15.7/5.15.7/gcc_64"),
        "/opt/Qt/5.15.7/gcc_64",
        "/opt/Qt/5.15.15/gcc_64",
        "/usr/local/Qt5.15.7/gcc_64",
    ]
    for candidate in candidates:
        if os.path.exists(candidate):
            return candidate

    # 4. 若未命中有效目录，返回标准用户家目录占位路径，由预检逻辑进行可操作性拦截
    return os.path.expanduser("~/Qt5.15.7/5.15.7/gcc_64")


# ==============================================================================
# [配置区] 项目与桌面运行时环境配置 (可按项目快速定制)
# ==============================================================================
CONFIG = {
    # 1. Qt SDK 安装根目录 (优先自动探测 QT_ROOT / QTDIR / qmake / 标准路径，亦可在此显式指定)
    "QT_ROOT": resolve_qt_root(),

    # 2. 桌面端构建输出二进制目录 (包含可执行文件与相关动态库插件，如 bin/)
    "BUILD_BIN_DIR": os.path.abspath("./build/Replacement_for_Desktop_Qt_5_15_7_GCC_64bit-Debug/bin"),

    # 3. 目标启动可执行程序名称 (如 ivi_compositor, ic_adas, ic_whud, ic_dashboard 等)
    "APP_EXECUTABLE": "ivi_compositor",

    # 4. X11 靶向窗口识别特征 (窗口标题或类名的正则/子串，用于 xwininfo 准确定位 WID)
    "TARGET_WINDOW_IDENTITY": "ivi_compositor",

    # 5. 总线 Broker 连接参数 (车载桌面 MQTT 默认通常为 127.0.0.1:1883)
    "MQTT_HOST": "127.0.0.1",
    "MQTT_PORT": 1883,

    # 6. 时序保护参数 (秒)
    "BOOT_WAIT_SEC": 7.0,          # 应用冷启动、动态库装载与 SceneGraph 映射就绪等待
    "ANIMATION_EASING_SEC": 1.2,    # 卡片切换、翻页或视图缓动插值过渡等待 (防止抓取到动态残影)

    # 7. 验收截图输出目录 (默认保存在当前 track 的 images/ 目录下)
    "IMAGE_OUTPUT_DIR": os.path.abspath("./images"),
}

# ==============================================================================
# 第一部分: 环境装配与 X11 凭据智能嗅探 (Smart Display & Environment)
# ==============================================================================

def detect_x11_environment() -> dict:
    """自动嗅探并构建坚固的 X11 与 Qt 运行时环境变量字典，处理 GDM 凭据自愈"""
    env = os.environ.copy()

    # 1. 显式装配 Qt 运行时库路径与插件路径
    qt_root = CONFIG["QT_ROOT"]
    build_bin_dir = CONFIG["BUILD_BIN_DIR"]

    env["QTDIR"] = qt_root
    env["PATH"] = f"{qt_root}/bin:{env.get('PATH', '')}"
    env["LD_LIBRARY_PATH"] = f"{qt_root}/lib:{build_bin_dir}:{env.get('LD_LIBRARY_PATH', '')}"
    env["QT_PLUGIN_PATH"] = f"{qt_root}/plugins"
    env["QT_QPA_PLATFORM"] = "xcb"
    env["QML_IMPORT_PATH"] = f"{build_bin_dir}:{qt_root}/qml"
    env["QML2_IMPORT_PATH"] = f"{build_bin_dir}:{qt_root}/qml"
    env["QML_DISABLE_DISK_CACHE"] = "1"  # 禁用 QML 磁盘缓存，防止跨车型脏缓存污染

    # 2. X11 Display 探测与自愈
    if "DISPLAY" not in env or not env["DISPLAY"]:
        env["DISPLAY"] = ":0"

    # 3. GDM / Xauthority 凭据探测与自愈
    if "XAUTHORITY" not in env or not os.path.exists(env["XAUTHORITY"]):
        candidate_paths = [
            f"/run/user/{os.getuid()}/gdm/Xauthority",
            os.path.expanduser("~/.Xauthority"),
        ]
        for candidate in candidate_paths:
            if os.path.exists(candidate):
                env["XAUTHORITY"] = candidate
                break

    return env

# ==============================================================================
# 第二部分: 总线模拟注入与打桩核心接口 (Stimulus Bus Injector API)
# ==============================================================================

def publish_mqtt(topic: str, payload_dict: dict, retain: bool = False, host: str = None, port: int = None):
    """
    通用 MQTT 消息模拟发布接口 (基于系统级 mosquitto_pub 命令行工具)
    @param topic: 目标 IPC / MQTT 话题名
    @param payload_dict: 待序列化为 JSON 的消息体
    @param retain: 是否设置 MQTT Retain 标志 (冷启动前置态必须置为 True 以防时序丢包)
    """
    h = host or CONFIG["MQTT_HOST"]
    p = port or CONFIG["MQTT_PORT"]
    raw_payload = json.dumps(payload_dict)

    cmd = ["mosquitto_pub", "-h", h, "-p", str(p), "-t", topic, "-m", raw_payload]
    if retain:
        cmd.append("-r")

    try:
        subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
    except FileNotFoundError:
        sys.stderr.write("[-] 错误: 系统未检测到 mosquitto_pub 命令，请先确认安装 mosquitto-clients。\n")
        raise
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"[-] MQTT 发布失败: topic={topic}, err={e.stderr.decode().strip()}\n")
        raise

def inject_power_ready(power_status: int = 1, efsm_mode: str = "NORMAL"):
    """
    [预置场景] 整车就绪态与电源模式注入 (强制开启 Retain 持久化，解决冷启动时序竞争)
    """
    print(f"[*] 注入整车电源就绪态 (Retain=True): PowerStatus={power_status}, EFSM={efsm_mode}...")
    publish_mqtt("T1CF1/PowerStatus", {"value": int(power_status), "valid": True}, retain=True)
    publish_mqtt("Power/EFSM/mode", {"value": {"mode": efsm_mode}}, retain=True)

def inject_drive_bypass_selfcheck(gear: int = 3, speed: float = 15.0):
    """
    [预置场景] 档位与车速注入 (注入非零车速以退出开机自检，强制唤醒主视口与行车电脑)
    """
    print(f"[*] 注入行车状态打断开机自检: Gear={gear} (D档), Speed={speed} km/h...")
    publish_mqtt("DrivingInfo/Gear", {"value": int(gear), "valid": True})
    publish_mqtt("DrivingInfo/Speed", {"value": float(speed), "valid": True})

def inject_card_switch(step_count: int = 1):
    """
    [预置场景] 触发行车电脑右侧卡片步进切换 (IVICompositor/ChgSwt)，并自动遵守缓动时序保护
    """
    for i in range(step_count):
        print(f"[*] 触发卡片步进切换脉冲 [{i+1}/{step_count}]...")
        publish_mqtt("IVICompositor/ChgSwt", {"value": 1})
        time.sleep(CONFIG["ANIMATION_EASING_SEC"])

# ==============================================================================
# 第三部分: X11 显存直读靶向截图引擎 (Native Pixmap Target Capture)
# ==============================================================================

def find_target_window_id(identity_pattern: str, env: dict, min_w: int = 200, min_h: int = 150) -> str:
    """
    遵循知识库【方案 A 健壮规则】: 结合窗口 Class/Identity 标识与有效几何区间过滤，探测唯一的靶向窗口 ID
    """
    cmd = ["xwininfo", "-root", "-tree"]
    try:
        proc = subprocess.run(cmd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, check=True)
    except Exception as e:
        sys.stderr.write(f"[-] 获取 X11 窗口树失败: {e}\n")
        return None

    regex = re.compile(
        r'^\s*(0x[0-9a-fA-F]+)\s+("(?:[^"\\]|\\.)*")\s+.*?\s+(\d+)x(\d+)\+(-?\d+)\+(-?\d+)'
    )

    for line in proc.stdout.splitlines():
        match = regex.match(line)
        if not match:
            continue

        wid, title, width, height, x, y = match.groups()
        w_val, h_val = int(width), int(height)

        # 过滤极小辅助小窗口或托盘图标
        if w_val < min_w or h_val < min_h:
            continue

        # 匹配目标标识 (不区分大小写)
        if re.search(identity_pattern, title, re.IGNORECASE):
            return wid

    return None

def capture_target_window(output_path: str, env: dict, timeout_sec: float = 5.0) -> bool:
    """
    执行无侵入显存直读采样: 探测窗口 WID -> 调用 ImageMagick import 抓取 Pixmap
    """
    identity = CONFIG["TARGET_WINDOW_IDENTITY"]
    start_time = time.time()
    wid = None

    print(f"[*] 正在探测目标应用窗口: '{identity}' (超时门限: {timeout_sec}s)...")
    while time.time() - start_time < timeout_sec:
        wid = find_target_window_id(identity, env)
        if wid:
            break
        time.sleep(0.5)

    if not wid:
        sys.stderr.write(f"[-] 截图超时: 未在当前 X11 树中检测到匹配 '{identity}' 的有效 GUI 窗口。\n")
        return False

    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    import_cmd = ["import", "-window", wid, output_path]

    try:
        subprocess.run(import_cmd, env=env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
        print(f"✅ 靶向截图生成成功! 窗口 ID: {wid} -> 落盘路径: {output_path}")
        return True
    except subprocess.CalledProcessError as e:
        sys.stderr.write(f"[-] import 抓图失败: {e.stderr.decode().strip()}\n")
        return False

# ==============================================================================
# 第四部分: 双轨图像判定与像素差分断言 (Oracle & Diff Assert)
# ==============================================================================

def verify_image_difference(img_path_a: str, img_path_b: str, expect_difference: bool = True) -> bool:
    """
    计算两张截图的 MD5 哈希与像素级差分，建立客观物理验收断言
    """
    if not os.path.exists(img_path_a) or not os.path.exists(img_path_b):
        sys.stderr.write("[-] 错误: 参与对比的图像文件不存在。\n")
        return False

    def get_md5(path):
        with open(path, "rb") as f:
            return hashlib.md5(f.read()).hexdigest()

    md5_a = get_md5(img_path_a)
    md5_b = get_md5(img_path_b)

    print(f"[*] 图像物理验真分析:")
    print(f"    - 图像 A ({os.path.basename(img_path_a)}) MD5: {md5_a}")
    print(f"    - 图像 B ({os.path.basename(img_path_b)}) MD5: {md5_b}")

    is_different = (md5_a != md5_b)

    # 尝试进行深入的 Pillow 像素级差分诊断 (若环境已安装 Pillow)
    try:
        from PIL import Image, ImageChops
        import numpy as np

        im1 = Image.open(img_path_a)
        im2 = Image.open(img_path_b)
        diff = ImageChops.difference(im1, im2)
        bbox = diff.getbbox()
        diff_count = np.sum(np.array(diff) > 0)

        if bbox:
            print(f"    - 差异包围盒 Bounding Box: {bbox}")
            print(f"    - 发生重绘翻转的像素总数: {diff_count} px")
    except ImportError:
        pass  # 环境未安装 Pillow 时以 MD5 为基准

    if expect_difference:
        if is_different:
            print("🎉 【物理断言成立】两张截图存在清晰物理差异，界面状态成功刷新响应！")
            return True
        else:
            sys.stderr.write("❌ 【物理断言失败】两张截图 MD5 完全一致，界面未能响应刺激信号！\n")
            return False
    else:
        if not is_different:
            print("🎉 【物理断言成立】两张截图完全一致，符合静止无副作用预期。")
            return True
        else:
            sys.stderr.write("❌ 【物理断言失败】两张截图存在非预期差异，发生了画面漂移或误刷！\n")
            return False

# ==============================================================================
# 第五部分: 业务特化验证工作流 (Custom Stimulus & Verification Scenario)
# [开发者/Agent 核心定制区域: 依据具体功能与缺陷替换此函数内部业务逻辑]
# ==============================================================================

def execute_verification_scenario(env: dict) -> bool:
    """
    业务测试用例主执行体: 定制具体的总线刺激顺序与截图阶段
    """
    img_dir = CONFIG["IMAGE_OUTPUT_DIR"]
    os.makedirs(img_dir, exist_ok=True)

    img_state_1 = os.path.join(img_dir, "verification_state_1.png")
    img_state_2 = os.path.join(img_dir, "verification_state_2.png")

    print("\n----------------------------------------------------------------------")
    print("[用例执行阶段 1] 注入基础工况与基准状态刺激...")
    print("----------------------------------------------------------------------")

    # 1. 注入整车就绪与车速跳过自检
    inject_power_ready(power_status=1, efsm_mode="NORMAL")
    inject_drive_bypass_selfcheck(gear=3, speed=20.0)
    time.sleep(0.5)

    # 2. TODO: [定制业务刺激 A] 在此发布你的第一个工况信号 (例如: 胎压正常、空调开、模式1等)
    # publish_mqtt("Your/Custom/Topic", {"value": 0, "valid": True})
    time.sleep(CONFIG["ANIMATION_EASING_SEC"])

    # 3. 截取状态 1 效果图
    print(f"[*] 截取状态 1 基准效果图 -> {img_state_1}")
    if not capture_target_window(img_state_1, env):
        return False

    print("\n----------------------------------------------------------------------")
    print("[用例执行阶段 2] 注入状态变更信号与动态响应刺激...")
    print("----------------------------------------------------------------------")

    # 4. TODO: [定制业务刺激 B] 在此发布你的第二个变更信号 (例如: 切换温度单位、触发告警、切歌等)
    # publish_mqtt("Your/Custom/Topic", {"value": 1, "valid": True})
    time.sleep(CONFIG["ANIMATION_EASING_SEC"])

    # 5. 截取状态 2 效果图
    print(f"[*] 截取状态 2 变更效果图 -> {img_state_2}")
    if not capture_target_window(img_state_2, env):
        return False

    print("\n----------------------------------------------------------------------")
    print("[用例执行阶段 3] 物理像素验真与断言比对...")
    print("----------------------------------------------------------------------")

    # 6. 比对状态 1 与状态 2 是否存在实质性渲染刷新
    return verify_image_difference(img_state_1, img_state_2, expect_difference=True)

# ==============================================================================
# 第六部分: 主入口与生命周期安全守护 (Main Entry & Lifecycle Harness)
# ==============================================================================

def main():
    parser = argparse.ArgumentParser(description="车载 Linux PC 桌面总线模拟注入与 GUI 靶向截图复合验证模板工具")
    parser.add_argument("--qt-root", help="覆盖默认 Qt SDK 根目录路径")
    parser.add_argument("--bin-dir", help="覆盖默认构建二进制目录路径")
    parser.add_argument("--app", help="覆盖目标启动可执行程序名称")
    parser.add_argument("--output-dir", help="覆盖验收截图保存输出目录")
    args = parser.parse_args()

    if args.qt_root: CONFIG["QT_ROOT"] = os.path.abspath(args.qt_root)
    if args.bin_dir: CONFIG["BUILD_BIN_DIR"] = os.path.abspath(args.bin_dir)
    if args.app:
        CONFIG["APP_EXECUTABLE"] = args.app
        CONFIG["TARGET_WINDOW_IDENTITY"] = args.app
    if args.output_dir: CONFIG["IMAGE_OUTPUT_DIR"] = os.path.abspath(args.output_dir)

    # 预检 Qt SDK 根路径
    qt_root = CONFIG["QT_ROOT"]
    if not os.path.exists(qt_root):
        sys.stderr.write(f"[-] 严重错误: 未检测到有效的 Qt SDK 根目录: {qt_root}\n")
        sys.stderr.write("[-] 提示: 请通过以下任一方式配置后再行运行:\n")
        sys.stderr.write("    1. 终端执行: export QT_ROOT=/path/to/Qt/<version>/gcc_64\n")
        sys.stderr.write("    2. 直接修改当前验证脚本顶部的 CONFIG['QT_ROOT']\n")
        sys.stderr.write("    3. 运行脚本时指定参数: python3 verify_xxx.py --qt-root /path/to/Qt\n\n")
        sys.exit(1)

    # 1. 嗅探并装配运行时环境
    env = detect_x11_environment()
    app_bin = os.path.join(CONFIG["BUILD_BIN_DIR"], CONFIG["APP_EXECUTABLE"])

    if not os.path.exists(app_bin):
        sys.stderr.write(f"[-] 严重错误: 未在构建目录下找到可执行程序: {app_bin}\n")
        sys.stderr.write("[-] 提示: 请先确认工程桌面端是否已完成编译构建。\n")
        sys.exit(1)

    print("======================================================================")
    print("[HARNESS] 启动桌面自动化复合验证流水线...")
    print(f"[HARNESS] 目标执行程序 : {app_bin}")
    print(f"[HARNESS] Qt SDK 根路径 : {CONFIG['QT_ROOT']}")
    print(f"[HARNESS] 显示服务配置 : DISPLAY={env['DISPLAY']}, XAUTH={env.get('XAUTHORITY', 'None')}")
    print(f"[HARNESS] 截图归档目录 : {CONFIG['IMAGE_OUTPUT_DIR']}")
    print("======================================================================")

    # 2. 安全启动目标应用子进程
    proc = subprocess.Popen(
        [app_bin],
        cwd=CONFIG["BUILD_BIN_DIR"],
        env=env,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    success = False
    try:
        print(f"[*] 等待应用就绪 ({CONFIG['BOOT_WAIT_SEC']}s)...")
        time.sleep(CONFIG["BOOT_WAIT_SEC"])

        # 3. 执行业务特化验证逻辑
        success = execute_verification_scenario(env)

    except KeyboardInterrupt:
        print("\n[!] 收到用户中断信号，准备安全回收...")
    except Exception as e:
        sys.stderr.write(f"\n[-] 验证流水线异常中断: {e}\n")
    finally:
        # 4. 严谨守护：优雅终止与强杀兜底，杜绝僵尸进程常驻
        print("[*] 正在安全回收目标应用子进程...")
        proc.terminate()
        try:
            proc.wait(timeout=2.5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("[*] 子进程已彻底安全退出。")

    if success:
        print("\n✅ 【整轨验收通过】端到端模拟发包、靶向抓图与物理断言全链路验证成功闭环！")
        sys.exit(0)
    else:
        sys.stderr.write("\n❌ 【整轨验收未通过】请检查总线通信协议或 UI 渲染刷新逻辑。\n")
        sys.exit(1)

if __name__ == "__main__":
    main()
