# -*- coding: utf-8 -*-
"""
生成 README 配图（可复现）：
  hero.png          裁剪图像生成结果的水印
  architecture.png  系统架构（App / 通信 / 固件 / 硬件）
  comm-flow.png     控制 / 图传 / OTA 三条链路
  features.png      功能总览
依赖：Pillow；字体用 Windows 自带 微软雅黑 / Consolas。
"""
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
IMG = os.path.join(HERE, "images")
S = 2  # 超采样倍数

# ---------- 调色板 ----------
BG1 = (7, 11, 22)
BG2 = (11, 18, 36)
PANEL = (14, 22, 42)
PANEL2 = (18, 28, 52)
LINE = (38, 56, 92)
TEXT = (234, 242, 251)
DIM = (150, 164, 186)
FAINT = (96, 112, 138)
CYAN = (63, 169, 255)
CYANC = (31, 230, 255)
PURPLE = (124, 92, 255)
RED = (255, 46, 77)
GREEN = (54, 226, 122)
AMBER = (244, 200, 74)
PINK = (255, 111, 181)

FD = "C:/Windows/Fonts/"


def font(size, bold=False, mono=False):
    if mono:
        return ImageFont.truetype(FD + "consola.ttf", int(size * S))
    return ImageFont.truetype(FD + ("msyhbd.ttc" if bold else "msyh.ttc"), int(size * S))


def sx(v):
    return int(round(v * S))


def new_canvas(w, h):
    img = Image.new("RGB", (sx(w), sx(h)), BG1)
    d = ImageDraw.Draw(img, "RGBA")
    # 竖向渐变
    for y in range(sx(h)):
        t = y / max(1, sx(h) - 1)
        r = int(BG1[0] + (BG2[0] - BG1[0]) * t)
        g = int(BG1[1] + (BG2[1] - BG1[1]) * t)
        b = int(BG1[2] + (BG2[2] - BG1[2]) * t)
        d.line([(0, y), (sx(w), y)], fill=(r, g, b, 255))
    # 网格
    for x in range(0, sx(w), sx(40)):
        d.line([(x, 0), (x, sx(h))], fill=(*LINE, 18))
    for y in range(0, sx(h), sx(40)):
        d.line([(0, y), (sx(w), y)], fill=(*LINE, 18))
    return img, d


def panel(d, x, y, w, h, fill=PANEL, border=LINE, r=14, glow=None, gw=3):
    x0, y0, x1, y1 = sx(x), sx(y), sx(x + w), sx(y + h)
    if glow:
        for i in range(gw, 0, -1):
            a = int(26 * (i / gw))
            d.rounded_rectangle([x0 - i, y0 - i, x1 + i, y1 + i], radius=sx(r) + i,
                                outline=(*glow, a), width=1)
    d.rounded_rectangle([x0, y0, x1, y1], radius=sx(r), fill=(*fill, 255),
                        outline=(*border, 255), width=max(1, sx(1)))


def chip(d, x, y, w, h, title, sub, accent, ts=15, ss=11.5):
    panel(d, x, y, w, h, fill=PANEL2, border=LINE, r=9)
    d.rounded_rectangle([sx(x), sx(y), sx(x + 4), sx(y + h)], radius=sx(2), fill=(*accent, 255))
    d.text((sx(x + 14), sx(y + 9)), title, font=font(ts, True), fill=TEXT)
    d.text((sx(x + 14), sx(y + 9 + ts + 5)), sub, font=font(ss), fill=DIM)


def text(d, x, y, s, size, color=TEXT, bold=False, mono=False, anchor="la"):
    d.text((sx(x), sx(y)), s, font=font(size, bold, mono), fill=color, anchor=anchor)


def arrow(d, x0, y0, x1, y1, color=CYAN, w=2.0, head=9):
    d.line([(sx(x0), sx(y0)), (sx(x1), sx(y1))], fill=(*color, 235), width=max(1, sx(w)))
    import math
    ang = math.atan2(y1 - y0, x1 - x0)
    hx, hy = x1, y1
    p1 = (hx - head * math.cos(ang - 0.42), hy - head * math.sin(ang - 0.42))
    p2 = (hx - head * math.cos(ang + 0.42), hy - head * math.sin(ang + 0.42))
    d.polygon([(sx(hx), sx(hy)), (sx(p1[0]), sx(p1[1])), (sx(p2[0]), sx(p2[1]))], fill=(*color, 235))


def title_block(d, t, sub):
    text(d, 46, 30, t, 40, TEXT, True)
    text(d, 48, 84, sub, 18, DIM)
    d.rounded_rectangle([sx(46), sx(120), sx(146), sx(124)], radius=sx(2), fill=(*CYANC, 255))


def wrap(d, s, size, maxw, bold=False, mono=False):
    if not s:
        return [""]
    f = font(size, bold, mono)
    lines, cur = [], ""
    for ch in s:
        if d.textlength(cur + ch, font=f) <= sx(maxw):
            cur += ch
        else:
            lines.append(cur)
            cur = ch
    if cur:
        lines.append(cur)
    return lines


# ============================================================ ARCHITECTURE
def architecture():
    W, H = 1600, 1000
    img, d = new_canvas(W, H)
    title_block(d, "MOCHAN · 系统架构",
                "ESP32-S3 机器人 与 Android 遥控 App · 两条 WebSocket + HTTP 控制面 · 实时图传 / 遥控 / OTA / 配网")

    # ---- App ----
    panel(d, 40, 138, 1520, 196, glow=PURPLE)
    text(d, 62, 152, "ANDROID APP", 22, PURPLE, True)
    text(d, 232, 158, "com.mochan.robot · 零第三方 UI/网络依赖 · arm64-v8a", 13, DIM)
    app_mods = [
        ("遥控台 UI", "全代码构建 · 赛博深色", CYAN),
        ("WebSocket 客户端", "手写 RFC6455 · 文本/二进制", GREEN),
        ("HTTP 客户端", "/status 每 2s 轮询", AMBER),
        ("图传渲染 CamSurface", "RGB565 · letterbox · 只留最新帧", CYANC),
        ("AI 检测 Detector", "ONNX Runtime · YOLOv8n", PINK),
        ("ECG 遥测 EcgView", "随机器人状态心跳", RED),
        ("画质/滤镜/OTA 面板", "深色自定义 Dialog", PURPLE),
        ("WiFi STA 配网", "扫描 · 密码 · 自动切 IP", CYAN),
    ]
    cw = (1520 - 40 - 3 * 16) / 4
    for i, (t, s, c) in enumerate(app_mods):
        row, col = divmod(i, 4)
        chip(d, 60 + col * (cw + 16), 186 + row * 68, cw, 56, t, s, c)

    # ---- 通信 ----
    panel(d, 40, 354, 1520, 286, glow=CYANC)
    text(d, 62, 368, "通信与控制协议", 22, CYANC, True)
    text(d, 300, 374, "2.4GHz Wi-Fi · AP 热点 + STA 共存", 13, DIM)
    comm = [
        ("WS · 控制  /ws_ctrl", "上行：f/b/l/r/s · spd0..2 · mood0..3 · dance · follow_on/off · crazy_on/off · ai:tx", GREEN),
        ("WS · 图传  /ws_cam", "机器人 → 手机二进制 JPEG 帧；收一帧回 a(ACK) 做背压，ACK RTT 回报 /status", CYANC),
        ("HTTP · 控制面", "/status · /cam_cfg · /cam_shot · /update(MD5) · /wifi_scan|save|status|ap · /sync_time", AMBER),
        ("连接模型", "AP 热点 MOCHAN/12345678 → 192.168.4.1（永不掉）；STA 连家用 WiFi → 192.168.107.57", PURPLE),
    ]
    ccw = (1520 - 40 - 20) / 2
    for i, (t, s, c) in enumerate(comm):
        row, col = divmod(i, 2)
        x = 60 + col * (ccw + 20)
        y = 402 + row * 116
        panel(d, x, y, ccw, 104, fill=PANEL2, border=LINE, r=10)
        d.rounded_rectangle([sx(x), sx(y), sx(x + 4), sx(y + 104)], radius=sx(2), fill=(*c, 255))
        text(d, x + 16, y + 12, t, 17, c, True)
        for j, ln in enumerate(wrap(d, s, 12.5, ccw - 34)):
            text(d, x + 16, y + 44 + j * 20, ln, 12.5, DIM)

    # ---- 固件 ----
    panel(d, 40, 660, 1520, 210, glow=GREEN)
    text(d, 62, 674, "ESP32-S3 固件", 22, GREEN, True)
    text(d, 208, 680, "ESP-IDF 5.5 · esp_http_server · esp32-camera · u8g2", 13, DIM)
    fw_mods = [
        ("HTTP + 2×WebSocket", "34 条路由 · /ws_ctrl · /ws_cam", CYAN),
        ("电机/动画/跳舞", "motor.cpp · 统一入口 motorWifi()", AMBER),
        ("疯狂模式状态机", "RAGE ↔ FATIGUE 自动交替", PINK),
        ("摄像头 + 推流", "OV2640 DVP · cameraTask · wsPushTask", CYANC),
        ("OLED + 眼睛 + HUD", "SSD1306 · RoboEyes · 赛博休眠屏", PURPLE),
        ("拟人行为层", "behavior.cpp · 心情/注意力/意图", GREEN),
        ("OTA 升级", "MD5 校验 · 启动确认/失败回滚", RED),
        ("WiFi AP+STA + 对时", "SNTP · 客户端 /sync_time 兜底", CYAN),
    ]
    cw2 = (1520 - 40 - 3 * 16) / 4
    for i, (t, s, c) in enumerate(fw_mods):
        row, col = divmod(i, 4)
        chip(d, 60 + col * (cw2 + 16), 706 + row * 68, cw2, 56, t, s, c)

    # ---- 硬件 ----
    panel(d, 40, 890, 1520, 78, fill=(10, 16, 30), border=LINE)
    text(d, 62, 908, "硬件", 18, TEXT, True)
    hw = ["OV2640 摄像头", "双 H 桥 · 4 电机", "SSD1306 128×64 OLED",
          "ESP32-S3 · 16MB Flash / 8MB PSRAM", "2.4GHz Wi-Fi"]
    hx = 150
    for i, h in enumerate(hw):
        d.ellipse([sx(hx), sx(926), sx(hx + 7), sx(933)], fill=(*CYANC, 255))
        text(d, hx + 14, 916, h, 14, DIM)
        hx += 24 + d.textlength(h, font=font(14)) / S

    img = img.resize((W * 1, H * 1), Image.LANCZOS)  # 已按 S 绘制, 缩回逻辑尺寸
    img.save(os.path.join(IMG, "architecture.png"))
    print("architecture.png", img.size)


# ============================================================ COMM FLOW
def comm_flow():
    W, H = 1600, 1000
    img, d = new_canvas(W, H)
    title_block(d, "机器人与 App 如何互相控制",
                "三条链路：控制（文本指令）· 图传（二进制 JPEG + ACK 背压）· OTA（multipart 上传 + 进度帧）")

    def lane(y, h, name, accent):
        panel(d, 40, y, 1520, h, glow=accent)
        d.rounded_rectangle([sx(40), sx(y), sx(40 + 6), sx(y + h)], radius=sx(3), fill=(*accent, 255))
        text(d, 64, y + 14, name, 20, accent, True)

    def step(x, y, w, h, t, s, accent):
        panel(d, x, y, w, h, fill=PANEL2, border=LINE, r=9)
        for j, ln in enumerate(wrap(d, t, 15, w - 22, bold=True)):
            text(d, x + 12, y + 12 + j * 20, ln, 15, TEXT, True)
        sy = y + 12 + 20 * len(wrap(d, t, 15, w - 22, bold=True)) + 4
        for j, ln in enumerate(wrap(d, s, 11.5, w - 22)):
            text(d, x + 12, sy + j * 17, ln, 11.5, DIM)

    # ---- 控制链路 ----
    y = 132
    lane(y, 208, "① 控制链路  Control", GREEN)
    steps = [
        ("手机按钮", "方向 / 速度 / 表情 / 动作", CYAN),
        ("/ws_ctrl 文本", "f·b·l·r·s / spd0..2 / mood0..3", GREEN),
        ("decodeMotorCmd", "固件解析指令", AMBER),
        ("motorWifi()", "统一入口：限速/互斥/冻结", PURPLE),
        ("电机 PWM", "LEDC 20kHz · 四轮差速", RED),
    ]
    n = len(steps); gap = 22; bw = (1520 - 40 - (n - 1) * gap) / n; by = y + 66; bh = 96
    for i, (t, s, c) in enumerate(steps):
        x = 60 + i * (bw + gap)
        step(x, by, bw, bh, t, s, c)
        if i < n - 1:
            arrow(d, x + bw + 3, by + bh / 2, x + bw + gap - 3, by + bh / 2, color=c)
    text(d, 60, y + 172, "松开 → 发 s 停车；手动 200ms 超时兜底；最后控制端断开自动停车", 12, FAINT)

    # ---- 图传链路 ----
    y = 356
    lane(y, 240, "② 图传链路  Video", CYANC)
    steps = [
        ("OV2640 采集", "DVP 并口 · JPEG", CYAN),
        ("cameraTask", "取帧 / 丢坏帧 / 控帧率", AMBER),
        ("wsPushTask", "背压发送 · 保留最新帧", PURPLE),
        ("/ws_cam 二进制", "JPEG 帧下发", CYANC),
        ("CamSurface", "RGB565 解码 · letterbox", GREEN),
    ]
    n = len(steps); bw = (1520 - 40 - (n - 1) * gap) / n; by = y + 66; bh = 96
    xs = []
    for i, (t, s, c) in enumerate(steps):
        x = 60 + i * (bw + gap)
        xs.append(x)
        step(x, by, bw, bh, t, s, c)
        if i < n - 1:
            arrow(d, x + bw + 2, by + bh / 2, x + bw + gap - 2, by + bh / 2, color=c)
    # ACK 回程（虚线）
    ax0 = xs[-1] + bw / 2
    ax1 = xs[2] + bw / 2
    yy = by + bh + 30
    for xx in range(sx(ax1), sx(ax0), sx(14)):
        d.line([(xx, sx(yy)), (min(xx + sx(7), sx(ax0)), sx(yy))], fill=(*CYANC, 200), width=sx(1.5))
    arrow(d, ax0, yy, ax1, yy, color=CYANC)
    text(d, ax1 + 10, yy - 18, "回 a (ACK)：每收一帧回一个 a，固件据 ACK RTT 做背压（窗口 520ms）", 12, CYANC)
    text(d, 60, y + 208, "只保留最新帧：渲染跟不上就丢帧，弱网表现为“掉帧”而不是“越看越延迟”", 12, FAINT)

    # ---- OTA 链路 ----
    y = 620
    h = 300
    lane(y, h, "③ OTA 升级链路  Firmware Update", RED)
    steps = [
        ("选择 .bin", "系统文件选择器 SAF", CYAN),
        ("POST /update", "multipart + X-Firmware-MD5", AMBER),
        ("esp_ota 写入", "写 app1 分区 (3MB)", PURPLE),
        ("校验 + 切分区", "MD5 / 镜像首字节 0xE9", GREEN),
        ("重启 + 回滚", "启动确认失败则回旧分区", RED),
    ]
    n = len(steps); bw = (1520 - 40 - (n - 1) * gap) / n; by = y + 62; bh = 104
    xs = []
    for i, (t, s, c) in enumerate(steps):
        x = 60 + i * (bw + gap)
        xs.append(x)
        step(x, by, bw, bh, t, s, c)
        if i < n - 1:
            arrow(d, x + bw + 2, by + bh / 2, x + bw + gap - 2, by + bh / 2, color=c)
    # 进度帧回程
    ax0 = xs[2] + bw / 2
    ax1 = xs[1] + bw / 2
    yy = by + bh + 34
    for xx in range(sx(ax1), sx(ax0), sx(14)):
        d.line([(xx, sx(yy)), (min(xx + sx(7), sx(ax0)), sx(yy))], fill=(*RED, 200), width=sx(1.5))
    arrow(d, ax0, yy, ax1, yy, color=RED)
    text(d, ax1 + 10, yy - 18, "进度帧 ota:<pct>:<stage>:<kb>：固件经 /ws_ctrl 主动推，App 进度条与机器人屏幕同源", 12, RED)
    text(d, 60, y + 268, "防变砖：首字节非 0xE9 或 <64KB 直接拒绝；应用层 NVS 记录 pending/tries，启动未确认则自动回滚", 12, FAINT)

    img = img.resize((W, H), Image.LANCZOS)
    img.save(os.path.join(IMG, "comm-flow.png"))
    print("comm-flow.png", img.size)


# ============================================================ FEATURES
def features():
    W, H = 1600, 1000
    img, d = new_canvas(W, H)
    title_block(d, "功能总览", "一条 WebSocket 控制 + 一条 WebSocket 图传，覆盖“看 / 控 / 拍 / 改 / 升”全链路")

    feats = [
        ("实时图传", "OV2640 JPEG 经 /ws_cam 下发，只保留最新帧，弱网掉帧不积压", CYANC),
        ("遥控驾驶", "多指方向键 / 差速转向 / 三档速度 / 急停，200ms 超时兜底", GREEN),
        ("画质与拍照", "/cam_cfg 6 档分辨率 · /cam_shot 运行时抓 UXGA 大图", AMBER),
        ("画面滤镜", "ColorMatrix 8 档预设 + 照片色标定 + 四项实时微调", PINK),
        ("疯狂模式", "RAGE 暴走 ↔ FATIGUE 喘息自动交替，多层安全退出", RED),
        ("拟人行为", "心情 / 注意力 / 动作意图：先看再动、会累会发呆", PURPLE),
        ("跳舞", "三套编排 + 节奏曲线 + 表情眼神联动", GREEN),
        ("AI 跟随", "YOLOv8n 检测 + ai:tx 闭环，只左右对准人", CYAN),
        ("OTA 升级", "MD5 校验 + 启动确认/失败回滚 + 进度帧", RED),
        ("WiFi STA 配网", "AP+STA 共存，热点永不掉；连家用 WiFi 后看画面", AMBER),
        ("时钟同步", "/sync_time 推送 + SNTP 兜底，休眠屏显示正确时间", PURPLE),
        ("状态遥测", "红色心电波形随机器人整体状态跳动（ECG）", CYANC),
    ]
    cols, rows = 4, 3
    gx, gy = 20, 22
    tw = (1520 - (cols - 1) * gx) / cols
    th = (800 - (rows - 1) * gy) / rows
    for i, (t, s, c) in enumerate(feats):
        r, col = divmod(i, cols)
        x = 40 + col * (tw + gx)
        y = 150 + r * (th + gy)
        panel(d, x, y, tw, th, fill=PANEL2, border=LINE, r=12)
        d.rounded_rectangle([sx(x), sx(y), sx(x + tw), sx(y + 5)], radius=sx(3), fill=(*c, 255))
        # 序号圆
        cx, cy, rr = x + 30, y + 40, 17
        d.ellipse([sx(cx - rr), sx(cy - rr), sx(cx + rr), sx(cy + rr)], outline=(*c, 255), width=sx(2))
        text(d, cx, cy, f"{i+1:02d}", 14, c, True, anchor="mm")
        text(d, x + 58, y + 22, t, 22, TEXT, True)
        for j, ln in enumerate(wrap(d, s, 13.5, tw - 30)):
            text(d, x + 22, y + 78 + j * 21, ln, 13.5, DIM)

    img = img.resize((W, H), Image.LANCZOS)
    img.save(os.path.join(IMG, "features.png"))
    print("features.png", img.size)


# ============================================================ HERO
def hero():
    src = None
    for f in os.listdir(IMG):
        if f.startswith("Ultra_detailed") or f.startswith("hero"):
            if f.lower().endswith(".png") and "hero" not in f:
                src = os.path.join(IMG, f)
    if src:
        im = Image.open(src).convert("RGB")
        w, h = im.size
        im = im.crop((0, 0, w, h - int(h * 0.06)))  # 裁掉底部水印
        im.save(os.path.join(IMG, "hero.png"))
        print("hero.png", im.size, "from", os.path.basename(src))


if __name__ == "__main__":
    os.makedirs(IMG, exist_ok=True)
    architecture()
    comm_flow()
    features()
    hero()
