from typing import (
    Literal, Optional, Any, Dict, 
    TypedDict, cast, NotRequired)

import json
import time
import os
import csv
from datetime import datetime


from P2Ray.config_parser import (
    parse_uri, ParsedConfig, VlessParsed, 
    VmessParsed, TrojanParsed, SSParsed)
from P2Ray.protocol_test import test_v2ray, test_shadowsocks



class ProxyConfigData(TypedDict):
    type: Literal["vless", "vmess", "ss", "trojan"]
    address: str
    port: int
    raw: Dict[str, Any]
    remark: str
    added:         NotRequired[float]
    ping_count:    NotRequired[int]
    last_ping:     NotRequired[ Optional[float] ]
    last_latency:  NotRequired[ Optional[float] ]
    working_count: NotRequired[int]
    working_times: NotRequired[ list[float] ]
    id:            NotRequired[ Optional[str] ]
    parsed:        NotRequired[ParsedConfig]


class ProxyConfig:
    def __init__(
        self, 
        data: ProxyConfigData, 
        parsed: ParsedConfig
        ) -> None:
        """
        data: metadata + core fields
        parsed: full output of parse_uri(uri) for testing
        """
        # Keep the parsed config for testing
        self._parsed: ParsedConfig = parsed

        # Core fields
        self.type: Literal["vless", "vmess", "ss", "trojan"] = data["type"]
        self.address:     str             = data["address"]
        self.port:        int             = data["port"]
        self.raw:         Dict[Any, Any]  = data.get("raw", {})
        self.remark:      str             = data.get("remark", "")

        # Metadata
        self.added:        float   = data.get("added", time.time())
        self.ping_count:   int     = data.get("ping_count", 0)
        self.last_ping:    Optional[float] = data.get("last_ping")
        self.last_latency: Optional[float] = data.get("last_latency")
        
        self.working_count: int         = data.get("working_count", 0)
        self.working_times: list[float] = data.get("working_times", [])
        
        # Internal unique ID (string)
        self.id: Optional[str] = data.get("id") # It is Required but it may be added after init

    @classmethod
    def from_uri(
        cls, 
        uri: str
        ) -> "ProxyConfig":
        """
        Create a ProxyConfig from a URI string.
        """
        parsed = parse_uri(uri) # type ParsedConfig
        data = ProxyConfigData(
            type =      parsed["type"],
            address =   parsed["address"],
            port =      parsed["port"],
            raw =       parsed.get("raw", {}),
            remark =    parsed.get("remark", ""),
            # metadata omitted → defaults
        )
        return cls(data, parsed)

    def to_dict(self) -> ProxyConfigData:
        """
        Persist **both** metadata and the original parsed dict.
        """
        return ProxyConfigData(
            # core + metadata
            type =           self.type,
            address =        self.address,
            port =           self.port,
            raw =            self.raw,
            remark =         self.remark,
            added =          self.added,
            ping_count =     self.ping_count,
            last_ping =      self.last_ping,
            last_latency =   self.last_latency,
            working_count =  self.working_count,
            working_times =  self.working_times,
            id =             self.id,
            # full parsed dict for future tests
            parsed =         self._parsed, # TypedConfig
        )


    def test(
        self, 
        v2ray_binary: str
        ) -> Optional[float]:
        # uses self._parsed (always present)
        if self.type in ("vless", "vmess", "trojan"):
            cfg = cast(VlessParsed | VmessParsed | TrojanParsed, self._parsed)
            latency = test_v2ray(cfg, v2ray_binary=v2ray_binary)
        elif self.type == "ss":
            ss = cast(SSParsed, self._parsed)
            latency = test_shadowsocks(ss)
        else:
            latency = None

        if latency is not None:
            self.ping_count += 1
            self.last_ping = time.time()
            self.last_latency = latency
        return latency

    
    
    def mark_working(self) -> None:
        """
        Record an actual successful usage event.
        """
        now = time.time()
        self.working_count += 1
        self.working_times.append(now)



class ConfigManager:
    """
    Manages a collection of ProxyConfig objects persisted in JSON.
    """
    def __init__(
        self,
        db_path: str = "config_db.json",
        v2ray_binary: str = "v2ray"
    ) -> None:
        self.db_path = db_path
        self.v2ray_binary = v2ray_binary
        self.configs: list[ProxyConfig] = []
        self._load()


    def _load(self) -> None:
        """Load both metadata and parsed dict from disk."""
        if not os.path.isfile(self.db_path):
            self.configs = []
            return

        with open(self.db_path, "r", encoding="utf-8") as f:
            entries = json.load(f)

        self.configs = []
        for entry in entries:
            # Restore parsed from entry["parsed"]
            parsed = entry.get("parsed", {
                # fallback minimal parsed
                "type":   entry["type"],
                "address": entry["address"],
                "port":    entry["port"],
                "raw":     entry.get("raw", {}),
                "remark":  entry.get("remark", ""),
            })
            cfg = ProxyConfig(entry, parsed)
            self.configs.append(cfg)
            
    def _save(self) -> None:
        """Save everything (metadata + parsed) back to disk."""
        with open(self.db_path, "w", encoding="utf-8") as f:
            json.dump([c.to_dict() for c in self.configs], f, ensure_ascii=False, indent=2)


    def load(self) -> None:
        """Public alias for _load"""
        self._load()

    def save(self) -> None:
        """Public alias for _save"""
        self._save()


    def _next_id(self) -> str:
        """
        Generate the next smallest positive integer (as string) not yet used as an ID.
        """
        used = {c.id for c in self.configs if c.id is not None}
        i = 1
        while str(i) in used:
            i += 1
        return str(i)

    def add_from_uri(
        self,
        uri: str,
        config_id: Optional[str] = None,
        verbose: bool = True
    ) -> ProxyConfig:
        """
        Parse a URI and add as a new config.
        If config_id provided, use it (must be unique); else auto-generate via _next_id().
        Avoid duplicates by type+address+port.
        """
        # Check duplicate
        parsed = parse_uri(uri)
        exists = next(
            (c for c in self.configs
             if c.type == parsed["type"]
             and c.address == parsed["address"]
             and c.port == parsed["port"]),
            None
        )
        if exists:
            if verbose:
                print(f"[!] Already exists with id={exists.id}")
            return exists

        # Create and assign ID
        pc = ProxyConfig.from_uri(uri)
        if config_id:
            if any(c.id == config_id for c in self.configs):
                raise ValueError(f"ID {config_id!r} already in use")
            pc.id = config_id
        else:
            pc.id = self._next_id()

        # Store and persist
        self.configs.append(pc)
        self._save()

        if verbose:
            print(f"[+] Added config id={pc.id}: {pc.address}:{pc.port} ({pc.remark})")
        return pc
    
    

    def test_all(
        self, 
        verbose: bool = True
        ) -> None:
        """
        Show 'testing [...] remark ...', then overwrite with the result line.
        """
        from P2Ray.utils import color
        total = len(self.configs)
        counter = 1
        for c in self.configs:
            # print testing line (no newline)
            print(f"testing [{c.id}] {c.remark} ...", end="", flush=True)
            lat = c.test(self.v2ray_binary)
            # clear line and print result
            print("\r" + " " * 80 + "\r", end="")  # blank out
            status = color(f"{lat:.1f} ms", "h green") if lat is not None else color("failed", "h red")
            if verbose:
                print(f"[{counter}/{total}] - [{c.id}] {c.type}@{c.address}:{c.port} → {status}")
                counter += 1
        self._save()
        


#    def test_all_tqdm(self):
#        """
#        Run protocol-level tests on every config, showing a live tqdm bar.
#        Results are printed above the bar via bar.write().
#        """
#        bar = tqdm(self.configs, desc="Testing configs", unit="cfg", leave=True)
#        for cfg in bar:
#            latency = cfg.test(self.v2ray_binary)
#            status = f"{latency:.1f} ms" if latency is not None else "❌ failed"
#            # Print above the progress bar
#            bar.write(f"[{cfg.id}] {cfg.type}@{cfg.address}:{cfg.port} → {status}")
#        bar.close()
#        self._save()
        

    def mark_working(
        self, 
        config_id: str, 
        verbose: bool = True
        ) -> None:
        """
        Mark the config with given id as successfully used.
        """
        target = next((c for c in self.configs if c.id == config_id), None)
        if not target:
            raise ValueError(f"No config with id={config_id!r}")
        target.mark_working()
        self._save()
        if verbose:
            print(f"[★] Marked id={config_id} as working (total count: {target.working_count})")
        
        
    def list_configs(
        self,
        sort_by: Optional[str] = None,
        reverse: bool = False
        ) -> list[dict[str, Any]]:
        """
        Return list of dicts with columns:
        id, remark, last_ping (ISO), ping_count, last_latency, working_count, last_work (ISO), type
        """
        rows: list[dict[str, Any]] = []
        for c in self.configs:
            last_work = (
                datetime.fromtimestamp(c.working_times[-1]).isoformat(sep=" ", timespec="seconds")
                if c.working_times else ""
            )
            last_ping = (
                datetime.fromtimestamp(c.last_ping).isoformat(sep=" ", timespec="seconds")
                if c.last_ping else ""
            )
            add_time = (
                datetime.fromtimestamp(c.added).isoformat(sep=" ", timespec="seconds")
                if c.added else ""
            )
            rows.append({
                "id":            c.id,
                "remark":        c.remark,
                "last_ping":     last_ping,
                "ping_count":    c.ping_count,
                "last_latency":  f"{c.last_latency:.1f}" if c.last_latency else "",
                "working_count": c.working_count,
                "last_work":     last_work,
                "type":          c.type,
                "add_time":      add_time
            })
        if sort_by:
            rows.sort(key=lambda r: r.get(sort_by) or "", reverse=reverse)
        return rows
        

    def export_csv(
        self,
        path: str,
        sort_by: Optional[str] = None,
        reverse: bool = False
        ) -> None:
        """
        Write list_configs(...) output to CSV file at `path`.
        """
        rows = self.list_configs(sort_by=sort_by, reverse=reverse)
        if not rows:
            return
        with open(path, "w", newline='', encoding="utf-8") as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
            
            
    def report(
        self, 
        stale_days: Optional[float] = None
        ) -> list[dict[str, Any]]:
        """
        Generate a simple report sorted by lastPing desc;
        if stale_days provided, list configs not pinged within that age.
        """
        sorted_cfgs = sorted(
            self.configs,
            key=lambda c: c.last_latency or float('inf')
        )
        report: list[dict[str, Any]] = []
        now = time.time()
        for c in sorted_cfgs:
            entry: dict[str, Any] = {
                'type': c.type,
                'address': c.address,
                'port': c.port,
                'lastLatency_ms': c.last_latency,
                'pingCount': c.ping_count,
                'lastPing': c.last_ping
            }
            if stale_days is not None:
                age = (now - (c.last_ping or 0)) / 86400
                if age > stale_days:
                    report.append(entry)
            else:
                report.append(entry)
        return report
    
    
    
    
    
    def get_by_id(
        self, 
        _id: str
        ) -> Optional[ProxyConfig]:
        """
        Return the ProxyConfig whose .id matches the given string,
        or None if not found.
        """
        for cfg in self.configs:
            if cfg.id == _id:
                return cfg
        return None

    # Optional convenience:
    def __getitem__(
        self, 
        _id: str
        ) -> ProxyConfig:
        """
        Allow mgr[_id] to fetch a config or raise KeyError.
        """
        cfg = self.get_by_id(_id)
        if cfg is None:
            raise KeyError(f"No config with id {_id!r}")
        return cfg
    
    
    def remove_by_id(
        self, 
        _id: str
        ) -> Optional[ProxyConfig]:
        """
        Remove the config with the given ID from this manager and save.
        Returns the removed ProxyConfig, or None if not found.
        """
        for i, cfg in enumerate(self.configs):
            if cfg.id == _id:
                removed = self.configs.pop(i)
                self._save()
                return removed
        return None
    
    
    def move_config_old(
        self, 
        _id: str, 
        other: "ConfigManager"
        ) -> bool:
        """
        Move a config identified by _id from this manager to another.
        Raises KeyError if not found here, ValueError if ID conflict in target.
        Returns True on success.
        """
        # 1) Find and remove locally
        cfg = self.get_by_id(_id)
        if not cfg:
            raise KeyError(f"No config with id {_id!r} to move.")

        if other.get_by_id(_id):
            raise ValueError(f"Target already has a config with id {_id!r}.")

        # 2) Deep‐copy via dict serialization
        data = cfg.to_dict()
        parsed = data.pop("parsed", data)
        new_cfg = ProxyConfig(data, parsed)  # type: ignore

        # 3) Add to other and save
        other.configs.append(new_cfg)
        other._save()

        # 4) Remove from this and save
        self.remove_by_id(_id)

        return True
    
    def move_config(
        self,
        _id: str,
        other: "ConfigManager",
        force: bool = False
        ) -> str:
        """
        Move a config identified by _id from this manager to another.

        Args:
          _id:   ID in this manager to move.
          other: target ConfigManager.
          force: if True, on ID conflict generate new ID instead of error.

        Returns:
          The ID used in the destination (same as _id unless forced).
        """
        # 1) Find locally
        cfg = self.get_by_id(_id)
        if not cfg:
            raise KeyError(f"No config with id {_id!r} to move.")

        # 2) Check conflict in target
        final_id = _id
        if other.get_by_id(final_id):
            if not force:
                raise ValueError(f"Target already has a config with id {final_id!r}.")
            # generate a new one
            final_id = other._next_id()  # your existing ID-generator
            print(f"⚠️ ID conflict: using new ID {final_id!r} instead of {_id!r}")

        # 3) Serialize and clone
        data = cfg.to_dict()
        parsed = data.pop("parsed", data)
        data["id"] = final_id   # override for destination
        new_cfg = ProxyConfig(data, parsed) # type: ignore
        
        # 4) Add to target & save
        other.configs.append(new_cfg)
        other._save()

        # 5) Remove from source & save
        self.remove_by_id(_id)

        return final_id