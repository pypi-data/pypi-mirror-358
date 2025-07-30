from typing import Mapping, Any

import base64
import json
import urllib.parse






def encode_shadowsocks_uri(config: Mapping[str, Any]) -> str:
    method = config["parsed"]["method"]
    password = config["parsed"]["password"]
    address = config["address"]
    port = config["port"]
    remark = config.get("remark")
    
    userinfo = f"{method}:{password}@{address}:{port}"
    userinfo_b64 = base64.urlsafe_b64encode(userinfo.encode()).decode().rstrip("=")
    uri = f"ss://{userinfo_b64}"
    if remark:
        uri += "#" + urllib.parse.quote(remark)
    return uri


def encode_vmess_uri(raw: Mapping[str, Any]) -> str:
    b64 = base64.urlsafe_b64encode(json.dumps(raw).encode()).decode().rstrip("=")
    return f"vmess://{b64}"


def encode_vless_uri(cfg: Mapping[str, Any]) -> str:
    user = cfg["parsed"]["uuid"]
    address = cfg["address"]
    port = cfg["port"]
    query = cfg["parsed"].get("params", {})
    query_str = urllib.parse.urlencode({k: v[0] for k, v in query.items()})
    remark = urllib.parse.quote(cfg.get("remark", ""))
    return f"vless://{user}@{address}:{port}?{query_str}#{remark}"


def encode_trojan_uri(cfg: Mapping[str, Any]) -> str:
    password = cfg["parsed"]["password"]
    address = cfg["address"]
    port = cfg["port"]
    query = cfg.get("params", {})
    query_str = urllib.parse.urlencode({k: v[0] for k, v in query.items()})
    remark = urllib.parse.quote(cfg.get("remark", ""))
    return f"trojan://{password}@{address}:{port}?{query_str}#{remark}"


def config_to_uri(config: Mapping[str, Any]) -> str:
    t = config["type"]
    if t == "ss":
        return encode_shadowsocks_uri(config)
    elif t == "vmess":
        return encode_vmess_uri(config["raw"])
    elif t == "vless":
        return encode_vless_uri(config)
    elif t == "trojan":
        return encode_trojan_uri(config)
    else:
        raise ValueError(f"Unsupported type: {t}")