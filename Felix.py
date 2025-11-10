# Felix.py
# Telethon userbot: plugin hot-reload yang stabil, anti-spam, rollback on error.
# - Place this file in project root
# - Create folder "plugins" with plugin files (eg. plugins/ping.py)
# - Create config.py with API_ID, API_HASH, SESSION, OWNER_ID, RESELLERS
#
# Plugin API (recommended):
#   def setup(client, db, logger):
#       # register handlers via @client.on or client.add_event_handler(...)
#       # return (optional) list_of_handlers  # not required; loader detects added handlers
#   async def teardown():  # optional
#       # cleanup if needed
#
# This loader will:
#  - load all plugins on start
#  - watch plugins/ for changes and apply single-plugin reloads
#  - remove old handlers before installing new ones
#  - if reload fails, rollback to previous version if available

import os
import sys
import json
import time
import asyncio
import importlib.util
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo
from telethon import TelegramClient, events
from colorama import Fore, Style, init as color_init

try:
    from config import API_ID, API_HASH, SESSION, OWNER_ID, RESELLERS, PREFIXES
except Exception as e:
    print("Missing config.py or variables. Create config.py with API_ID, API_HASH, SESSION")
    raise

# ----------------------------
# init
# ----------------------------
color_init(autoreset=True)
DB_PATH = Path("database.json")
PLUGINS_DIR = Path("plugins")
PLUGINS_DIR.mkdir(exist_ok=True)
AUTOSAVE_INTERVAL = 30        # seconds
PLUGIN_CHECK_INTERVAL = 1.0   # seconds (watcher tick)
RELOAD_DEBOUNCE = 0.6        # seconds to debounce rapid file changes

client = TelegramClient(SESSION, API_ID, API_HASH)

# ----------------------------
# waktuWIB function (mimic JS formatting)
# ----------------------------
def waktuWIB():
    now = datetime.now(ZoneInfo("Asia/Jakarta"))
    # mimic: weekday short, year numeric, month short, day 2-digit, hour 2-digit, minute second
    formatted = now.strftime("%a, %Y %b %d, %I:%M:%S %p")
    # append GMT+0700 and label similar to JS version
    return f"[{formatted} GMT+0700 (Western Indonesia Time - WIB)]"

# ----------------------------
# logger similar style
# ----------------------------
class ConnLogger:
    def info(self, msg):
        print(f"{Fore.GREEN}{Style.BRIGHT}INFO{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}{waktuWIB()}: {Fore.CYAN}{msg}")
    def warn(self, msg):
        print(f"{Fore.MAGENTA}{Style.BRIGHT}WARNING{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}{waktuWIB()}: {Fore.YELLOW}{msg}")
    def error(self, msg):
        print(f"{Fore.RED}{Style.BRIGHT}ERROR{Style.RESET_ALL} {Fore.WHITE + Style.BRIGHT}{waktuWIB()}: {Fore.RED}{msg}")

logger = ConnLogger()

# ----------------------------
# Simple JSON DB (async-friendly)
# ----------------------------
class JSONDB:
    def __init__(self, path: Path):
        self.path = path
        self.data = None
        self.READ = False

    async def load(self):
        if self.READ:
            while self.READ:
                await asyncio.sleep(0.05)
        if self.data is not None:
            return self.data
        self.READ = True
        if not self.path.exists():
            self.data = {}
            self.READ = False
            return self.data
        try:
            with open(self.path, "r", encoding="utf-8") as f:
                self.data = json.load(f)
        except Exception:
            self.data = {}
        self.READ = False
        return self.data

    async def save(self):
        try:
            if self.data is None:
                return
            tmp = str(self.path) + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
            os.replace(tmp, str(self.path))
        except Exception as e:
            logger.error(f"Save database error: {e}")

db = JSONDB(DB_PATH)

# ----------------------------
# plugin store structures
# ----------------------------
# plugin_records[name] = {
#   'module': module_obj,
#   'path': Path,
#   'mtime': float,
#   'handlers': [callables],
#   'last_change': float,  # used for debounce
#   'status': 'ok'|'error'
# }
plugin_records = {}

# helper: safely load module from file path, return module or None + exception
def load_module_from_path(name: str, path: Path):
    try:
        spec = importlib.util.spec_from_file_location(f"plugin_{name}", str(path))
        if spec is None or spec.loader is None:
            raise ImportError("Cannot create spec")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        # register in sys.modules so plugins can import relative modules if needed
        sys.modules[f"plugin_{name}"] = module
        return module, None
    except Exception as e:
        return None, e

# helper: compare event handlers before/after to detect added handlers
def get_handlers_snapshot():
    # Telethon has client.list_event_handlers() returning list of handler objects.
    # We'll keep the function objects to be able to remove them later.
    try:
        handlers = client.list_event_handlers()
        # return list of callables (the first element of tuple), but list_event_handlers returns wrapper objects.
        # We'll store the actual handler function objects where possible.
        # Each item is a tuple (callback, eventbuilder) or Handler object depending on Telethon version
        # We'll keep representation to remove via client.remove_event_handler(callback)
        snapshot = []
        for h in handlers:
            # Telethon's list_event_handlers may return either (callback, event) or handler objects
            if isinstance(h, tuple) or isinstance(h, list):
                # (callback, event)
                callback = h[0]
                snapshot.append(callback)
            else:
                # handler object — try to get .callback
                cb = getattr(h, "callback", None)
                if cb:
                    snapshot.append(cb)
                else:
                    # fallback: append raw h
                    snapshot.append(h)
        return snapshot
    except Exception:
        # best-effort
        return []

# unregister handlers list
def remove_handlers(handlers):
    for cb in handlers:
        try:
            client.remove_event_handler(cb)
        except Exception:
            # sometimes Telethon stores wrapper objects; try best-effort removal
            try:
                client.remove_event_handler(cb, strict=False)
            except Exception:
                pass

# register plugin:
# - call setup(module) and detect newly added handlers by snapshot diff
def install_plugin(name: str, path: Path):
    # take snapshot of handlers before
    before = get_handlers_snapshot()
    module, err = load_module_from_path(name, path)
    if module is None:
        return None, err
    # Call setup
    try:
        # Allow plugin.setup to optionally return list of handlers; prefer that if provided.
        ret = None
        if hasattr(module, "setup") and callable(module.setup):
            try:
                ret = module.setup(client, db, logger)
            except TypeError:
                # maybe plugin.setup is async? support both sync and async
                coro = module.setup(client, db, logger)
                if asyncio.iscoroutine(coro):
                    ret = asyncio.get_event_loop().run_until_complete(coro)
            # ret may be None or list
        # compute newly added handlers
        after = get_handlers_snapshot()
        new_handlers = [h for h in after if h not in before]
        if isinstance(ret, (list, tuple)):
            # prefer handlers returned by plugin if they are functions
            handlers = [h for h in ret if callable(h)]
            # if returned empty but we detected new handlers, use detected ones
            if not handlers and new_handlers:
                handlers = new_handlers
        else:
            handlers = new_handlers
        return {
            "module": module,
            "path": path,
            "mtime": path.stat().st_mtime,
            "handlers": handlers,
            "status": "ok",
            "last_change": time.time()
        }, None
    except Exception as e:
        # if setup failed, best-effort cleanup of any partial handlers newly added
        after = get_handlers_snapshot()
        new_handlers = [h for h in after if h not in before]
        remove_handlers(new_handlers)
        return None, e

# unregister and remove module
def unload_plugin_record(record):
    try:
        # call plugin teardown if exists (sync or async)
        module = record.get("module")
        if module:
            try:
                if hasattr(module, "teardown") and callable(module.teardown):
                    res = module.teardown()
                    if asyncio.iscoroutine(res):
                        asyncio.get_event_loop().run_until_complete(res)
            except Exception:
                pass
            # remove handlers tracked
            handlers = record.get("handlers", []) or []
            remove_handlers(handlers)
            # remove module from sys.modules
            modname = getattr(module, "__name__", None)
            if modname and modname in sys.modules:
                try:
                    del sys.modules[modname]
                except Exception:
                    pass
    except Exception:
        pass

# rollback helper: reinstall old record's handlers (by re-importing old module file)
def rollback_plugin(old_record):
    # attempt to reinstall previous module by executing its file again
    try:
        path = old_record["path"]
        name = path.stem
        # attempt to load module again
        newrec, err = install_plugin(name, path)
        if newrec:
            return newrec
    except Exception:
        pass
    return None
    
@client.on(events.NewMessage)
async def global_prefix_handler(event):
    msg_text = event.raw_text.strip()
    if not msg_text:
        return
    prefix_used = next((p for p in PREFIXES if msg_text.startswith(p)), None)
    if not prefix_used:
        return
    event._prefix_used = prefix_used
    event._command = msg_text[len(prefix_used):].split()[0].lower()
    # plugin handlers still receive event

# initial load of all plugins
def initial_load():
    for file in sorted(PLUGINS_DIR.glob("*.py")):
        name = file.stem
        rec, err = install_plugin(name, file)
        if rec:
            plugin_records[name] = rec
            logger.info(f"Plugin '{name}' aktif ✅")
        else:
            plugin_records[name] = {
                "module": None,
                "path": file,
                "mtime": file.stat().st_mtime if file.exists() else 0,
                "handlers": [],
                "status": "error",
                "last_change": time.time()
            }
            logger.error(f"Plugin '{name}' gagal dimuat: {err}")

# watcher: monitor only changed files; debounce changes per file; safe reload; rollback if fail
async def plugin_watcher():
    # map name -> last seen mtime
    last_mtime = {name: rec["mtime"] for name, rec in plugin_records.items()}
    # ensure entries for existing files not in plugin_records
    for p in PLUGINS_DIR.glob("*.py"):
        if p.stem not in last_mtime:
            last_mtime[p.stem] = p.stat().st_mtime

    while True:
        try:
            await asyncio.sleep(PLUGIN_CHECK_INTERVAL)
            # list current plugin files
            current_files = {p.stem: p for p in PLUGINS_DIR.glob("*.py")}

            # detect deleted
            deleted = [name for name in list(plugin_records.keys()) if name not in current_files]
            for name in deleted:
                rec = plugin_records.pop(name, None)
                if rec:
                    unload_plugin_record(rec)
                last_mtime.pop(name, None)
                logger.warn(f"Plugin '{name}' dihapus ❌")

            # detect new or changed
            for name, path in current_files.items():
                try:
                    mtime = path.stat().st_mtime
                except Exception:
                    continue
                prev_mtime = last_mtime.get(name)
                # new plugin
                if prev_mtime is None:
                    # debounce: wait small time to avoid editor multiple saves
                    nowt = time.time()
                    # briefly wait RELOAD_DEBOUNCE before applying
                    await asyncio.sleep(RELOAD_DEBOUNCE)
                    # re-get mtime after debounce
                    try:
                        mtime2 = path.stat().st_mtime
                    except Exception:
                        continue
                    if mtime2 != mtime:
                        # file changed again quickly; skip this tick, next loop will handle
                        last_mtime[name] = mtime2
                        continue
                    # install
                    rec, err = install_plugin(name, path)
                    if rec:
                        plugin_records[name] = rec
                        last_mtime[name] = rec["mtime"]
                        logger.info(f"Plugin '{name}' dimuat ✅")
                    else:
                        # mark as error but don't spam
                        plugin_records[name] = {
                            "module": None,
                            "path": path,
                            "mtime": mtime,
                            "handlers": [],
                            "status": "error",
                            "last_change": time.time()
                        }
                        logger.error(f"Plugin '{name}' gagal dimuat: {err}")
                        last_mtime[name] = mtime
                    continue

                # changed plugin
                if mtime != prev_mtime:
                    # debounce a bit
                    await asyncio.sleep(RELOAD_DEBOUNCE)
                    try:
                        mtime2 = path.stat().st_mtime
                    except Exception:
                        continue
                    if mtime2 != mtime:
                        last_mtime[name] = mtime2
                        continue
                    # attempt reload safely
                    old_record = plugin_records.get(name)
                    # unregister old handlers first to avoid duplicates
                    if old_record:
                        unload_plugin_record(old_record)
                    # try install new
                    rec, err = install_plugin(name, path)
                    if rec:
                        plugin_records[name] = rec
                        last_mtime[name] = rec["mtime"]
                        logger.info(f"Plugin '{name}' diperbarui 🔁")
                    else:
                        # install failed; attempt rollback to old_record (if existed)
                        if old_record:
                            # attempt re-install by re-executing old file (it still exists)
                            rb = rollback_plugin(old_record)
                            if rb:
                                plugin_records[name] = rb
                                last_mtime[name] = rb["mtime"]
                                logger.warn(f"Plugin '{name}' reload gagal — rollback sukses")
                            else:
                                # cannot rollback, mark as error and continue
                                plugin_records[name] = {
                                    "module": None,
                                    "path": path,
                                    "mtime": mtime,
                                    "handlers": [],
                                    "status": "error",
                                    "last_change": time.time()
                                }
                                logger.error(f"Plugin '{name}' reload gagal dan rollback gagal: {err}")
                                last_mtime[name] = mtime
                        else:
                            plugin_records[name] = {
                                "module": None,
                                "path": path,
                                "mtime": mtime,
                                "handlers": [],
                                "status": "error",
                                "last_change": time.time()
                            }
                            logger.error(f"Plugin '{name}' reload gagal: {err}")
                            last_mtime[name] = mtime

            # loop continues
        except Exception as e:
            logger.error(f"Watcher fatal error: {e}")
            await asyncio.sleep(1)

# ----------------------------
# basic help command to list plugin status
# ----------------------------
@client.on(events.NewMessage(pattern=r"^\.help$", outgoing=True))
async def show_plugins(event):
    lines = []
    for name, rec in sorted(plugin_records.items()):
        status = rec.get("status", "ok") if rec else "error"
        lines.append(f"• {name} — {status}")
    text = "📦 Plugin status:\n" + ("\n".join(lines) if lines else "(no plugin)")
    await event.reply(text)

# ----------------------------
# main
# ----------------------------
async def main():
    await db.load()
    await client.start()
    logger.info("Userbot berhasil terhubung!")

    # initial load
    initial_load()

    # start watcher and autosave
    watcher = asyncio.create_task(plugin_watcher())
    async def autosave_loop():
        while True:
            await asyncio.sleep(AUTOSAVE_INTERVAL)
            await db.save()
    autosave = asyncio.create_task(autosave_loop())

    try:
        await client.run_until_disconnected()
    finally:
        watcher.cancel()
        autosave.cancel()
        # try save db before exit
        try:
            await db.save()
        except Exception:
            pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.warn("Dihentikan manual oleh user.")
