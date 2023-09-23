#!/usr/bin/env python3

"""
Send an email to an SMTP server.

This script simply allows to submit an email to an SMTP server.
It supports explicitly setting certain values like the envolope
fields MAIL FROM and RCPT TO, which can be useful for spoofing attacks.
"""

import argparse
from email.message import EmailMessage
from email.utils import formatdate
import mimetypes
import os
import smtplib
import ssl
import sys


def send_email(
    server,
    port,
    from_addr,
    to_addrs,
    subject,
    content,
    content_type="plain",
    attachments=None,
    security="starttls",
    insecure=False,
    username=None,
    password=None,
    envelope_from=None,
    envelope_to=None
):
    msg = EmailMessage()
    msg["Date"] = formatdate(localtime=True)
    msg["From"] = from_addr
    msg["To"] = ", ".join(to_addrs)
    msg["Subject"] = subject
    msg.set_content(content, subtype=content_type)

    if attachments:
        for attachment in attachments:
            mime, encoding = mimetypes.guess_type(attachment)
            if mime is None or encoding is not None:
                mime = "application/octet-stream"
            maintype, subtype = mime.split("/", maxsplit=1)
            with open(attachment, "rb") as f:
                msg.add_attachment(f.read(), maintype=maintype, subtype=subtype, filename=os.path.basename(attachment))

    ssl_context = ssl.create_default_context() if not insecure else None
    if security == "tls":
        smtp = smtplib.SMTP_SSL(server, port=port, context=ssl_context)
    else:
        smtp = smtplib.SMTP(server, port=port)
        if security == "starttls":
            smtp.starttls(context=ssl_context)

    if username and password:
        smtp.login(username, password)

    smtp.send_message(msg, from_addr=envelope_from, to_addrs=envelope_to)
    smtp.quit()


def main():
    argparser = argparse.ArgumentParser(description="Send an email to an SMTP server.")
    argparser.add_argument("server", help="SMTP server to connect to (with optional port suffix, default :25)")

    addressing_group = argparser.add_argument_group("addressing")
    addressing_group.add_argument("--from", "-f", metavar="ADDR", dest="from_addr", required=True, help="Sender's email address (From header)")
    addressing_group.add_argument("--to", "-t", metavar="ADDR", dest="to_addrs", required=True, nargs="+", help="Recipients' email addresses (To header)")
    addressing_group.add_argument("--envelope-from", metavar="ADDR", help="Set different sender's address for envelope (MAIL FROM)")
    addressing_group.add_argument("--envelope-to", metavar="ADDR", nargs="+", help="Set different recipients' addresses for envelope (RCPT TO)")

    content_group = argparser.add_argument_group("content")
    content_group.add_argument("--subject", "-s", required=True, help="Subject line")
    content_group.add_argument("--content", "-c", help="Message content (if not set, read from stdin)")
    content_group.add_argument("--html", dest="content_type", action="store_const", const="html", default="plain", help="Set Content-Type to text/html instead of text/plain")
    content_group.add_argument("--attach", "-a", metavar="FILE", nargs="+", help="File attachments")

    security_group = argparser.add_argument_group("security")
    security_group.add_argument("--auth", help="Authentication credentials (username:password)")
    security_group.add_argument("--sec", choices=["none", "starttls", "tls"], default="starttls", help="Connection security (default: starttls)")
    security_group.add_argument("--insecure", action="store_true", help="Disable TLS certificate checks")

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

    if args.auth:
        username, password = args.auth.split(":", maxsplit=1)
    else:
        username, password = None, None

    try:
        send_email(
            server,
            port,
            args.from_addr,
            args.to_addrs,
            args.subject,
            content,
            args.content_type,
            args.attach,
            args.sec,
            args.insecure,
            username,
            password,
            args.envelope_from,
            args.envelope_to
        )
    except (smtplib.SMTPException, ssl.SSLCertVerificationError) as e:
        print(f"{e.__class__.__name__}: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
