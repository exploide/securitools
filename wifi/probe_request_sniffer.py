#!/usr/bin/env python3

"""
Tool to capture 802.11 Probe Request frames and print them.

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


def packet_handler(pkt):
    source = pkt.addr2
    ssid = pkt.info.decode()
    if ssid:
        if hasattr(packet_handler, "recent_probes"):
            if (source, ssid) in packet_handler.recent_probes:
                return
            else:
                packet_handler.recent_probes.append((source, ssid))
        print("Probe Request from {} for SSID {}".format(source, ssid))


def main(args):
    signal.signal(signal.SIGINT, signal_handler)
    if args.throttle:
        packet_handler.recent_probes = collections.deque(maxlen=10)
    iwlist_output = subprocess.run(["iwlist", args.iface, "freq"], stdout=subprocess.PIPE, encoding="utf-8").stdout
    supported_channels = re.findall(r"Channel (\d+) :", iwlist_output)
    for chan in itertools.cycle(supported_channels):
        subprocess.run(["iw", "dev", args.iface, "set", "channel", chan])
        sniff(iface=args.iface, timeout=3, prn=packet_handler, lfilter=lambda pkt: pkt.haslayer(Dot11ProbeReq))


if __name__ == '__main__':
    argparser = argparse.ArgumentParser(description="Sniff for 802.11 Probe Request frames.")
    argparser.add_argument("iface", help="the monitor mode enabled interface")
    argparser.add_argument("--throttle", action="store_true",
                           help="throttle the occurrence of duplicate probe requests")
    main(argparser.parse_args())
