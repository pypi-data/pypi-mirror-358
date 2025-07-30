from emoji import replace_emoji

import qrcode
from PIL import Image, ImageTk
import tkinter as tk

from multiprocessing import Process



# ─────────────────────────────────────────────────────────────────────────────
def strip_emojis(
    text: str, 
    replacement: str = "□"
    ) -> str:
    return replace_emoji(text, replacement)

# ─────────────────────────────────────────────────────────────────────────────



# ─────────────────────────────────────────────────────────────────────────────
def generate_qrcode(uri: str) -> Image.Image:
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(uri)
    qr.make(fit=True)
    return qr.make_image(fill_color="black", back_color="white") # type: ignore


def show_image_popup(img: Image.Image, title: str = "QR Code"):
    root = tk.Tk()
    root.title(title)
    root.resizable(False, False)

    tk_img = ImageTk.PhotoImage(img)
    lbl = tk.Label(root, image=tk_img)
    lbl.pack()

    # Center the window
    w, h = img.size
    ws = root.winfo_screenwidth()
    hs = root.winfo_screenheight()
    x = (ws - w) // 2
    y = (hs - h) // 2
    root.geometry(f"{w}x{h}+{x}+{y}")

    # Keep reference to avoid garbage collection
    lbl.image = tk_img # type: ignore

    root.mainloop()
    
    
def _show_qr_process(uri: str, title: str):
    """
    Worker function in a new process. Regenerates the QR and displays it.
    """
    img = generate_qrcode(uri)
    show_image_popup(img, title)
    
    
def show_qr(uri: str, title: str = "QR Code"):
    """
    Spawn a separate process that regenerates and shows the QR code,
    so we never try to pickle a PIL.Image object.
    """
    proc = Process(target=_show_qr_process, args=(uri, title), daemon=True)
    proc.start()

# ─────────────────────────────────────────────────────────────────────────────


    
def test_speed(
    proxy_host: str = "127.0.0.1",
    proxy_port: int = 1081,
    test_url: str = "http://speedtest.tele2.net/5MB.zip",
    max_bytes: int = 1_000_000,
    timeout: float = 15.0
) -> float:
    import time
    import requests
    """
    Measures download speed through a local SOCKS5 proxy:
      - proxy_host/proxy_port: your v2ray inbound
      - test_url: a stable large file
      - max_bytes: cap measurement to this many bytes
    Returns throughput in Mbps.
    """
    proxy = f"socks5h://{proxy_host}:{proxy_port}"
    session = requests.Session()
    session.proxies = {"http": proxy, "https": proxy}

    start = time.time()
    resp = session.get(test_url, stream=True, timeout=timeout)
    downloaded = 0
    for chunk in resp.iter_content(64*1024):
        downloaded += len(chunk)
        if downloaded >= max_bytes:
            break
    end = time.time()

    seconds = end - start
    # bits per second → megabits per second
    mbps = (downloaded * 8) / (seconds * 1_000_000)
    return mbps


# ─────────────────────────────────────────────────────────────────────────────
# Formating Utils
# ─────────────────────────────────────────────────────────────────────────────

CLR_DICT = {
    "reset"  : "\033[0m",
    "gray"   : "\033[90m",
    # Regular Color
    "black"  : "\033[30m",
    "red"    : "\033[31m",
    "green"  : "\033[32m",
    "yellow" : "\033[33m",
    "blue"   : "\033[34m",
    "purple" : "\033[35m",
    "cyan"   : "\033[36m",
    "white"  : "\033[37m",
    # High Intensity (Bright)
    "h black"  : "\033[90m",
    "h red"    : "\033[91m",
    "h green"  : "\033[92m",
    "h yellow" : "\033[93m",
    "h blue"   : "\033[94m",
    "h purple" : "\033[95m",
    "h cyan"   : "\033[96m",
    "h white"  : "\033[97m",   
    # Background
    "b black"  : "\033[40m",
    "b red"    : "\033[41m",
    "b green"  : "\033[42m",
    "b yellow" : "\033[43m",
    "b blue"   : "\033[44m",
    "b purple" : "\033[45m",
    "b cyan"   : "\033[46m",
    "b white"  : "\033[47m",
    # High Intensity Background (Bright)
    "hb black": "\033[100m",  
    "hb red": "\033[101m",    
    "hb green": "\033[102m",
    "hb yellow": "\033[103m", 
    "hb blue": "\033[104m",   
    "hb purple": "\033[105m",
    "hb cyan": "\033[106m",  
    "hb white": "\033[107m",
    # Styles
    "bold": "\033[1m",
    "dim": "\033[2m",
    "italic": "\033[3m",        # Not supported in all terminals
    "underline": "\033[4m",
    "blink": "\033[5m",         # Often ignored in Windows
    "reverse": "\033[7m",       # Swap FG and BG
    "hidden": "\033[8m",        # Not widely supported
    "strikethrough": "\033[9m"  # May not render in CMD
} 


def color(inp: str, color: str) -> str:
    code = CLR_DICT.get(color)
    return f"{code}{inp}\033[0m"

def colorp(inp: str, color: str) -> None:
    code = CLR_DICT.get(color)
    print(f"{code}{inp}\033[0m")

def underline(text: str) -> str:
    return f"\033[4m{text}\033[24m"

# ─────────────────────────────────────────────────────────────────────────────
def styled_header(
    text: str,
    alias: str,
    fg_color: str = "h cyan"
) -> str:
    """
    Return `text` in bright‐cyan, underlining each character
    in `alias` in sequence as they appear (case‐insensitive).
    """
    alias_chars = list(alias.lower())
    ai = 0  # index into alias_chars
    out: list[str] = []

    for ch in text:
        if ai < len(alias_chars) and ch.lower() == alias_chars[ai]:
            # Underline+color this character
            # Combine CSI codes: 4 for underline, plus fg code
            code = CLR_DICT[fg_color][2:-1]  # e.g. "96"
            out.append(f"\033[4;{code}m{ch}\033[0m")
            ai += 1
        else:
            # Just color it
            out.append(color(ch, fg_color))

    return "".join(out)