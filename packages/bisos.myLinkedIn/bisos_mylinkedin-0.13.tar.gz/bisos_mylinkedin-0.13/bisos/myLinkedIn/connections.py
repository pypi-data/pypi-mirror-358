from pathlib import Path
from typing import List, Dict, Optional
import csv
import vobject


import logging
logger = logging.getLogger(__name__)


class LinkedInConnections:
    """
    Parses LinkedIn Connections CSV and generates vCards.
    """

    def __init__(self, csv_path: Path):
        """
        Initialize with path to LinkedIn Connections.csv.
        """
        self.csv_path: Path = csv_path
        self.connections: List[Dict[str, str]] = []

    def load(self) -> None:
        """
        Load connection records from CSV, skipping header comments.
        """
        with self.csv_path.open(newline='', encoding='utf-8') as f:
            for _ in range(3):
                next(f)
            reader = csv.DictReader(f)
            self.connections = list(reader)

    def create_vcards(self, output_dir: Path) -> int:
        """
        Generate vCard files for each connection.
        """
        if not self.connections:
            self.load()

        output_dir.mkdir(parents=True, exist_ok=True)

        counter = 0

        for entry in self.connections:

            counter += 1

            vcard = vobject.vCard()
            vcard.add('fn').value = f"{entry['First Name']} {entry['Last Name']}"
            vcard.add('n').value = vobject.vcard.Name(
                family=entry['Last Name'], given=entry['First Name']
            )
            vcard.add('note').value = f"Connected On: {entry['Connected On']}"
            vcard.add('org').value = [entry.get('Company', '')]
            vcard.add('title').value = entry.get('Position', '')

            url: Optional[str] = entry.get('URL', '')
            uid = url.rstrip('/').split('/')[-1] if url else f"{entry['First Name']}_{entry['Last Name']}"
            filename: Path = output_dir / f"{uid}.vcf"

            logger.debug(filename)
            with filename.open('w', encoding='utf-8') as f:
                vcf_str = vcard.serialize()
                logger.debug(vcf_str)
                f.write(vcf_str)

        return counter
