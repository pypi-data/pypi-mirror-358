import csv
import mailbox
import logging
from email.message import EmailMessage
from pathlib import Path
from typing import Optional
# from telemetry import Telemetry

class LinkedInMessagesToMaildir:
    """
    Converts LinkedIn Messages.csv into Maildir-format RFC822 messages.
    """

    def __init__(self, csv_path: Path, maildir_path: Path,
                 #telemetry: Optional[Telemetry] = None):
                 ):
        self.csv_path = csv_path.expanduser().resolve()
        self.maildir_path = maildir_path.expanduser().resolve()
        #self.telemetry = telemetry or Telemetry("LinkedInMessagesToMaildir")
        self.logger = logging.getLogger(__name__)

    def load_messages(self) -> list[dict]:
        self.logger.debug(f"Loading messages from: {self.csv_path}")
        # with self.telemetry.span("load_csv"), self.csv_path.open(encoding="utf-8") as f:
        with self.csv_path.open(encoding="utf-8") as f:
            reader = csv.DictReader(f)
            return list(reader)

    def create_email(self, row: dict) -> EmailMessage:
        msg = EmailMessage()
        msg["From"] = f"{row['FROM']} <{row.get('SENDER PROFILE URL', '').strip() or 'unknown@linkedin.com'}>"
        msg["To"] = f"{row['TO']} <{row.get('RECIPIENT PROFILE URLS', '').strip() or 'unknown@linkedin.com'}>"
        msg["Date"] = row.get("DATE", "")
        msg["Subject"] = row.get("SUBJECT", "No Subject").strip() or "No Subject"

        body = row.get("CONTENT", "").strip()
        msg.set_content(body)
        return msg

    def export_to_maildir(self):
        self.logger.info(f"Exporting messages to maildir: {self.maildir_path}")

        # with self.telemetry.span("export_maildir"):
        #
        maildir = mailbox.Maildir(self.maildir_path, create=True)

        messages = self.load_messages()
        count = 0
        for row in messages:
            try:
                msg = self.create_email(row)
                maildir.add(msg)
                count += 1
            except Exception as e:
                self.logger.warning(f"Failed to convert row to mail: {e}")

        self.logger.info(f"Exported {count} messages.")

    def run(self):
        self.export_to_maildir()
