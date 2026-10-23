import asyncio
import glob
import json
import logging
import os
import re
import shutil
import signal
import sys
import time
import gc  # Added for strict memory management
from telethon import TelegramClient, events, errors
from telethon.sessions import StringSession
from telethon.tl.types import (
    MessageMediaWebPage,
    MessageMediaEmpty,
    MessageMediaUnsupported,
    Channel,
    Chat,
    User,
    PeerChannel,
    PeerChat,
    PeerUser,
    MessageActionChatEditTitle,
    MessageActionPinMessage
)
from telethon.tl.functions.channels import EditTitleRequest
from telethon.tl.functions.messages import EditChatTitleRequest

# =====================================================================
# 5 ACCOUNTS CONFIGURATION (API CREDENTIALS & ISOLATED SESSIONS)
# =====================================================================
DEFAULT_ACCOUNTS = [
    {
        "id": 1,
        "name": "First Account",
        "api_id": 33248589,
        "api_hash": "cb94a9acfa11e9aaf1195610f4144e65",
        "phone": "+916209065785",
        "session": "1BVtsOLwBu7MlAul6aus_Dqc-NYeZYb5HzuH4U3tv9BLx7niAQUkiEA4FegpUXFkVyJvWHIChOHyDNhyXnBgqUIHhNXUOH1Q8dhUNBZ3B1eUXCg4AJUG0JwYLC0u0r_zDDbeth-vC3AdTdsincSJKSv9PMvYlTgoAyLlCFfSkhUxZ0Ng6tgmdz0hRhfVBDMrJAOn7rzeC6hTwIiVQNMMI10uYk-6fzqDdpLqAbWRlyFd7fYIZhquSTbXsDN0AFHOVSF3mv0Hh8qDw1be4-Y6Wh4e7d0ZemA9I2P1u4Hq8uAM5yUsKL6Tkj3U8Yfg7aki1Rm-5z-eN3KgIyTjkjaxeFl6GlVZIdAU="
    },
    {
        "id": 2,
        "name": "Second Account",
        "api_id": 34096655,
        "api_hash": "ed7b99a630dc421b80df31e46f7ae32c",
        "phone": "+917051615832",
        "session": "1BVtsOIwBuzirqArO5vBy70DEEnenKzALvheZ9vqQwkwjW-4lndYHX7L_iCuTrpr7u0lqoWBXbBr4_XDMAsalrydcW0LM1TU21gWzJgRwgkARO__DAlcHIys5JQ5hSyrVQqq8eIY8zPJyFI7k0KMZV3yJo121bFpzgnORMj-YNK7l00g96ih9z-G4PbZpvGgObrtZMGxeu8rQ64kXALuHj4S5e924zV3u9MdtxX2QEQ27D6504oWjnjIVcB1bScNDK5ezHbBttJ9VWP6gERigXILpeBTnPuDYS_c8UCwhOAZFeeSCLYrAFtDOI8Dqrceo-u-NXsgu_76UdJUZ6weJlTKjIUCBA7w="
    },
    {
        "id": 3,
        "name": "Third Account",
        "api_id": 33272640,
        "api_hash": "bb1df63726fabb470b0e3f7262511a9b",
        "phone": "+916306499318",
        "session": "1BVtsOJMBu7MahlPiCTe_vUcNebguVTyThz38edRlhVg6GNYYk-UAsceo8WyRkiYtL3KSbQZPyzO2lxl86XzRyn0FlQGjzvG8D4YBxQ8UjmJOT7mwjcCmo1MWD9KLC1Cd0eS0vPV9bwz5T2pbhNxxwlG0bjVaaH5wBFxcmULNMuQOskkhkTFTANtpV5wMHleNE3Fx8L0cbNhI5LUQEj891Ic7yk_ZSkVXuKwTsbHpMfFf-gxQL9GwUuvP9sw-5y6kDB-OiZfw0vvxcq7uNFrEiaAjykUf2vWv2N3MHm-gb-RfctAU7p3Ih8o7uK4P2EbQEPSdIL8aL0COX9NyurtRrEzQBcNmHho="
    },
    {
        "id": 4,
        "name": "Fourth Account",
        "api_id": 39538277,
        "api_hash": "17aa161a9eaafef73a0e7e5aa9a665b5",
        "phone": "+919870857249",
        "session": "1BVtsOJMBu7YbvYAtt5FpVDQz2fZD66idtGM4QguBtZvoVHwxAYF4obF7XDHLjyEnc1zkRkTdkoaWM9_IhIwEjsdUGJ8nP3K89chIOaVoKiiCnFwYAotCrSD-YM_ueDXn6l8guV1Z3nLELmqtRAIOJTMl4VNBhG4Uq7vCPqVQV8Cz2SI8VSPy38LtOkFxJp2_QTpw0t8PxmLvXZkKIdTYAdsGzS1pb1vUSzNt51Ua-kuRWthuYS20Eh6afCZkLpCJQ-mNKIjNWG8EIExRQrpl9z3qBFdTy8uFmBww7O5tbmWYD_hveyiYUvDUQ2Dy1D75yDc6pHx7uBLoodQAC8ge8PIujMHgouc="
    },
    {
        "id": 5,
        "name": "Fifth Account",
        "api_id": 34874968,
        "api_hash": "ef6de5c8b022888bcb58b690aab26eea",
        "phone": "+18459083686",
        "session": "1AZWarzkBuySbzL8SgOStP7OZp7axk4XUXiuX8cO5q1LorJiiButY7K5WOFAA3BOOjM9MdH4i_i7ked1FHnmeOdE-CnsBM4pDP4cBSlqv5yVeLxwU86QHw7otFaxOW0AgrWUwv0bIrxsbwK313A9CBMHIwEW8MPK7MBRMYnWTpTPFpR7q8DUDifOreIiCza2ETBtinv7ViYVWyCWVlRBi2Nxnk5YXMACL6S66nrX4Ulv2QCUBdjq_Z5sXoMtaSjesWJnlFmsxQRypytJmcpJsLki7uEQ3DGfbmrtalRABTH8hJegKmHWICktgJ4OCzLsWjKBTUkBtjHE9nh6D4STbn6vGEMRM6Cw="
    }
]

ACCOUNTS_CONFIG = []
for d_acc in DEFAULT_ACCOUNTS:
    aid = d_acc["id"]
    api_id_env = os.environ.get(f"API_ID_{aid}")
    api_hash_env = os.environ.get(f"API_HASH_{aid}")
    phone_env = os.environ.get(f"PHONE_{aid}")
    session_env = os.environ.get(f"SESSION_{aid}") or os.environ.get(f"SESSION_STRING_{aid}")

    acc_entry = {
        "id": aid,
        "name": os.environ.get(f"NAME_{aid}", d_acc["name"]),
        "api_id": int(api_id_env) if api_id_env and api_id_env.isdigit() else d_acc["api_id"],
        "api_hash": api_hash_env if api_hash_env else d_acc["api_hash"],
        "phone": phone_env if phone_env else d_acc["phone"],
        "session": session_env if session_env else d_acc["session"]
    }
    ACCOUNTS_CONFIG.append(acc_entry)

ACCOUNTS_BY_ID = {acc["id"]: acc for acc in ACCOUNTS_CONFIG}
FILE = "settings.json"

PIN_REACTION = "🔥"
DEFAULT_NC_TITLES = ["🔥 ALPHA ZONE 🔥", "⚡ THUNDER REIGN ⚡", "👑 APEX EMPIRE 👑", "💎 NITRO KINGS 💎", "🚀 SUPREME RULE 🚀"]
DEFAULT_GC_REPLIES = ["Hello! Currently away, will reply shortly ⚡", "Active in group, message acknowledged 👍", "Busy at the moment, checking notifications later 🚀", "Auto-reply active. Stay tuned! 💬", "Ping received. I will review this soon 🔥"]
DEFAULT_DM_REPLIES = ["Hey! Currently away from DM, will respond soon ⚡", "Message received in private chat 👍", "Please hold on, reviewing DMs shortly 🚀", "Auto-responder active for direct messages 💬", "Thanks for reaching out! Will get back to you soon 🔥"]

GC_REPLIES = list(DEFAULT_GC_REPLIES)
DM_REPLIES = list(DEFAULT_DM_REPLIES)
NC_TITLES = list(DEFAULT_NC_TITLES)
TEXT = GC_REPLIES[0]
NC_INT, VANISH, MAX_REP, COOLDOWN = 3.0, 1.5, 3, 1.5

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

ACCOUNT_STATES = {1: True, 2: False, 3: False, 4: False, 5: False}
CLIENTS = {}          
MY_IDS = {}           
USER_INFOS = {}       
STOP_EVENT = None
RENDER_SERVER = None
CACHE_CLEAN_TASK = None

REPLY_CHATS, MUTE_CHATS, LOCK_CHATS, UNMUTE_EXEMPTS = set(), set(), set(), set()
DEL_NAME_CHATS = set()  
PIN_CHATS, PIN_EXEMPTS = set(), set()
PIN_DEL_CHATS = set()
PIN_ALL = False
PIN_DEL_ALL = False
PIN_PROCESSED = set()
PIN_NOTIF_REACTED = set()
PIN_NOTIF_DELETED = set()
RECENT_DELETED = set()  

T_REPLY, T_MUTE, T_LOCK, T_NC_R, T_NC_M, T_NC_L = {}, {}, {}, {}, {}, {}
T_DELNAME = {}          
CACHE, LAST_REP, REP_CNT, NC_TASKS, NC_SETUP = {}, {}, {}, {}, {}
GC_INDEX, DM_INDEX, NC_INDEX = {}, {}, {}
MUTE_ALL = False
USER_CACHE = {}         
ENTITY_CACHE = {}       

# =====================================================================
# AUTOMATIC CACHE FILES & MEMORY CLEANER (OPTIMIZED FOR RENDER)
# =====================================================================
def clear_cache_files():
    removed_dirs, removed_files = 0, 0
    current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    try:
        for root, dirs, files in os.walk(current_dir, topdown=False):
            for d in dirs:
                if d == "__pycache__" or d == ".pytest_cache":
                    try:
                        shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                        removed_dirs += 1
                    except: pass
            for f in files:
                if f.endswith((".pyc", ".pyo", ".pyd", ".tmp")):
                    try:
                        os.remove(os.path.join(root, f))
                        removed_files += 1
                    except: pass

        global CACHE, USER_CACHE, ENTITY_CACHE, RECENT_DELETED, PIN_PROCESSED, PIN_NOTIF_REACTED, PIN_NOTIF_DELETED
        
        if len(CACHE) > 300: CACHE = dict(list(CACHE.items())[-150:])
        if len(USER_CACHE) > 500: USER_CACHE.clear()
        if len(ENTITY_CACHE) > 200: ENTITY_CACHE.clear()
        if len(RECENT_DELETED) > 1000: RECENT_DELETED.clear()
        if len(PIN_PROCESSED) > 1000: PIN_PROCESSED.clear()
        if len(PIN_NOTIF_REACTED) > 1000: PIN_NOTIF_REACTED.clear()
        if len(PIN_NOTIF_DELETED) > 1000: PIN_NOTIF_DELETED.clear()

        # 🔥 FORCED GARBAGE COLLECTION TO PREVENT RAM CRASH 🔥
        gc.collect() 

        logging.info(f"🧹 [Memory Optimizer] Cleared {removed_dirs} dirs, {removed_files} files, RAM Trimmed & GC Collected.")
        return removed_dirs, removed_files
    except Exception as exc:
        return 0, 0

async def auto_cache_cleaner_worker(interval_seconds=300): # 🔥 REDUCED TO 5 MINS
    try:
        while True:
            await asyncio.sleep(interval_seconds)
            clear_cache_files()
    except asyncio.CancelledError:
        pass

def is_target_user(cid, uid):
    if not uid: return False
    if cid in T_DELNAME and uid in T_DELNAME[cid]: return True
    if cid in T_NC_L and uid in T_NC_L[cid]: return True
    if cid in T_NC_M and uid in T_NC_M[cid]: return True
    if cid in T_NC_R and uid in T_NC_R[cid]: return True
    if cid in T_LOCK and uid in T_LOCK[cid]: return True
    if cid in T_MUTE and uid in T_MUTE[cid]: return True
    if cid in T_REPLY and uid in T_REPLY[cid]: return True
    return False

# =====================================================================
# RENDER HTTP HEALTH-CHECK DUMMY SERVER
# =====================================================================
async def start_render_health_server():
    port = int(os.environ.get("PORT", 10000))
    async def handle_http_request(reader, writer):
        try:
            line = await reader.readline()
            while True:
                header = await reader.readline()
                if not header or header == b"\r\n": break
            body = json.dumps({"status": "healthy", "service": "Userbot"}, indent=2).encode("utf-8")
            response = (b"HTTP/1.1 200 OK\r\nContent-Type: application/json\r\nContent-Length: " + str(len(body)).encode("ascii") + b"\r\nConnection: close\r\n\r\n" + body)
            writer.write(response)
            await writer.drain()
        except: pass
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except: pass
    try:
        server = await asyncio.start_server(handle_http_request, "0.0.0.0", port)
        return server
    except: return None

def save_cfg():
    try:
        d = {
            "accounts": {str(k): bool(v) for k, v in ACCOUNT_STATES.items()},
            "r": list(REPLY_CHATS), "m": list(MUTE_CHATS), "l": list(LOCK_CHATS), "u": list(UNMUTE_EXEMPTS),
            "all_dm": MUTE_ALL, "del_name_chats": list(DEL_NAME_CHATS), "pin": list(PIN_CHATS),
            "pin_all": PIN_ALL, "pin_del": list(PIN_DEL_CHATS), "pin_del_all": PIN_DEL_ALL,
            "pin_exempt": list(PIN_EXEMPTS), "pin_reaction": PIN_REACTION,
            "gc_replies": GC_REPLIES, "dm_replies": DM_REPLIES, "nc_titles": NC_TITLES,
            "tr": {str(k): list(v) for k, v in T_REPLY.items()}, "tm": {str(k): list(v) for k, v in T_MUTE.items()},
            "tl": {str(k): list(v) for k, v in T_LOCK.items()}, "ncr": {str(k): list(v) for k, v in T_NC_R.items()},
            "ncm": {str(k): list(v) for k, v in T_NC_M.items()}, "ncl": {str(k): list(v) for k, v in T_NC_L.items()},
            "tdel": {str(k): list(v) for k, v in T_DELNAME.items()}
        }
        with open(FILE, "w", encoding="utf-8") as f: json.dump(d, f, indent=2)
    except: pass

def load_cfg():
    global MUTE_ALL, GC_REPLIES, DM_REPLIES, NC_TITLES, PIN_ALL, PIN_DEL_ALL, PIN_REACTION
    if not os.path.exists(FILE): return
    try:
        with open(FILE, "r", encoding="utf-8") as f: d = json.load(f)
        for aid in [acc["id"] for acc in ACCOUNTS_CONFIG]:
            if str(aid) in d.get("accounts", {}): ACCOUNT_STATES[aid] = bool(d["accounts"][str(aid)])
        REPLY_CHATS.clear(); REPLY_CHATS.update(d.get("r", []))
        MUTE_CHATS.clear(); MUTE_CHATS.update(d.get("m", []))
        LOCK_CHATS.clear(); LOCK_CHATS.update(d.get("l", []))
        UNMUTE_EXEMPTS.clear(); UNMUTE_EXEMPTS.update(d.get("u", []))
        DEL_NAME_CHATS.clear(); DEL_NAME_CHATS.update(d.get("del_name_chats", []))
        MUTE_ALL = d.get("all_dm", False)
        PIN_CHATS.clear(); PIN_CHATS.update(d.get("pin", []))
        PIN_ALL = bool(d.get("pin_all", False))
        PIN_DEL_CHATS.clear(); PIN_DEL_CHATS.update(d.get("pin_del", []))
        PIN_DEL_ALL = bool(d.get("pin_del_all", False))
        PIN_EXEMPTS.clear(); PIN_EXEMPTS.update(d.get("pin_exempt", []))
        PIN_REACTION = str(d.get("pin_reaction", "🔥"))
        if len(d.get("gc_replies", [])) >= 5: GC_REPLIES[:] = d["gc_replies"][:5]
        if len(d.get("dm_replies", [])) >= 5: DM_REPLIES[:] = d["dm_replies"][:5]
        if len(d.get("nc_titles", [])) >= 2: NC_TITLES[:] = d["nc_titles"][:10]
        for k, v in d.get("tr", {}).items(): T_REPLY[int(k)] = set(v)
        for k, v in d.get("tm", {}).items(): T_MUTE[int(k)] = set(v)
        for k, v in d.get("tl", {}).items(): T_LOCK[int(k)] = set(v)
        for k, v in d.get("ncr", {}).items(): T_NC_R[int(k)] = set(v)
        for k, v in d.get("ncm", {}).items(): T_NC_M[int(k)] = set(v)
        for k, v in d.get("ncl", {}).items(): T_NC_L[int(k)] = set(v)
        for k, v in d.get("tdel", {}).items(): T_DELNAME[int(k)] = set(v)
    except: pass

async def _delayed_delete(msg, delay):
    try: await asyncio.sleep(delay); await msg.delete()
    except: pass

async def fb(e, txt, d=VANISH):
    try:
        target = await e.edit(txt, parse_mode="md")
        if d: asyncio.create_task(_delayed_delete(target or e, d))
    except:
        try:
            target = await e.edit(txt, parse_mode=None)
            if d: asyncio.create_task(_delayed_delete(target or e, d))
        except: pass

class TargetUser:
    def __init__(self, uid, first_name=None, username=None):
        self.id = uid
        self.first_name = first_name or f"User_{uid}"
        self.username = username
        self.title = None

async def get_targets(client, e, arg=""):
    targets = []
    if e.is_reply:
        try:
            r = await e.get_reply_message()
            if r and r.sender_id:
                s = getattr(r, '_sender', None) or getattr(r, 'sender', None)
                if not s: s = await r.get_sender()
                targets.append(s if s else TargetUser(r.sender_id))
        except: pass
    tokens = [p.strip(",;@ ") for p in (arg or "").split() if p.strip(",;@ ")]
    for tok in tokens:
        clean_tok = tok.lstrip("-")
        try:
            uid = int(tok) if clean_tok.isdigit() else tok
            ent = await client.get_entity(uid)
            if ent and ent not in targets: targets.append(ent)
        except:
            if clean_tok.isdigit(): targets.append(TargetUser(int(tok)))
    return targets

def uname(u):
    if not u: return "@User"
    if getattr(u, "username", None): return f"@{u.username}"
    uid = getattr(u, "id", None)
    clean_name = re.sub(r"[\[\]\(\)*_`]", "", getattr(u, "first_name", "") or getattr(u, "title", "")).strip() or f"User_{uid}"
    return f"[{clean_name}](tg://user?id={uid})" if uid else f"@{clean_name}"

async def get_mention(e):
    sid = e.sender_id
    if not sid: return "@there"
    if sid in USER_CACHE: return USER_CACHE[sid]
    s = getattr(e, '_sender', None) or getattr(e, 'sender', None)
    if not s:
        try: s = await e.get_sender()
        except: s = None
    mention = uname(s) if s else f"[User](tg://user?id={sid})"
    USER_CACHE[sid] = mention
    return mention

def is_media(m): return m and not isinstance(m, (MessageMediaWebPage, MessageMediaEmpty, MessageMediaUnsupported))

def cache(m):
    if not m or not getattr(m, "chat_id", None) or not getattr(m, "id", None): return
    if len(CACHE) > 100: CACHE.pop(next(iter(CACHE))) # Restrict cache size
    CACHE[(m.chat_id, m.id)] = {"cid": m.chat_id, "sid": getattr(m, "sender_id", None), "text": m.text or m.raw_text or "", "media": m.media if is_media(m.media) else None}

async def toggle_target(client, e, arg, dic, label, is_stop=False):
    cid, t = e.chat_id, await get_targets(client, e, arg)
    if is_stop:
        if t and cid in dic:
            for x in t: dic[cid].discard(x.id)
            msg = f"🛑 {label} OFF: " + ", ".join(uname(x) for x in t)
        elif cid in dic: dic[cid].clear(); msg = f"🛑 All {label} cleared."
        else: msg = f"ℹ️ No active {label}."
    else:
        if not t: return await fb(e, "⚠️ **Specify @username, ID, or reply.**")
        dic.setdefault(cid, set()).update(x.id for x in t)
        msg = f"🎯 **{label} ON**: " + ", ".join(uname(x) for x in t)
    save_cfg()
    return await fb(e, msg)

def should_auto_pin(cid): return False if not cid or cid in PIN_EXEMPTS else (True if PIN_ALL else cid in PIN_CHATS)
def should_delete_pin_notification(cid): return False if not cid else (True if PIN_DEL_ALL else cid in PIN_DEL_CHATS)
def is_pin_action(m): return True if getattr(m, "new_pin", False) or type(getattr(m, "action", None)).__name__ == "MessageActionPinMessage" else False

async def pin_own_message(client, msg):
    if not msg or not getattr(msg, "id", None) or not getattr(msg, "chat_id", None): return
    key = (msg.chat_id, msg.id)
    if key in PIN_PROCESSED: return
    PIN_PROCESSED.add(key)
    try: await client.pin_message(msg.chat_id, msg.id, notify=False)
    except: pass

async def toggle_pin(client, e, arg, is_stop=False):
    cid, tokens = e.chat_id, [p.strip(",;@ ") for p in (arg or "").split() if p.strip(",;@ ") and p.lower() not in ("on", "off")]
    if not tokens:
        if is_stop: PIN_CHATS.discard(cid)
        else: PIN_CHATS.add(cid); PIN_EXEMPTS.discard(cid)
        save_cfg()
        return await fb(e, "🛑 **PIN OFF**" if is_stop else "✅ **PIN ON**")
    for tok in tokens:
        try:
            ent = await client.get_entity(int(tok) if tok.lstrip("-").isdigit() else tok)
            target_id = getattr(ent, "id", None)
            if target_id:
                if is_stop: PIN_CHATS.discard(target_id)
                else: PIN_CHATS.add(target_id)
        except: pass
    save_cfg()
    return await fb(e, "Done.")

async def react_to_pin_notification(client, m):
    try: await client.send_reaction(m.chat_id, m.id, PIN_REACTION)
    except: pass

async def handle_pin_notification(client, acc_id, m):
    if not m or not getattr(m, "chat_id", None) or not getattr(m, "id", None): return
    cid, mid, sid = m.chat_id, m.id, getattr(m, "sender_id", None)
    if getattr(m, "out", False) or (sid == MY_IDS.get(acc_id)):
        if (cid, mid) not in PIN_NOTIF_REACTED:
            PIN_NOTIF_REACTED.add((cid, mid))
            asyncio.create_task(react_to_pin_notification(client, m))
    elif should_delete_pin_notification(cid):
        if (cid, mid) not in PIN_NOTIF_DELETED:
            PIN_NOTIF_DELETED.add((cid, mid))
            try: await m.delete()
            except: pass

async def execute_title_change(client, cid, title):
    try:
        cached_info = ENTITY_CACHE.get(cid)
        if not cached_info:
            ent = await client.get_entity(cid)
            ENTITY_CACHE[cid] = cached_info = {"input": await client.get_input_entity(cid), "is_channel": getattr(ent, "megagroup", False) or getattr(ent, "broadcast", False) or isinstance(ent, Channel), "raw_id": getattr(ent, "id", abs(cid))}
        if cached_info["is_channel"]: await client(EditTitleRequest(channel=cached_info["input"], title=title))
        else: await client(EditChatTitleRequest(chat_id=cached_info["raw_id"], title=title))
        return True, "Success"
    except errors.FloodWaitError as err: await asyncio.sleep(err.seconds + 1); return False, "FloodWait"
    except Exception: return False, "Error"

async def nc_worker(client, cid, names):
    i = 0
    try:
        while cid in NC_TASKS:
            title = names[i % len(names)]
            i += 1
            await execute_title_change(client, cid, title)
            await asyncio.sleep(NC_INT)
    except asyncio.CancelledError: pass
    finally: NC_TASKS.pop(cid, None)

def start_nc(client, cid, names):
    stop_nc_task(cid)
    NC_TASKS[cid] = asyncio.create_task(nc_worker(client, cid, [n.strip() for n in names if n.strip()] or list(DEFAULT_NC_TITLES)))

def stop_nc_task(cid):
    if cid in NC_TASKS: NC_TASKS.pop(cid).cancel()
    NC_SETUP.pop(cid, None)

async def start_account(acc_id):
    conf = ACCOUNTS_BY_ID.get(acc_id)
    if not conf: return False, "Not found"
    cl = CLIENTS.get(acc_id)
    if cl and cl.is_connected(): return True, "Connected"
    session_instance = StringSession(conf["session"]) if isinstance(conf["session"], str) else conf["session"]
    
    if not cl:
        # 🔥 CRITICAL MEMORY FIX: message_cache_size=0 forces Telethon not to bloat RAM over time
        cl = TelegramClient(session_instance, conf["api_id"], conf["api_hash"], message_cache_size=0)
        CLIENTS[acc_id] = cl
        register_handlers(cl, acc_id)
        
    try:
        await cl.connect()
        if not await cl.is_user_authorized(): return False, "Auth failed"
        me = await cl.get_me()
        MY_IDS[acc_id] = me.id
        USER_INFOS[acc_id] = {"id": me.id, "name": me.first_name, "username": me.username or "None", "phone": conf["phone"]}
        return True, f"Connected as {me.first_name}"
    except Exception as exc: return False, str(exc)

async def stop_account(acc_id):
    cl = CLIENTS.pop(acc_id, None)
    if cl and cl.is_connected(): await cl.disconnect()
    MY_IDS.pop(acc_id, None); USER_INFOS.pop(acc_id, None)

async def toggle_account_cmd(e, acc_num, turn_on):
    if acc_num not in (1, 2, 3, 4, 5): return await fb(e, "⚠️ Invalid acc num")
    ACCOUNT_STATES[acc_num] = turn_on; save_cfg()
    if turn_on:
        ok, res = await start_account(acc_num)
        return await fb(e, f"✅ **Acc {acc_num} ON:** {res}" if ok else f"❌ Error: {res}")
    else:
        await stop_account(acc_num)
        return await fb(e, f"🛑 **Acc {acc_num} OFF**")

async def toggle_all_accounts_cmd(e, turn_on):
    results = []
    for aid in (1, 2, 3, 4, 5):
        ACCOUNT_STATES[aid] = turn_on
        if turn_on:
            ok, _ = await start_account(aid); results.append(f"{aid}: {'🟢' if ok else '❌'}")
            await asyncio.sleep(0.5)
        else: await stop_account(aid)
    save_cfg()
    return await fb(e, f"✅ **All ON:** " + " | ".join(results) if turn_on else "🛑 **All OFF**")

def register_handlers(client, acc_id):
    @client.on(events.NewMessage(outgoing=True))
    @client.on(events.MessageEdited(outgoing=True))
    async def on_cmd(e):
        global MUTE_ALL, GC_REPLIES, DM_REPLIES, NC_TITLES, PIN_ALL, PIN_DEL_ALL, PIN_REACTION
        txt = (e.raw_text or "").strip()
        cid = e.chat_id
        if cid is None: return

        if is_pin_action(e):
            asyncio.create_task(handle_pin_notification(client, acc_id, e)); return

        if cid in NC_SETUP and not txt.startswith("*"):
            st = NC_SETUP[cid]
            for l in [x.strip() for x in (txt.split("\n") if "\n" in txt else txt.split("|")) if x.strip()]:
                if len(st["names"]) < 5: st["names"].append(l)
            try: await e.delete()
            except: pass
            if len(st["names"]) < 5:
                await fb(e, f"Send Name {len(st['names'])+1}/5", d=None)
            else:
                names = st["names"][:5]; NC_TITLES[:] = names; save_cfg(); del NC_SETUP[cid]; start_nc(client, cid, names)
                await fb(e, f"🚀 **NC Started**\n" + "\n".join(names))
            return

        if not txt.startswith("*"):
            if e.action is None and should_auto_pin(cid): asyncio.create_task(pin_own_message(client, e))
            return

        c = txt[1:].strip(); cl = c.lower()
        if cl in ("accs", "acc status"): return await fb(e, "📱 **Accounts Active:**\n" + "\n".join([f"Acc {aid}: {'🟢 ON' if ACCOUNT_STATES.get(aid) else '🔴 OFF'}" for aid in ACCOUNTS_BY_ID]), d=None)
        if re.match(r"^acc\s*all\s*(on|off)$", cl): return await toggle_all_accounts_cmd(e, cl.endswith("on"))
        acc_match = re.match(r"^acc\s*([1-5])\s*(on|off)$", cl)
        if acc_match: return await toggle_account_cmd(e, int(acc_match.group(1)), acc_match.group(2)=="on")

        if cl == "clearcache":
            d, f = clear_cache_files()
            return await fb(e, f"🧹 **Cache Cleaned:** {d} dirs, {f} files, RAM Trimmed & GC run.")

        if cl == "help": return await fb(e, "📋 Check script for all * commands.", d=None)
        
        # Stop All
        if cl in ("stopall", "clearall"):
            stop_nc_task(cid); REPLY_CHATS.discard(cid); MUTE_CHATS.discard(cid); LOCK_CHATS.discard(cid); DEL_NAME_CHATS.discard(cid)
            for dic in (T_REPLY, T_MUTE, T_LOCK, T_NC_R, T_NC_M, T_NC_L, T_DELNAME): dic.pop(cid, None)
            save_cfg(); return await fb(e, "🛑 **All features stopped here.**")

        # Basic Commands
        if cl == "stopnc": stop_nc_task(cid); return await fb(e, "🛑 NC Stopped.")
        if cl.startswith("nc") and not cl.startswith("ncr"):
            start_nc(client, cid, [x.strip() for x in c[2:].split("|")] if "|" in c[2:] else NC_TITLES)
            return await fb(e, "🚀 **NC Started.**")

        if cl == "pinall": PIN_ALL = True; save_cfg(); return await fb(e, "📌 Global Pin ON")
        if cl == "stop pinall": PIN_ALL = False; save_cfg(); return await fb(e, "🛑 Global Pin OFF")
        if cl == "pin": return await toggle_pin(client, e, "", False)
        if cl == "stop pin": return await toggle_pin(client, e, "", True)

        # Chat-Wide
        if cl == "delname": DEL_NAME_CHATS.add(cid); save_cfg(); return await fb(e, "✅ Auto-Del Name ON")
        if cl == "stop delname": DEL_NAME_CHATS.discard(cid); save_cfg(); return await fb(e, "🛑 Auto-Del Name OFF")
        if cl == "replyall": REPLY_CHATS.add(cid); save_cfg(); return await fb(e, "✅ ReplyAll ON")
        if cl == "stop replyall": REPLY_CHATS.discard(cid); save_cfg(); return await fb(e, "🛑 ReplyAll OFF")
        if cl == "mutegc": MUTE_CHATS.add(cid); save_cfg(); return await fb(e, "✅ MuteGC ON")
        if cl == "stop mutegc": MUTE_CHATS.discard(cid); save_cfg(); return await fb(e, "🛑 MuteGC OFF")
        if cl == "lockall": LOCK_CHATS.add(cid); save_cfg(); return await fb(e, "🛡️ LockAll ON")
        if cl == "stop lockall": LOCK_CHATS.discard(cid); save_cfg(); return await fb(e, "🛑 LockAll OFF")
        
        # Targets
        if cl.startswith("target mute"): return await toggle_target(client, e, c[11:], T_MUTE, "Target Mute")
        if cl.startswith("stop target mute"): return await toggle_target(client, e, c[16:], T_MUTE, "Target Mute", True)
        if cl.startswith("target reply"): return await toggle_target(client, e, c[12:], T_REPLY, "Target Reply")
        if cl.startswith("stop target reply"): return await toggle_target(client, e, c[17:], T_REPLY, "Target Reply", True)
        
        if cl == "status": return await fb(e, "⚙️ See code for status vars.", d=None)

    @client.on(events.NewMessage(incoming=True))
    @client.on(events.MessageEdited(incoming=True))
    async def on_incoming(e):
        if not ACCOUNT_STATES.get(acc_id, False): return
        cid, sid, my_id = e.chat_id, e.sender_id, MY_IDS.get(acc_id)
        if cid is None or sid == my_id: return

        # 🔥 SMART EARLY EXIT (SUPER MEMORY SAVER) 🔥
        # Agar ye group hamari kisi bhi target ya filter list mein nahi hai, toh message yahi par drop kardo
        # Ye RAM aur CPU ko 90% tak free rakhega kyunki useless chat process nahi hogi.
        is_monitored = (
            cid in T_NC_L or cid in T_NC_M or cid in T_LOCK or cid in LOCK_CHATS or
            cid in T_MUTE or cid in MUTE_CHATS or cid in T_NC_R or
            cid in REPLY_CHATS or cid in T_REPLY or cid in DEL_NAME_CHATS or
            cid in T_DELNAME or (e.is_private and MUTE_ALL) or should_delete_pin_notification(cid) or
            cid in NC_TASKS
        )
        if not is_monitored and not is_pin_action(e):
            return

        cache(e)

        action = getattr(e, "action", None)
        if action is not None:
            if type(action).__name__ == "MessageActionChatEditTitle":
                if is_target_user(cid, sid) or cid in DEL_NAME_CHATS:
                    try: await e.delete()
                    except: pass
                    if is_target_user(cid, sid) and (cid in NC_TASKS or cid in T_NC_L or cid in T_NC_M):
                        asyncio.create_task(execute_title_change(client, cid, NC_TITLES[0] if NC_TITLES else "🔥 ALPHA ZONE 🔥"))
                    return
            if is_pin_action(e): await handle_pin_notification(client, acc_id, e); return

        should_delete = False
        if cid in T_NC_L and sid in T_NC_L[cid]: should_delete = True
        elif cid in T_NC_M and sid in T_NC_M[cid]:
            should_delete = True; asyncio.create_task(execute_title_change(client, cid, f"🚫 MUTED: User {sid}"))
        elif cid in T_LOCK and sid in T_LOCK[cid]: should_delete = True
        elif cid in LOCK_CHATS: should_delete = True
        elif cid in T_MUTE and sid in T_MUTE[cid]: should_delete = True
        elif cid in MUTE_CHATS or (e.is_private and MUTE_ALL and cid not in UNMUTE_EXEMPTS): should_delete = True

        if should_delete:
            if (cid, e.id) not in RECENT_DELETED:
                RECENT_DELETED.add((cid, e.id))
                try: await e.delete()
                except: pass
            return

        if cid in T_NC_R and sid in T_NC_R[cid]:
            try:
                mention, idx = await get_mention(e), GC_INDEX.get(cid, 0)
                GC_INDEX[cid] = (idx + 1) % len(GC_REPLIES)
                await e.reply(f"🎯 {mention} {GC_REPLIES[idx % len(GC_REPLIES)]}", parse_mode="md")
                asyncio.create_task(execute_title_change(client, cid, f"🎯 TARGET ALERT: {sid}"))
            except: pass

        if cid in REPLY_CHATS or (cid in T_REPLY and sid in T_REPLY[cid]):
            now = time.time()
            if now - LAST_REP.get((cid, sid), 0) < COOLDOWN: return
            LAST_REP[(cid, sid)] = now
            try:
                mention, idx = await get_mention(e), (DM_INDEX.get(cid, 0) if e.is_private else GC_INDEX.get(cid, 0))
                msgs = DM_REPLIES if e.is_private else GC_REPLIES
                if e.is_private: DM_INDEX[cid] = (idx + 1) % len(msgs)
                else: GC_INDEX[cid] = (idx + 1) % len(msgs)
                await e.reply(f"{mention} {msgs[idx % len(msgs)]}", parse_mode="md")
            except: pass

async def main():
    global STOP_EVENT, RENDER_SERVER, CACHE_CLEAN_TASK
    STOP_EVENT = asyncio.Event(); load_cfg(); clear_cache_files()
    CACHE_CLEAN_TASK = asyncio.create_task(auto_cache_cleaner_worker(300))
    RENDER_SERVER = await start_render_health_server()
    if not any(ACCOUNT_STATES.values()): ACCOUNT_STATES[1] = True; save_cfg()
    for aid in [a["id"] for a in ACCOUNTS_CONFIG]:
        if ACCOUNT_STATES.get(aid, False): await start_account(aid); await asyncio.sleep(1.0)
    print("\n🚀 USERBOT RUNNING (Optimized for Render)\n")
    await STOP_EVENT.wait()

if __name__ == "__main__":
    loop = asyncio.new_event_loop(); asyncio.set_event_loop(loop)
    for sig in (signal.SIGINT, signal.SIGTERM):
        try: loop.add_signal_handler(sig, lambda: STOP_EVENT.set() if STOP_EVENT else None)
        except: pass
    try: loop.run_until_complete(main())
    except KeyboardInterrupt: pass
    finally:
        save_cfg(); clear_cache_files()
        for cl in list(CLIENTS.values()):
            if cl.is_connected(): loop.run_until_complete(cl.disconnect())
