import subprocess
import sys

def get_ipv6_neighbors(interface):
    try:
        result = subprocess.run(
            ["ip", "-6", "neigh", "show", "dev", interface],
            capture_output=True,
            text=True,
            check=True
        )
    except subprocess.CalledProcessError as e:
        print(f"Failed to get neighbors on {interface}: {e.stderr}", file=sys.stderr)
        return []

    neighbors = []
    for line in result.stdout.strip().split("\n"):
        if "FAILED" in line or not line.strip():
            continue
        parts = line.split()
        if len(parts) < 1:
            continue
        addr = parts[0]
        try:
            resolved = subprocess.run(
                ["avahi-resolve-address", addr],
                capture_output=True,
                text=True,
                check=True
            )
            resolved_output = resolved.stdout.strip().split()
            if len(resolved_output) >= 2:
                name = resolved_output[1]
                neighbors.append({
                    "hostname": name.split("."),
                    "ipv6": addr.split(":")
                })
        except subprocess.CalledProcessError:
            continue
    return neighbors
