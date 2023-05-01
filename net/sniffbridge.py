#!/usr/bin/env python3

"""
Create a network bridge for passive traffic sniffing.

This script creates a bridge device and attaches the specified
network interfaces to it. The bridge interface can then be
monitored to observe traffic flowing over the bridge.

It also sets the group_fwd_mask to the maximum possible value
in order to also forward traffic destined to
'IEEE 802.1D MAC Bridge Filtered MAC Group Addresses'
which would otherwise not be forwarded.
This is required, e.g. for 802.1X EAP traffic to cross the bridge.

In order to avoid traffic originating from the bridge setup,
IPv6 is disabled on the involved interfaces, due to SLAAC traffic.
"""

import argparse
import os
import subprocess
import sys

try:
    from pyroute2 import NDB
except ModuleNotFoundError:
    print("Error: Missing dependency pyroute2", file=sys.stderr)
    sys.exit(1)


def setup_sniffbridge(bridge, interfaces, fwd_mask):
    with NDB() as ndb:
        print(f"Creating bridge interface {bridge}")
        with ndb.interfaces.create(ifname=bridge, kind="bridge") as br:
            for ifname in interfaces:
                print(f"Disabling IPv6 on interface {ifname}")
                subprocess.run(["sysctl", "-q", "-w", f"net.ipv6.conf.{ifname}.disable_ipv6=1"], check=True)
                print(f"Attaching interface {ifname} to bridge")
                br.add_port(ifname)
            print(f"Setting fwd_mask {fwd_mask} for bridge")
            br.set(state="down", br_group_fwd_mask=fwd_mask)
            br.commit()
            print(f"Disabling IPv6 on bridge interface {bridge}")
            subprocess.run(["sysctl", "-q", "-w", f"net.ipv6.conf.{bridge}.disable_ipv6=1"], check=True)
            print(f"Setting bridge interface {bridge} up")
            br.set(state="up")


def teardown_sniffbridge(bridge, interfaces):
    with NDB() as ndb:
        print(f"Removing bridge interface {bridge}")
        with ndb.interfaces[bridge] as br:
            br.remove()
    for ifname in interfaces:
        print(f"Enabling IPv6 on interface {ifname}")
        subprocess.run(["sysctl", "-q", "-w", f"net.ipv6.conf.{ifname}.disable_ipv6=0"], check=True)


def main():
    if os.geteuid() != 0:
        print("Error: Need to run as root", file=sys.stderr)
        sys.exit(1)

    argparser = argparse.ArgumentParser(description="Create a network bridge for passive traffic sniffing.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    argparser.add_argument("--bridge", "-b", default="sniffBr0", help="Name of bridge device to create")
    argparser.add_argument("--fwd-mask", default=65528, help="Change forward mask for 'IEEE 802.1D MAC Bridge Filtered MAC Group Addresses'")
    argparser.add_argument("--cleanup", action="store_true", default=False, help="Teardown instead of create the bridge setup")
    argparser.add_argument("interfaces", nargs="+", help="Interfaces to connect to the bridge")
    parsed_args = argparser.parse_args()

    if parsed_args.cleanup:
        teardown_sniffbridge(parsed_args.bridge, parsed_args.interfaces)
    else:
        setup_sniffbridge(parsed_args.bridge, parsed_args.interfaces, parsed_args.fwd_mask)


if __name__ == "__main__":
    main()
