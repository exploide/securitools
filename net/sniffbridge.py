#!/usr/bin/env python3

"""
Create a network bridge for passive traffic sniffing.

This script creates a bridge device and attaches the specified
network interfaces to it. The bridge interface can then be
monitored to observe traffic flowing over the bridge.

It also sets the group_fwd_mask to the maximum possible value
(by default) in order to also forward traffic destined to
'IEEE 802.1D MAC Bridge Filtered MAC Group Addresses'
which would otherwise not be forwarded.
This is required, e.g. for 802.1X EAP traffic to cross the bridge.

In order to avoid traffic originating from the bridge setup,
IPv6 is disabled on the bridge interface, due to SLAAC traffic.
"""

import argparse
import logging
import os
import subprocess
import sys


log = logging.getLogger(__name__)


try:
    from pyroute2 import NDB
except ModuleNotFoundError:
    log.error("Error: Missing dependency pyroute2")
    sys.exit(1)


def setup_sniffbridge(bridge, interfaces, fwd_mask):
    with NDB() as ndb:
        log.info("Creating bridge interface %s", bridge)
        br = ndb.interfaces.create(ifname=bridge, kind="bridge")

        log.info("Setting group_fwd_mask for bridge to %d", fwd_mask)
        br.set(state="down", br_group_fwd_mask=fwd_mask)
        br.commit()

        log.info("Disabling IPv6 on bridge interface")
        subprocess.run(["sysctl", "-q", "-w", f"net.ipv6.conf.{bridge}.disable_ipv6=1"], check=True)

        for ifname in interfaces:
            log.info("Attaching interface %s to bridge", ifname)
            br.add_port(ifname)

        log.info("Setting bridge interface up")
        br.set(state="up")
        br.commit()


def teardown_sniffbridge(bridge):
    with NDB() as ndb:
        log.info("Removing bridge interface %s", bridge)
        ndb.interfaces[bridge].remove().commit()


def main():
    log.setLevel(logging.INFO)
    handler = logging.StreamHandler()
    formatter = logging.Formatter("%(levelname)s: %(message)s")
    handler.setFormatter(formatter)
    log.addHandler(handler)

    argparser = argparse.ArgumentParser(description="Create a network bridge for passive traffic sniffing.", formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    argparser.add_argument("--bridge", "-b", default="sniffBr0", help="Name of bridge device to create")
    argparser.add_argument("--fwd-mask", default=65528, help="Set forward mask for 'IEEE 802.1D MAC Bridge Filtered MAC Group Addresses'")
    argparser.add_argument("--cleanup", action="store_true", default=False, help="Teardown instead of create the bridge setup")
    argparser.add_argument("interfaces", metavar="INTERFACE", nargs="+", help="Interfaces to connect to the bridge")
    parsed_args = argparser.parse_args()

    if os.geteuid() != 0:
        log.error("Need to run as root")
        sys.exit(1)

    if parsed_args.cleanup:
        teardown_sniffbridge(parsed_args.bridge)
    else:
        setup_sniffbridge(parsed_args.bridge, parsed_args.interfaces, parsed_args.fwd_mask)


if __name__ == "__main__":
    main()
