#!/usr/bin/env python3

"""
Send an email to an SMTP server.

This script simply allows to submit an email to an SMTP server.
It supports explicitly setting certail values like the envolope
fields MAIL FROM and RCPT TO, which can be useful for spoofing attacks.
"""

import argparse
from email.message import EmailMessage
from email.utils import formatdate
import mimetypes
import os
import smtplib
import sys


def send_email(server, port, from_addr, to_addrs, subject, content, attachments, security, envelope_from=None, envelope_to=None):
    msg = EmailMessage()
    msg["Date"] = formatdate(localtime=True)
    msg["From"] = from_addr
    msg["To"] = ", ".join(to_addrs)
    msg["Subject"] = subject
    msg.set_content(content)

    if attachments:
        for attachment in attachments:
            mime, encoding = mimetypes.guess_type(attachment)
            if mime is None or encoding is not None:
                mime = "application/octet-stream"
            maintype, subtype = mime.split("/", maxsplit=1)
            with open(attachment, "rb") as f:
                msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(attachment))

    smtp = smtplib.SMTP(server, port=port)
    if security == "starttls":
        smtp.starttls()
    smtp.send_message(msg, from_addr=envelope_from, to_addrs=envelope_to)
    smtp.quit()


def main():
    argparser = argparse.ArgumentParser(description="Send an email to an SMTP server.")
    argparser.add_argument("--from", "-f", metavar="ADDR", dest="from_addr", required=True, help="Sender's email address (From header)")
    argparser.add_argument("--to", "-t", metavar="ADDR", dest="to_addrs", required=True, nargs="+", help="Recipients' email addresses (To header)")
    argparser.add_argument("--envelope-from", metavar="ADDR", help="Set different sender's address for envelope (MAIL FROM)")
    argparser.add_argument("--envelope-to", metavar="ADDR", nargs="+", help="Set different recipients' addresses for envelope (RCPT TO)")
    argparser.add_argument("--subject", "-s", required=True, help="Subject line")
    argparser.add_argument("--content", "-c", help="Message content (if not set, read from stdin)")
    argparser.add_argument("--attach", "-a", metavar="FILE", nargs="+", help="File attachments")
    argparser.add_argument("--sec", choices=["none", "starttls"], default="starttls", help="Connection security (default: starttls)")
    argparser.add_argument("server", help="SMTP server to connect to (with optional port suffix, default :25)")
    args = argparser.parse_args()

    target = args.server.rsplit(":", maxsplit=1)
    server = target[0]
    if len(target) == 2:
        port = target[1]
    else:
        port = 25

    if args.content is None:
        content = sys.stdin.read()
    else:
        content = args.content

    try:
        send_email(server, port, args.from_addr, args.to_addrs, args.subject, content, args.attach, args.sec, args.envelope_from, args.envelope_to)
    except smtplib.SMTPException as e:
        print(f"{e.__class__.__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
