from typing import TypedDict, List, Dict, Literal, Any
import base64
import json
import urllib.parse

# ─────────────────────────────────────────────────────────────────────────────
# 1) TypedDict for VLESS
class VlessParsed(TypedDict):
    type:       Literal["vless"]     # always "vless"
    uuid:       str
    address:    str
    port:       int
    params:     Dict[str, List[str]]  # e.g. {"security": ["none"], ...}
    remark:     str

class VmessParsed(TypedDict):
    type:       Literal["vmess"]
    uuid:       str
    address:    str
    port:       int
    remark:     str
    raw:        Dict[str, Any]       # the full decoded JSON


class SSParsed(TypedDict):
    type:       Literal["ss"]
    method:     str
    password:   str
    address:    str
    port:       int
    remark:     str

class TrojanParsed(TypedDict):
    type:       Literal["trojan"]
    password:   str
    address:    str
    port:       int
    params:     Dict[str, List[str]]
    remark:     str

ParsedConfig = VlessParsed | VmessParsed | SSParsed | TrojanParsed


# ─────────────────────────────────────────────────────────────────────────────
def parse_uri(uri: str) -> ParsedConfig:
    """
    Dispatch to the appropriate parser based on URI scheme.
    """
    parsed = urllib.parse.urlparse(uri)
    scheme = parsed.scheme.lower()
    if scheme == "vless":
        return parse_vless(parsed)
    elif scheme == "vmess":
        return parse_vmess(uri)
    elif scheme == "ss":
        return parse_shadowsocks(parsed)
    elif scheme == "trojan":
        return parse_trojan(parsed)
    else:
        raise ValueError(f"Unsupported protocol: {scheme}")

def parse_vless(p: urllib.parse.ParseResult) -> VlessParsed:
    """
    vless://uuid@host:port?key=val&…#remark
    """
    # userinfo → uuid
    user, _, hostport = p.netloc.rpartition('@')
    host, _, port = hostport.partition(':')
    params = urllib.parse.parse_qs(p.query)
    remark = urllib.parse.unquote(p.fragment)
    return VlessParsed(
        type="vless",
        uuid=user,
        address=host,
        port=int(port),
        params=params,
        remark=remark
    )

def parse_vmess(uri: str) -> VmessParsed:
    """
    vmess://BASE64(JSON)
    """
    b64 = uri[len("vmess://"):]
    # pad base64
    b64 += '=' * ((4 - len(b64) % 4) % 4)
    data = json.loads(base64.urlsafe_b64decode(b64).decode())
    return VmessParsed(
        type = "vmess",
        uuid = data.get("id"),
        address = data.get("add"),
        port = int(data.get("port")),
        remark = data.get("ps", ""),
        raw = data
    )

def parse_shadowsocks(p: urllib.parse.ParseResult) -> SSParsed:
    """
    ss://[base64(method:pass)]@host:port#remark
    or ss://base64(method:pass@host:port)#remark
    """
    # strip fragment
    remark = urllib.parse.unquote(p.fragment)
    body = p.netloc + p.path  # either "<b64>@host:port" or just "<b64>"
    if "@" in body:
        # format: b64(method:pass) @ host:port
        b64, hostport = body.split("@", 1)
        b64 += '=' * ((4 - len(b64) % 4) % 4)
        method_pass = base64.urlsafe_b64decode(b64).decode()
        method, password = method_pass.split(":", 1)
        host, _, port = hostport.partition(':')
    else:
        # entire authority is base64
        b64 = body.lstrip('/')
        b64 += '=' * ((4 - len(b64) % 4) % 4)
        decoded = base64.urlsafe_b64decode(b64).decode()
        # now decoded = "method:pass@host:port"
        method_pass, hostport = decoded.split("@", 1)
        method, password = method_pass.split(":", 1)
        host, _, port = hostport.partition(':')
    return SSParsed(
        type = "ss",
        method = method,
        password = password,
        address = host,
        port = int(port),
        remark = remark
    )

def parse_trojan(p: urllib.parse.ParseResult) -> TrojanParsed:
    """
    trojan://password@host:port?…#remark
    """
    # p.netloc = "password@host:port"
    password, _, hostport = p.netloc.rpartition('@')
    host, _, port = hostport.partition(':')
    remark = urllib.parse.unquote(p.fragment)
    params = urllib.parse.parse_qs(p.query)
    return TrojanParsed(
        type = "trojan",
        password = password,
        address = host,
        port = int(port),
        params = params,      # e.g. security/tls, sni, etc.
        remark = remark
    )



