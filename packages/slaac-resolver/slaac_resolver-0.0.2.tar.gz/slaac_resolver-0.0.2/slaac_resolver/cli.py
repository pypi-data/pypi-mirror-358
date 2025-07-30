import argparse
import json
from slaac_resolver.core import get_ipv6_neighbors

def main():
    parser = argparse.ArgumentParser(description="Discover IPv6 neighbors via SLAAC on a given interface")
    parser.add_argument("interface", help="The network interface to scan (e.g. br0)")
    args = parser.parse_args()

    data = get_ipv6_neighbors(args.interface)
    print(json.dumps(data))
