# SLAAC Resolver

Discover SLAAC-configured IPv6 neighbors and resolve their mDNS names using Avahi.

## Overview

This tool scans a given network interface for IPv6 neighbors discovered via SLAAC, and attempts to resolve their names using `avahi-resolve-address`. It can be used both as a command-line utility and as a Python library.

## Installation

Clone the repository and install it in editable mode:

```bash
git clone https://github.com/cjuniorfox/slaac-resolver.git
cd slaac-resolver
pip install -e .
````

This will make the `slaac-resolver` command available on your system.

## Usage

### Command-Line Interface

```bash
slaac-resolver <interface>
```

Example:

```bash
slaac-resolver br0
```

The output is a JSON list of resolved neighbors, like:

```json
[
  {
    "hostname": ["mydevice", "local"],
    "ipv6": ["fe80", "", "abcd", "1234", "5678", "9abc", "def0", "1234"]
  }
]
```

### Python Library

You can also use the resolver in your Python code:

```python
from slaac_resolver import get_ipv6_neighbors

neighbors = get_ipv6_neighbors("br0")
print(neighbors)
```

## Requirements

* Python 3.7+
* `ip` command (from iproute2)
* `avahi-resolve-address` (part of `avahi-utils`)

## License

GNU 3.0 License