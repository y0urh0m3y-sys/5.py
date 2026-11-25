import asyncio
import json
import logging
import os
import re
import shutil
import signal
import time
import gc  # Memory Optimizer
from telethon import TelegramClient, events, errors
from telethon.sessions import StringSession
from telethon.tl.types import (
    MessageMediaWebPage,
    MessageMediaEmpty,
    MessageMediaUnsupported,
    Channel,
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
        "session": "1BVtsOJcBu17g7yxmN3Pgny33Jwdc1dLAoQOeU_lziXEU6jBGIwlSwVph6_lPmOXPTi-9K3qA6HaSiIeiekW0zQ37zUPAGl9hI1yTTZ0mnyv0npZTaygrOunNtBZ7XgXFunqVbJfbepABApnJMdSg4J7loF33A9ZPQMbCohaBjC30ewWHDd01mA7SpdhD69Jcir3NP8mDMU89TJ_MaOQ2rTWnX7b9d5IwSivIa_zMopujOY6bAPUIJAvIi3hkJJY-yHLfEtj97OWq6dh23uZGVSOKBmeiJjJ6bWAYN9kHGs4RDIY3OuA-gjyHsSrWHlyBm6EvffP5uuqfbjHtQiEFOtaCVwWBXg0="
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
        "session": "1AZWarzQBuwM-b_t9xlyw69wdDtal6O6Da9gvyaq5OhpogLYy2LpqyOM9Cw5VXBLdrCWIXp6hx7nQPdu7eS1cW7_zfp8v2vsFIDRir_GfdBjcaHgIQappuHw-rS1VcATN14HBF_QdnySO8FL8gWOHTj3hhpkZaDKWVrDTiNGLIsbqK5Ii0a9VtoZMjGnDf8-RAOTqxByJ_kRXwlnji_BABm9pEmtVgmwfmV2XcmvRrssMQWUk9OrpnvdgtWneIOVGv3jZ2M5DUh6HCyPIXNiZz-kvYZ05RdeaNZNrqNARkm9a7gBfXCS6VWrcDMUUJCLWaWJzRF2bvM7isFJPtbZXj-JVF5chwjo="
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
BACKUP_TAG = "#USERBOT_CFG_BACKUP_V3"

PIN_REACTION = "🔥"
DEFAULT_NC_TITLES = ["🔥 ALPHA ZONE 🔥", "⚡ THUNDER REIGN ⚡", "👑 APEX EMPIRE 👑", "💎 NITRO KINGS 💎", "🚀 SUPREME RULE 🚀"]
DEFAULT_GC_REPLIES = ["Hello! Currently away, will reply shortly ⚡", "Active in group, message acknowledged 👍", "Busy at the moment, checking notifications later 🚀", "Auto-reply active. Stay tuned! 💬", "Ping received. I will review this soon 🔥"]
DEFAULT_DM_REPLIES = ["Hey! Currently away from DM, will respond soon ⚡", "Message received in private chat 👍", "Please hold on, reviewing DMs shortly 🚀", "Auto-responder active for direct messages 💬", "Thanks for reaching out! Will get back to you soon 🔥"]

NC_INT, VANISH, MAX_REP, COOLDOWN = 3.0, 1.5, 3, 1.5

logging.basicConfig(level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(message)s")

ACCOUNT_STATES = {1: True, 2: False, 3: False, 4: False, 5: False}
CLIENTS = {}
MY_IDS = {}
USER_INFOS = {}
STOP_EVENT = None
RENDER_SERVER = None
CACHE_CLEAN_TASK = None
CLOUD_SYNC_TASK = None
UNJOINED_POLL_TASK = None
BACKUP_MSG_ID = None

# =====================================================================
# STRICT PER-ACCOUNT ISOLATED STATE STORE (NO CROSS-ACCOUNT LEAKAGE)
# =====================================================================
def create_empty_acc_state():
    return {
        "reply_chats": set(),
        "mute_chats": set(),
        "lock_chats": set(),
        "unmute_exempts": set(),
        "del_name_chats": set(),
        "pin_chats": set(),
        "pin_exempts": set(),
        "pin_del_chats": set(),
        "pin_all": False,
        "pin_del_all": False,
        "mute_all": False,
        "pin_reaction": PIN_REACTION,
        "auto_reaction": "🔥",
        "react_chats": set(),       # Chats where ALL posts/messages get reacted
        "t_react": {},            # {chat_id: set(user_ids)} target reactions
        "unjoined_refs": {},      # {str(chat_id): "@username"} for unjoined public polling
        "gc_replies": list(DEFAULT_GC_REPLIES),
        "dm_replies": list(DEFAULT_DM_REPLIES),
        "nc_titles": list(DEFAULT_NC_TITLES),
        "t_reply": {},
        "t_mute": {},
        "t_lock": {},
        "t_nc_r": {},
        "t_nc_m": {},
        "t_nc_l": {},
        "t_delname": {},
        # Runtime ephemeral caches per account
        "nc_tasks": {},
        "nc_setup": {},
        "gc_index": {},
        "dm_index": {},
        "last_rep": {},
        "reacted_msgs": set(),
        "poll_last_id": {},
        "pin_processed": set(),
        "pin_notif_reacted": set(),
        "pin_notif_deleted": set(),
        "recent_deleted": set(),
        "user_cache": {},
        "entity_cache": {},
        "dialog_cache": {"ts": 0, "items": []},
    }

ACC_DATA = {acc["id"]: create_empty_acc_state() for acc in ACCOUNTS_CONFIG}

def get_st(acc_id):
    if acc_id not in ACC_DATA:
        ACC_DATA[acc_id] = create_empty_acc_state()
    return ACC_DATA[acc_id]

# =====================================================================
# HELP MENU
# =====================================================================
HELP = """📋 **USERBOT ALL COMMANDS & CONTROLS**
*(Har account ki settings 100% alag hain — jis account se command doge sirf wahi chalega!)*
*(Prefix `*` ya `/` dono kaam karte hain. Kisi bhi chat se `@gc_name`, `"GC Name"`, ya `https://t.me/...` likhkar remote control karein!)*

📱 **5-ACCOUNT MANAGEMENT:**
- `*acc <1-5> on` / `off` ➔ Turn ON/OFF specific account
- `*acc status` / `*accs` ➔ View status of all 5 accounts
- `*acc all on` / `off` ➔ Turn ON/OFF all accounts

🔥 **AUTO-REACTION (JOINED + UNJOINED PUBLIC CHANNELS/GROUPS):**
- `*target react <@user/ID/Name> [@gc/channel/link]` ➔ Set reaction on users in GC/Channel
- `*stop target react [@user] [@gc/channel/link]` ➔ Stop target react on user(s)
- `*react all <@gc1 @channel2 t.me/link3>` ➔ React to ALL posts/msgs in target chats (even unjoined public)
- `*stop all react [@gc/channel/link]` ➔ Stop all reaction commands
- `*setreact <emoji>` ➔ Change reaction emoji (default 🔥)

🧹 **CACHE & CLOUD BACKUP:**
- `*clearcache` / `*cache` ➔ Immediately trim RAM & clear cache
- `*sync` ➔ Force save all 5 accounts' settings to Saved Messages

📌 **MESSAGE PINNING:**
- `*pin [@gc]` / `*stop pin [@gc]` ➔ Toggle auto-pin in current or target GC
- `*pinall` / `*stop pinall` ➔ Global auto-pinning (for this account)
- `*pin except [@gc]` / `*stop pin except [@gc]` ➔ Exempt chat from global pin
- `*pindel [@gc]` / `*stop pindel [@gc]` ➔ Auto-delete pin notifications
- `*pindelall` / `*stop pindelall` ➔ Global pin notification deletion

🔄 **CONTINUOUS TITLE CHANGER (NC):**
- `*nc [@gc]` ➔ Start 5-title cycle in current or target GC
- `*nc n1 | n2 | n3 | n4 | n5 [@gc]` ➔ Start custom names
- `*nc setup` ➔ Interactive step-by-step setup wizard
- `*stopnc [@gc]` / `*stop nc [@gc]` ➔ Stop title loop

🎯 **TARGET COMMANDS (`*target <mode> <@user/ID/Name> [@gc]`):**
- `*target nc reply <user> [@gc]` / `*stop target nc reply [user] [@gc]`
- `*target nc mute <user> [@gc]` / `*stop target nc mute [user] [@gc]`
- `*target nc lock <user> [@gc]` / `*stop target nc lock [user] [@gc]`
- `*target delname <user> [@gc]` / `*stop target delname [user] [@gc]`
- `*target reply <user> [@gc]` / `*stop target reply [user] [@gc]`
- `*target mute <user> [@gc]` / `*stop target mute [user] [@gc]`
- `*target lock <user> [@gc]` / `*stop target lock [user] [@gc]`
- `*delname [@gc]` / `*stop delname [@gc]` ➔ Auto-delete ALL group name changes

👥 **GROUP COMMANDS (Remote `@gc` Supported):**
- `*replyall [@gc]` / `*stop replyall [@gc]` ➔ 1-5 rotating reply to all members
- `*gcmsgs` / `*setgc <1-5> <msg>` ➔ View/edit 5 group auto-replies
- `*mutegc [@gc]` / `*stop mutegc [@gc]` ➔ Auto-delete all incoming GC messages
- `*lockall [@gc]` / `*stop lockall [@gc]` ➔ Full group lockdown

💬 **DM COMMANDS:**
- `*reply [@user]` / `*stop reply [@user]` ➔ Toggle DM auto-reply
- `*dmmsgs` / `*setdm <1-5> <msg>` ➔ View/edit 5 DM auto-replies
- `*mute [@user]` / `*stop mute [@user]` ➔ Mute DM
- `*muteall` / `*stop muteall` ➔ Global DM mute
- `*lock [@user]` / `*stop lock [@user]` ➔ Lock DM

🛑 **STOP & STATUS:**
- `*stopall [@gc]` ➔ Stop all features in current or target chat (this account)
- `*status [@gc]` ➔ Real-time active status (this account)"""

# =====================================================================
# STRICT RAM & CACHE CLEANER (PREVENTS 512MB RENDER OOM)
# =====================================================================
def clear_cache_files():
    removed_dirs, removed_files = 0, 0
    current_dir = os.path.dirname(os.path.abspath(__file__)) if "__file__" in globals() else os.getcwd()
    try:
        for root, dirs, files in os.walk(current_dir, topdown=False):
            for d in dirs:
                if d in ("__pycache__", ".pytest_cache"):
                    try:
                        shutil.rmtree(os.path.join(root, d), ignore_errors=True)
                        removed_dirs += 1
                    except Exception:
                        pass
            for f in files:
                if f.endswith((".pyc", ".pyo", ".pyd", ".tmp")):
                    try:
                        os.remove(os.path.join(root, f))
                        removed_files += 1
                    except Exception:
                        pass

        now = time.time()
        for st in ACC_DATA.values():
            if len(st["user_cache"]) > 150:
                st["user_cache"].clear()
            if len(st["entity_cache"]) > 100:
                st["entity_cache"].clear()
            if len(st["recent_deleted"]) > 250:
                st["recent_deleted"].clear()
            if len(st["reacted_msgs"]) > 400:
                st["reacted_msgs"].clear()
            if len(st["pin_processed"]) > 250:
                st["pin_processed"].clear()
            if len(st["pin_notif_reacted"]) > 250:
                st["pin_notif_reacted"].clear()
            if len(st["pin_notif_deleted"]) > 250:
                st["pin_notif_deleted"].clear()
            if len(st["last_rep"]) > 200:
                st["last_rep"] = {k: v for k, v in st["last_rep"].items() if now - v < 60}
            if len(st["gc_index"]) > 150:
                st["gc_index"].clear()
            if len(st["dm_index"]) > 150:
                st["dm_index"].clear()

        gc.collect()
        return removed_dirs, removed_files
    except Exception:
        return 0, 0

async def auto_cache_cleaner_worker(interval_seconds=180):
    try:
        while True:
            await asyncio.sleep(interval_seconds)
            clear_cache_files()
    except asyncio.CancelledError:
        pass

def is_target_user(st, cid, uid):
    if not uid:
        return False
    return (
        (cid in st["t_delname"] and uid in st["t_delname"][cid]) or
        (cid in st["t_nc_l"] and uid in st["t_nc_l"][cid]) or
        (cid in st["t_nc_m"] and uid in st["t_nc_m"][cid]) or
        (cid in st["t_nc_r"] and uid in st["t_nc_r"][cid]) or
        (cid in st["t_lock"] and uid in st["t_lock"][cid]) or
        (cid in st["t_mute"] and uid in st["t_mute"][cid]) or
        (cid in st["t_reply"] and uid in st["t_reply"][cid]) or
        (cid in st["t_react"] and uid in st["t_react"][cid])
    )

# =====================================================================
# RENDER HTTP HEALTH-CHECK SERVER (KEEP-ALIVE FOR CRON-JOB.ORG)
# =====================================================================
async def start_render_health_server():
    port = int(os.environ.get("PORT", 10000))
    async def handle_http_request(reader, writer):
        try:
            await reader.readline()
            while True:
                header = await reader.readline()
                if not header or header == b"\r\n":
                    break
            active_accs = [aid for aid, st in ACCOUNT_STATES.items() if st]
            body = json.dumps({"status": "healthy", "active_accounts": active_accs}).encode("utf-8")
            response = (
                b"HTTP/1.1 200 OK\r\n"
                b"Content-Type: application/json\r\n"
                b"Content-Length: " + str(len(body)).encode("ascii") + b"\r\n"
                b"Connection: close\r\n\r\n" + body
            )
            writer.write(response)
            await writer.drain()
        except Exception:
            pass
        finally:
            try:
                writer.close()
                await writer.wait_closed()
            except Exception:
                pass
    try:
        return await asyncio.start_server(handle_http_request, "0.0.0.0", port)
    except Exception:
        return None

# =====================================================================
# PERSISTENT PER-ACCOUNT SETTINGS (LOCAL JSON + TELEGRAM SAVED MESSAGES)
# =====================================================================
def serialize_single_acc(st):
    return {
        "r": list(st["reply_chats"]),
        "m": list(st["mute_chats"]),
        "l": list(st["lock_chats"]),
        "u": list(st["unmute_exempts"]),
        "all_dm": st["mute_all"],
        "del_name_chats": list(st["del_name_chats"]),
        "pin": list(st["pin_chats"]),
        "pin_all": st["pin_all"],
        "pin_del": list(st["pin_del_chats"]),
        "pin_del_all": st["pin_del_all"],
        "pin_exempt": list(st["pin_exempts"]),
        "pin_reaction": st["pin_reaction"],
        "auto_reaction": st["auto_reaction"],
        "react_chats": list(st["react_chats"]),
        "treact": {str(k): list(v) for k, v in st["t_react"].items() if v},
        "unjoined_refs": st["unjoined_refs"],
        "gc_replies": st["gc_replies"],
        "dm_replies": st["dm_replies"],
        "nc_titles": st["nc_titles"],
        "tr": {str(k): list(v) for k, v in st["t_reply"].items() if v},
        "tm": {str(k): list(v) for k, v in st["t_mute"].items() if v},
        "tl": {str(k): list(v) for k, v in st["t_lock"].items() if v},
        "ncr": {str(k): list(v) for k, v in st["t_nc_r"].items() if v},
        "ncm": {str(k): list(v) for k, v in st["t_nc_m"].items() if v},
        "ncl": {str(k): list(v) for k, v in st["t_nc_l"].items() if v},
        "tdel": {str(k): list(v) for k, v in st["t_delname"].items() if v},
    }

def deserialize_single_acc(st, d):
    if not isinstance(d, dict):
        return
    st["reply_chats"].clear(); st["reply_chats"].update(d.get("r", []))
    st["mute_chats"].clear(); st["mute_chats"].update(d.get("m", []))
    st["lock_chats"].clear(); st["lock_chats"].update(d.get("l", []))
    st["unmute_exempts"].clear(); st["unmute_exempts"].update(d.get("u", []))
    st["del_name_chats"].clear(); st["del_name_chats"].update(d.get("del_name_chats", []))
    st["mute_all"] = bool(d.get("all_dm", False))
    st["pin_chats"].clear(); st["pin_chats"].update(d.get("pin", []))
    st["pin_all"] = bool(d.get("pin_all", False))
    st["pin_del_chats"].clear(); st["pin_del_chats"].update(d.get("pin_del", []))
    st["pin_del_all"] = bool(d.get("pin_del_all", False))
    st["pin_exempts"].clear(); st["pin_exempts"].update(d.get("pin_exempt", []))
    st["pin_reaction"] = str(d.get("pin_reaction", "🔥"))
    st["auto_reaction"] = str(d.get("auto_reaction", "🔥"))
    st["react_chats"].clear(); st["react_chats"].update(d.get("react_chats", []))
    st["unjoined_refs"].clear()
    if isinstance(d.get("unjoined_refs"), dict):
        st["unjoined_refs"].update(d["unjoined_refs"])
    if len(d.get("gc_replies", [])) >= 5:
        st["gc_replies"][:] = d["gc_replies"][:5]
    if len(d.get("dm_replies", [])) >= 5:
        st["dm_replies"][:] = d["dm_replies"][:5]
    if len(d.get("nc_titles", [])) >= 2:
        st["nc_titles"][:] = d["nc_titles"][:10]
    for target_key, json_key in [
        ("t_reply", "tr"), ("t_mute", "tm"), ("t_lock", "tl"),
        ("t_nc_r", "ncr"), ("t_nc_m", "ncm"), ("t_nc_l", "ncl"),
        ("t_delname", "tdel"), ("t_react", "treact")
    ]:
        st[target_key].clear()
        for k, v in d.get(json_key, {}).items():
            st[target_key][int(k)] = set(v)

def build_cfg_dict():
    return {
        "v": 3,
        "accounts": {str(k): bool(v) for k, v in ACCOUNT_STATES.items()},
        "per_acc": {str(aid): serialize_single_acc(get_st(aid)) for aid in ACCOUNTS_BY_ID}
    }

def apply_cfg_dict(d):
    if not isinstance(d, dict):
        return
    for aid in ACCOUNTS_BY_ID:
        if str(aid) in d.get("accounts", {}):
            ACCOUNT_STATES[aid] = bool(d["accounts"][str(aid)])
    if "per_acc" in d and isinstance(d["per_acc"], dict):
        for aid in ACCOUNTS_BY_ID:
            if str(aid) in d["per_acc"]:
                deserialize_single_acc(get_st(aid), d["per_acc"][str(aid)])
    else:
        deserialize_single_acc(get_st(1), d)

async def _push_cloud_backup():
    global BACKUP_MSG_ID
    await asyncio.sleep(2.0)
    primary_client = CLIENTS.get(1)
    if not primary_client or not primary_client.is_connected():
        for cl in CLIENTS.values():
            if cl and cl.is_connected():
                primary_client = cl
                break
    if not primary_client:
        return
    try:
        payload = f"{BACKUP_TAG}\n```json\n{json.dumps(build_cfg_dict(), separators=(',', ':'))}\n```"
        if BACKUP_MSG_ID:
            try:
                await primary_client.edit_message("me", BACKUP_MSG_ID, payload)
                return
            except Exception:
                BACKUP_MSG_ID = None
        async for msg in primary_client.iter_messages("me", limit=15, search=BACKUP_TAG):
            if msg.raw_text and BACKUP_TAG in msg.raw_text:
                BACKUP_MSG_ID = msg.id
                await primary_client.edit_message("me", BACKUP_MSG_ID, payload)
                return
        sent = await primary_client.send_message("me", payload)
        BACKUP_MSG_ID = sent.id
        try:
            await primary_client.pin_message("me", sent.id, notify=False)
        except Exception:
            pass
    except Exception:
        pass

def save_cfg():
    global CLOUD_SYNC_TASK
    try:
        with open(FILE, "w", encoding="utf-8") as f:
            json.dump(build_cfg_dict(), f, indent=2)
    except Exception:
        pass
    try:
        loop = asyncio.get_running_loop()
        if CLOUD_SYNC_TASK and not CLOUD_SYNC_TASK.done():
            CLOUD_SYNC_TASK.cancel()
        CLOUD_SYNC_TASK = loop.create_task(_push_cloud_backup())
    except Exception:
        pass

def load_cfg():
    if not os.path.exists(FILE):
        return
    try:
        with open(FILE, "r", encoding="utf-8") as f:
            apply_cfg_dict(json.load(f))
    except Exception:
        pass

async def restore_cfg_from_cloud(client):
    global BACKUP_MSG_ID
    if not client or not client.is_connected():
        return False
    try:
        async for msg in client.iter_messages("me", limit=20, search=BACKUP_TAG):
            if msg.raw_text and BACKUP_TAG in msg.raw_text:
                BACKUP_MSG_ID = msg.id
                m = re.search(r"\{.*\}", msg.raw_text, re.DOTALL)
                if m:
                    data = json.loads(m.group(0))
                    apply_cfg_dict(data)
                    with open(FILE, "w", encoding="utf-8") as f:
                        json.dump(data, f, indent=2)
                    return True
    except Exception:
        pass
    return False

# =====================================================================
# REMOTE CHAT & USER RESOLVER (SUPPORTS LINKS, USERNAMES, IDs, NAMES)
# =====================================================================
def extract_tg_username_or_ref(tok):
    if not tok:
        return ""
    clean = tok.strip().strip('"').strip("'")
    # Handle https://t.me/username or t.me/username/123
    m = re.match(r"^(?:https?://)?(?:www\.)?(?:t\.me|telegram\.me)/([a-zA-Z0-9_]{3,})(?:/.*)?$", clean, re.IGNORECASE)
    if m:
        slug = m.group(1)
        if slug.lower() not in ("c", "joinchat", "s"):
            return slug
    return clean[1:] if clean.startswith("@") else clean

async def _refresh_dialogs_if_needed(client, st):
    now = time.time()
    dcache = st["dialog_cache"]
    if now - dcache["ts"] < 45 and dcache["items"]:
        return dcache["items"]
    items = []
    try:
        async for dlg in client.iter_dialogs(limit=120):
            ent = dlg.entity
            title = (getattr(ent, "title", None) or getattr(ent, "first_name", None) or "").strip()
            uname_val = (getattr(ent, "username", None) or "").strip()
            items.append({
                "id": dlg.id,
                "raw_id": getattr(ent, "id", dlg.id),
                "title": title.lower(),
                "username": uname_val.lower(),
                "is_group": dlg.is_group or dlg.is_channel,
                "entity": ent
            })
        dcache["ts"] = now
        dcache["items"] = items
    except Exception:
        pass
    return dcache["items"]

async def resolve_chat_token(client, st, tok, record_unjoined=True):
    if not tok:
        return None, None
    clean_no_at = extract_tg_username_or_ref(tok)
    if not clean_no_at:
        return None, None

    if clean_no_at.lstrip("-").isdigit():
        num_id = int(clean_no_at)
        try:
            ent = await client.get_entity(num_id)
            cid = await client.get_peer_id(ent)
            return cid, getattr(ent, "title", None) or getattr(ent, "first_name", str(cid))
        except Exception:
            return num_id, str(num_id)

    try:
        ent = await client.get_entity(clean_no_at)
        cid = await client.get_peer_id(ent)
        if record_unjoined and getattr(ent, "left", False) and getattr(ent, "username", None):
            st["unjoined_refs"][str(cid)] = f"@{ent.username}"
        return cid, getattr(ent, "title", None) or getattr(ent, "first_name", str(cid))
    except Exception:
        pass

    items = await _refresh_dialogs_if_needed(client, st)
    q = clean_no_at.lower()
    for it in items:
        if it["username"] == q or it["title"] == q:
            return it["id"], getattr(it["entity"], "title", None) or getattr(it["entity"], "first_name", str(it["id"]))
    for it in items:
        if q and q in it["title"]:
            return it["id"], getattr(it["entity"], "title", None) or getattr(it["entity"], "first_name", str(it["id"]))
    return None, None

def tokenize_args(arg_str):
    if not arg_str:
        return []
    raw_tokens = re.findall(r'@?"[^"]+"|@?\'[^\']+\'|\S+', arg_str.strip())
    cleaned = []
    for t in raw_tokens:
        t = t.strip(",")
        if t.startswith('@"') and t.endswith('"'):
            t = "@" + t[2:-1]
        elif t.startswith("@'") and t.endswith("'"):
            t = "@" + t[2:-1]
        elif (t.startswith('"') and t.endswith('"')) or (t.startswith("'") and t.endswith("'")):
            t = t[1:-1]
        if t:
            cleaned.append(t)
    return cleaned

async def resolve_target_chat_from_arg(client, st, default_cid, arg_str):
    tokens = tokenize_args(arg_str)
    if not tokens:
        return default_cid, None
    cid, label = await resolve_chat_token(client, st, tokens[-1])
    if cid is not None:
        return cid, label
    return default_cid, None

class TargetUser:
    def __init__(self, uid, first_name=None, username=None):
        self.id = uid
        self.first_name = first_name or f"User_{uid}"
        self.username = username
        self.title = None

async def resolve_single_user(client, st, tok, chat_hint=None):
    clean = extract_tg_username_or_ref(tok)
    if not clean:
        return None
    if clean.lstrip("-").isdigit():
        uid = int(clean)
        try:
            ent = await client.get_entity(uid)
            return ent if hasattr(ent, "first_name") else TargetUser(uid)
        except Exception:
            return TargetUser(uid)
    try:
        ent = await client.get_entity(clean)
        if getattr(ent, "first_name", None) or getattr(ent, "username", None):
            return ent
    except Exception:
        pass
    items = await _refresh_dialogs_if_needed(client, st)
    q = clean.lower()
    for it in items:
        if not it["is_group"] and (it["username"] == q or it["title"] == q or (q and q in it["title"])):
            return it["entity"]
    if chat_hint:
        try:
            async for p in client.iter_participants(chat_hint, search=clean, limit=5):
                return p
        except Exception:
            pass
    return None

async def parse_user_and_gc_targets(client, st, e, arg_str, default_cid):
    tokens = tokenize_args(arg_str)
    target_cid = default_cid
    target_gc_label = None
    users = []

    if e.is_reply:
        try:
            r = await e.get_reply_message()
            if r and r.sender_id:
                s = getattr(r, "_sender", None) or getattr(r, "sender", None) or await r.get_sender()
                users.append(s if s else TargetUser(r.sender_id))
        except Exception:
            pass

    if not tokens:
        return target_cid, target_gc_label, users

    if len(tokens) >= 2 or (len(tokens) == 1 and users):
        maybe_gc_id, maybe_gc_name = await resolve_chat_token(client, st, tokens[-1])
        if maybe_gc_id is not None and (
            str(maybe_gc_id).startswith("-100")
            or maybe_gc_id < 0
            or str(maybe_gc_id) in st["unjoined_refs"]
            or any(d["id"] == maybe_gc_id and d["is_group"] for d in st["dialog_cache"]["items"])
        ):
            target_cid = maybe_gc_id
            target_gc_label = maybe_gc_name
            tokens = tokens[:-1]

    for tok in tokens:
        u_ent = await resolve_single_user(client, st, tok, chat_hint=target_cid)
        if u_ent and all(getattr(u_ent, "id", None) != getattr(x, "id", None) for x in users):
            users.append(u_ent)

    return target_cid, target_gc_label, users

# =====================================================================
# AUTO-REACTION ENGINE (JOINED EVENTS + UNJOINED PUBLIC POLLER)
# =====================================================================
async def send_auto_reaction(client, st, cid, mid):
    key = (cid, mid)
    if key in st["reacted_msgs"]:
        return
    st["reacted_msgs"].add(key)
    try:
        await client.send_reaction(cid, mid, st["auto_reaction"])
    except Exception:
        pass

async def unjoined_public_reaction_worker():
    """Polls unjoined public channels/groups every 3.5s so reactions work without joining."""
    try:
        while True:
            await asyncio.sleep(3.5)
            for aid, cl in list(CLIENTS.items()):
                if not ACCOUNT_STATES.get(aid, False) or not cl or not cl.is_connected():
                    continue
                st = get_st(aid)
                active_cids = set(st["react_chats"]) | {k for k, v in st["t_react"].items() if v}
                for cid in active_cids:
                    ref = st["unjoined_refs"].get(str(cid))
                    if not ref:
                        continue
                    try:
                        msgs = await cl.get_messages(ref, limit=5)
                        if not msgs:
                            continue
                        last_seen = st["poll_last_id"].get(cid, 0)
                        newest_id = max(m.id for m in msgs if getattr(m, "id", None))
                        if last_seen == 0:
                            # On first check, react to latest post and mark baseline
                            st["poll_last_id"][cid] = newest_id
                            latest_m = msgs[0]
                            sid = getattr(latest_m, "sender_id", None)
                            if cid in st["react_chats"] or (cid in st["t_react"] and sid in st["t_react"][cid]):
                                await send_auto_reaction(cl, st, cid, latest_m.id)
                            continue
                        for m in reversed(msgs):
                            if not getattr(m, "id", None) or m.id <= last_seen:
                                continue
                            sid = getattr(m, "sender_id", None)
                            if cid in st["react_chats"] or (cid in st["t_react"] and sid in st["t_react"][cid]):
                                await send_auto_reaction(cl, st, cid, m.id)
                        if newest_id > last_seen:
                            st["poll_last_id"][cid] = newest_id
                    except Exception:
                        pass
    except asyncio.CancelledError:
        pass

# =====================================================================
# HELPERS & UI FEEDBACK
# =====================================================================
async def _delayed_delete(msg, delay):
    try:
        await asyncio.sleep(delay)
        await msg.delete()
    except Exception:
        pass

async def fb(e, txt, d=VANISH):
    try:
        target = await e.edit(txt, parse_mode="md")
        if d:
            asyncio.create_task(_delayed_delete(target or e, d))
    except Exception:
        try:
            target = await e.edit(txt, parse_mode=None)
            if d:
                asyncio.create_task(_delayed_delete(target or e, d))
        except Exception:
            pass

def uname(u):
    if not u:
        return "@User"
    if getattr(u, "username", None):
        return f"@{u.username}"
    uid = getattr(u, "id", None)
    clean_name = re.sub(r"[\[\]\(\)*_`]", "", getattr(u, "first_name", "") or getattr(u, "title", "")).strip() or f"User_{uid}"
    return f"[{clean_name}](tg://user?id={uid})" if uid else f"@{clean_name}"

async def get_mention(st, e):
    sid = e.sender_id
    if not sid:
        return "@there"
    ucache = st["user_cache"]
    if sid in ucache:
        return ucache[sid]
    s = getattr(e, "_sender", None) or getattr(e, "sender", None)
    if not s:
        try:
            s = await e.get_sender()
        except Exception:
            s = None
    mention = uname(s) if s else f"[User](tg://user?id={sid})"
    ucache[sid] = mention
    return mention

async def toggle_target(client, acc_id, e, arg, dict_key, label, is_stop=False):
    st = get_st(acc_id)
    dic = st[dict_key]
    cid, gc_label, t = await parse_user_and_gc_targets(client, st, e, arg, e.chat_id)
    loc_tag = f" in **{gc_label}**" if gc_label else ""
    acc_tag = f"[Acc {acc_id}] "
    if is_stop:
        if t and cid in dic:
            for x in t:
                dic[cid].discard(x.id)
            if not dic[cid]:
                dic.pop(cid, None)
            msg = f"🛑 {acc_tag}{label} OFF{loc_tag}: " + ", ".join(uname(x) for x in t)
        elif cid in dic:
            dic.pop(cid, None)
            msg = f"🛑 {acc_tag}All {label} cleared{loc_tag}."
        else:
            msg = f"ℹ️ {acc_tag}No active {label}{loc_tag}."
    else:
        if not t:
            return await fb(e, "⚠️ **Specify @username, ID, or Profile Name (optional `@gc/channel/link`).**")
        dic.setdefault(cid, set()).update(x.id for x in t)
        msg = f"🎯 **{acc_tag}{label} ON**{loc_tag}: " + ", ".join(uname(x) for x in t)
    save_cfg()
    return await fb(e, msg)

def should_auto_pin(st, cid):
    return False if not cid or cid in st["pin_exempts"] else (True if st["pin_all"] else cid in st["pin_chats"])

def should_delete_pin_notification(st, cid):
    return False if not cid else (True if st["pin_del_all"] else cid in st["pin_del_chats"])

def is_pin_action(m):
    return True if getattr(m, "new_pin", False) or type(getattr(m, "action", None)).__name__ == "MessageActionPinMessage" else False

async def pin_own_message(client, st, msg):
    if not msg or not getattr(msg, "id", None) or not getattr(msg, "chat_id", None):
        return
    key = (msg.chat_id, msg.id)
    if key in st["pin_processed"]:
        return
    st["pin_processed"].add(key)
    try:
        await client.pin_message(msg.chat_id, msg.id, notify=False)
    except Exception:
        pass

async def toggle_pin(client, acc_id, e, arg, is_stop=False):
    st = get_st(acc_id)
    tokens = [t for t in tokenize_args(arg) if t.lower() not in ("on", "off")]
    if not tokens:
        cid = e.chat_id
        if is_stop:
            st["pin_chats"].discard(cid)
        else:
            st["pin_chats"].add(cid)
            st["pin_exempts"].discard(cid)
        save_cfg()
        return await fb(e, f"🛑 **[Acc {acc_id}] PIN OFF**" if is_stop else f"✅ **[Acc {acc_id}] PIN ON**")
    names = []
    for tok in tokens:
        target_id, label = await resolve_chat_token(client, st, tok)
        if target_id:
            if is_stop:
                st["pin_chats"].discard(target_id)
            else:
                st["pin_chats"].add(target_id)
                st["pin_exempts"].discard(target_id)
            names.append(label or str(target_id))
    save_cfg()
    return await fb(e, f"{'🛑' if is_stop else '✅'} [Acc {acc_id}] PIN {'OFF' if is_stop else 'ON'}: {', '.join(names) or 'Done'}")

async def react_to_pin_notification(client, st, m):
    try:
        await client.send_reaction(m.chat_id, m.id, st["pin_reaction"])
    except Exception:
        pass

async def handle_pin_notification(client, acc_id, m):
    if not m or not getattr(m, "chat_id", None) or not getattr(m, "id", None):
        return
    st = get_st(acc_id)
    cid, mid, sid = m.chat_id, m.id, getattr(m, "sender_id", None)
    if getattr(m, "out", False) or (sid == MY_IDS.get(acc_id)):
        if (cid, mid) not in st["pin_notif_reacted"]:
            st["pin_notif_reacted"].add((cid, mid))
            asyncio.create_task(react_to_pin_notification(client, st, m))
    elif should_delete_pin_notification(st, cid):
        if (cid, mid) not in st["pin_notif_deleted"]:
            st["pin_notif_deleted"].add((cid, mid))
            try:
                await m.delete()
            except Exception:
                pass

async def execute_title_change(client, st, cid, title):
    try:
        ecache = st["entity_cache"]
        cached_info = ecache.get(cid)
        if not cached_info:
            ent = await client.get_entity(cid)
            ecache[cid] = cached_info = {
                "input": await client.get_input_entity(cid),
                "is_channel": getattr(ent, "megagroup", False) or getattr(ent, "broadcast", False) or isinstance(ent, Channel),
                "raw_id": getattr(ent, "id", abs(cid))
            }
        if cached_info["is_channel"]:
            await client(EditTitleRequest(channel=cached_info["input"], title=title))
        else:
            await client(EditChatTitleRequest(chat_id=cached_info["raw_id"], title=title))
        return True, "Success"
    except errors.FloodWaitError as err:
        await asyncio.sleep(err.seconds + 1)
        return False, "FloodWait"
    except Exception:
        return False, "Error"

async def nc_worker(client, st, cid, names):
    i = 0
    tasks_dict = st["nc_tasks"]
    try:
        while cid in tasks_dict:
            title = names[i % len(names)]
            i += 1
            await execute_title_change(client, st, cid, title)
            await asyncio.sleep(NC_INT)
    except asyncio.CancelledError:
        pass
    finally:
        tasks_dict.pop(cid, None)

def start_nc(client, st, cid, names):
    stop_nc_task(st, cid)
    clean_names = [n.strip() for n in names if n.strip()] or list(DEFAULT_NC_TITLES)
    st["nc_tasks"][cid] = asyncio.create_task(nc_worker(client, st, cid, clean_names))

def stop_nc_task(st, cid):
    if cid in st["nc_tasks"]:
        st["nc_tasks"].pop(cid).cancel()
    st["nc_setup"].pop(cid, None)

async def start_account(acc_id):
    conf = ACCOUNTS_BY_ID.get(acc_id)
    if not conf:
        return False, "Not found"
    cl = CLIENTS.get(acc_id)
    if cl and cl.is_connected():
        return True, "Connected"
    session_instance = StringSession(conf["session"]) if isinstance(conf["session"], str) else conf["session"]

    if not cl:
        cl = TelegramClient(session_instance, conf["api_id"], conf["api_hash"])
        CLIENTS[acc_id] = cl
        register_handlers(cl, acc_id)

    try:
        await cl.connect()
        if not await cl.is_user_authorized():
            return False, "Auth failed"
        me = await cl.get_me()
        MY_IDS[acc_id] = me.id
        USER_INFOS[acc_id] = {"id": me.id, "name": me.first_name, "username": me.username or "None", "phone": conf["phone"]}
        return True, f"Connected as {me.first_name}"
    except Exception as exc:
        return False, str(exc)

async def stop_account(acc_id):
    st = get_st(acc_id)
    for cid in list(st["nc_tasks"].keys()):
        stop_nc_task(st, cid)
    cl = CLIENTS.pop(acc_id, None)
    if cl and cl.is_connected():
        await cl.disconnect()
    MY_IDS.pop(acc_id, None)
    USER_INFOS.pop(acc_id, None)

async def toggle_account_cmd(e, acc_num, turn_on):
    if acc_num not in (1, 2, 3, 4, 5):
        return await fb(e, "⚠️ Invalid acc num")
    ACCOUNT_STATES[acc_num] = turn_on
    save_cfg()
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
            ok, _ = await start_account(aid)
            results.append(f"{aid}: {'🟢' if ok else '❌'}")
            await asyncio.sleep(0.5)
        else:
            await stop_account(aid)
    save_cfg()
    return await fb(e, "✅ **All ON:** " + " | ".join(results) if turn_on else "🛑 **All OFF**")

async def show_accounts_status(e):
    lines = ["📱 **ACCOUNTS DASHBOARD**"]
    for acc in ACCOUNTS_CONFIG:
        aid = acc["id"]
        is_enabled = ACCOUNT_STATES.get(aid, False)
        cl = CLIENTS.get(aid)
        is_conn = cl is not None and cl.is_connected()
        status = "🟢 ACTIVE" if (is_enabled and is_conn) else "🟡 ENABLED" if is_enabled else "🔴 OFF"
        lines.append(f"• Acc {aid} ({acc['phone']}): {status}")
    return await fb(e, "\n".join(lines), d=None)

# =====================================================================
# EVENT HANDLERS (STRICTLY SCOPED TO THE ACCOUNT THAT SENT THE COMMAND)
# =====================================================================
def register_handlers(client, acc_id):
    @client.on(events.NewMessage(outgoing=True))
    @client.on(events.MessageEdited(outgoing=True))
    async def on_cmd(e):
        if getattr(e, "sender_id", None) and e.sender_id != MY_IDS.get(acc_id):
            return

        st = get_st(acc_id)
        txt = (e.raw_text or "").strip()
        cid = e.chat_id
        if cid is None:
            return

        if is_pin_action(e):
            asyncio.create_task(handle_pin_notification(client, acc_id, e))
            return

        if cid in st["nc_setup"] and not txt.startswith(("*", "/")):
            setup_box = st["nc_setup"][cid]
            for l in [x.strip() for x in (txt.split("\n") if "\n" in txt else txt.split("|")) if x.strip()]:
                if len(setup_box["names"]) < 5:
                    setup_box["names"].append(l)
            try:
                await e.delete()
            except Exception:
                pass
            if len(setup_box["names"]) < 5:
                await fb(e, f"[Acc {acc_id}] Send Name {len(setup_box['names'])+1}/5", d=None)
            else:
                names = setup_box["names"][:5]
                st["nc_titles"][:] = names
                save_cfg()
                del st["nc_setup"][cid]
                start_nc(client, st, cid, names)
                await fb(e, f"🚀 **[Acc {acc_id}] NC Started**\n" + "\n".join(names))
            return

        if not txt.startswith(("*", "/")):
            if e.action is None and should_auto_pin(st, cid):
                asyncio.create_task(pin_own_message(client, st, e))
            return

        c = txt[1:].strip()
        cl = c.lower()

        if cl in ("accs", "acc status", "accounts"):
            return await show_accounts_status(e)
        if re.match(r"^(?:acc|accs)\s*all\s*(on|off)$", cl):
            return await toggle_all_accounts_cmd(e, cl.endswith("on"))
        acc_match = re.match(r"^(?:acc|account)\s*([1-5])\s*(on|off)$", cl)
        if acc_match:
            return await toggle_account_cmd(e, int(acc_match.group(1)), acc_match.group(2) == "on")

        if cl in ("clearcache", "cache"):
            d, f = clear_cache_files()
            return await fb(e, f"🧹 **Cache Cleaned:** {d} dirs, {f} files, RAM Trimmed & GC run.")

        if cl == "sync":
            await _push_cloud_backup()
            return await fb(e, "☁️ **All 5 accounts' settings synced to Saved Messages.**")

        if cl in ("help", "cmds"):
            return await fb(e, HELP, d=None)

        if cl in ("gcmsgs", "gc reply"):
            list_txt = "\n".join([f"**{i+1}.** {m}" for i, m in enumerate(st["gc_replies"])])
            return await fb(e, f"👥 **[Acc {acc_id} - 5 GROUP AUTO-REPLIES]**\n{list_txt}\n\n✏️ Change: `*setgc <1-5> <msg>`", d=None)

        if cl.startswith("setgc"):
            parts = c.split(maxsplit=2)
            if len(parts) >= 3 and parts[1].isdigit() and 1 <= int(parts[1]) <= 5:
                st["gc_replies"][int(parts[1]) - 1] = parts[2].strip()
                save_cfg()
                return await fb(e, f"✅ [Acc {acc_id}] GC Reply {parts[1]} updated.")

        if cl in ("dmmsgs", "dm reply"):
            list_txt = "\n".join([f"**{i+1}.** {m}" for i, m in enumerate(st["dm_replies"])])
            return await fb(e, f"💬 **[Acc {acc_id} - 5 DM AUTO-REPLIES]**\n{list_txt}\n\n✏️ Change: `*setdm <1-5> <msg>`", d=None)

        if cl.startswith("setdm"):
            parts = c.split(maxsplit=2)
            if len(parts) >= 3 and parts[1].isdigit() and 1 <= int(parts[1]) <= 5:
                st["dm_replies"][int(parts[1]) - 1] = parts[2].strip()
                save_cfg()
                return await fb(e, f"✅ [Acc {acc_id}] DM Reply {parts[1]} updated.")

        # =================================================================
        # REACTION COMMANDS (*target react, *stop target react, *react all, *stop all react)
        # =================================================================
        if cl.startswith("setreact "):
            emoji = c[9:].strip()
            if emoji:
                st["auto_reaction"] = emoji
                save_cfg()
                return await fb(e, f"🔥 **[Acc {acc_id}] Reaction emoji set to:** {emoji}")

        if cl == "stop target react" or cl.startswith("stop target react "):
            return await toggle_target(client, acc_id, e, c[17:], "t_react", "Target React", True)

        if cl == "target react" or cl.startswith("target react "):
            return await toggle_target(client, acc_id, e, c[12:], "t_react", "Target React", False)

        if cl in ("stop all react", "stop react all") or cl.startswith(("stop all react ", "stop react all ")):
            arg_part = c[14:] if cl.startswith("stop all react") else c[14:]
            toks = tokenize_args(arg_part)
            if not toks:
                st["react_chats"].clear()
                st["t_react"].clear()
                st["unjoined_refs"].clear()
                st["poll_last_id"].clear()
                save_cfg()
                return await fb(e, f"🛑 **[Acc {acc_id}] All reaction commands stopped globally.**")
            stopped_names = []
            for tok in toks:
                tcid, glabel = await resolve_chat_token(client, st, tok, record_unjoined=False)
                if tcid is not None:
                    st["react_chats"].discard(tcid)
                    st["t_react"].pop(tcid, None)
                    st["unjoined_refs"].pop(str(tcid), None)
                    st["poll_last_id"].pop(tcid, None)
                    stopped_names.append(glabel or str(tcid))
            save_cfg()
            return await fb(e, f"🛑 **[Acc {acc_id}] Reactions stopped for:** {', '.join(stopped_names) or 'Target'}")

        if cl == "react all" or cl.startswith("react all "):
            toks = tokenize_args(c[9:])
            if not toks:
                st["react_chats"].add(cid)
                save_cfg()
                return await fb(e, f"🔥 **[Acc {acc_id}] React All ON** ({st['auto_reaction']}) in current chat.")
            added_names = []
            for tok in toks:
                tcid, glabel = await resolve_chat_token(client, st, tok, record_unjoined=True)
                if tcid is not None:
                    st["react_chats"].add(tcid)
                    added_names.append(glabel or str(tcid))
            save_cfg()
            if not added_names:
                return await fb(e, "⚠️ **Could not resolve target group/channel link or username.**")
            return await fb(e, f"🔥 **[Acc {acc_id}] React All ON** ({st['auto_reaction']}) for: {', '.join(added_names)}")

        # STOPALL (Scoped only to this acc_id)
        for pfx in ("stopall", "stop all", "clearall"):
            if cl == pfx or cl.startswith(pfx + " "):
                tcid, glabel = await resolve_target_chat_from_arg(client, st, cid, c[len(pfx):])
                stop_nc_task(st, tcid)
                st["reply_chats"].discard(tcid)
                st["mute_chats"].discard(tcid)
                st["lock_chats"].discard(tcid)
                st["del_name_chats"].discard(tcid)
                st["pin_chats"].discard(tcid)
                st["pin_del_chats"].discard(tcid)
                st["pin_exempts"].discard(tcid)
                st["react_chats"].discard(tcid)
                st["unjoined_refs"].pop(str(tcid), None)
                for key in ("t_reply", "t_mute", "t_lock", "t_nc_r", "t_nc_m", "t_nc_l", "t_delname", "t_react"):
                    st[key].pop(tcid, None)
                save_cfg()
                return await fb(e, f"🛑 **[Acc {acc_id}] All features stopped{f' in {glabel}' if glabel else ''}.**")

        # STOPNC (Scoped only to this acc_id)
        for pfx in ("stopnc", "stop nc", "nc off"):
            if cl == pfx or cl.startswith(pfx + " "):
                tcid, glabel = await resolve_target_chat_from_arg(client, st, cid, c[len(pfx):])
                stop_nc_task(st, tcid)
                return await fb(e, f"🛑 [Acc {acc_id}] NC Stopped{f' in {glabel}' if glabel else ''}.")

        # NC START (Scoped only to this acc_id)
        if (cl == "nc" or cl.startswith("nc ")) and not cl.startswith(("nc reply", "nc mute", "nc lock", "ncr", "ncm", "ncl")):
            sub_arg = c[2:].strip()
            if sub_arg.lower() in ("setup", "add"):
                stop_nc_task(st, cid)
                st["nc_setup"][cid] = {"names": [], "pid": e.id}
                return await fb(e, f"📝 **[Acc {acc_id} Auto-NC Setup]** Send 5 names one by one.\n👉 **Send Name 1 of 5:**", d=None)
            tcid, glabel = cid, None
            toks = tokenize_args(sub_arg)
            if toks:
                maybe_cid, maybe_lbl = await resolve_chat_token(client, st, toks[-1])
                if maybe_cid and (str(maybe_cid).startswith("-100") or maybe_cid < 0 or any(
                    d["id"] == maybe_cid and d["is_group"] for d in st["dialog_cache"]["items"]
                )):
                    tcid, glabel = maybe_cid, maybe_lbl
                    sub_arg = sub_arg[:sub_arg.rfind(toks[-1])].strip().rstrip('"').rstrip("'")
            names = [x.strip() for x in sub_arg.split("|")] if "|" in sub_arg else ([sub_arg] if sub_arg else st["nc_titles"])
            start_nc(client, st, tcid, names)
            return await fb(e, f"🚀 **[Acc {acc_id}] NC Started{f' in {glabel}' if glabel else ''}.**")

        # PINNING COMMANDS (Scoped only to this acc_id)
        if cl == "pinall":
            st["pin_all"] = True; save_cfg(); return await fb(e, f"📌 [Acc {acc_id}] Global Pin ON")
        if cl in ("stop pinall", "unpinall"):
            st["pin_all"] = False; save_cfg(); return await fb(e, f"🛑 [Acc {acc_id}] Global Pin OFF")
        if cl == "pin except" or cl.startswith("pin except "):
            tcid, glabel = await resolve_target_chat_from_arg(client, st, cid, c[10:])
            st["pin_exempts"].add(tcid); st["pin_chats"].discard(tcid); save_cfg()
            return await fb(e, f"🛡️ [Acc {acc_id}] Pin Exception ON{f' ({glabel})' if glabel else ''}")
        if cl == "stop pin except" or cl.startswith("stop pin except "):
            tcid, glabel = await resolve_target_chat_from_arg(client, st, cid, c[15:])
            st["pin_exempts"].discard(tcid); save_cfg()
            return await fb(e, f"🛑 [Acc {acc_id}] Pin Exception OFF{f' ({glabel})' if glabel else ''}")
        if cl == "pindelall":
            st["pin_del_all"] = True; save_cfg(); return await fb(e, f"🗑️ [Acc {acc_id}] Global Pin-Del ON")
        if cl == "stop pindelall":
            st["pin_del_all"] = False; save_cfg(); return await fb(e, f"🛑 [Acc {acc_id}] Global Pin-Del OFF")
        if cl in ("pindel", "pindel on") or cl.startswith("pindel "):
            tcid, glabel = await resolve_target_chat_from_arg(client, st, cid, c[6:])
            st["pin_del_chats"].add(tcid); save_cfg()
            return await fb(e, f"✅ [Acc {acc_id}] Pin-Del ON{f' ({glabel})' if glabel else ''}")
        if cl == "stop pindel" or cl.startswith("stop pindel "):
            tcid, glabel = await resolve_target_chat_from_arg(client, st, cid, c[11:])
            st["pin_del_chats"].discard(tcid); save_cfg()
            return await fb(e, f"🛑 [Acc {acc_id}] Pin-Del OFF{f' ({glabel})' if glabel else ''}")

        if cl.startswith(("stop pin", "unpin")):
            return await toggle_pin(client, acc_id, e, c[8:].strip() if cl.startswith("stop pin") else c[5:].strip(), True)
        if cl in ("pin", "pin on"):
            return await toggle_pin(client, acc_id, e, "", False)
        if cl == "pin off":
            return await toggle_pin(client, acc_id, e, "", True)
        if cl.startswith("pin ") and not cl.startswith(("pinall", "pin except", "pindel")):
            return await toggle_pin(client, acc_id, e, c[4:].strip(), False)

        # TARGET COMMANDS (Scoped only to this acc_id)
        target_routes = [
            ("stop target nc reply", "t_nc_r", "Target NC Reply", True),
            ("stop target nc mute", "t_nc_m", "Target NC Mute", True),
            ("stop target nc lock", "t_nc_l", "Target NC Lock", True),
            ("stop target delname", "t_delname", "Target DelName", True),
            ("target nc reply", "t_nc_r", "Target NC Reply", False),
            ("target nc mute", "t_nc_m", "Target NC Mute", False),
            ("target nc lock", "t_nc_l", "Target NC Lock", False),
            ("target delname", "t_delname", "Target DelName", False),
            ("stop target reply", "t_reply", "Target Reply", True),
            ("stop target mute", "t_mute", "Target Mute", True),
            ("stop target lock", "t_lock", "Target Lock", True),
            ("target reply", "t_reply", "Target Reply", False),
            ("target mute", "t_mute", "Target Mute", False),
            ("target lock", "t_lock", "Target Lock", False),
        ]
        for pfx, dkey, lbl, is_stp in target_routes:
            if cl == pfx or cl.startswith(pfx + " "):
                return await toggle_target(client, acc_id, e, c[len(pfx):], dkey, lbl, is_stp)

        # CHAT-WIDE TOGGLES (Scoped only to this acc_id)
        chat_toggles = [
            ("delname", "del_name_chats", "Auto-Del Name", True),
            ("delncmsg", "del_name_chats", "Auto-Del Name", True),
            ("stop delname", "del_name_chats", "Auto-Del Name", False),
            ("replyall", "reply_chats", "ReplyAll", True),
            ("stop replyall", "reply_chats", "ReplyAll", False),
            ("unreplyall", "reply_chats", "ReplyAll", False),
            ("mutegc", "mute_chats", "MuteGC", True),
            ("stop mutegc", "mute_chats", "MuteGC", False),
            ("unmutegc", "mute_chats", "MuteGC", False),
            ("lockall", "lock_chats", "LockAll", True),
            ("stop lockall", "lock_chats", "LockAll", False),
            ("unlockall", "lock_chats", "LockAll", False),
            ("reply", "reply_chats", "DM Reply", True),
            ("stop reply", "reply_chats", "DM Reply", False),
            ("unreply", "reply_chats", "DM Reply", False),
            ("lock", "lock_chats", "DM Lock", True),
            ("stop lock", "lock_chats", "DM Lock", False),
            ("unlock", "lock_chats", "DM Lock", False),
        ]
        for pfx, set_key, lbl, enable in chat_toggles:
            if cl == pfx or cl.startswith(pfx + " "):
                tcid, glabel = await resolve_target_chat_from_arg(client, st, cid, c[len(pfx):])
                if enable:
                    st[set_key].add(tcid)
                else:
                    st[set_key].discard(tcid)
                save_cfg()
                return await fb(e, f"{'✅' if enable else '🛑'} [Acc {acc_id}] {lbl} {'ON' if enable else 'OFF'}{f' ({glabel})' if glabel else ''}")

        if cl == "mute" or cl.startswith("mute "):
            tcid, glabel = await resolve_target_chat_from_arg(client, st, cid, c[4:])
            st["mute_chats"].add(tcid); st["unmute_exempts"].discard(tcid); save_cfg()
            return await fb(e, f"✅ [Acc {acc_id}] DM Mute ON{f' ({glabel})' if glabel else ''}")
        if cl in ("stop mute", "unmute") or cl.startswith(("stop mute ", "unmute ")):
            arg_part = c[9:] if cl.startswith("stop mute") else c[6:]
            tcid, glabel = await resolve_target_chat_from_arg(client, st, cid, arg_part)
            st["mute_chats"].discard(tcid); st["unmute_exempts"].add(tcid); save_cfg()
            return await fb(e, f"🛑 [Acc {acc_id}] DM Mute OFF{f' ({glabel})' if glabel else ''}")
        if cl == "muteall":
            st["mute_all"] = True; save_cfg(); return await fb(e, f"🔒 [Acc {acc_id}] Mute All DMs ON")
        if cl == "stop muteall":
            st["mute_all"] = False; save_cfg(); return await fb(e, f"🔓 [Acc {acc_id}] Mute All DMs OFF")

        if cl == "status" or cl.startswith("status "):
            tcid, glabel = await resolve_target_chat_from_arg(client, st, cid, c[6:])
            active = []
            if tcid in st["reply_chats"]: active.append("Reply")
            if tcid in st["mute_chats"]: active.append("Mute")
            if tcid in st["lock_chats"]: active.append("Lock")
            if tcid in st["pin_chats"] or st["pin_all"]: active.append("Pin")
            if tcid in st["del_name_chats"]: active.append("DelName")
            if tcid in st["nc_tasks"]: active.append("NC")
            if tcid in st["react_chats"]: active.append(f"ReactAll({st['auto_reaction']})")
            if st["t_react"].get(tcid): active.append(f"TReact({len(st['t_react'][tcid])})")
            if st["t_reply"].get(tcid): active.append(f"TReply({len(st['t_reply'][tcid])})")
            if st["t_mute"].get(tcid): active.append(f"TMute({len(st['t_mute'][tcid])})")
            if st["t_lock"].get(tcid): active.append(f"TLock({len(st['t_lock'][tcid])})")
            return await fb(e, f"⚙️ **[Acc {acc_id}] Status{f' ({glabel})' if glabel else ''}:** {', '.join(active) or 'None'}", d=None)

    @client.on(events.NewMessage(incoming=True))
    @client.on(events.MessageEdited(incoming=True))
    async def on_incoming(e):
        if not ACCOUNT_STATES.get(acc_id, False):
            return
        cid, sid = e.chat_id, e.sender_id
        my_id = MY_IDS.get(acc_id)
        if cid is None or sid == my_id:
            return

        st = get_st(acc_id)
        is_monitored = (
            cid in st["t_nc_l"] or cid in st["t_nc_m"] or cid in st["t_lock"] or cid in st["lock_chats"] or
            cid in st["t_mute"] or cid in st["mute_chats"] or cid in st["t_nc_r"] or
            cid in st["reply_chats"] or cid in st["t_reply"] or cid in st["del_name_chats"] or
            cid in st["t_delname"] or (e.is_private and st["mute_all"]) or
            should_delete_pin_notification(st, cid) or cid in st["nc_tasks"] or
            cid in st["react_chats"] or cid in st["t_react"]
        )
        if not is_monitored and not is_pin_action(e):
            return

        action = getattr(e, "action", None)
        if action is not None:
            if type(action).__name__ == "MessageActionChatEditTitle":
                if is_target_user(st, cid, sid) or cid in st["del_name_chats"]:
                    try:
                        await e.delete()
                    except Exception:
                        pass
                    if is_target_user(st, cid, sid) and (cid in st["nc_tasks"] or cid in st["t_nc_l"] or cid in st["t_nc_m"]):
                        titles = st["nc_titles"]
                        asyncio.create_task(execute_title_change(client, st, cid, titles[0] if titles else "🔥 ALPHA ZONE 🔥"))
                    return
            if is_pin_action(e):
                await handle_pin_notification(client, acc_id, e)
                return

        should_delete = False
        if cid in st["t_nc_l"] and sid in st["t_nc_l"][cid]:
            should_delete = True
        elif cid in st["t_nc_m"] and sid in st["t_nc_m"][cid]:
            should_delete = True
            asyncio.create_task(execute_title_change(client, st, cid, f"🚫 MUTED: User {sid}"))
        elif cid in st["t_lock"] and sid in st["t_lock"][cid]:
            should_delete = True
        elif cid in st["lock_chats"]:
            should_delete = True
        elif cid in st["t_mute"] and sid in st["t_mute"][cid]:
            should_delete = True
        elif cid in st["mute_chats"] or (e.is_private and st["mute_all"] and cid not in st["unmute_exempts"]):
            should_delete = True

        if should_delete:
            if (cid, e.id) not in st["recent_deleted"]:
                st["recent_deleted"].add((cid, e.id))
                try:
                    await e.delete()
                except Exception:
                    pass
            return

        # Auto-Reaction (for joined groups/channels & target users)
        if cid in st["react_chats"] or (cid in st["t_react"] and sid in st["t_react"][cid]):
            asyncio.create_task(send_auto_reaction(client, st, cid, e.id))

        # Prevent your own other accounts from triggering auto-replies on each other
        if sid and sid in MY_IDS.values():
            return

        if cid in st["t_nc_r"] and sid in st["t_nc_r"][cid]:
            try:
                mention = await get_mention(st, e)
                gc_msgs = st["gc_replies"]
                idx = st["gc_index"].get(cid, 0)
                st["gc_index"][cid] = (idx + 1) % len(gc_msgs)
                await e.reply(f"🎯 {mention} {gc_msgs[idx % len(gc_msgs)]}", parse_mode="md")
                asyncio.create_task(execute_title_change(client, st, cid, f"🎯 TARGET ALERT: {sid}"))
            except Exception:
                pass

        if cid in st["reply_chats"] or (cid in st["t_reply"] and sid in st["t_reply"][cid]):
            now = time.time()
            if now - st["last_rep"].get((cid, sid), 0) < COOLDOWN:
                return
            st["last_rep"][(cid, sid)] = now
            try:
                mention = await get_mention(st, e)
                msgs = st["dm_replies"] if e.is_private else st["gc_replies"]
                idx_dict = st["dm_index"] if e.is_private else st["gc_index"]
                idx = idx_dict.get(cid, 0)
                idx_dict[cid] = (idx + 1) % len(msgs)
                await e.reply(f"{mention} {msgs[idx % len(msgs)]}", parse_mode="md")
            except Exception:
                pass

# =====================================================================
# MAIN BOOTSTRAP (CLOUD RESTORE FIRST, THEN START ACCOUNTS)
# =====================================================================
async def main():
    global STOP_EVENT, RENDER_SERVER, CACHE_CLEAN_TASK, UNJOINED_POLL_TASK
    STOP_EVENT = asyncio.Event()
    load_cfg()
    clear_cache_files()
    CACHE_CLEAN_TASK = asyncio.create_task(auto_cache_cleaner_worker(180))
    RENDER_SERVER = await start_render_health_server()

    # Connect Account 1 first to restore latest cloud settings from Saved Messages
    ok1, _ = await start_account(1)
    if ok1 and 1 in CLIENTS:
        restored = await restore_cfg_from_cloud(CLIENTS[1])
        if restored and not ACCOUNT_STATES.get(1, True):
            await stop_account(1)

    if not any(ACCOUNT_STATES.values()):
        ACCOUNT_STATES[1] = True
        save_cfg()

    for aid in [a["id"] for a in ACCOUNTS_CONFIG]:
        if ACCOUNT_STATES.get(aid, False):
            await start_account(aid)
            await asyncio.sleep(1.0)

    UNJOINED_POLL_TASK = asyncio.create_task(unjoined_public_reaction_worker())
    print("\n🚀 USERBOT RUNNING (Per-Account Isolated + Unjoined React + Cloud Sync + Zero-Leak)\n")
    await STOP_EVENT.wait()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda: STOP_EVENT.set() if STOP_EVENT else None)
        except Exception:
            pass
    try:
        loop.run_until_complete(main())
    except KeyboardInterrupt:
        pass
    finally:
        save_cfg()
        clear_cache_files()
        for cl in list(CLIENTS.values()):
            if cl.is_connected():
                loop.run_until_complete(cl.disconnect())
