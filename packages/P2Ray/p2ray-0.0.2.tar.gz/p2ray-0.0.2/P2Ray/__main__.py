import os
import sys
import json
import logging


from importlib.metadata import metadata, PackageNotFoundError
from appdirs import user_data_dir

from P2Ray.CLIApp import CLIApp
from P2Ray.settings import SettingsDict, DEFAULT_SETTINGS
from P2Ray.utils import colorp, press_enter



def main():
    # ─── 1) Determine AppName & AppAuthor dynamically ────────────
    try:
        dist_meta  = metadata("P2Ray")          # your PyPI package name
        app_name   = dist_meta["Name"]          or "P2Ray"
        app_author = dist_meta.get("Author")    or app_name
    except PackageNotFoundError:
        # Running from source or not installed via pip
        app_name   = "P2Ray"
        app_author = "P2Ray"

    # ─── 2) Compute per-user data directory and ensure it exists ──
    data_dir = user_data_dir(app_name, app_author)
    os.makedirs(data_dir, exist_ok=True)

    # ─── 3) Build absolute paths for our JSON DBs ────────────────
    config_db_path  = os.path.join(data_dir, "config_db.json")
    archive_db_path = os.path.join(data_dir, "archive_db.json")
    settings_path   = os.path.join(data_dir, "settings.json")
    log_file_path   = os.path.join(data_dir, "log.txt")
    

    # ─── 3) Load or initialize settings ─────────────────────────────
    if os.path.exists(settings_path):
        with open(settings_path, "r", encoding="utf-8") as f:
            settings: SettingsDict = json.load(f)
        # Detect and add any new keys from DEFAULT_SETTINGS
        updated = False
        for key, default_val in DEFAULT_SETTINGS.items():
            if key not in settings:
                settings[key] = default_val
                updated = True
                colorp(f" -Added new setting '{key}' with default value: {default_val}", "h green")
                press_enter()
        if updated:
            # Persist the augmented settings file
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=2)
    else:
        # First run: just write defaults
        settings = DEFAULT_SETTINGS.copy()
        with open(settings_path, "w", encoding="utf-8") as f:
            json.dump(settings, f, ensure_ascii=False, indent=2)

    # ─── Setup logging based on settings ───────────────────────────
    log_level_name = settings.get("log_level", "INFO").upper()
    log_level      = getattr(logging, log_level_name, logging.INFO)

    logging.basicConfig(
        filename=log_file_path,
        filemode='a',
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )
    logger = logging.getLogger("P2Ray")

    logger.info("App started")
          
    # ─── Instantiate & run CLIApp ─────────────────────────────────
    app = CLIApp(
        config_db_path=config_db_path,
        archive_db_path=archive_db_path,
        settings=settings,
        settings_path=settings_path,
        logger=logger
    )

    try:
        app.run()
    except Exception:
        # Defer logging setup to Phase 2; for now we just print and exit
        logger.exception("Unhandled exception in main loop")
        colorp("A fatal error occurred. Please report it.", "h red")
        # sys.exit(1)


# Entry point
if __name__ == "__main__":
    main()