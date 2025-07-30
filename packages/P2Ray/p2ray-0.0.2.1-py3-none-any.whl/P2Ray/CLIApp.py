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
from P2Ray.settings import SettingsDict, DEFAULT_SETTINGS
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
        self.logger        = logger  # <── Save logger for use in methods

        # 1) Initialize ConfigManagers with the provided files
       # 1) Initialize ConfigManagers with the provided files
        self.manager:     ConfigManager   = ConfigManager(db_path=config_db_path)
        self.arc_manager: ConfigManager   = ConfigManager(db_path=archive_db_path)
        self.logger.debug(f"ConfigManager initialized with: {config_db_path}")
        self.logger.debug(f"ArchiveManager initialized with: {archive_db_path}")

        # 2) Settings
        self.settings      = settings
        self.settings_path = settings_path

        # 3) CLI application state
        self.running:   bool   = True
        self.main_menu: Menu   = self.create_main_menu()
        self.logger.debug("Main menu created")

        # 4) VPN connection state
        self.connected_id: Optional[str] = None
        self.system_proxy: bool          = False
        self.v2ray_proc                  = None  # subprocess handle

        # ─── Phase 5: Store settings into attributes ──────────────
        if "v2ray_path" not in self.settings:
            fallback = DEFAULT_SETTINGS["v2ray_path"]
            self.logger.warning("Missing 'v2ray_path' in settings; using fallback: %s", fallback)
            colorp("Warning: Missing 'v2ray_path' in settings; using default.", "h red")
            press_enter()
            self.v2ray_binary = fallback
        else:
            self.v2ray_binary = self.settings["v2ray_path"]

        if "default_timeout" not in self.settings:
            fallback = DEFAULT_SETTINGS["default_timeout"]
            self.logger.warning(
                "Missing 'default_timeout' in settings; using fallback: %s", fallback
                )
            colorp("Warning: Missing 'default_timeout' in settings; using default.", "h red")
            press_enter()
            self.default_timeout = fallback
        else:
            self.default_timeout = self.settings["default_timeout"]

        self.logger.debug(f"Settings resolved: v2ray_binary={self.v2ray_binary}, "
                          f"default_timeout={self.default_timeout}")


    def create_main_menu(self) -> Menu:
        """Defining the Main Menu"""
        self.logger.debug("Creating main menu")
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
        self.logger.info("Application exiting. Disconnecting...")
        self.disconnect()
        self.logger.debug("Application exiting. Clearing System Proxy...")
        self._clear_system_proxy()
        print("Goodbye!")
        self.logger.info("Exited cleanly.")


    # -------------------- State‐Aware Display --------------------
    def run(self) -> None:
        """
        Main Loop
        """
        self.logger.info("Entering CLI main loop")

        while self.running:
            status = self._connection_status_line()
            self.main_menu.display(status)

            selection = None
            while selection is None:
                selection = self.main_menu.get_selection()

            if selection == 0:
                self.logger.info("User chose to exit via main menu")
                self.running = False
                self.exit_app()
                break

            option = self.main_menu.options[selection - 1]
            self.logger.debug(f"User selected menu option: {option.label}")

            try:
                option.action()
            except Exception as _:
                self.logger.exception(
                    f"Error while executing action for menu option: {option.label}"
                    )
                colorp("An error occurred while executing that action.", "h red")

            press_enter("Press Enter to return to main menu...")

    def _connection_status_line(self) -> str:
        if not self.connected_id:
            self.logger.debug("Status line: not connected")
            return color("[Not connected]", "red")

        mode = color("Set", "green") if self.system_proxy else color("Clear", "red")
        self.logger.debug(
            f"Status line: connected to {self.connected_id}, \
              system proxy {'enabled' if self.system_proxy else 'disabled'}"
            )
        return f"[{self.connected_id}] System Proxy: {mode}"


    # ------------------ Connection Management --------------------
    def connect(self) -> None:
        """Option: Connect to a config (without or with system proxy)."""
        cfg_id = input("Enter ID to connect: ").strip()
        self.logger.info(f"CONNECT: User requested connection to [{cfg_id}]")
        self._connect(cfg_id)

    def _connect(
        self,
        cfg_id: str
        ) -> None:
        """Helper For Connection Logic."""
        cfg = self.manager.get_by_id(cfg_id)
        if not cfg:
            self.logger.warning(f"CONNECT FAILED: No config with ID [{cfg_id}]")
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

        self.logger.debug(f"CONNECT: Temp config written to {tmp.name}")

        # 2) Spawn v2ray process
        if self.v2ray_proc:
            self.logger.info("CONNECT: Killing existing v2ray process")
            self.v2ray_proc.kill()

        try:
            self.v2ray_proc = subprocess.Popen(
                [self.v2ray_binary, "-config", tmp.name],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except Exception as e:
            self.logger.exception(f"CONNECT FAILED: Unable to spawn v2ray process: {e}")
            colorp("Failed to start V2Ray process.", "h red")
            return

        self.connected_id = cfg_id
        self.logger.info(f"CONNECT: Connected to [{cfg_id}] using [{self.v2ray_binary}]")
        print(f"Connected to [{cfg_id}]")

        # 3) Apply system proxy if flagged
        if self.system_proxy:
            self.logger.debug("CONNECT: System proxy enabled, applying...")
            self._apply_system_proxy()

    def _disconnect(self) -> None:
        """Fully tear down any existing V2Ray connection and clear proxy."""
        self.logger.info("DISCONNECT: Tearing down current connection")
        if self.v2ray_proc:
            self.logger.debug("DISCONNECT: Killing v2ray process")
            self.v2ray_proc.kill()
            self.v2ray_proc = None
        if self.system_proxy:
            self.logger.debug("DISCONNECT: Clearing system proxy")
            self._clear_system_proxy()

    def disconnect(self) -> None:
        """Tear down current connection and clear proxy."""
        self.logger.info(f"DISCONNECT: User requested disconnect from [{self.connected_id}]")
        if self.v2ray_proc:
            self.logger.debug("DISCONNECT: Killing v2ray process")
            self.v2ray_proc.kill()
            self.v2ray_proc = None
        if self.system_proxy:
            self.logger.debug("DISCONNECT: Clearing system proxy")
            self._clear_system_proxy()
        print(f"Disconnected from [{self.connected_id}]")
        self.connected_id = None

    def toggle_system_proxy(self) -> None:
        """Option: flip the system-proxy flag, apply immediately if connected."""
        self.system_proxy = not self.system_proxy
        self.logger.info(f"TOGGLE_PROXY: {'Enabling' if self.system_proxy else 'Disabling'} system proxy")

        if self.connected_id:
            if self.system_proxy:
                self.logger.debug("TOGGLE_PROXY: Connected, applying system proxy now")
                self._apply_system_proxy()
            else:
                self.logger.debug("TOGGLE_PROXY: Connected, clearing system proxy now")
                self._clear_system_proxy()

        print("System proxy", "enabled" if self.system_proxy else "disabled")

    # ────────── Helpers for System Proxy ─────────────────────────────────────
    def _apply_system_proxy(self) -> None:
        """Apply local proxy settings using platform-specific tools."""
        try:
            self.logger.debug("PROXY: Applying system proxy via `netsh`")
            subprocess.run(["netsh", "winhttp", "set", "proxy", "127.0.0.1:1081"], check=True)
            self.logger.info("PROXY: System proxy applied")
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"PROXY: Failed to apply system proxy: {e}")
            colorp("Failed to apply system proxy.", "h red")

    def _clear_system_proxy(self) -> None:
        """Reset system proxy settings."""
        try:
            self.logger.debug("PROXY: Clearing system proxy via `netsh`")
            subprocess.run(["netsh", "winhttp", "reset", "proxy"], check=True)
            self.logger.info("PROXY: System proxy cleared")
        except subprocess.CalledProcessError as e:
            self.logger.warning(f"PROXY: Failed to clear system proxy: {e}")
            colorp("Failed to clear system proxy.", "h red")

    # ────────── Test Commands ────────────────────────────────────────────────
    def _is_connected(self) -> bool:
        """Return True if we believe a v2ray process is currently running for connected_id."""
        connected = bool(self.connected_id and self.v2ray_proc and self.v2ray_proc.poll() is None)
        self.logger.debug(f"_is_connected(): {connected}")
        return connected

    def _choose_config_for_test(self) -> ProxyConfig | None:
        """
        Return the config to test:
        • If already connected, use that.
        • Otherwise prompt the user for an ID.
        """
        if self._is_connected() and self.connected_id:
            cfg = self.manager.get_by_id(self.connected_id)
            if not cfg:
                msg = f"Config [{self.connected_id}] no longer exists."
                self.logger.warning(f"_choose_config_for_test(): {msg}")
                colorp(msg, "h red")
                press_enter()
            else:
                self.logger.debug(
                    f"_choose_config_for_test(): Using connected config [{cfg.id}]"
                    )
            return cfg

        # Not connected: ask the user
        _id = input("Enter config ID to test: ").strip()
        cfg = self.manager.get_by_id(_id)
        if not cfg:
            self.logger.warning(f"_choose_config_for_test(): No such config with ID {_id!r}")
            colorp(f"No such config with ID {_id!r}", "h red")
        else:
            self.logger.debug(f"_choose_config_for_test(): Selected config [{cfg.id}]")
        return cfg


    def test_ping(self) -> None:
        """Ping a config (connected or chosen), with full disconnect/reconnect."""
        cfg = self._choose_config_for_test()
        if not cfg:
            self.logger.info("test_ping(): No valid config selected.")
            return

        cfg_id  = cfg.id
        had_sys = self.system_proxy

        self.logger.info(f"test_ping(): Starting ping for [{cfg_id}]")

        # 1) Tear down any existing connection
        if self._is_connected():
            self.logger.debug("test_ping(): Disconnecting before test.")
            self._disconnect()
            time.sleep(DISCONNECT_SLEEP)

        # 2) Run the ping test
        try:
            latency = cfg.test(
                v2ray_binary=self.v2ray_binary,
                timeout=self.default_timeout
            )
        except Exception as _:
            self.logger.exception(f"test_ping(): Ping test for [{cfg_id}] failed.")
            latency = None

        # 3) Reconnect if we had been connected
        if had_sys or cfg_id == self.connected_id:
            self.logger.debug(f"test_ping(): Reconnecting to [{cfg_id}]")
            self._connect(cfg_id)  # type: ignore
            if had_sys:
                self._apply_system_proxy()

        # 4) Display
        if latency is not None:
            self.logger.info(f"test_ping(): Latency for [{cfg_id}] = {latency:.1f} ms")
            print(f"Latency: {latency:.1f} ms")
        else:
            self.logger.warning(f"test_ping(): Ping failed for [{cfg_id}]")
            colorp("Ping failed.", "h red")


    def test_speed(self) -> None:
        """Measure download speed using the currently connected config."""
        cfg = self._choose_config_for_test()
        if not cfg:
            self.logger.info("test_speed(): No valid config selected.")
            return

        self.logger.info(f"test_speed(): Measuring speed for [{cfg.id}]")

        # 1. Fully disconnect proxy
        self.logger.debug("test_speed(): Disconnecting before speed test.")
        self._disconnect()

        # 2. Reconnect using selected config
        self.logger.debug(f"test_speed(): Reconnecting to [{cfg.id}] for speed test.")
        self._connect(cfg.id)  # type: ignore

        # 3. Wait briefly to ensure system proxy applied
        time.sleep(DISCONNECT_SLEEP)

        # 4. Run the test
        try:
            mbps = test_speed(timeout=self.default_timeout)
            self.logger.info(
                f"test_speed(): Download speed for [{cfg.id}] = {mbps:.2f} Mbps"
                )
            print(f"Download speed: {mbps:.2f} Mbps")
        except Exception as _:
            self.logger.exception("test_speed(): Speed test failed")
            print(color("Speed test failed.", "h red"))

        # No restoration of previous state — user is now connected via tested proxy


    def test_all(self) -> None:
        """
        Main-menu option: test every config, fully disconnecting and then restoring
        both the V2Ray process and system proxy state.
        """
        self.logger.info("test_all(): Starting test for all configs.")

        # 1) Remember previous connection state
        was_conn = self._is_connected()
        cfg_id   = self.connected_id
        had_sys  = self.system_proxy

        # 2) Fully tear down any existing connection
        if was_conn:
            self.logger.debug(f"test_all(): Disconnecting from [{cfg_id}] before bulk test.")
            self._disconnect()
            time.sleep(DISCONNECT_SLEEP)

        # 3) Run all tests
        try:
            self.manager.test_all(
                v2ray_binary=self.v2ray_binary,
                timeout=self.default_timeout
            )
            self.logger.info("test_all(): Completed testing all configs.")
        except Exception:
            self.logger.exception("test_all(): Error during bulk config test.")

        # 4) Restore the previous connection if it existed
        if was_conn and cfg_id:
            self.logger.debug(f"test_all(): Reconnecting to [{cfg_id}]")
            self._connect(cfg_id)
            if had_sys:
                self._apply_system_proxy()

    # -------------------------- Options --------------------------
    def log_connectivity(self) -> None:
        """Manually mark configs as working."""
        self.logger.info("log_connectivity(): Started manual marking session.")
        while True:
            _id = input("ID: ").strip()
            if _id.lower() == 'q':
                self.logger.info("log_connectivity(): User exited marking session.")
                break
            try:
                self.manager.mark_working(config_id=_id)
                self.logger.info(f"log_connectivity(): Marked [{_id}] as working.")
            except ValueError:
                self.logger.warning(f"log_connectivity(): Invalid ID entered: {_id}")
                colorp("Invalid ID", "h red")


    def add_configs(self) -> None:
        """
        Option in Main Menu for adding Config
        """
        print("\nAdd Configs: Type each config URI and ID. Type 'q' to stop.")
        added_count = 0
        self.logger.info("add_configs(): Starting URI import loop.")

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
                    self.logger.info(f"add_configs(): Added config {config_id or '[auto-id]'} from URI.")
                else:
                    self.logger.debug(f"add_configs(): URI processed but no config added: {uri}")
            except ValueError as e:
                self.logger.warning(f"add_configs(): Failed to add config from URI '{uri}': {e}")
                colorp(f" - Invalid URI or ID error: {e}", "h red")

        total = len(self.manager.configs)
        self.logger.info(f"add_configs(): Finished. Added {added_count}, total now {total}.")
        print(f"\nSummary: Added {added_count}. Total now: {total}")


    def list_configs(self) -> None:
        """List and interact with the main config database."""
        self.logger.info("list_configs(): Showing main configurations.")
        self._interactive_list(self.manager, "Main Configurations")


    def list_archive(self) -> None:
        """List and interact with the archived config database."""
        self.logger.info("list_archive(): Showing archived configurations.")
        self._interactive_list(self.arc_manager, "Archived Configurations")


    def _interactive_list(self, mgr: ConfigManager, title: str) -> None:
        """
        Generic interactive listing screen for any ConfigManager.
        Renders a table of configs, shows available commands, and dispatches
        user input (sort, reverse, export, share, remove, archive, unarchive,
        edit, test, connect, toggle, quit).
        """
        self.logger.info(f"_interactive_list(): Entered interactive view for '{title}'")
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

                        self.logger.info(f"_interactive_list(): Sorting by field: {field}")

                    else:
                        colorp(f"Invalid field '{field}'. Valid: {', '.join(valid_fields)}", "h red")

                        self.logger.warning(f"_interactive_list(): Invalid sort field: {field}")

                        press_enter()

            # 2- Reverse: toggle ascending/descending
            elif cmd in ['reverse', 're']:
                reverse = not reverse
                self.logger.info("_interactive_list(): Sort order reversed")

            # 3- Export: write current view to CSV
            elif cmd in ['export', 'ex']:
                path = arg or "configs.csv"
                path = path if os.path.isabs(path) else os.path.join(os.getcwd(), path)

                self.logger.info(f"_interactive_list(): Exporting to {path}")

                try:
                    mgr.export_csv(path, sort_by=sort_by, reverse=reverse)
                    print("Exported to", path)
                except Exception as e:
                    colorp(f"Export failed: {e}", "h red")

                    self.logger.exception(f"_interactive_list(): Export failed to {path}")

                press_enter()

            # 4- Share: reconstruct and copy/share a single URI and displays the qr code
            elif cmd in ['share', 'sh']:
                if arg:
                    self._share_uri(arg)

                    self.logger.info(f"_interactive_list(): Sharing config ID: {arg}")
                else:
                    print("Usage: share <id>")
                press_enter()

            # 5- Remove: prompt confirmation, then delete by ID
            elif cmd in ['remove', 'del']:
                if not arg:
                    print("Usage: remove <id>")
                    self.logger.warning("_interactive_list(): Remove called without argument")
                else:
                    self.logger.debug(f"_interactive_list(): Attempting to remove [{arg}]")
                    cfg = mgr.get_by_id(arg)

                    if not cfg:
                        colorp("No such config.", "h red")
                        self.logger.warning(f"_interactive_list(): Config [{arg}] not found for removal")
                    else:
                        rem = cfg.remark or "(no remark)"
                        confirm = input(f"Confirm deletion of [{cfg.id}] {rem}? (y/N): ").strip().lower()

                        if confirm == 'y':
                            mgr.remove_by_id(arg)
                            print(f"[{arg}] removed.")
                            # Log full config dict for auditing
                            self.logger.info(f"_interactive_list(): Removed config [{cfg.id}]: {cfg.to_dict()}")
                        else:
                            print("Aborted.")
                            self.logger.info(f"_interactive_list(): Removal of [{cfg.id}] aborted by user")

                press_enter()

            # 6- Archive: move from main DB → archive DB
            elif cmd in ['archive', 'arc']:
                self.logger.info(f"_interactive_list(): Archiving [{arg}]")
                if arg:
                    try:
                        # Always move from main → archive
                        self.manager.move_config(arg, self.arc_manager, force=True)
                        print(f"[{arg}] archived.")
                    except KeyError:
                        colorp("No such config in main DB.", "h red")
                        self.logger.warning(f"_interactive_list(): Archive failed, not found: {arg}")
                    except ValueError as e:
                        print("!", e)
                        self.logger.exception(f"_interactive_list(): Archive failed for {arg}: {e}")

                else:
                    print("Usage: archive <id>")
                press_enter()

            # 7- Unarchive: move from archive DB → main DB
            elif cmd in ['unarchive', 'unarc']:
                self.logger.info(f"_interactive_list(): Unarchiving [{arg}]")
                if arg:
                    try:
                        # Always move from archive → main
                        self.arc_manager.move_config(arg, self.manager, force=True)
                        print(f"[{arg}] restored to main DB.")
                    except KeyError:
                        colorp("No such config in archive DB.", "h red")
                        self.logger.warning(f"_interactive_list(): Unarchiving failed, not found: {arg}")
                    except ValueError as e:
                        print("!", e)
                        self.logger.exception(f"_interactive_list(): Unarchiving failed for {arg}: {e}")

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

                    self.logger.info(f"_interactive_list(): Editing [{cfg_id}] field '{field}' to '{new_value}'")

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
                            self.logger.warning(f"_interactive_list(): ID conflict: {new_value} already exists")
                        else:
                            old = cfg.id
                            cfg.id = new_value
                            mgr._save() # type: ignore
                            print(f"ID changed from {old!r} to {new_value!r}")
                    else:
                        colorp(f"! Editing '{field}' is not implemented yet.", "h red")
                        self.logger.warning(f"_interactive_list(): Attempted to edit unsupported field '{field}'")

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

                self.logger.info(f"_interactive_list(): Testing config [{cfg.id}]")

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
                    self.logger.info(f"_interactive_list(): Ping to [{cfg.id}] = {latency:.1f} ms")
                else:
                    print(f"[{cfg.id}] {quoted} → {color('failed', 'h red')}")
                    self.logger.warning(f"_interactive_list(): Ping to [{cfg.id}] failed")

                press_enter()

            # 10- Connect: establish a new VPN connection by ID
            elif cmd in ["connect", "c"]:
                if arg:
                    self._connect(arg)
                    mode = color("Set", "green") if self.system_proxy else color("Clear", "red")
                    print(f"System Proxy: {mode}")
                    self.logger.info(f"_interactive_list(): Connecting to [{arg}]")
                else:
                    print("Usage: connect <id>")
                press_enter()


            # 11- Toggle System Proxy: flip system proxy on/off immediately
            elif cmd in ["toggle", "tog"]:
                self.toggle_system_proxy()
                mode = color("Set", "green") if self.system_proxy else color("Clear", "red")
                print(f"System Proxy: {mode}")
                self.logger.info(
                    f"_interactive_list(): Toggled system proxy: \
                    {'enabled' if self.system_proxy else 'disabled'}")
                press_enter()


            # Unknown command fallback
            else:
                colorp("Unknown command", "h red")
                self.logger.info(f"_interactive_list(): Unknown command: '{raw}'")
                press_enter()

    def share_uri(self) -> None:
        """
        Prompt the user for a config ID, convert it to a URI,
        copy it to clipboard, and display a QR code.
        """
        _id = input("Enter config ID to share: ").strip()
        self.logger.debug(f"share_uri(): Attempting to share config [{_id}]")
        self._share_uri(_id)


    def _share_uri(self, _id: str) -> None:
        """
        Internal helper for share_uri. Raises no exceptions — all are caught
        and reported to the user & logger with granular messages.
        """
        cfg = self.manager.get_by_id(_id)
        if not cfg:
            colorp("X! Config not found.", "h red")
            self.logger.warning(f"_share_uri(): No config with ID [{_id}]")
            return

        # 1) Build URI
        try:
            uri = config_to_uri(cfg.to_dict())
        except KeyError as e:
            colorp("X! Failed to build URI: missing field.", "h red")
            self.logger.error(f"_share_uri(): config_to_uri KeyError for [{_id}]: {e}")
            return
        except Exception as e:
            colorp("X! Unexpected error constructing URI.", "h red")
            print(e)
            self.logger.exception(
                f"_share_uri(): Unexpected error in config_to_uri for [{_id}]"
                )
            return

        # 2) Print & copy
        print(uri)
        try:
            pyperclip.copy(uri)
        except pyperclip.PyperclipException as e:
            colorp("! Clipboard copy failed. Ensure clipboard is accessible.", "h yellow")
            self.logger.warning(f"_share_uri(): Clipboard error for [{_id}]: {e}")
        else:
            colorp("✓ URI copied to clipboard.", "green")
            self.logger.info(f"_share_uri(): URI copied to clipboard for [{_id}]")

        # 3) Show QR
        try:
            show_qr(uri)
        except Exception as e:
            colorp("! QR display failed.", "h yellow")
            self.logger.exception(f"_share_uri(): QR code display error for [{_id}]")
        else:
            self.logger.info(f"_share_uri(): QR code shown for [{_id}]")

        # 4) Full config logged for audit
        self.logger.debug(f"_share_uri(): Full config data: {cfg.to_dict()}")
    def share_all(self) -> None:
        """
        Export all stored URIs into a text file. Each URI is separated by a blank line.
        Prompts for filename (default: uris.txt). Handles and logs I/O errors.
        """
        path = input(
            "Enter filename to export to (leave blank for uris.txt): "
            ).strip() or "uris.txt"
        self.logger.debug(f"share_all(): User chose export path: {path}")

        try:
            with open(path, "w", encoding="utf-8") as f:
                for cfg in self.manager.configs:
                    try:
                        uri = config_to_uri(cfg.to_dict())
                    except Exception as e:
                        self.logger.error(
                            f"share_all(): Failed to build URI for [{cfg.id}]: {e}"
                            )
                        continue  # skip this one
                    f.write(uri + "\n\n")
        except PermissionError as e:
            colorp(f"X! Permission denied when writing to {path}.", "h red")
            self.logger.error(f"share_all(): PermissionError opening {path}: {e}")
            return
        except OSError as e:
            colorp(f"X! I/O error when writing to {path}: {e}", "h red")
            self.logger.error(f"share_all(): OSError writing to {path}: {e}")
            return

        total = len(self.manager.configs)
        colorp(f"+ URIs exported to {path} ({total} entries).", "h green")
        self.logger.info(f"share_all(): Successfully exported {total} URIs to {path}")

    def remove_config(self) -> None:
        """
        Prompt for a config ID and ask for confirmation before permanently
        deleting the config from the active database. Logs actions and config data.
        """
        _id = input("Enter ID to remove: ").strip()
        self.logger.debug(f"remove_config(): Prompted removal for [{_id}]")
        cfg = self.manager.get_by_id(_id)

        if not cfg:
            colorp("No such config.", "h red")
            self.logger.warning(f"remove_config(): No such config [{_id}]")
            return

        confirm = input(f"Confirm removal of [{_id}]? (y/N): ").strip().lower()
        if confirm == 'y':
            self.manager.remove_by_id(_id)
            print(f"[{_id}] removed.")
            self.logger.info(f"remove_config(): Removed config [{_id}]")
            self.logger.debug(f"remove_config(): Config data: {cfg.to_dict()}")
        else:
            print("Aborted.")
            self.logger.info(f"remove_config(): Removal of [{_id}] aborted by user")


    def archive_config(self) -> None:
        """
        Prompt for a config ID and move it from the active database into the archive database.
        If an ID conflict occurs in the archive DB, a new ID will be generated (force=True).
        Detailed logging and user feedback for each outcome.
        """
        _id = input("Enter ID to archive: ").strip()
        self.logger.debug(f"archive_config(): User requested archive for [{_id}]")

        # 1) Validate existence in main DB
        cfg = self.manager.get_by_id(_id)
        if not cfg:
            colorp("X! No such config in active DB.", "h red")
            self.logger.warning(f"archive_config(): No config [{_id}] found to archive")
            return

        # 2) Confirm with user
        confirm = input(f"Confirm archive of [{_id}] '{cfg.remark or '(no remark)'}'? (y/N): ").strip().lower()
        if confirm != 'y':
            print("Aborted.")
            self.logger.info(f"archive_config(): Archive of [{_id}] aborted by user")
            return

        # 3) Attempt the move
        try:
            new_id = self.manager.move_config(_id, self.arc_manager, force=True)
        except KeyError as e:
            colorp("X! Archive failed: config not found.", "h red")
            self.logger.error(f"archive_config(): KeyError moving [{_id}]: {e}")
            return
        except ValueError as e:
            colorp(f"X! Archive failed: {e}", "h red")
            self.logger.error(f"archive_config(): ValueError moving [{_id}]: {e}")
            return
        except Exception as e:
            colorp("X! Unexpected error during archive.", "h red")
            self.logger.exception(f"archive_config(): Unexpected error moving [{_id}]")
            return

        # 4) Success — report to user & log details
        if new_id != _id:
            colorp(f"! ID conflict: archived as [{new_id}] instead of [{_id}].", "h yellow")
            self.logger.info(f"archive_config(): [{_id}] archived with new ID [{new_id}]")
        else:
            print(f"[{_id}] archived.")
            self.logger.info(f"archive_config(): [{_id}] archived successfully")

        # 5) Log the full config that was moved
        self.logger.debug(f"archive_config(): Archived config data: {cfg.to_dict()}")


    def unarchive_config(self) -> None:
        """
        Prompt for a config ID and move it from the archive database back into the active database.
        If an ID conflict occurs in the active DB, a new ID will be generated (force=True).
        Detailed logging and user feedback for each outcome.
        """
        _id = input("Enter ID to unarchive: ").strip()
        self.logger.debug(f"unarchive_config(): User requested unarchive for [{_id}]")

        # 1) Validate existence in archive DB
        cfg = self.arc_manager.get_by_id(_id)
        if not cfg:
            colorp("X! No such archived config.", "h red")
            self.logger.warning(f"unarchive_config(): No archived config [{_id}] found")
            return

        # 2) Confirm with user
        confirm = input(
            f"Confirm unarchive of [{_id}] '{cfg.remark or '(no remark)'}'? (y/N): "
            ).strip().lower()
        if confirm != 'y':
            print("Aborted.")
            self.logger.info(f"unarchive_config(): Unarchive of [{_id}] aborted by user")
            return

        # 3) Attempt the move
        try:
            new_id = self.arc_manager.move_config(_id, self.manager, force=True)
        except KeyError as e:
            colorp("X! Unarchive failed: config not found in archive DB.", "h red")
            self.logger.error(f"unarchive_config(): KeyError moving [{_id}]: {e}")
            return
        except ValueError as e:
            colorp(f"X! Unarchive failed: {e}", "h red")
            self.logger.error(f"unarchive_config(): ValueError moving [{_id}]: {e}")
            return
        except Exception as e:
            colorp("X! Unexpected error during unarchive.", "h red")
            self.logger.exception(f"unarchive_config(): Unexpected error moving [{_id}]")
            return

        # 4) Success — report to user & log details
        if new_id != _id:
            colorp(f"⚠️ ID conflict: restored as [{new_id}] instead of [{_id}].", "h yellow")
            self.logger.info(f"unarchive_config(): [{_id}] restored with new ID [{new_id}]")
        else:
            print(f"[{_id}] restored to main DB.")
            self.logger.info(f"unarchive_config(): [{_id}] restored successfully")

        # 5) Log the full config that was moved
        self.logger.debug(f"unarchive_config(): Restored config data: {cfg.to_dict()}")


    def open_settings(self):
        """
        Open the interactive settings menu.
        This allows the user to modify application-wide settings.
        """
        self.logger.debug("open_settings(): Opening settings menu")

        try:
            sm = SettingsMenu(
                settings=self.settings,
                settings_path=self.settings_path,
                logger=self.logger
            )
            sm.run()
            self.logger.info("open_settings(): Settings menu closed")
        except FileNotFoundError as e:
            colorp("X Settings file not found.", "h red")
            self.logger.error(
                f"open_settings(): FileNotFoundError — {e}"
            )
        except json.JSONDecodeError as e:
            colorp("X Failed to load settings (invalid JSON).", "h red")
            self.logger.error(
                f"open_settings(): JSONDecodeError — {e}"
            )
        except Exception as e:
            colorp("X Unexpected error in settings menu.", "h red")
            self.logger.exception(
                "open_settings(): Unhandled exception in settings menu"
            )
