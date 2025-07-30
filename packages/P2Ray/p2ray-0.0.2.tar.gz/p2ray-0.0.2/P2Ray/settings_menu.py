from typing import Optional, Any
import os
import json
import logging

from P2Ray.settings import SettingsDict ,VALID_SETTINGS
from P2Ray.utils import underline, color, colorp, strip_ansi, press_enter


class SettingsMenu:
    """
    A lightweight menu for viewing and editing a SettingsDict.
    """
    def __init__(
        self,
        settings: SettingsDict,
        settings_path: str,
        logger: Optional[logging.Logger] = None
    ):
        self.settings      = settings
        self.settings_path = settings_path
        self.logger        = logger
        self.keys: list[str] = list(settings.keys())
        # Preserve the key order from the dict
        self.keys: list[str] = list(settings.keys())


    def clear_screen(self) -> None:
        os.system("cls" if os.name == "nt" else "clear")



    def display(self) -> None:
        """Render the current settings as a neatly aligned table."""
        self.clear_screen()

        # Prepare column headers
        h1 = "No."
        h2 = "Setting"
        h3 = "Current Value"

        # Build display titles (with underline) and plain values
        titles = [underline(k[0].upper()) + k[1:] for k in self.keys]
        vals   = [str(self.settings[k]) for k in self.keys]

        # Compute column widths based on content + headers
        col1_w = max(len(h1), *(len(str(i+1)) for i in range(len(self.keys))))
        col2_w = max(len(strip_ansi(h2)), *(len(strip_ansi(t)) for t in titles))
        col3_w = max(len(strip_ansi(h3)), *(len(v) for v in vals))

        # Build the horizontal border segments
        border = (
            "+" + "-"*(col1_w+2)
            + "+" + "-"*(col2_w+2)
            + "+" + "-"*(col3_w+2)
            + "+"
        )
        # Header row
        header = (
            f"| {h1:^{col1_w}} "
            f"| {h2:^{col2_w}} "
            f"| {h3:^{col3_w}} |"
        )

        print(border)
        print(header)
        print(border)

        # Data rows
        for idx, (title, val) in enumerate(zip(titles, vals), 1):
            # Strip ANSI to measure
            raw_title = strip_ansi(title)
            print(
                f"| {idx:>{col1_w}} "
                f"| {title:<{col2_w + (len(title)-len(raw_title))}} "
                f"| {val:<{col3_w}} |"
            )
        print(border)

        # “Back” row spanning all columns
        inner_width = (col1_w+2) + (col2_w+2) + (col3_w+2) + 2  # +2 for the two inner '|' removal
        back_text = "(0/q). Back to main menu"
        print(f"|{back_text:^{inner_width}}|")
        print(border)

        print("\nEnter number (0/q) of setting to edit:")

    def get_selection(self) -> Optional[int]:
        raw = input("> ").strip()
        if raw == "0":
            return 0
        if raw.isdigit():
            n = int(raw)
            if 1 <= n <= len(self.keys):
                return n
        colorp("Invalid selection.", "h red")
        return None

    def save(self) -> None:
        """Persist settings to disk and log."""
        with open(self.settings_path, "w", encoding="utf-8") as f:
            json.dump(self.settings, f, ensure_ascii=False, indent=2)
        if self.logger:
            self.logger.debug(f"Settings saved to {self.settings_path}")

    def _validate_and_cast(
        self,
        key: str,
        old: Any,
        new_raw: str
    ) -> Any | None:
        """
        Validate new_raw against VALID_SETTINGS, cast to old's type,
        return the new value or None if invalid.
        """
        allowed = VALID_SETTINGS.get(key, None)

        # Enumerated string choices
        if isinstance(allowed, list) and allowed:
            if new_raw not in allowed:
                colorp(f"- '{new_raw}' not in allowed: {allowed}", "h red")
                if self.logger:
                    self.logger.warning(f"Validation failed for {key}: '{new_raw}' not in {allowed}")
                return None
            return new_raw

        # Numeric range
        if isinstance(allowed, tuple) and len(allowed) == 2 and isinstance(old, (int, float)):
            try:
                val = type(old)(new_raw)
            except ValueError:
                colorp("- Must be a number.", "h red")
                if self.logger:
                    self.logger.warning(f"Validation failed for {key}: '{new_raw}' not a number")
                return None
            lo, hi = allowed
            if not (lo <= val <= hi):
                colorp(f"- Value must be between {lo} and {hi}.", "h red")
                if self.logger:
                    self.logger.warning(f"Validation failed for {key}: {val} not in range {allowed}")
                return None
            return val

        # Fallback: infer type from old value
        try:
            if isinstance(old, bool):
                val = new_raw.lower() in ("1", "true", "yes", "y", "on")
            elif isinstance(old, int):
                val = int(new_raw)
            elif isinstance(old, float):
                val = float(new_raw)
            else:
                val = new_raw
        except ValueError:
            colorp("-Invalid type for this setting.", "h red")
            if self.logger:
                self.logger.warning(f"Validation failed for {key}: cannot cast '{new_raw}' to {type(old).__name__}")
            return None

        return val
            
    def run(self) -> None:
        """
        Loop: display, pick a setting, show allowed values,
        validate & cast, save, and log changes.
        """
        while True:
            self.display()

            sel = None
            while sel is None:
                sel = self.get_selection()

            if sel in [0, "q", "quit"]:
                break  # back to main menu

            key = self.keys[sel - 1]
            old = self.settings[key]
            allowed = VALID_SETTINGS.get(key, None)

            # Build prompt, including allowed values if any
            prompt = f"Enter new value for '{key}' (current: {old})"
            if isinstance(allowed, list) and allowed:
                prompt += f" [allowed: {', '.join(allowed)}]"
            elif isinstance(allowed, tuple) and len(allowed) == 2:
                prompt += f" [range: {allowed[0]}–{allowed[1]}]"
            prompt += ": "

            new_raw = input(prompt).strip()
            if not new_raw:
                print("No change.")
                continue

            new = self._validate_and_cast(key, old, new_raw)
            if new is None:
                press_enter()
                continue

            # Apply change
            self.settings[key] = new
            self.save()
            if self.logger:
                self.logger.info(f"Setting '{key}' changed from '{old}' to '{new}'")

            colorp(f"+ {key} updated to {new}", "h green")
            press_enter()