#!/usr/bin/env python3

"""
Tool to capture IEEE 802.11 Probe Request frames and print them.

Useful in a demonstration to show known WiFi networks of visitors.
"""

import argparse
import collections
import itertools
import re
import signal
import subprocess
import sys

from scapy.all import sniff, Dot11ProbeReq


def signal_handler(signal, frame):
    sys.exit(0)


def channel_list(device):
    iw_dev_info = subprocess.run(["iw", "dev", device, "info"], check=True, capture_output=True, text=True).stdout
    phy = re.findall(r"\s*wiphy (\d+)\s*", iw_dev_info)[0]
    iw_phy_channels = subprocess.run(["iw", "phy", f"phy{phy}", "channels"], check=True, capture_output=True, text=True).stdout
    return re.findall(r"\[(\d+)\] \n", iw_phy_channels)


def packet_handler(pkt):
    source = pkt.addr2
    ssid = pkt.info.decode()
    if ssid:
        if hasattr(packet_handler, "recent_probes"):
            if ssid in packet_handler.recent_probes:
                return
            packet_handler.recent_probes.append(ssid)
        print(f"Probe Request from {source} for SSID {ssid}")


def sniff_probe_requests(iface, throttle=False):
    if throttle:
        packet_handler.recent_probes = collections.deque(maxlen=10)
    for chan in itertools.cycle(channel_list(iface)):
        subprocess.run(["iw", "dev", iface, "set", "channel", chan], check=True)
        sniff(iface=iface, timeout=3, prn=packet_handler, lfilter=lambda pkt: pkt.haslayer(Dot11ProbeReq))


def main():
    argparser = argparse.ArgumentParser(description="Sniff for IEEE 802.11 Probe Request frames.")
    argparser.add_argument("iface", help="the monitor mode enabled interface")
    argparser.add_argument("--throttle", action="store_true",
                           help="throttle the occurrence of duplicate SSIDs")
    args = argparser.parse_args()

    signal.signal(signal.SIGINT, signal_handler)
    sniff_probe_requests(args.iface, args.throttle)


if __name__ == "__main__":
    main()
