import csv
import logging
from pathlib import Path
from collections import defaultdict
from typing import List, Dict, DefaultDict

import vobject

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
# logging.basicConfig(level=logging.INFO)

class LinkedInMessages:
    """
    Processes Messages.csv to annotate vCards with message history from first-level connections.
    """

    def __init__(self, csv_path: Path):
        """
        Initialize with the path to Messages.csv.
        """
        self.csv_path: Path = csv_path
        self.messages_by_uid: DefaultDict[str, List[str]] = defaultdict(list)

    def load(self) -> None:
        """
        Load and group messages by LinkedIn user ID extracted from SENDER or RECIPIENT PROFILE URL.
        """
        with self.csv_path.open(newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                sender_url = row.get("SENDER PROFILE URL", "").strip()
                recipient_url = row.get("RECIPIENT PROFILE URLS", "").strip()
                profile_url = sender_url or recipient_url
                if not profile_url:
                    logger.warning("Skipping message with no profile URL: %s", row)
                    continue

                uid = profile_url.rstrip('/').split('/')[-1]
                sender = row.get("FROM", "").strip()
                date = row.get("DATE", "").strip()
                content = row.get("CONTENT", "").strip()

                message = f"{date} — {sender}: {content}"
                self.messages_by_uid[uid].append(message)

    def augment_vcards(self, vcard_dir: Path) -> None:
        """
        Add messages to vCards using custom X-Message fields.
        """
        if not self.messages_by_uid:
            self.load()

        for uid, messages in self.messages_by_uid.items():
            vcard_path = vcard_dir / f"{uid}.vcf"
            if not vcard_path.exists():
                logger.info("Skipping missing vCard: %s", vcard_path)
                continue

            with vcard_path.open('r', encoding='utf-8') as f:
                vcard = vobject.readOne(f.read())

            existing_messages = {
                line.value for line in vcard.contents.get('x-message', [])
            }

            new_messages = [
                msg for msg in messages if msg not in existing_messages
            ]

            if not new_messages:
                logger.debug("No new messages for %s", uid)
                continue

            for msg in new_messages:
                xmsg = vcard.add('x-message')
                xmsg.value = msg

            with vcard_path.open('w', encoding='utf-8') as f:
                f.write(vcard.serialize())

            logger.info("Updated vCard with %d new messages: %s", len(new_messages), vcard_path)
