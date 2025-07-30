import socket
import re
import json


class WhoisLite:
    WHOIS_SERVERS = {
        ".com": "whois.verisign-grs.com",
        ".net": "whois.verisign-grs.com",
        ".org": "whois.pir.org",
        ".info": "whois.afilias.net",
        ".biz": "whois.biz",
        ".us": "whois.nic.us",
        ".uk": "whois.nic.uk",
        ".co.uk": "whois.nic.uk",
        ".ca": "whois.cira.ca",
        ".de": "whois.denic.de",
        ".eu": "whois.eu",
        ".ru": "whois.tcinet.ru",
        ".su": "whois.tcinet.ru",
        ".рф": "whois.tcinet.ru",
        ".jp": "whois.jprs.jp",
        ".cn": "whois.cnnic.cn",
        ".xyz": "whois.nic.xyz",
        ".io": "whois.nic.io",
        ".me": "whois.nic.me",
        ".tv": "whois.nic.tv",
        ".cc": "whois.nic.cc",
        ".site": "whois.nic.site",
        ".online": "whois.nic.online",
        ".store": "whois.nic.store",
        ".app": "whois.nic.google",
        ".dev": "whois.nic.google",
        ".ai": "whois.ai",
        ".lt": "whois.domreg.lt",
        ".fr": "whois.afnic.fr",
        ".it": "whois.nic.it",
        ".pl": "whois.dns.pl",
        ".fi": "whois.fi",
        ".cz": "whois.nic.cz",
        ".dk": "whois.dk-hostmaster.dk",
        ".se": "whois.iis.se",
        ".no": "whois.norid.no",
        ".sk": "whois.sk-nic.sk",
        ".ua": "whois.ua",
        ".by": "whois.cctld.by",
    }

    SUMMARY_FIELDS = {
        "domain_name": r"Domain Name:\s*([^\s]+)",
        "registrar": r"Registrar:\s*(.+)",
        "creation_date": r"Creation Date:\s*([^\s]+)",
        "expiration_date": r"(?:Registry Expiry|Expiration Date):\s*([^\s]+)",
        "updated_date": r"Updated Date:\s*([^\s]+)",
        "name_servers": r"Name Server:\s*([^\s]+)",
        "status": r"Status:\s*([^\s]+)",
        "registrant": r"Registrant(?: Name)?:\s*(.+)",
    }

    def __init__(self, domain):
        self.domain = domain.lower()
        self.tld = self._get_tld(domain)
        self.server = self._get_server()
        self.raw = None
        self._json = None

    def _get_tld(self, domain):
        parts = domain.lower().split(".")
        for i in range(len(parts)):
            tld = "." + ".".join(parts[i:])
            if tld in self.WHOIS_SERVERS:
                return tld
        return "." + parts[-1]

    def _get_server(self):
        if self.tld in self.WHOIS_SERVERS:
            return self.WHOIS_SERVERS[self.tld]
        return self._discover_whois_server_from_iana()

    def _discover_whois_server_from_iana(self):
        try:
            result = self._raw_whois_query("whois.iana.org", self.tld[1:])
            match = re.search(r"whois:\s*(\S+)", result, re.IGNORECASE)
            if match:
                return match.group(1)
        except Exception:
            pass
        return None

    def _raw_whois_query(self, server, query):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(15)
            s.connect((server, 43))
            s.send((query + "\r\n").encode())
            response = b""
            while True:
                data = s.recv(4096)
                if not data:
                    break
                response += data
        return response.decode(errors="ignore")

    def lookup(self):
        if not self.server:
            raise Exception(f"WHOIS server not found for domain {self.domain}")
        data = self._raw_whois_query(self.server, self.domain)
        match = re.search(r"Registrar WHOIS Server:\s*(\S+)", data)
        if match and match.group(1) != self.server:
            try:
                data = self._raw_whois_query(match.group(1), self.domain)
            except Exception:
                pass
        self.raw = data
        self._json = None  # Reset parsed data
        return self.raw

    def parse_json(self):
        if not self.raw:
            return None
        result = {}
        for field, pattern in self.SUMMARY_FIELDS.items():
            if field == "name_servers":
                matches = re.findall(pattern, self.raw, re.IGNORECASE)
                result[field] = (
                    list(set([m.strip() for m in matches])) if matches else None
                )
            elif field == "status":
                matches = re.findall(pattern, self.raw, re.IGNORECASE)
                result[field] = (
                    list(set([m.strip() for m in matches])) if matches else None
                )
            else:
                match = re.search(pattern, self.raw, re.IGNORECASE)
                result[field] = match.group(1).strip() if match else None
        self._json = result
        return result

    def to_json(self):
        if self._json is not None:
            return self._json
        return self.parse_json()

    def print_summary(self):
        summary = self.to_json()
        if not summary:
            print("No summary available.")
            return
        print(json.dumps(summary, indent=2, ensure_ascii=False))
