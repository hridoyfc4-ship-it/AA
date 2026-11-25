import time, json, requests, os, urllib3, tempfile
from Crypto.Cipher import AES
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

CDN = "https://cdn.jsdelivr.net/gh/ShahGCreator/icon@main/PNG"
K = b'Yg&tc%DEuh6%Zc^8'
V = b'6oyZDr22E3ychjM%'

def find_font():
    # Termux, Android এবং Linux hosting—সব জায়গার সাধারণ font path পরীক্ষা করে।
    candidates = [
        os.path.join(os.path.dirname(os.path.abspath(__file__)), "arial_unicode_bold.otf"),
        "/system/fonts/Roboto-Bold.ttf",
        "/system/fonts/DroidSans-Bold.ttf",
        "/system/fonts/NotoSans-Bold.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
        "/usr/share/fonts/truetype/liberation2/LiberationSans-Bold.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Bold.ttf",
    ]
    for path in candidates:
        if os.path.isfile(path):
            return path

    # Hosting-এ font না থাকলে temporary directory-তে Noto Sans নামিয়ে নেয়।
    font_path = os.path.join(tempfile.gettempdir(), "hridoy_noto_sans.ttf")
    if not os.path.isfile(font_path):
        try:
            url = "https://raw.githubusercontent.com/google/fonts/main/ofl/notosans/NotoSans%5Bwdth,wght%5D.ttf"
            response = requests.get(url, timeout=20)
            response.raise_for_status()
            if len(response.content) < 10000:
                raise ValueError("Downloaded font file is invalid")
            with open(font_path, "wb") as font_file:
                font_file.write(response.content)
        except Exception:
            return None
    return font_path

FONT = find_font()

def vr(n):
    d = []
    while True:
        b = n & 0x7F
        n >>= 7
        if n: b |= 0x80
        d.append(b)
        if not n: break
    return bytes(d)

def pb(F):
    p = bytearray()
    for f, v in F.items():
        if isinstance(v, bool):
            p.extend(vr((f << 3) | 0)); p.extend(vr(1 if v else 0))
        elif isinstance(v, int):
            p.extend(vr((f << 3) | 0)); p.extend(vr(v))
        elif isinstance(v, str):
            d = v.encode(); p.extend(vr((f << 3) | 2)); p.extend(vr(len(d))); p.extend(d)
        elif isinstance(v, (bytes, bytearray)):
            d = bytes(v); p.extend(vr((f << 3) | 2)); p.extend(vr(len(d))); p.extend(d)
    return bytes(p)

def rv(data, pos):
    r = 0; s = 0
    while pos < len(data):
        b = data[pos]; pos += 1
        r |= (b & 0x7F) << s
        if not (b & 0x80): break
        s += 7
    return r, pos

def parse(data):
    f = {}; pos = 0; n = len(data)
    while pos < n:
        try: k, pos = rv(data, pos)
        except: break
        fn = k >> 3; wt = k & 7
        try:
            if wt == 0: v, pos = rv(data, pos)
            elif wt == 2: ln, pos = rv(data, pos); v = data[pos:pos+ln]; pos += ln
            elif wt == 5: v = data[pos:pos+4]; pos += 4
            elif wt == 1: v = data[pos:pos+8]; pos += 8
            else: break
        except: break
        f.setdefault(fn, []).append(v)
    return f

def enc(k, i, p):
    pl = 16 - (len(p) % 16)
    return AES.new(k, AES.MODE_CBC, i).encrypt(p + bytes([pl]*pl))

def strip_prefix(b):
    if len(b) <= 64: return b
    try:
        if 8 in parse(b): return b
    except: pass
    try:
        if 8 in parse(b[64:]): return b[64:]
    except: pass
    return b[64:]

def oauth(uid, pwd):
    H = {"User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)", "Content-Type": "application/x-www-form-urlencoded"}
    try:
        R = requests.post("https://100067.connect.garena.com/oauth/guest/token/grant", headers=H, data={"uid": uid, "password": pwd, "response_type": "token", "client_type": "2", "client_id": "100067"}, verify=False, timeout=15)
    except: return None
    if R.status_code != 200: return None
    J = R.json()
    if "access_token" not in J or "open_id" not in J: return None
    return {"access_token": J["access_token"], "open_id": J["open_id"]}

def major_login(at, oi):
    P = {}
    P[3] = time.strftime("%Y-%m-%d %H:%M:%S"); P[4] = "free fire"; P[5] = 1; P[7] = "1.132.9"
    P[8] = "Android OS 14 / API-34 (UP1A.231005.007/V816.0.15.0.UNQMIXM)"
    P[9] = "Handheld"; P[10] = "Grameenphone"; P[11] = "CarrierDataNetwork"
    P[12] = 1666; P[13] = 750; P[14] = "352"; P[15] = "ARM64 FP ASIMD AES | 2400 | 8"
    P[16] = 5563; P[17] = "Mali-G57 MC2"
    P[18] = "OpenGL ES 3.2 v1.r32p1-01eac0.0a0b917d9265b4c01be9925306306139"
    P[19] = "Google|9cc73f7a-91f6-40f6-87ec-5b67e597eb8c"; P[20] = "59.152.5.188"
    P[21] = "en"; P[22] = oi; P[23] = "8"; P[24] = "Handheld"
    P[25] = "Xiaomi 2312DRAABI"; P[26] = "BD"; P[29] = at; P[30] = 1
    P[41] = "Grameenphone"; P[42] = "Cellular"
    P[57] = "7428b253defc164018c604a1ebbfebdf"
    P[60] = 109685; P[61] = 58294; P[62] = 797; P[63] = 18000; P[64] = 58818; P[65] = 109685
    P[66] = 58818; P[67] = 109685; P[73] = 2
    P[74] = "/data/app/~~cqQgpdMykLQEM3odipXatw==/com.dts.freefireth-G6e5yOt1dtuXG5Ambhj18g==/lib/arm64"
    P[76] = 1
    P[77] = "b8e0cd5e295eee42f5860d3c86e483dd|/data/app/~~cqQgpdMykLQEM3odipXatw==/com.dts.freefireth-G6e5yOt1dtuXG5Ambhj18g==/base.apk"
    P[78] = 3; P[79] = 2; P[81] = "64"; P[83] = "2019121229"; P[85] = 3; P[86] = "OpenGLES2"
    P[87] = 4095; P[88] = 8
    P[89] = b"FwQVTgUPX1UaUllDDwcWCRBpWAUOUgsvA1snWlBaO1kFYg=="
    P[90] = "Dhaka"; P[91] = "C"; P[92] = 8043; P[93] = "android"
    P[94] = "KqsHT4XbSZhqerDNUhjbS3DxG/4+I62zQU2tZFJN91kBUICAlZ5yujshLKvjlk/KiShfKfis8EeB1PMhFHIodWPncZC4fCHYF3TcTwNj95aWY/S3"
    P[95] = 111207; P[96] = '{"cur_rate":[60,90,120],"support_etc2":false}'
    P[97] = 1; P[98] = 1; P[99] = "4"; P[100] = "4"; P[102] = "GQ]        e"; P[103] = 1
    P[104] = 45174; P[105] = 1
    P[106] = "https://dl-bs.ggpolarbear.com/live/ABHotUpdates/|https://core-bs.ggpolarbear.com/live/ABHotUpdates/|a4332cb1c1a84e51dd77441e4856ed5a"
    P[107] = "1.9393e7b8e53e8aeb"
    H = {"User-Agent": "UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)", "Accept": "*/*", "Accept-Encoding": "deflate, gzip", "X-GA-SV": str(int(time.time())), "Authorization": "Bearer ", "X-GA": "v1 1", "ReleaseVersion": "OB55", "Content-Type": "application/x-www-form-urlencoded", "X-Unity-Version": "2018.4.12f1"}
    try:
        R = requests.post("https://loginbp.ppmainecoonghj.com/MajorLogin", headers=H, data=enc(K, V, pb(P)), verify=False, timeout=20)
    except: return None
    if R.status_code not in (200, 201) or not R.content: return None
    body = R.content
    f = parse(body)
    j = f.get(8, [None])[0]
    s = f.get(10, [None])[0]
    if isinstance(j, bytes):
        try: jwt = j.decode()
        except: jwt = None
    else: jwt = j
    if not jwt:
        f = parse(body[64:]) if len(body) > 64 else {}
        j = f.get(8, [None])[0]
        s = f.get(10, [None])[0]
        if isinstance(j, bytes):
            try: jwt = j.decode()
            except: jwt = None
        else: jwt = j
    if not jwt: return None
    server = s.decode() if isinstance(s, bytes) else "https://clientbp.ppmainecoonghj.com"
    if not server.startswith("http"): server = "https://" + server
    return jwt, server

def get_player(uid, jwt, server):
    p = enc(K, V, pb({1: int(uid), 2: 7}))
    H = {"Expect": "100-continue", "Authorization": f"Bearer {jwt}", "X-Unity-Version": "2018.4.11f1", "X-GA": "v1 1", "ReleaseVersion": "OB55", "Content-Type": "application/x-www-form-urlencoded", "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-A305F Build/RP1A.200720.012)", "Host": server.replace("https://", "").replace("http://", "").split("/")[0], "Connection": "Keep-Alive", "Accept-Encoding": "gzip"}
    try:
        R = requests.post(server + "/GetPlayerPersonalShow", headers=H, data=p, timeout=15, verify=False)
    except: return None
    if R.status_code != 200: return None
    return parse(R.content)

def sub(fields, k):
    v = fields.get(k)
    if not v: return {}
    v = v[0]
    if isinstance(v, bytes): return parse(v)
    return v if isinstance(v, dict) else {}

def g(d, k):
    if not isinstance(d, dict): return None
    v = d.get(k)
    if isinstance(v, list): v = v[0] if v else None
    if isinstance(v, bytes):
        try: return v.decode()
        except: return v.hex()
    return v

def load_img(item_id):
    if not item_id: return Image.new("RGBA", (100, 100), (30, 30, 30, 255))
    try:
        r = requests.get(f"{CDN}/{item_id}.png", timeout=15)
        if r.status_code != 200: return Image.new("RGBA", (100, 100), (30, 30, 30, 255))
        return Image.open(BytesIO(r.content)).convert("RGBA")
    except: return Image.new("RGBA", (100, 100), (30, 30, 30, 255))


# ================= TELEGRAM BOT =================
import asyncio, logging, html, threading
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# Hosting-এর Environment Variables-এ নতুন BOT_TOKEN সেট করতে হবে।
BOT_TOKEN = os.getenv("BOT_TOKEN", "8824546611:AAGrwpEytqDpuWVXq4jWTzl-8V5RXq_RIjo").strip()

logging.basicConfig(level=logging.INFO)

# একসাথে বেশি রিকোয়েস্ট এলে লাইনে দাঁড়াবে (একসাথে ২টা)
SEM = asyncio.Semaphore(2)


SESSION_TTL = 50 * 60
POWERED_BY = os.getenv("POWERED_BY", "HRIDOY X STORE")
_sess = {"jwt": None, "server": None, "ts": 0}
_sess_lock = threading.Lock()


def _relogin():
    # একই Garena ID দিয়ে /banner আর /info দুটোই চলে; লগইন শেয়ার হয়।
    garena_uid = os.getenv("GARENA_UID", "8494306217").strip()
    garena_password = os.getenv("GARENA_PASSWORD", "2E8700D3F5FBDAAFA0C46BCDB6EB559BE29A513AAB4AE57F6A93186A015B13AA").strip()
    if not garena_uid or not garena_password:
        return "GARENA_UID এবং GARENA_PASSWORD সেট করা নেই।"
    acc = oauth(garena_uid, garena_password)
    if not acc:
        return "oauth failed"
    res = major_login(acc["access_token"], acc["open_id"])
    if not res:
        return "majorlogin failed"
    _sess.update(jwt=res[0], server=res[1], ts=time.time())
    return None


def get_raw(uid):
    """Returns (raw_fields | None, error | None)"""
    with _sess_lock:
        if not _sess["jwt"] or time.time() - _sess["ts"] > SESSION_TTL:
            err = _relogin()
            if err:
                return None, err
        jwt, server, ts = _sess["jwt"], _sess["server"], _sess["ts"]
    raw = get_player(uid, jwt, server)
    if raw:
        return raw, None
    # session expire হয়ে থাকলে একবার নতুন লগইন (ভুল UID-তে বারবার লগইন এড়াতে ৩০ সেকেন্ড শর্ত)
    with _sess_lock:
        if _sess["ts"] == ts and time.time() - ts > 30:
            err = _relogin()
            if err:
                return None, err
        jwt, server = _sess["jwt"], _sess["server"]
    raw = get_player(uid, jwt, server)
    if raw:
        return raw, None
    return None, "player fetch failed (UID ভুল হতে পারে)"


LEVELS = {"1":0,"2":48,"3":202,"4":544,"5":1012,"6":1844,"7":2792,"8":3800,"9":4870,"10":6004,"11":7192,"12":8448,"13":9776,"14":11140,"15":12566,"16":14060,"17":15610,"18":17224,"19":18902,"20":20632,"21":22424,"22":24728,"23":26192,"24":28166,"25":30200,"26":32294,"27":34448,"28":37804,"29":41174,"30":44870,"31":48852,"32":53334,"33":58566,"34":64096,"35":69994,"36":76460,"37":83108,"38":91128,"39":99322,"40":108092,"41":120144,"42":133266,"43":147472,"44":162760,"45":179126,"46":196572,"47":215368,"48":235516,"49":257010,"50":279860,"51":304056,"52":348318,"53":394982,"54":444044,"55":495508,"56":549364,"57":633756,"58":721744,"59":813336,"60":908522,"61":1041438,"62":1180352,"63":1325256,"64":1476184,"65":1634300,"66":1840946,"67":2056594,"68":2281242,"69":2514880,"70":2757530,"71":3059506,"72":3372284,"73":3699456,"74":4041030,"75":4397020,"76":4829104,"77":5282204,"78":5756304,"79":6251404,"80":6767504,"81":7381324,"82":8043154,"83":8752952,"84":9510808,"85":10316638,"86":11277190,"87":12360748,"88":13360304,"89":14482858,"90":15659418,"91":17026708,"92":18453688,"93":19941280,"94":21488570,"95":23095858,"96":24763138,"97":26490138,"98":28277708,"99":30124996,"100":32032284}


def calc_level(lvl, exp):
    lvl = int(lvl or 0); exp = int(exp or 0)
    if lvl < 1: lvl = 1
    if lvl >= 100: return 100, 0, 0, 100
    cur = LEVELS.get(str(lvl), 0)
    nxt = LEVELS.get(str(lvl + 1), cur)
    needed = max(0, nxt - exp)
    in_lvl = max(0, exp - cur)
    rng = max(1, nxt - cur)
    prog = min(100, (in_lvl / rng) * 100)
    return lvl, needed, nxt, round(prog, 1)


def check_ban(uid: str):
    """Returns (is_banned: bool, days: int) or None যদি চেক না হয়।"""
    url = f"https://ff.garena.com/api/antihack/check_banned?lang=en&uid={uid}"
    headers = {"User-Agent": "Mozilla/5.0 (Linux; Android 10; K)", "Accept": "application/json",
               "referer": "https://ff.garena.com/en/support/",
               "x-requested-with": "B6FksShzIgjfrYImLpTsadjS86sddhFH"}
    try:
        r = requests.get(url, headers=headers, timeout=15, verify=False)
        if r.status_code != 200:
            return None
        data = r.json().get("data", {})
        return bool(data.get("is_banned", 0)), int(data.get("period", 0) or 0)
    except Exception:
        return None


def fetch_info(uid: str):
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=1) as ex:
        ban_future = ex.submit(check_ban, uid)
        raw, err = get_raw(uid)
        ban = ban_future.result()
    if not raw:
        return None, err
    bi = sub(raw, 1)
    if not g(bi, 3):
        return None, "Player পাওয়া যায়নি (UID ভুল হতে পারে)"
    exp = g(bi, 7) or 0
    lvl, needed, nxt, prog = calc_level(g(bi, 6), exp)
    return {"uid": uid, "name": g(bi, 3), "region": g(bi, 5), "level": lvl, "likes": g(bi, 21),
            "exp": exp, "needed": needed, "next": nxt, "prog": prog, "ban": ban}, None


def format_info(d):
    name = html.escape(str(d["name"]))
    line = "❁──────✧❁✦❁✧──────❁"
    if d["ban"] is None:
        status = "Unknown"
    elif d["ban"][0]:
        status = f"BANNED ({d['ban'][1]} days)"
    else:
        status = "Not Banned"
    if d["level"] >= 100:
        lvl_lines = f"├─ Level: {d['level']} (MAX)\n├─ EXP: {d['exp']}\n"
    else:
        lvl_lines = (
            f"├─ Level: {d['level']}\n"
            f"├─ EXP: {d['exp']}\n"
            f"├─ Next Level EXP: {d['next']}\n"
            f"├─ Needed: {d['needed']}\n"
            f"├─ Progress: {d['prog']}%\n"
        )
    return (
        "🔍 <b>INFORMATION</b>\n"
        f"{line}\n"
        "<pre>"
        f"├─ UID: {d['uid']}\n"
        f"├─ Username: {name}\n"
        f"├─ Region: {d['region'] or 'N/A'}\n"
        f"{lvl_lines}"
        f"├─ Likes: {d['likes'] or 0}\n"
        f"└─ Status: {status}"
        "</pre>\n"
        f"{line}\n"
        f"✨ <i>Powered by {html.escape(POWERED_BY)}</i> ✨"
    )


def make_banner(uid: str):
    """main() এর হুবহু একই লজিক, শুধু ফাইলের বদলে BytesIO রিটার্ন করে।
    Returns (BytesIO | None, name | error_message)"""
    if not FONT:
        return None, "Font load হয়নি। Hosting-এর internet access এবং font download অনুমতি পরীক্ষা করো।"

    raw, err = get_raw(uid)
    if not raw:
        return None, err

    bi = sub(raw, 1)
    ci = sub(raw, 6)

    name = g(bi, 3) or "Unknown"
    avatar_id = g(bi, 12)
    banner_id = g(bi, 11)
    guild_name = g(ci, 2) or ""

    avatar = load_img(avatar_id)
    banner = load_img(banner_id)

    # Reference size: 4:1 wide banner. Avatar = full-height square with white frame.
    WIDTH, HEIGHT = 1000, 250
    level = g(bi, 6)

    def cover(image, size):
        target_w, target_h = size
        image = image.convert("RGBA")
        scale = max(target_w / image.width, target_h / image.height)
        resized = image.resize(
            (int(image.width * scale), int(image.height * scale)),
            Image.LANCZOS
        )
        left = (resized.width - target_w) // 2
        top = (resized.height - target_h) // 2
        return resized.crop((left, top, left + target_w, top + target_h))

    if banner_id:
        bg = cover(banner, (WIDTH, HEIGHT))
    else:
        bg = Image.new("RGBA", (WIDTH, HEIGHT), (18, 22, 30, 255))

    # Banner PNG-র স্বচ্ছ (transparent) অংশ sticker-এ কালো দেখায়, তাই আগে opaque করা হচ্ছে।
    try:
        solid = bg
        mask = solid.getchannel("A").point(lambda v: 255 if v > 128 else 0)
        from PIL import ImageStat
        r, g_, b_ = [int(x) for x in ImageStat.Stat(solid.convert("RGB"), mask=mask).mean[:3]]
        base_color = (r, g_, b_, 255)
    except Exception:
        base_color = (18, 22, 30, 255)
    base = Image.new("RGBA", (WIDTH, HEIGHT), base_color)
    bg = Image.alpha_composite(base, bg)

    # Light dark overlay (reference banner is dark but textured).
    overlay = Image.new("RGBA", (WIDTH, HEIGHT), (0, 0, 0, 60))
    bg = Image.alpha_composite(bg, overlay)
    draw = ImageDraw.Draw(bg)

    # Avatar: square, full height, white frame (left edge = banner edge).
    border = 6
    bg.paste(Image.new("RGBA", (HEIGHT, HEIGHT), (255, 255, 255, 255)), (0, 0))
    inner = HEIGHT - border * 2
    bg.paste(cover(avatar, (inner, inner)), (border, border))

    bold_path = FONT
    reg_path = FONT
    for old in ("-Bold", "Bold"):
        cand = FONT.replace(old, "-Regular" if old == "-Bold" else "Regular")
        if cand != FONT and os.path.isfile(cand):
            reg_path = cand
            break

    def fit_font(path, text, max_width, start_size, min_size=22):
        for size in range(start_size, min_size - 1, -2):
            candidate = ImageFont.truetype(path, size)
            if draw.textlength(str(text), font=candidate) <= max_width:
                return candidate
        return ImageFont.truetype(path, min_size)

    text_x = 285
    name_text = str(name)
    guild_text = str(guild_name) if guild_name else "No Guild"

    name_font = fit_font(reg_path, name_text, WIDTH - text_x - 20, 60, 28)
    guild_font = fit_font(bold_path, guild_text, WIDTH - text_x - 200, 56, 24)

    # Top: player name (baseline anchored), bottom-left: guild, bottom-right: level.
    draw.text((text_x, 88), name_text, font=name_font, fill="white", anchor="ls")
    draw.text((text_x, 210), guild_text, font=guild_font, fill="white", anchor="ls")
    if level:
        lvl_font = ImageFont.truetype(bold_path, 48)
        draw.text((WIDTH - 24, 238), f"Lvl. {level}", font=lvl_font,
                  fill=(235, 235, 235, 255), anchor="rs")

    buf = BytesIO()
    bg.save(buf, format="PNG")
    buf.seek(0)
    buf.name = f"{uid}_banner.png"
    return buf, str(name)


def to_sticker(buf):
    """Telegram photo হিসেবে পাঠালে চওড়া banner দুই পাশ থেকে কেটে যায়।
    Sticker হিসেবে পাঠালে পুরো banner অক্ষত থাকে (512x128)।"""
    buf.seek(0)
    img = Image.open(buf).convert("RGBA").resize((512, 128), Image.LANCZOS)
    out = BytesIO()
    img.save(out, format="WEBP", quality=95, method=6)
    out.seek(0)
    out.name = "banner.webp"
    return out


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 স্বাগতম!\n\n/info <UID> — প্লেয়ার ইনফো\n/banner <UID> — ব্যানার\n/like <UID> — লাইক পাঠাও\n\nউদাহরণ: /info 123456789"
    )


def progress_text(percent: int, status: str = "Generating banner...") -> str:
    # 12-block bar, same look as the reference bot.
    filled = max(0, min(12, round(percent * 12 / 100)))
    bar = "🟥" * filled + "⬛" * (12 - filled)
    line = "❄──────✧❄✦❄✧──────❄"
    return (
        "⋮ <b>FETCHING BANNER</b> ⋮\n"
        f"{line}\n"
        f"{bar}\n"
        f"⚡ {percent}%\n"
        f"🖼 <i>{status}</i>\n"
        f"{line}"
    )


async def banner_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❌ UID দাও।\nউদাহরণ: /banner 123456789")
        return

    uid = context.args[0].strip()
    if not uid.isdigit():
        await update.message.reply_text("❌ UID শুধু সংখ্যা হতে হবে।")
        return

    progress = await update.message.reply_text(progress_text(0), parse_mode="HTML")
    task = None
    try:
        async with SEM:
            task = asyncio.create_task(asyncio.to_thread(make_banner, uid))
            percent = 0
            while True:
                await asyncio.wait({task}, timeout=0.6)
                if task.done():
                    break
                percent = min(90, percent + 10)
                try:
                    await progress.edit_text(progress_text(percent), parse_mode="HTML")
                except Exception:
                    pass

            # কাজ দ্রুত শেষ হলেও 20 -> 100 লাফ না দিয়ে ধাপে ধাপে ১০০ পর্যন্ত যাবে
            if percent < 90:
                for pc in range(percent + 20, 100, 20):
                    try:
                        await progress.edit_text(progress_text(min(pc, 90)), parse_mode="HTML")
                    except Exception:
                        pass
                    await asyncio.sleep(0.35)

            buf, info = await task
    except Exception as e:
        logging.exception("banner error")
        try:
            await progress.edit_text(f"❌ Error: {e}")
        except Exception:
            await update.message.reply_text(f"❌ Error: {e}")
        return

    if buf is None:
        await progress.edit_text(f"❌ {info}")
        return

    # 100% দেখানো আর sticker পাঠানো একসাথে — শেষ হওয়া মাত্র sticker আসবে।
    # সব জায়গায় (private + group) শুধু sticker যাবে, কখনো photo না।
    sticker = to_sticker(buf)
    results = await asyncio.gather(
        progress.edit_text(progress_text(100, "Banner ready! Sending..."), parse_mode="HTML"),
        update.message.reply_sticker(sticker=sticker),
        return_exceptions=True,
    )
    if isinstance(results[1], Exception):
        logging.error("sticker send failed: %s", results[1])
        try:
            await progress.edit_text(
                "❌ Sticker পাঠানো যায়নি। Group হলে বটকে sticker পাঠানোর অনুমতি দাও।"
            )
        except Exception:
            pass
        return
    try:
        await progress.delete()
    except Exception:
        pass


# ---------------- LIKE SYSTEM ----------------
from concurrent.futures import ThreadPoolExecutor

# accs.txt (uid:password, প্রতি লাইনে একটা) বট.py এর পাশে থাকলে সেটা পড়বে, না থাকলে নিচের লিস্ট ব্যবহার হবে।
ACCOUNTS_RAW = """
4676754038:7CD3E7B1AB8E4190E4943B0414A3725BADF006615382C8E713E0732382289E45
4676739529:C8FBDA3588B253D980410EAC921693D6B0406479B7D36B881B92449FB597EAC8
4711110407:D391BA95F20A3FAEBD56BEDA710CFABD17113CC2C5A0BE597BCED72BDDB32E76
4707490502:F7CB4192DF7CB3C4D5F16AA0DD944A1B4777F74BA8C5B71B2E4598BCD50DC3DC
4630762925:5387FAFB4B224F7215AFC5B05B182C0D3F27A74E4F2B5D3C7F0607ABB98CE9C3
4630715299:EE5FFF1862E2B63A42AC1983C59B651E99B2196DF4D6752A50DB77C514ACA817
4631355125:B63F26FFFECCFDB87BBC5D01B9553C9652FC1B78721B548E4E21B36E53173713
4631652756:10645801446AD1BB98953B0DA05E56A14D8D19D5767B7E3B0F16005B70890885
4633603053:C04FCB5CBE90EAC1612AD6277ED1069717CF5CBF44FED7FD574FBF4ABC175A20
4633996559:9AD6AE89F588C3C94924FD1B8365FC98A996FEABA365A799662D36A216FDF11F
4634018346:3EDFF2CB2ECB365B7CB7FFE544C9A8D3B6A4F31E02372878CF6F0CC29E1CDE11
4634072449:CB6BF014D64D95354D388731A69DD54F615E2F7A57970F39582C05E61FF17D01
4635347376:16BD2679FA90876C45F80CC13DD45D7308299F3D3D5E81F9B1384670CE865DC8
4635440882:454BD42FD7DFB9251E43B097F7FD44982818CB99FFB4C9B682A24E8AA06D626B
4642197280:F1384E2F34F72C1CA9028006286EB05B3708C7CA2B2650D9282F1DA4743A7328
4642246297:F8BA67165D80FE82173E13E44F847C5C806E512E0032999C9A4EC797E4E1CB50
4725698457:D2F694D70B4A5CC464868AC6776C4A38113E2C1F89BD5D29198A896D7BD1454C
"""
LIKE_COOLDOWN = 600          # একই UID-তে আবার লাইক দিতে অপেক্ষা (সেকেন্ড)
LIKE_WORKERS = 5             # একসাথে কয়টা অ্যাকাউন্ট চলবে


def load_accounts():
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "accs.txt")
    raw = ACCOUNTS_RAW
    if os.path.isfile(path):
        with open(path, encoding="utf-8") as fh:
            raw = fh.read()
    out = []
    for ln in raw.splitlines():
        ln = ln.strip()
        if ":" in ln:
            u, p = ln.split(":", 1)
            if u.strip().isdigit() and p.strip():
                out.append((u.strip(), p.strip()))
    return out


ACCOUNTS = load_accounts()
_like_sess = {}
_like_sess_lock = threading.Lock()
_like_last = {}


def oauth_v2(uid, pwd):
    H = {"User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)", "Content-Type": "application/json; charset=utf-8"}
    try:
        R = requests.post(
            "https://100067.connect.garena.com/api/v2/oauth/guest/token:grant", headers=H,
            json={"client_id": 100067, "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
                  "client_type": 2, "device_id": "", "password": pwd, "response_type": "token", "uid": int(uid)},
            verify=False, timeout=20)
        if R.status_code not in (200, 201):
            return None
        J = R.json()
        if J.get("code") != 0:
            return None
        d = J.get("data", {})
        if not d.get("access_token") or not d.get("open_id"):
            return None
        return d
    except Exception:
        return None


def send_like(jwt, target, server):
    H = {"Expect": "100-continue", "Authorization": f"Bearer {jwt}", "X-Unity-Version": "2018.4.11f1",
         "X-GA": "v1 1", "ReleaseVersion": "OB55", "Content-Type": "application/x-www-form-urlencoded",
         "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 11; SM-A305F Build/RP1A.200720.012)",
         "Host": server.replace("https://", "").replace("http://", "").split("/")[0],
         "Connection": "Keep-Alive", "Accept-Encoding": "gzip"}
    p = enc(K, V, pb({1: int(target), 2: "ME"}))
    err = "unknown"
    for _ in range(2):
        try:
            R = requests.post(server + "/LikeProfile", data=p, headers=H, timeout=10, verify=False)
            if R.status_code == 200:
                return True, None
            err = f"code={R.status_code}"
        except Exception as e:
            err = f"err={e}"
        time.sleep(1)
    return False, err


def _like_login(acc_uid, pwd):
    acc = oauth_v2(acc_uid, pwd)
    if not acc:
        return None
    res = major_login(acc["access_token"], acc["open_id"])
    if not res:
        return None
    with _like_sess_lock:
        _like_sess[acc_uid] = {"jwt": res[0], "server": res[1], "ts": time.time()}
    return _like_sess[acc_uid]


def like_one(acc_uid, pwd, target):
    with _like_sess_lock:
        ss = _like_sess.get(acc_uid)
    if not ss or time.time() - ss["ts"] > SESSION_TTL:
        ss = _like_login(acc_uid, pwd)
    if not ss:
        return False, "login failed"
    ok, err = send_like(ss["jwt"], target, ss["server"])
    if not ok:  # session expire হলে একবার নতুন লগইন করে আবার চেষ্টা
        ss = _like_login(acc_uid, pwd)
        if not ss:
            return False, "login failed"
        ok, err = send_like(ss["jwt"], target, ss["server"])
    return ok, err


def run_likes(target):
    """Returns dict with before/after likes, name, success count."""
    raw, err = get_raw(target)
    if not raw:
        return {"error": err}
    bi = sub(raw, 1)
    name = g(bi, 3)
    if not name:
        return {"error": "Player পাওয়া যায়নি (UID ভুল হতে পারে)"}
    before = int(g(bi, 21) or 0)
    with ThreadPoolExecutor(max_workers=LIKE_WORKERS) as ex:
        results = list(ex.map(lambda a: like_one(a[0], a[1], target), ACCOUNTS))
    success = sum(1 for ok, _ in results if ok)
    time.sleep(2)
    raw2, _ = get_raw(target)
    after = int(g(sub(raw2, 1), 21) or before) if raw2 else before
    return {"name": name, "region": g(bi, 5), "before": before, "after": after,
            "success": success, "total": len(ACCOUNTS)}


def format_like(uid, d):
    line = "❁──────✧❁✦❁✧──────❁"
    added = d["after"] - d["before"]
    text = (
        "❤️ <b>LIKE RESULT</b>\n"
        f"{line}\n"
        "<pre>"
        f"├─ UID: {uid}\n"
        f"├─ Username: {html.escape(str(d['name']))}\n"
        f"├─ Likes Before: {d['before']}\n"
        f"├─ Likes After: {d['after']}\n"
        f"├─ Added: +{added}\n"
        f"└─ Sent: {d['success']}/{d['total']}"
        "</pre>\n"
        f"{line}\n"
    )
    if added <= 0:
        text += "⚠️ <i>লাইক বাড়েনি — আজকের লাইক আগেই দেওয়া থাকতে পারে।</i>\n"
    text += f"✨ <i>Powered by {html.escape(POWERED_BY)}</i> ✨"
    return text


async def like_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not context.args[0].strip().isdigit():
        await update.message.reply_text("❌ UID দাও (শুধু সংখ্যা)।\nউদাহরণ: /like 123456789")
        return
    if not ACCOUNTS:
        await update.message.reply_text("❌ কোনো অ্যাকাউন্ট লোড হয়নি (accs.txt বা ACCOUNTS_RAW চেক করো)।")
        return
    uid = context.args[0].strip()
    left = LIKE_COOLDOWN - (time.time() - _like_last.get(uid, 0))
    if left > 0:
        await update.message.reply_text(f"⏳ এই UID-তে এইমাত্র লাইক দেওয়া হয়েছে। {int(left)} সেকেন্ড পর আবার চেষ্টা করো।")
        return
    _like_last[uid] = time.time()
    wait = await update.message.reply_text("❤️ Sending likes...")
    try:
        async with SEM:
            d = await asyncio.to_thread(run_likes, uid)
    except Exception as e:
        logging.exception("like error")
        _like_last.pop(uid, None)
        await wait.edit_text(f"❌ Error: {html.escape(str(e))[:200]}")
        return
    if "error" in d:
        _like_last.pop(uid, None)
        await wait.edit_text(f"❌ {d['error']}")
        return
    await wait.edit_text(format_like(uid, d), parse_mode="HTML")


async def info_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args or not context.args[0].strip().isdigit():
        await update.message.reply_text("❌ UID দাও (শুধু সংখ্যা)।\nউদাহরণ: /info 123456789")
        return
    uid = context.args[0].strip()
    wait = await update.message.reply_text("⏳ Fetching...")
    try:
        async with SEM:
            data, err = await asyncio.to_thread(fetch_info, uid)
    except Exception as e:
        logging.exception("info error")
        await wait.edit_text(f"❌ Error: {html.escape(str(e))[:200]}")
        return
    if not data:
        await wait.edit_text(f"❌ {err}")
        return
    await wait.edit_text(format_info(data), parse_mode="HTML")


# ======================= ADMIN PANEL =======================
# /admin দিলে admin panel আসবে। Admin ID সেট করতে Environment Variable ADMIN_IDS="123456,789012"
# (অথবা নিচের DEFAULT_ADMIN_IDS-এ লেখো)। নিজের ID জানতে যে কাউকে /id দিতে বলো।
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ChatMemberHandler
from telegram.error import BadRequest

DEFAULT_ADMIN_IDS = "7098502793"   # যেমন: "123456789,987654321"
ADMIN_IDS = {
    int(x) for x in (os.getenv("ADMIN_IDS", DEFAULT_ADMIN_IDS) or "").replace(" ", "").split(",")
    if x.lstrip("-").isdigit()
}

CONFIG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_config.json")
FEATURES = [("info", "ℹ️ Info"), ("banner", "🖼 Banner"), ("like", "❤️ Like")]
_cfg_lock = threading.Lock()


def _default_cfg():
    return {
        "bot_on": True,
        "private_on": True,
        "group_mode": "whitelist",   # whitelist = শুধু অনুমতি পাওয়া group, open = সব group
        "features": {k: True for k, _ in FEATURES},
        "groups": {},
    }


def load_cfg():
    cfg = _default_cfg()
    try:
        with open(CONFIG_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
        for k in ("bot_on", "private_on", "group_mode"):
            if k in data:
                cfg[k] = data[k]
        cfg["features"].update(data.get("features", {}))
        cfg["groups"] = data.get("groups", {})
    except Exception:
        pass
    return cfg


CFG = load_cfg()


def save_cfg():
    with _cfg_lock:
        tmp = CONFIG_PATH + ".tmp"
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(CFG, fh, ensure_ascii=False, indent=1)
        os.replace(tmp, CONFIG_PATH)


def is_admin(uid) -> bool:
    return uid in ADMIN_IDS


def get_group(chat, create=True):
    key = str(chat.id)
    g = CFG["groups"].get(key)
    if g is None and create:
        g = {"title": chat.title or key, "allowed": False,
             "features": {k: True for k, _ in FEATURES}, "notified": 0}
        CFG["groups"][key] = g
        save_cfg()
    elif g is not None and chat.title and g.get("title") != chat.title:
        g["title"] = chat.title
        save_cfg()
    return g


def onoff(v):
    return "✅" if v else "❌"


async def notify_admins_new_group(context, chat_id, title):
    kb = InlineKeyboardMarkup([[
        InlineKeyboardButton("✅ Allow", callback_data=f"a:ap:{chat_id}"),
        InlineKeyboardButton("🚫 Deny", callback_data=f"a:dn:{chat_id}"),
    ]])
    text = (f"👥 <b>নতুন group অনুমতি চাইছে</b>\n\n"
            f"নাম: <b>{html.escape(str(title))}</b>\nID: <code>{chat_id}</code>")
    for aid in ADMIN_IDS:
        try:
            await context.bot.send_message(aid, text, parse_mode="HTML", reply_markup=kb)
        except Exception:
            pass


async def check_access(update: Update, context: ContextTypes.DEFAULT_TYPE, feature: str) -> bool:
    chat, user, msg = update.effective_chat, update.effective_user, update.effective_message
    if not msg:
        return False
    if user and is_admin(user.id):
        return True  # admin সব জায়গায় সব কমান্ড চালাতে পারে

    if not CFG["bot_on"]:
        await msg.reply_text("⛔ Bot এখন বন্ধ আছে।")
        return False
    if not CFG["features"].get(feature, True):
        await msg.reply_text(f"⛔ /{feature} কমান্ড এখন বন্ধ আছে।")
        return False

    if chat.type == "private":
        if not CFG["private_on"]:
            await msg.reply_text("⛔ Private chat-এ bot এখন বন্ধ আছে। অনুমোদিত group-এ ব্যবহার করো।")
            return False
        return True

    g = get_group(chat)
    if CFG["group_mode"] == "whitelist" and not g.get("allowed"):
        await msg.reply_text("⛔ এই group-এ bot ব্যবহারের অনুমতি নেই। Admin-এর অনুমোদন লাগবে।")
        if ADMIN_IDS and time.time() - g.get("notified", 0) > 6 * 3600:
            g["notified"] = time.time()
            save_cfg()
            await notify_admins_new_group(context, chat.id, chat.title or chat.id)
        return False
    if not g["features"].get(feature, True):
        await msg.reply_text(f"⛔ এই group-এ /{feature} কমান্ড বন্ধ আছে।")
        return False
    return True


def gated(feature, fn):
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE):
        if await check_access(update, context, feature):
            await fn(update, context)
    return wrapper


# ---------- panel screens ----------
def main_panel():
    groups = CFG["groups"]
    allowed = sum(1 for g in groups.values() if g.get("allowed"))
    mode = "🔒 Whitelist" if CFG["group_mode"] == "whitelist" else "🌐 Open"
    text = (
        "🛠 <b>ADMIN PANEL</b>\n"
        "━━━━━━━━━━━━━━\n"
        f"🤖 Bot: <b>{'ON' if CFG['bot_on'] else 'OFF'}</b>\n"
        f"💬 Private chat: <b>{'ON' if CFG['private_on'] else 'OFF'}</b>\n"
        f"👥 Group mode: <b>{mode}</b>\n"
        f"📋 Group: {len(groups)} টি (অনুমতি পেয়েছে {allowed} টি)\n"
        "━━━━━━━━━━━━━━\n"
        "কমান্ড on/off (সব জায়গার জন্য):"
    )
    rows = [
        [InlineKeyboardButton(f"🤖 Bot: {onoff(CFG['bot_on'])}", callback_data="a:bot")],
        [InlineKeyboardButton(f"{lbl} {onoff(CFG['features'][k])}", callback_data=f"a:f:{k}")
         for k, lbl in FEATURES],
        [InlineKeyboardButton(f"💬 Private: {onoff(CFG['private_on'])}", callback_data="a:pv"),
         InlineKeyboardButton(f"👥 Mode: {mode}", callback_data="a:gm")],
        [InlineKeyboardButton(f"📋 Groups ({len(groups)})", callback_data="a:gl:0")],
        [InlineKeyboardButton("🔄 Refresh", callback_data="a:main"),
         InlineKeyboardButton("✖️ Close", callback_data="a:close")],
    ]
    return text, InlineKeyboardMarkup(rows)


PAGE = 8


def groups_panel(page):
    items = list(CFG["groups"].items())
    pages = max(1, (len(items) + PAGE - 1) // PAGE)
    page = max(0, min(page, pages - 1))
    chunk = items[page * PAGE:(page + 1) * PAGE]
    text = f"📋 <b>GROUPS</b> ({len(items)})  — পেজ {page + 1}/{pages}\n━━━━━━━━━━━━━━\n"
    text += "group-এ ক্লিক করে অনুমতি ও কমান্ড নিয়ন্ত্রণ করো।" if items else \
            "এখনো কোনো group নেই। Bot-কে group-এ add করলে এখানে আসবে।"
    rows = [[InlineKeyboardButton(f"{onoff(g.get('allowed'))} {str(g.get('title'))[:30]}",
                                  callback_data=f"a:g:{cid}")] for cid, g in chunk]
    nav = []
    if page > 0:
        nav.append(InlineKeyboardButton("⬅️", callback_data=f"a:gl:{page - 1}"))
    if page < pages - 1:
        nav.append(InlineKeyboardButton("➡️", callback_data=f"a:gl:{page + 1}"))
    if nav:
        rows.append(nav)
    rows.append([InlineKeyboardButton("🔙 Back", callback_data="a:main")])
    return text, InlineKeyboardMarkup(rows)


def group_panel(cid):
    g = CFG["groups"].get(cid)
    if not g:
        return groups_panel(0)
    text = (
        f"👥 <b>{html.escape(str(g.get('title')))}</b>\n"
        f"ID: <code>{cid}</code>\n"
        f"অনুমতি: <b>{'দেওয়া আছে' if g.get('allowed') else 'নেই'}</b>"
    )
    rows = [
        [InlineKeyboardButton(f"{'✅ Allowed' if g.get('allowed') else '🚫 Not allowed'} (ক্লিক করে বদলাও)",
                              callback_data=f"a:ga:{cid}")],
        [InlineKeyboardButton(f"{lbl} {onoff(g['features'].get(k, True))}", callback_data=f"a:gf:{cid}:{k}")
         for k, lbl in FEATURES],
        [InlineKeyboardButton("🗑 Remove", callback_data=f"a:gd:{cid}"),
         InlineKeyboardButton("🔙 Back", callback_data="a:gl:0")],
    ]
    return text, InlineKeyboardMarkup(rows)


async def safe_edit(q, text, kb):
    try:
        await q.edit_message_text(text, parse_mode="HTML", reply_markup=kb)
    except BadRequest as e:
        if "not modified" not in str(e).lower():
            raise


async def admin_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    if not ADMIN_IDS:
        await update.message.reply_text(
            f"⚠️ কোনো admin সেট করা নেই।\nতোমার Telegram ID: <code>{user.id}</code>\n\n"
            f"Hosting-এর Environment Variables-এ <code>ADMIN_IDS={user.id}</code> দাও, তারপর bot restart করো।",
            parse_mode="HTML")
        return
    if not is_admin(user.id):
        await update.message.reply_text("⛔ শুধু admin এই panel ব্যবহার করতে পারবে।")
        return
    text, kb = main_panel()
    await update.message.reply_text(text, parse_mode="HTML", reply_markup=kb)


async def id_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"🆔 তোমার ID: <code>{update.effective_user.id}</code>\n"
        f"💬 Chat ID: <code>{update.effective_chat.id}</code>", parse_mode="HTML")


async def allow_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE, value=True):
    chat = update.effective_chat
    if not is_admin(update.effective_user.id):
        return
    if chat.type == "private":
        await update.message.reply_text("এই কমান্ড group-এর ভেতরে দাও।")
        return
    get_group(chat)["allowed"] = value
    save_cfg()
    await update.message.reply_text("✅ এই group-এ bot চালু করা হয়েছে।" if value else "🚫 এই group-এ bot বন্ধ করা হয়েছে।")


async def deny_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await allow_cmd(update, context, False)


async def admin_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    if not is_admin(q.from_user.id):
        await q.answer("⛔ শুধু admin", show_alert=True)
        return
    p = q.data.split(":")
    act = p[1]
    try:
        if act == "main":
            await safe_edit(q, *main_panel())
        elif act == "close":
            await q.message.delete()
            await q.answer()
            return
        elif act == "bot":
            CFG["bot_on"] = not CFG["bot_on"]; save_cfg()
            await safe_edit(q, *main_panel())
        elif act == "pv":
            CFG["private_on"] = not CFG["private_on"]; save_cfg()
            await safe_edit(q, *main_panel())
        elif act == "gm":
            CFG["group_mode"] = "open" if CFG["group_mode"] == "whitelist" else "whitelist"; save_cfg()
            await safe_edit(q, *main_panel())
        elif act == "f":
            CFG["features"][p[2]] = not CFG["features"].get(p[2], True); save_cfg()
            await safe_edit(q, *main_panel())
        elif act == "gl":
            await safe_edit(q, *groups_panel(int(p[2])))
        elif act == "g":
            await safe_edit(q, *group_panel(p[2]))
        elif act == "ga":
            g = CFG["groups"].get(p[2])
            if g:
                g["allowed"] = not g.get("allowed"); save_cfg()
                if g["allowed"]:
                    try:
                        await context.bot.send_message(int(p[2]), "✅ এই group-এ bot চালু করা হয়েছে।")
                    except Exception:
                        pass
            await safe_edit(q, *group_panel(p[2]))
        elif act == "gf":
            g = CFG["groups"].get(p[2])
            if g:
                g["features"][p[3]] = not g["features"].get(p[3], True); save_cfg()
            await safe_edit(q, *group_panel(p[2]))
        elif act == "gd":
            CFG["groups"].pop(p[2], None); save_cfg()
            await safe_edit(q, *groups_panel(0))
        elif act in ("ap", "dn"):
            cid = p[2]
            g = CFG["groups"].get(cid)
            if g is None:
                g = {"title": cid, "allowed": False, "features": {k: True for k, _ in FEATURES}, "notified": 0}
                CFG["groups"][cid] = g
            g["allowed"] = (act == "ap"); save_cfg()
            await safe_edit(q, f"{'✅ Allowed' if g['allowed'] else '🚫 Denied'}: "
                               f"<b>{html.escape(str(g.get('title')))}</b>\n<code>{cid}</code>", None)
            if g["allowed"]:
                try:
                    await context.bot.send_message(int(cid), "✅ এই group-এ bot চালু করা হয়েছে।")
                except Exception:
                    pass
    except Exception:
        logging.exception("admin callback error")
    await q.answer()


async def my_chat_member(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Bot কোনো group-এ add হলে admin-কে Allow/Deny বাটনসহ জানায়।"""
    cm = update.my_chat_member
    chat = cm.chat
    if chat.type not in ("group", "supergroup"):
        return
    if cm.new_chat_member.status in ("member", "administrator"):
        g = get_group(chat)
        if not g.get("allowed") and CFG["group_mode"] == "whitelist":
            g["notified"] = time.time(); save_cfg()
            await notify_admins_new_group(context, chat.id, chat.title or chat.id)
    elif cm.new_chat_member.status in ("left", "kicked"):
        CFG["groups"].pop(str(chat.id), None); save_cfg()



def main():
    if not BOT_TOKEN:
        raise RuntimeError("BOT_TOKEN সেট করা নেই। Hosting Environment Variables-এ নতুন bot token দিন।")
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("banner", gated("banner", banner_cmd)))
    app.add_handler(CommandHandler(["info", "u"], gated("info", info_cmd)))
    app.add_handler(CommandHandler("like", gated("like", like_cmd)))
    app.add_handler(CommandHandler("admin", admin_cmd))
    app.add_handler(CommandHandler("id", id_cmd))
    app.add_handler(CommandHandler("allow", allow_cmd))
    app.add_handler(CommandHandler("deny", deny_cmd))
    app.add_handler(CallbackQueryHandler(admin_callback, pattern=r"^a:"))
    app.add_handler(ChatMemberHandler(my_chat_member, ChatMemberHandler.MY_CHAT_MEMBER))
    print("Bot running...")
    app.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
