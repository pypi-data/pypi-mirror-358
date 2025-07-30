import sys
import json
import csv
import os
from datetime import datetime

from openmailer.client import OpenMailerClient
from openmailer.template_engine import render_template
from openmailer.logger import log_event
from openmailer.secrets import get_smtp_config


def parse_args(args):
    params = {
        "to": None,
        "subject": None,
        "template": None,
        "context": {},
        "attachments": [],
        "dry_run": False,
        "schedule": None,
        "priority": "normal",
        "track_open": False,
        "secret_source": None
    }

    i = 0
    while i < len(args):
        if args[i] == "--to":
            params["to"] = args[i + 1]
            i += 2
        elif args[i] == "--subject":
            params["subject"] = args[i + 1]
            i += 2
        elif args[i] == "--template":
            params["template"] = args[i + 1]
            i += 2
        elif args[i] == "--context":
            params["context"] = json.loads(args[i + 1])
            i += 2
        elif args[i] == "--attachment":
            params["attachments"].append(args[i + 1])
            i += 2
        elif args[i] == "--dry-run":
            params["dry_run"] = True
            i += 1
        elif args[i] == "--schedule":
            try:
                dt = datetime.strptime(args[i + 1], "%Y-%m-%d %H:%M")
                params["schedule"] = (dt - datetime.now()).total_seconds()
            except ValueError:
                print("❌ Invalid --schedule format. Use: YYYY-MM-DD HH:MM")
                sys.exit(1)
            i += 2
        elif args[i] == "--priority":
            params["priority"] = args[i + 1]
            i += 2
        elif args[i] == "--track-open":
            params["track_open"] = True
            i += 1
        elif args[i] == "--secret-source":
            params["secret_source"] = args[i + 1]
            i += 2
        else:
            i += 1

    return params


def handle_bulk_send(csv_path, template_path, dry_run=False, source=None):
    if not os.path.exists(csv_path) or not os.path.exists(template_path):
        print("❌ CSV or template file not found.")
        return

    with open(template_path, "r") as f:
        template_str = f.read()

    smtp_config = get_smtp_config(source=source)
    client = OpenMailerClient(config=smtp_config, dry_run=dry_run)

    with open(csv_path, newline='') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            to = row.get("email")
            subject = row.get("subject", "No Subject")
            context = {k: v for k, v in row.items() if k not in ("email", "subject")}
            html = render_template(template_str, context)

            try:
                result = client.send_email(
                    to=to,
                    subject=subject,
                    html_body=html,
                    context=context
                )
                print(f"✅ Sent to {to}: {result['status']}")
                log_event(to, result["status"])
            except Exception as e:
                print(f"❌ Failed to send to {to}: {e}")
                log_event(to, "failed", str(e))


def main():
    args = sys.argv[1:]

    if not args or "--help" in args or "-h" in args:
        print("""
Usage:

  📨 Single Email:
    opmcli --to <email> --subject <subject> --template <file.html>
           [--context '{"key": "value"}'] [--attachment <file>]
           [--schedule "YYYY-MM-DD HH:MM"]
           [--priority high|normal|low]
           [--track-open] [--dry-run]
           [--secret-source env|vault|aws|azure]

  📥 Bulk Email:
    opmcli bulk --csv <emails.csv> --template <file.html>
           [--dry-run] [--secret-source env|vault|aws|azure]

Options:
  --to              Email recipient
  --subject         Email subject line
  --template        Path to HTML template
  --context         JSON dict to inject into template
  --attachment      One or more files to attach
  --schedule        Future datetime to send email (e.g., "2025-06-28 10:00")
  --priority        Email queue priority: high, normal, or low
  --track-open      Enable open tracking
  --dry-run         Save email to ./outbox/ instead of sending
  --secret-source   Load secrets from: env, vault, aws, or azure
  --help, -h        Show this help message
""")
        return

    if args[0] == "bulk":
        if "--csv" in args and "--template" in args:
            csv_path = args[args.index("--csv") + 1]
            template_path = args[args.index("--template") + 1]
            dry_run = "--dry-run" in args
            source = None
            if "--secret-source" in args:
                idx = args.index("--secret-source")
                if idx + 1 < len(args):
                    source = args[idx + 1]
            handle_bulk_send(csv_path, template_path, dry_run=dry_run, source=source)
            return
        else:
            print("❌ Missing --csv or --template for bulk mode.")
            return

    params = parse_args(args)
    if not params["to"] or not params["subject"] or not params["template"]:
        print("❌ Missing required parameters. Use --help for usage.")
        return

    try:
        with open(params["template"], "r") as f:
            template_str = f.read()
    except Exception as e:
        print(f"❌ Could not read template file: {e}")
        return

    smtp_config = get_smtp_config(source=params["secret_source"])
    client = OpenMailerClient(config=smtp_config, dry_run=params["dry_run"])

    try:
        result = client.send_email(
            to=params["to"],
            subject=params["subject"],
            html_body=template_str,
            context=params["context"],
            attachments=params["attachments"],
            schedule=params["schedule"],
            priority=params["priority"],
            track_open=params["track_open"]
        )
        print("✅ Result:", result)
        log_event(params["to"], result["status"], smtp_config.get("host"))
    except Exception as e:
        print(f"❌ Failed to send email: {e}")
        log_event(params["to"], "failed", smtp_config.get("host"), str(e))


if __name__ == "__main__":
    main()
