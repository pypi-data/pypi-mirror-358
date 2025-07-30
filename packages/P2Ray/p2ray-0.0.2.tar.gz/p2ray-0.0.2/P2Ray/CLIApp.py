from typing import Optional, Any

import os
import json
import time
import logging
import textwrap
import tempfile
import subprocess

from tabulate import tabulate

import pyperclip

from P2Ray.config_manager import ConfigManager, ProxyConfig
from P2Ray.protocol_test import config_to_v2ray_outbound
from P2Ray.menu import Menu, Option, Separator
from P2Ray.uri_encoder import config_to_uri
from P2Ray.settings import SettingsDict
from P2Ray.settings_menu import SettingsMenu
from P2Ray.utils import (
    strip_emojis, show_qr, test_speed, 
    color, colorp, underline, styled_header,
    press_enter
    )

DISCONNECT_SLEEP = 2.0



class CLIApp:
    def __init__(
        self,
        config_db_path: str,
        archive_db_path: str,
        settings: SettingsDict,
        settings_path: str,
        logger: logging.Logger
    ) -> None:
        """
        :param config_db_path: Path to active configs JSON.
        :param archive_db_path: Path to archived configs JSON.
        :param settings: Loaded settings dict (may be modified at runtime).
        :param settings_path: File path to write back updates.
        """
        # 1) Initialize ConfigManagers with the provided files
        self.manager:     ConfigManager   = ConfigManager(db_path=config_db_path)
        self.arc_manager: ConfigManager   = ConfigManager(db_path=archive_db_path)

        # 2) Settings
        self.settings      = settings
        self.settings_path = settings_path
        self.logger        = logger  # <── Save logger for use in methods

        # 3) CLI application state
        self.running:   bool   = True
        self.main_menu: Menu   = self.create_main_menu()

        # 4) VPN connection state
        self.connected_id: Optional[str] = None
        self.system_proxy: bool          = False
        self.v2ray_proc                  = None  # subprocess handle
        
        # ─── Phase 5: Store settings into attributes ──────────────
        self.v2ray_binary     = self.settings.get("v2ray_path", "v2ray")
        self.default_timeout  = self.settings.get("default_timeout", 15.0)
        


    def create_main_menu(self) -> Menu:
        return Menu("P2Ray Config Manager", [
            Option(f"{underline("C")}onnect",          
                            "",                      self.connect, ["c"]),
            Option(f"{underline("D")}isconnect",       
                            "",                      self.disconnect, ["d"]),
            Option(f"{underline("T")}oggle Sys Proxy", 
                            "",                      self.toggle_system_proxy, ["t"]),
            Separator(),
            
            Option(f"{underline("L")}ist Configs",     
                                       "View configs",          self.list_configs,    ["l"]),
            Option("Test All",         "Latency test all",      self.test_all),
            Option("Add Configs",      "Import URIs",           self.add_configs),
            Option("Share",            "Share URI by ID",       self.share_uri),
            Option("Share All",        "Share All URIs",        self.share_all),
            Option("Log Con",          "Log connection",        self.log_connectivity),
            Separator(),
            
            Option("Archive Config",   "Archive Config",        self.archive_config),
            Option("Unarchive",        "Unrchive Config",       self.unarchive_config),
            Option("List Archive",     "",                      self.list_archive),
            Option("Remove Config",    "Delete by ID",          self.remove_config),
            Separator(),
            
            Option("Test Ping",        "",                      self.test_ping),
            Option("Test Speed",       "",                      self.test_speed),
            Separator(),
            
            Option("Settings",         "Application settings",  self.open_settings),
            # … other options …
        ])
    
    def exit_app(self) -> None:
        """Cleanup on exit."""
        self.disconnect()
        print("Goodbye!")
    
    
    # -------------------- State‐Aware Display --------------------
    def run(self) -> None:
        while self.running:
            status = self._connection_status_line()
            self.main_menu.display(status)
            selection = None
            while selection is None:
                selection = self.main_menu.get_selection()
            if selection == 0:
                self.running = False
                self.exit_app()
                break
            action = self.main_menu.options[selection - 1].action
            action()
            press_enter("Press Enter to return to main menu...")
    
    def _connection_status_line(self) -> str:
        if not self.connected_id:
            return color("[Not connected]", "red")
        mode = color("Set", "green") if self.system_proxy else color("Clear", "red")
        return f"[{self.connected_id}] System Proxy: {mode}"
    
    
    # ------------------ Connection Management --------------------
    def connect(self) -> None:
        """Option: Connect to a config (without or with system proxy)."""
        cfg_id = input("Enter ID to connect: ").strip()
        self._connect(cfg_id)
        
    def _connect(
        self, 
        cfg_id: str
        ) -> None:
        """Helper For Connection Logic."""
        cfg = self.manager.get_by_id(cfg_id)
        if not cfg:
            colorp("No such config.", "h red")
            return

        # 1) Write temporary v2ray JSON
        v2_conf: dict[str, Any] = {
            "inbounds": [{
                "port": 1081,
                "listen": "127.0.0.1",
                "protocol": "socks",
                "settings": {"auth": "noauth"}
            }],
            "outbounds": [config_to_v2ray_outbound(cfg._parsed)], # type: ignore
        }
        tmp = tempfile.NamedTemporaryFile("w+", suffix=".json", delete=False)
        json.dump(v2_conf, tmp)
        tmp.flush()

        # 2) Spawn v2ray process
        if self.v2ray_proc:
            self.v2ray_proc.kill()
        self.v2ray_proc = subprocess.Popen(
            [self.v2ray_binary, "-config", tmp.name],
            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
        )

        self.connected_id = cfg_id
        self.logger.debug(f"CONNECT: Spawning: {self.v2ray_binary} with config {tmp.name}")
        print(f"Connected to [{cfg_id}]")

        # 3) Apply system proxy if flagged
        if self.system_proxy:
            self._apply_system_proxy()

    def _disconnect(self) -> None:
        """
        Fully tear down any existing V2Ray connection and clear proxy.
        """
        if self.v2ray_proc:
            self.v2ray_proc.kill()
            self.v2ray_proc = None
        if self.system_proxy:
            # ensure proxy is truly cleared
            self._clear_system_proxy()
            
    def disconnect(self) -> None:
        """Tear down current connection and clear proxy."""
        if self.v2ray_proc:
            self.v2ray_proc.kill()
            self.v2ray_proc = None
        if self.system_proxy:
            self._clear_system_proxy()
        print(f"Disconnected from [{self.connected_id}]")
        self.connected_id = None

    def toggle_system_proxy(self) -> None:
        """Option: flip the system-proxy flag, apply immediately if connected."""
        self.system_proxy = not self.system_proxy
        if self.connected_id:
            if self.system_proxy:
                self._apply_system_proxy()
            else:
                self._clear_system_proxy()
        print("System proxy", "enabled" if self.system_proxy else "disabled")
        
    # ────────── Helpers for System Proxy ─────────────────────────────────────
    def _apply_system_proxy(self) -> None:
        # Windows example: winhttp
        subprocess.run(["netsh", "winhttp", "set", "proxy", "127.0.0.1:1081"])
        
    def _clear_system_proxy(self) -> None:
        subprocess.run(["netsh", "winhttp", "reset", "proxy"])  
        
    # ────────── Test Commands ────────────────────────────────────────────────
    def _is_connected(self) -> bool:
        """Return True if we believe a v2ray process is currently running for connected_id."""
        return bool(self.connected_id and self.v2ray_proc and self.v2ray_proc.poll() is None)

    def _choose_config_for_test(self) -> ProxyConfig | None:
        """
        Return the config to test:
        • If already connected, use that.
        • Otherwise prompt the user for an ID.
        """
        if self._is_connected() and self.connected_id:
            cfg = self.manager.get_by_id(self.connected_id)
            if not cfg:
                colorp(f"Config [{self.connected_id}] no longer exists.", "h red")
                press_enter()
            return cfg

        # Not connected: ask the user
        _id = input("Enter config ID to test: ").strip()
        cfg = self.manager.get_by_id(_id)
        if not cfg:
            colorp(f"No such config with ID {_id!r}", "h red")
        return cfg


    def test_ping(self) -> None:
        """Ping a config (connected or chosen), with full disconnect/reconnect."""
        cfg = self._choose_config_for_test()
        if not cfg:
            return

        cfg_id  = cfg.id
        had_sys = self.system_proxy

        # 1) Tear down any existing connection
        if self._is_connected():
            self._disconnect()
            time.sleep(DISCONNECT_SLEEP)

        # 2) Run the ping test
        latency = cfg.test(
            v2ray_binary=self.v2ray_binary,
            timeout=self.default_timeout
        )

        # 3) Reconnect if we had been connected
        if had_sys or cfg_id == self.connected_id:
            self._connect(cfg_id) # type: ignore
            if had_sys:
                self._apply_system_proxy()

        # 4) Display
        if latency is not None:
            print(f"Latency: {latency:.1f} ms")
        else:
            colorp("Ping failed.", "h red")


    def test_speed(self) -> None:
        # If no config is selected, prompt
        cfg = self._choose_config_for_test()
        if not cfg:
            return

        # 1. Fully disconnect proxy
        self._disconnect()

        # 2. Reconnect using selected config
        self._connect(cfg.id) # type: ignore

        # 3. Wait briefly to ensure system proxy applied
        time.sleep(DISCONNECT_SLEEP)

        # 4. Run the test
        try:
            mbps = test_speed(timeout=self.default_timeout)
            print(f"Download speed: {mbps:.2f} Mbps")
        except Exception as e:
            self.logger.exception("Speed test failed")
            print(color("Speed test failed.", "h red"))

        # No need to restore old state — we're now connected through our VPN
       
       
    def test_all(self) -> None:
        """
        Main-menu option: test every config, fully disconnecting and then restoring
        both the V2Ray process and system proxy state.
        """
        # 1) Remember previous connection state
        was_conn = self._is_connected()
        cfg_id   = self.connected_id
        had_sys  = self.system_proxy

        # 2) Fully tear down any existing connection
        if was_conn:
            self._disconnect()
            time.sleep(DISCONNECT_SLEEP)

        # 3) Run all tests
        self.manager.test_all(
            v2ray_binary=self.v2ray_binary,
            timeout=self.default_timeout
        )

        # 4) Restore the previous connection if it existed
        if was_conn and cfg_id:
            self._connect(cfg_id)
            if had_sys:
                self._apply_system_proxy()
             
    # -------------------------- Options --------------------------
    def log_connectivity(self) -> None:
        while True:
            _id = input("ID: ").strip()
            if _id.lower() == 'q':
                break
            try:
                self.manager.mark_working(config_id=_id)
            except ValueError:
                colorp("Invalid ID", "h red")
    
    
    def add_configs(self) -> None:
        print("\nAdd Configs: Type each config URI and ID. Type 'q' to stop.")
        added_count = 0
        
        while True:
            
            uri = input("URI: ").strip()
            if uri.lower() == 'q':
                break
            
            config_id = input("ID: ").strip() or None
            try:
                before = len(self.manager.configs)
                self.manager.add_from_uri(uri, config_id=config_id, verbose=True)
                if len(self.manager.configs) > before:
                    added_count += 1
            except ValueError as e:
                # parse_uri or add_from_uri can raise on invalid format or duplicate ID
                colorp(f" - Invalid URI or ID error: {e}", "h red")

        total = len(self.manager.configs)
        print(f"\nSummary: Added {added_count}. Total now: {total}")
        
            
    def list_configs(self) -> None:
        """List and interact with the main config database."""
        self._interactive_list(self.manager, "Main Configurations")
            

    def list_archive(self) -> None:
        """List and interact with the archived config database."""
        self._interactive_list(self.arc_manager, "Archived Configurations")
                

    def _interactive_list(self, mgr: ConfigManager, title: str) -> None:
        """
        Generic interactive listing screen for any ConfigManager.
        Renders a table of configs, shows available commands, and dispatches
        user input (sort, reverse, export, share, remove, archive, unarchive,
        edit, test, connect, toggle, quit).
        """
        
        # ─── Setup: field‐name aliases and command shortcuts ──────────────────
        FIELDS = [
            # (alias,   internal_key, display_title)
            ("i",       "id",           "ID"),
            ("re",      "remark",       "Remark"),
            ("lp",      "last_ping",    "Last Ping"),
            ("pc",      "ping_count",   "Ping Count"),
            ("ll",      "last_latency", "Last Latency"),
            ("wc",      "working_count","Working Count"),
            ("lw",      "last_work",    "Last Work"),
            ("t",       "type",         "Type"),
            ("at",      "add_time",     "Add Time"),
        ]
        
        headers_aliases = {alias: key for alias, key, _ in FIELDS}
        valid_fields    = [key   for _, key, _ in FIELDS] # All legal sort keys
        headers  = [
            styled_header(title, alias, fg_color="h cyan")
            for alias, _, title in FIELDS
        ]
        
        # Build the help‐string listing all commands, underlining the chosen
        # shortcut letters via the underline() helper.
        # NOTE: underline() wraps its argument in ANSI underline codes.
        cmds = (
            f"{underline("s")}ort <field>, "
            f"{underline("re")}verse, "
            f"{underline("ex")}port <path>, "
            f"{underline("sh")}are <id>, "
            f"({underline("del")}) remove <id>, "
            f"{underline("arc")}hive <id>, "
            f"{underline("unarc")}hive <id>, "
            f"{underline("e")}dit <id>, "
            f"{underline("t")}est <id>, "
            f"{underline("c")}onnect <id>, "
            f"{underline("tog")}gle, "
            f"q"
        )
        
        
        sort_by = None      # Which field to sort on
        reverse = True      # Sort order: True = descending

        # ─── Main loop: redraw table and handle one command per iteration ─────
        while True:
            
            # 1) Fetch rows
            rows = mgr.list_configs(sort_by=sort_by, reverse=reverse)
            
            table_data: list[list[str]] = []
            for r in rows:
                # Clip/clean remark for display
                remark       = strip_emojis(
                    textwrap.shorten(r["remark"], width=30, placeholder="…")
                )
                last_ping    = r["last_ping"] or "-"
                last_latency = f"{r['last_latency']}" if r["last_latency"] else "-"
                last_work    = r["last_work"] or "-"

                table_data.append([
                    str(r["id"]),
                    remark,
                    last_ping,
                    str(r["ping_count"]),
                    last_latency.rjust(6),
                    str(r["working_count"]),
                    last_work,
                    r["type"],
                    r["add_time"]
                ])

            # 3) Clear screen & render table
            os.system("cls" if os.name == "nt" else "clear")
            print(f"=== {title} ===\n")
            print(tabulate(
                table_data,
                headers=headers,
                tablefmt="pretty",
                stralign="left",
                numalign="right"
            ))
            
            print(f"\n[sorted by: {sort_by or 'none'} {'DESC' if reverse else 'ASC'}]")
            print(color("Commands:", "h purple"), cmds)
            print(self._connection_status_line()) # show current VPN status

            # 4) Read one raw command line from user
            raw = input("\n(list) > ").strip()
            if raw.lower() in ('q', 'quit', 'exit'):
                break
            if ' ' in raw:
                cmd, arg = raw.split(' ', 1)
                cmd = cmd.lower()
                arg = arg.strip()
            else:
                cmd, arg = raw.lower(), ""

            # 5) Dispatch commands
            
            # 1- Sort: change sort_by field based on alias/full name
            if cmd in ['sort', 's']:
                # resolve short or full form
                if not arg:
                    print("Usage: sort <field>")
                    press_enter()
                else:
                    field = headers_aliases.get(arg, arg)
                    if field in valid_fields:
                        sort_by = field
                    else:
                        colorp(f"Invalid field '{field}'. Valid: {', '.join(valid_fields)}", "h red")
                        press_enter()
                    
            # 2- Reverse: toggle ascending/descending
            elif cmd in ['reverse', 're']:
                reverse = not reverse
                
            # 3- Export: write current view to CSV
            elif cmd in ['export', 'ex']:
                path = arg or "configs.csv"
                path = path if os.path.isabs(path) else os.path.join(os.getcwd(), path)
                try:
                    mgr.export_csv(path, sort_by=sort_by, reverse=reverse)
                    print("Exported to", path)
                except Exception as e:
                    colorp(f"Export failed: {e}", "h red")
                press_enter()
                
            # 4- Share: reconstruct and copy/share a single URI and displays the qr code
            elif cmd in ['share', 'sh']:
                if arg: self._share_uri(arg)
                else: print("Usage: share <id>")
                press_enter()
                
            # 5- Remove: prompt confirmation, then delete by ID
            elif cmd in ['remove', 'del']:
                if not arg:
                    print("Usage: remove <id>")
                else:
                    cfg = mgr.get_by_id(arg)
                    if not cfg:
                        colorp("No such config.", "h red")
                    else:
                        # Ask for confirmation, showing id and remark
                        rem = cfg.remark or "(no remark)"
                        confirm = input(f"Confirm deletion of [{cfg.id}] {rem}? (y/N): ").strip().lower()
                        if confirm == 'y':
                            mgr.remove_by_id(arg)
                            print(f"[{arg}] removed.")
                        else:
                            print("Aborted.")
                press_enter()

            # 6- Archive: move from main DB → archive DB
            elif cmd in ['archive', 'arc']:
                if arg:
                    try:
                        # Always move from main → archive
                        self.manager.move_config(arg, self.arc_manager, force=True)
                        print(f"[{arg}] archived.")
                    except KeyError:
                        colorp("No such config in main DB.", "h red")
                    except ValueError as e:
                        print("⚠️", e)
                else:
                    print("Usage: archive <id>")
                press_enter()

            # 7- Unarchive: move from archive DB → main DB
            elif cmd in ['unarchive', 'unarc']:
                if arg:
                    try:
                        # Always move from archive → main
                        self.arc_manager.move_config(arg, self.manager, force=True)
                        print(f"[{arg}] restored to main DB.")
                    except KeyError:
                        colorp("No such config in archive DB.", "h red")
                    except ValueError as e:
                        print("⚠️", e)
                else:
                    print("Usage: unarchive <id>")
                press_enter()
            
            # 8- Edit: change `id` or `remark`, other fields stubbed (For now)
            elif cmd in ['edit', 'e']:
                parts = [p.strip() for p in arg.split(',', 2)]
                if len(parts) != 3:
                    print("Usage: edit <id>, <field>, <new_value>")
                else:
                    cfg_id, fld, new_value = parts
                    field = headers_aliases.get(fld, fld)  # resolve short names

                    cfg = mgr.get_by_id(cfg_id)
                    if not cfg:
                        colorp(f"No config with ID {cfg_id!r}", "h red")
                    # Editing Remark
                    elif field == "remark":
                        old = cfg.remark
                        cfg.remark = new_value
                        mgr._save() # type: ignore
                        print(f"[{cfg_id}] Remark changed from {old!r} to {new_value!r}")
                    # Editing ID
                    elif field == "id":
                        if mgr.get_by_id(new_value):
                            print(color(f"ID {new_value!r} already in use.", "h red"))
                        else:
                            old = cfg.id
                            cfg.id = new_value
                            mgr._save() # type: ignore
                            print(f"ID changed from {old!r} to {new_value!r}")
                    else:
                        colorp(f"⚠️ Editing '{field}' is not implemented yet.", "h red")
                        
                press_enter()
            
            # 9- Test: protocol‐level ping, temporarily disabling system proxy
            elif cmd in ["test", "t"]:
                # 1) Determine which config to test
                if not arg:
                    print("Usage: test <id>")
                    press_enter()
                    continue

                cfg = mgr.get_by_id(arg)
                if not cfg:
                    colorp(f"No such config with ID {arg!r}", "h red")
                    press_enter()
                    continue

                # 2) Prep display
                raw_remark = cfg.remark or ""
                truncated = textwrap.shorten(raw_remark, width=20, placeholder="…")
                quoted = f"'{truncated}'" if truncated else "''"
                line = f"Testing [{cfg.id}] {quoted} ..."
                print(line, end="", flush=True)

                # 3) Remember state & full teardown if needed
                was_conn = self._is_connected() and self.connected_id == arg
                had_sys  = self.system_proxy and was_conn
                if was_conn:
                    self._disconnect()
                    time.sleep(DISCONNECT_SLEEP)

                # 4) Run the ping test with settings
                latency = cfg.test(
                    v2ray_binary=self.v2ray_binary,
                    timeout=self.default_timeout
                )

                # 5) Clear the “Testing …” line
                print("\r\033[K", end="")

                # 6) Restore connection & proxy if we’d torn it down
                if was_conn:
                    self._connect(cfg.id) # type: ignore
                    if had_sys:
                        self._apply_system_proxy()

                # 7) Show the result
                if latency is not None:
                    print(f"[{cfg.id}] {quoted} → {latency:.1f} ms")
                else:
                    print(f"[{cfg.id}] {quoted} → {color('failed', 'h red')}")

                press_enter()

            # 10- Connect: establish a new VPN connection by ID
            elif cmd in ["connect", "c"]:
                if arg:
                    self._connect(arg)
                    mode = color("Set", "green") if self.system_proxy else color("Clear", "red")
                    print(f"System Proxy: {mode}")
                else:
                    print("Usage: connect <id>")
                press_enter()
                
                
            # 11- Toggle System Proxy: flip system proxy on/off immediately
            elif cmd in ["toggle", "tog"]:
                self.toggle_system_proxy()
                mode = color("Set", "green") if self.system_proxy else color("Clear", "red")
                print(f"System Proxy: {mode}")
                press_enter()

            
            # Unknown command fallback
            else:
                colorp("Unknown command", "h red") 
                press_enter()
    
                
    def share_uri(self) -> None:
        _id = input("Enter config ID to share: ").strip()
        self._share_uri(_id)
        

    def _share_uri(self, _id: str) -> None:
        config = self.manager.get_by_id(_id)
        if not config:
            colorp("Config not found.", "h red")
            return
        # config = cast(ProxyConfig, config)
        uri = config_to_uri(config.to_dict())
        print(uri)
        pyperclip.copy(uri)
        colorp("URI copied to clipboard.", "green")
        show_qr(uri)
        

    def share_all(self) -> None:
        path = input("Enter filename to export to (leave blank for uris.txt): ").strip()
        path = path or "uris.txt"
        with open(path, "w", encoding="utf-8") as f:
            for config in self.manager.configs:
                uri = config_to_uri(config.to_dict())
                f.write(uri + "\n\n")
        print(f"✅ URIs exported to {path}")
        
         
    def remove_config(self) -> None:
        """Main-menu: Permanently delete a config from the active DB."""
        _id = input("Enter ID to remove: ").strip()
        if not self.manager.get_by_id(_id):
            colorp("No such config.", "h red")
            return
        confirm = input(f"Confirm removal of [{_id}]? (y/N): ").strip().lower()
        if confirm == 'y':
            self.manager.remove_by_id(_id)
            print(f"[{_id}] removed.")
        else:
            print("Aborted.")
            
                    
    def archive_config(self) -> None:
        """Move a config from the active DB into the archive DB (force on ID conflicts)."""
        _id = input("Enter ID to archive: ").strip()
        if not self.manager.get_by_id(_id):
            colorp("No such config.", "h red")
            return
        
        confirm = input(f"Confirm archive of [{_id}]? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Aborted.")
            return
        
        try:
            new_id = self.manager.move_config(_id, self.arc_manager, force=True)
            if new_id != _id:
                # Inform about the ID change
                colorp(f"ID conflict: archived as [{new_id}] instead of [{_id}].", "h red")
            else:
                print(f"[{_id}] archived.")
        except Exception as e:
            print(color("Error:", "h red"), e)
            
                 
    def unarchive_config(self) -> None:
        """Restore a config from the archive DB into the active DB (force on ID conflicts)."""
        _id = input("Enter ID to unarchive: ").strip()
        if not self.arc_manager.get_by_id(_id):
            colorp("No such archived config.", "h red")
            return
        
        confirm = input(f"Confirm unarchive of [{_id}]? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Aborted.")
            return
        
        try:
            new_id = self.arc_manager.move_config(_id, self.manager, force=True)
            if new_id != _id:
                colorp(f"ID conflict: restored as [{new_id}] instead of [{_id}].", "h red")
            else:
                print(f"[{_id}] restored to main DB.")
        except Exception as e:
            print(color("Error:", "h red"), e)

            
    def open_settings(self):
        """Open the interactive Settings menu."""
        sm = SettingsMenu(
            settings=self.settings,
            settings_path=self.settings_path,
            logger=self.logger
        )
        sm.run()
        
           