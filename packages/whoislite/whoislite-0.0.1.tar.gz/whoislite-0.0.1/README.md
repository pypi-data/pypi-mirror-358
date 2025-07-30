
## whoislite

WhoisLite is a fast, pure Python library for querying WHOIS information for domain names across hundreds of TLDs.

#### Install

```bash
pip install whoislite
```

#### Example

```python
from whoislite.utils import WhoisLite

domain = "google.com"
w = WhoisLite(domain)
w.lookup()
w.print_summary()
print(w.to_json())
```