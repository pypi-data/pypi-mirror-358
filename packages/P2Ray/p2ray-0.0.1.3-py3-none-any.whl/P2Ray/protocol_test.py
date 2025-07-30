from typing import Union, cast, Any
import socket
import subprocess
import tempfile
import time
import json
import requests

from P2Ray.config_parser import TrojanParsed, SSParsed, VlessParsed, VmessParsed

V2RAYBINARY = "v2ray"

def tcp_ping(host: str, port: int, timeout: float = 5.0) -> float | None:
    """
    Basic TCP ping: returns latency in milliseconds or None if timeout/failure.
    """
    start = time.time()
    try:
        with socket.create_connection((host, port), timeout):
            return (time.time() - start) * 1000
    except Exception:
        return None

def test_shadowsocks(
    config: SSParsed, 
    test_url: str = "http://www.google.com/generate_204", 
    timeout: float = 10.0) -> float | None:
    """
    Test Shadowsocks by making an HTTP request through the proxy.
    config = {
        'address': host,
        'port': port,
        'password': password,
        'method': method
    }
    """
    proxy_url = f"socks5://127.0.0.1:1081"  # Assume we use 1081 locally via v2ray
    proxies = {
        "http": proxy_url,
        "https": proxy_url
    }
    try:
        start = time.time()
        resp = requests.get(test_url, proxies=proxies, timeout=timeout)
        if resp.status_code == 204 or resp.status_code < 400:
            return (time.time() - start) * 1000
    except Exception:
        return None
    return None


def test_v2ray(
    config: Union[VlessParsed, VmessParsed, TrojanParsed], 
    v2ray_binary: str = V2RAYBINARY, 
    timeout: float = 15.0
    ) -> float | None:
    """
    Tests VLESS / VMess / Trojan using v2ray-core.
    Spawns a temporary v2ray instance and routes an HTTP request via local SOCKS5.
    """
    v2_config: dict[str, Any] = {
        "log": {"loglevel": "warning"},
        "inbounds": [{
            "port": 1081,
            "listen": "127.0.0.1",
            "protocol": "socks",
            "settings": {"auth": "noauth", "udp": False}
        }],
        "outbounds": [config_to_v2ray_outbound(config)],
        "routing": {"domainStrategy": "AsIs"},
    }

    with tempfile.NamedTemporaryFile(mode="w+", suffix=".json", delete=False) as tmp:
        json.dump(v2_config, tmp)
        tmp.flush()
        cmd = [v2ray_binary, "-config", tmp.name]
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        try:
            time.sleep(2.0)  # wait for v2ray to start
            start = time.time()
            proxies = {
                "http": "socks5://127.0.0.1:1081",
                "https": "socks5://127.0.0.1:1081"
            }
            resp = requests.get("http://www.google.com/generate_204", proxies=proxies, timeout=timeout)
            if resp.status_code == 204:
                return (time.time() - start) * 1000
        except Exception:
            return None
        finally:
            proc.terminate()
            proc.wait()
    return None

def config_to_v2ray_outbound(
    cfg: VlessParsed | VmessParsed | SSParsed | TrojanParsed
    ) -> dict[str, Any]:
    """
    Converts parsed config into v2ray outbound block.
    Supports: vless, vmess, trojan.
    """
    protocol = cfg['type']
    if protocol == "vless":
        vl = cast(VlessParsed, cfg)
        return {
            "protocol": "vless",
            "settings": {
                "vnext": [{
                    "address": vl["address"],
                    "port": vl["port"],
                    "users": [{
                        "id": vl["uuid"],
                        "encryption": vl.get("params", {}).get("encryption", ["none"])[0]
                    }]
                }]
            },
            "streamSettings": {
                "network": vl.get("params", {}).get("type", ["tcp"])[0],
                "security": vl.get("params", {}).get("security", ["none"])[0],
                "tcpSettings": {
                    "header": {"type": vl.get("params", {}).get("headerType", ["none"])[0]}
                },
                "wsSettings": {
                    "path": vl.get("params", {}).get("path", [""])[0],
                    "headers": {"Host": vl.get("params", {}).get("host", [""])[0]}
                }
            }
        }

    elif protocol == "vmess":
        vm = cast(VmessParsed, cfg)
        raw = vm["raw"]
        return {
            "protocol": "vmess",
            "settings": {"vnext": [{
                "address": vm["address"],
                "port": vm["port"],
                "users": [{
                    "id": raw["id"],
                    "alterId": int(raw.get("aid", 0)),
                    "security": raw.get("scy", "auto")
                }]
            }]},
            "streamSettings": {
                "network": raw.get("net", "tcp"),
                "security": "tls" if raw.get("tls") else "none",
                "tcpSettings": {"header": {"type": raw.get("type", "")}},
                "kcpSettings": {},
                "wsSettings": {
                    "path": raw.get("path", "/"),
                    "headers": {"Host": raw.get("host", "")}
                },
                "httpSettings": {"path": raw.get("path", "/"), "host": [raw.get("host", "")]}
            }
        }

    elif protocol == "trojan":
        tor = cast(TrojanParsed, cfg)
        return {
            "protocol": "trojan",
            "settings": {
                "servers": [{
                    "address": tor["address"],
                    "port": tor["port"],
                    "password": tor["password"]
                }]
            },
            "streamSettings": {
                "security": tor.get("params", {}).get("security", ["tls"])[0],
                "tcpSettings": {"header": {"type": cfg.get("params", {}).get("headerType", ["none"])[0]}},
                "tlsSettings": {
                    "serverName": tor.get("params", {}).get("sni", [""])[0]
                }
            }
        }

    
    elif protocol == "ss":
        # Shadowsocks via v2ray-core
        ss = cast(SSParsed, cfg)
        return {
            "protocol": "shadowsocks",
            "settings": {
                "servers": [{
                    "address":  ss["address"],
                    "port":     ss["port"],
                    "method":   ss["method"],
                    "password": ss["password"],
                }]
            },
            # Optional streamSettings if you had any params (e.g. plugin)
            "streamSettings": {}
        }
        
    else:
        raise ValueError(f"Unsupported protocol for outbound: {protocol}")
