import os
import re
from typing import List, Callable, Optional

from P2Ray.utils import colorp, color

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
    def __init__(
        self, 
        label: str, 
        description: str, 
        action: Callable[[], None],
        aliases: list[str] | None = None,
        ):
        """
        Represents one menu option.
        
        :param label: A short name for the option (e.g., "1", "A", or "Add Config")
        :param description: A fuller description shown in the menu
        :param action: A no-argument callable that executes the option
        """
        self.label = label
        self.description = description
        self.action = action
        self.aliases     = [a.lower() for a in (aliases or [])]

    @property
    def is_separator(self) -> bool:
        return False


class Separator(Option):
    def __init__(
        self, 
        length: int = 18,
        char: str = "─"
        ):
        label = length * char
        self.label = color(label, "gray")  # apply ANSI here
        self.description = None
        self.action = None
        self.aliases = []
    
    @property
    def is_separator(self) -> bool:
        return True


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
    def display(
        self, 
        status: str
        ) -> None:
        os.system("cls" if os.name=="nt" else "clear")

        # Prepare raw title and options with ANSI
        ansi_title = f"{CLR_TITLE}{self.title}{CLR_RESET}"
        entries: list[tuple[str, str]] = []
        visible_idx = 1  # only for non-separators

        for opt in self.options:
            if opt.is_separator:
                # Just show a visual separator — maybe in dim or border color
                sep_line = color(opt.label, "gray")
                entries.append((sep_line, ""))  # no description
            else:
                num = f"{CLR_NUMBER}{visible_idx}.{CLR_RESET}"
                lbl = f"{CLR_OPTION}{opt.label}{CLR_RESET}"
                desc = f"{CLR_DESC}{opt.description}{CLR_RESET}"
                entries.append((num + lbl, desc))
                visible_idx += 1
            
        # Add Exit
        entries.append((f"{CLR_NUMBER}0.{CLR_RESET}{CLR_OPTION} Exit{CLR_RESET}", ""))

        # ANSI-stripped for measurements
        def strip(x: str): return re.sub(r'\x1b\[[0-9;]*m', '', x)

        # Only consider non-separator options for label/description width
        visible_opts: list[Option] = []
        for opt in self.options:
            if not opt.is_separator:
                visible_opts.append(opt)

        label_width = max(
            len(self._strip_ansi(f"{CLR_NUMBER}{i+1}.{CLR_RESET}{CLR_OPTION}{opt.label}{CLR_RESET}"))
            for i, opt in enumerate(visible_opts)
        )

        desc_width = max(
            len(self._strip_ansi(f"{CLR_DESC}{opt.description}{CLR_RESET}"))
            for opt in visible_opts
        )

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
            _ = raw_lbl.ljust(label_width) + " "*pad_mid + raw_desc.ljust(desc_width) # content = 
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
        """
        Read user input and return:
        • 0          → Exit
        • N (1-based)→ the Nth non-separator option, returned as its index+1
        • None      → invalid input
        """
        raw = input("\nSelect option: ").strip().lower()
        # 0 always means “Exit”
        if raw == "0":
            return 0

        # Build a list of positions of non-separator options
        visible_positions = [
            idx for idx, opt in enumerate(self.options)
            if not getattr(opt, "is_separator", False)
        ]  # these are 0-based indices in self.options

        # 1) Digit input → map to Nth non-separator
        if raw.isdigit():
            n = int(raw)
            if 1 <= n <= len(visible_positions):
                # We return position+1 so that run() can do self.options[sel-1]
                return visible_positions[n-1] + 1
            else:
                print("Invalid selection.")
                return None

        # 2) Alias input → look up in each real option
        for idx, opt in enumerate(self.options):
            if not getattr(opt, "is_separator", False) and raw in getattr(opt, "aliases", []):
                return idx + 1

        # 3) Anything else is invalid
        colorp("Invalid selection.", "h red")
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