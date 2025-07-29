import os
import re
from typing import List, Callable, Optional


# ─────────────────────────────────────────────────────────────────────────────
# Color configuration (easy to override)
CLR_RESET     = "\033[0m"
CLR_BORDER    = "\033[97m"  # white
CLR_TITLE     = "\033[97m"  # white (menu title)
CLR_OPTION    = "\033[97m"  # white (option label)
CLR_NUMBER    = "\033[95m"  # purple (the choice number)
CLR_DESC      = "\033[90m"  # gray   (the description)
# ─────────────────────────────────────────────────────────────────────────────



class Option:
    def __init__(self, label: str, description: str, action: Callable[[], None]):
        """
        Represents one menu option.
        
        :param label: A short name for the option (e.g., "1", "A", or "Add Config")
        :param description: A fuller description shown in the menu
        :param action: A no-argument callable that executes the option
        """
        self.label = label
        self.description = description
        self.action = action




class Menu:
    def __init__(self, title: str, options: List[Option], parent: Optional['Menu'] = None):
        """
        A text-based menu, displaying options and handling user selection.

        :param title: The title of the menu
        :param options: A list of Option instances
        :param parent: Optional parent Menu (for 'back' functionality)
        """
        self.title = title
        self.options = options
        self.parent = parent

    def clear_screen(self):
        """Clear the terminal screen."""
        os.system('cls' if os.name == 'nt' else 'clear')
        
    # v4
    def display(self, status):
        os.system("cls" if os.name=="nt" else "clear")

        # Prepare raw title and options with ANSI
        ansi_title = f"{CLR_TITLE}{self.title}{CLR_RESET}"
        entries = []
        for idx, opt in enumerate(self.options, 1):
            num = f"{CLR_NUMBER}{idx}.{CLR_RESET}"
            lbl = f"{CLR_OPTION}{opt.label}{CLR_RESET}"
            desc= f"{CLR_DESC}{opt.description}{CLR_RESET}"
            entries.append((num + lbl, desc))
            
        # Add Exit
        entries.append((f"{CLR_NUMBER}0.{CLR_RESET}{CLR_OPTION} Exit{CLR_RESET}", ""))

        # ANSI-stripped for measurements
        def strip(x): return re.sub(r'\x1b\[[0-9;]*m', '', x)

        # Column widths
        label_width = max(len(strip(lbl)) for lbl,_ in entries)
        desc_width  = max(len(strip(desc)) for _,desc in entries)

        # Padding config
        pad_lr = 2         # spaces on left & right
        pad_mid = 4        # spaces between label & desc

        content_width = label_width + pad_mid + desc_width
        title_width   = len(strip(self.title))
        box_inner     = max(content_width, title_width)

        total_width = box_inner + pad_lr*2
        border = CLR_BORDER + "+" + "-"*total_width + "+" + CLR_RESET

        # Blank line inside box
        blank = CLR_BORDER + "|" + " "*(total_width) + "|" + CLR_RESET

        # Print top border
        print(border)
        print(blank)

        # Title line (centered in box_inner, then padded)
        ### title_str = ansi_title.center(box_inner)
        title_spaces = (total_width - title_width) / 2
        if title_spaces % 1 == 0:
            title_spaces = int(title_spaces)
            title_str = " " * title_spaces + ansi_title + " " * title_spaces
        else:
            title_spaces = int(title_spaces)
            title_str = " " * (title_spaces + 1) + ansi_title + " " * title_spaces
        title_line = title_str
        print(CLR_BORDER + "|" + title_line + "|" + CLR_RESET)
        print(blank)

        # Option lines
        for lbl, desc in entries:
            raw_lbl = strip(lbl)
            raw_desc= strip(desc)
            # Build content: label + mid padding + desc, then pad to box_inner
            content = raw_lbl.ljust(label_width) + " "*pad_mid + raw_desc.ljust(desc_width)
            # Now insert ANSI wrappers around the appropriate slices
            ansi_content = lbl + " "*(label_width - len(raw_lbl)) \
                          + " "*pad_mid \
                          + desc + " "*(desc_width - len(raw_desc))
            # Pad left/right
            line = " " * pad_lr + ansi_content + " " * pad_lr
            print(CLR_BORDER + "|" + line + "|" + CLR_RESET)

        # Bottom padding and border
        print(blank)
        print(border)
        
        if status:
            print(status)


    @staticmethod
    def _strip_ansi(text: str) -> str:
        """Remove ANSI escape sequences for measuring lengths."""
        import re
        ansi = re.compile(r'\x1b\[[0-9;]*m')
        return ansi.sub('', text)
    
    
        
    def get_selection(self) -> Optional[int]:
        raw = input("\nSelect option: ").strip()
        if raw == "0":
            return 0
        if raw.isdigit():
            idx = int(raw)
            if 1 <= idx <= len(self.options):
                return idx
        print("Invalid selection.")
        return None


# Example usage (uncomment to test):
# def say_hello():
#     print("Hello, world!")
#
# def say_goodbye():
#     print("Goodbye!")
#
# main_menu = Menu("Main Menu", [
#     Option("Say Hello", "Print a greeting", say_hello),
#     Option("Say Goodbye", "Print a farewell", say_goodbye),
# ])
# main_menu.run()