
from pathlib import Path as libpath
from typing import List, Dict
import csv
import vobject
import logging

# logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

class LinkedInInvitations:
    """
    Processes Invitations.csv to annotate vCards with invitation direction and message.
    """

    def __init__(self, csv_path: libpath):
        """
        Initialize with the path to Invitations.csv.
        """
        self.csv_path: libpath = libpath(csv_path).expanduser()
        self.invitations: List[Dict[str, str]] = []

    def load(self) -> None:
        """
        Load invitation records from CSV into memory.
        """
        with self.csv_path.open(newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            self.invitations = list(reader)
        logger.info(f"Loaded {len(self.invitations)} invitations.")

    def augment_vcards(self, vcard_dir: libpath) -> None:
        """
        Add invitation direction and message to matching vCards, avoiding duplication.
        """
        vcard_dir = libpath(vcard_dir).expanduser()
        if not self.invitations:
            self.load()

        for invitation in self.invitations:
            direction = invitation.get("Direction", "").strip().upper()
            message = invitation.get("Message", "").strip()
            profile_url = (
                invitation.get("inviteeProfileUrl") if direction == "OUTGOING"
                else invitation.get("inviterProfileUrl")
            )

            if not profile_url:
                logger.warning("Skipping invitation with missing profile URL.")
                continue

            uid = profile_url.rstrip('/').split('/')[-1]
            vcard_path = vcard_dir / f"{uid}.vcf"

            if not vcard_path.exists():
                logger.debug(f"vCard not found for {uid}, skipping.")
                continue

            with vcard_path.open('r', encoding='utf-8') as f:
                vcard = vobject.readOne(f.read())

            note_value = f"Invitation {direction.capitalize()}"
            if message:
                note_value += f" — {message}"

            # Check for existing identical note
            existing_note = vcard.note.value if 'note' in vcard.contents else ''
            if note_value in existing_note:
                logger.debug(f"Note already present for {uid}, skipping.")
                continue

            if 'note' in vcard.contents:
                vcard.note.value += f"\n{note_value}"
            else:
                vcard.add('note').value = note_value

            with vcard_path.open('w', encoding='utf-8') as f:
                f.write(vcard.serialize())
            logger.info(f"Updated vCard for {uid}.")

