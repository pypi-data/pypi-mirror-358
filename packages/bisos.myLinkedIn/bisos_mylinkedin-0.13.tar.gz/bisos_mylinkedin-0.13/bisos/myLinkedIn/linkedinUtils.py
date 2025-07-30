import csv
import logging
from pathlib import Path
import zipfile
import vobject
from typing import Optional, List, Dict
from urllib.parse import urlparse

from datetime import datetime

logger = logging.getLogger(__name__)
# logger.setLevel(logging.INFO)

class LinkedinId:
    """
    Utility functions for handling LinkedinId
    """

    @staticmethod
    def fromUrl(url: str) -> str:
        """
        Extract the LinkedIn ID from the profile URL.
        """
        parts = url.rstrip('/').split('/')
        return parts[-1]

    @staticmethod
    def toPath( uid: str, vcard_dir: Path,) -> Optional[Path]:
        """
        Find the vCard file corresponding to the LinkedIn ID (UID) in the directory.
        """

        assert vcard_dir
        vcard_path = vcard_dir / f"{uid}.vcf"
        if vcard_path.exists():
            return vcard_path
        else:
            # vcard_path = vcard_dir / f"EXTRA_{uid}.vcf"
            return None

    @staticmethod
    def toUrl(id: str) -> str:
        """
        Convert linkedinId to linkedin Url.
        """
        prefix = "EXTRA_"
        if id.startswith(prefix):
            id =  id[len(prefix):]

        return f"https://www.linkedin.com/in/{id}"


class LinkedinQualifier:
    """
    A LinkedInQualifer is one of:

        - LinkedInVCardAbsPath   : starts with / ends with /LinkedInVCardBasename
        - LinkedInVCardBasename  : non-directory part of file path formed as id.vcf
        - LinkedInId             : The id part of https://www.linkedin.com/in/{id}
        - LinkedInUrl            : The URL in the form of

   LinkedInQualifer is then combined with:
        - vcardsDir              : dirname in which  LinkedInVCardBasename resides
                                 : vcardsDir = LinkedInVCardAbsPath -  LinkedInVCardBasename

    LinkedInVCardPath is a pathlib.Path object that is used for conversions and processing

    Usage is like this:
           LinkedInVCardPath = LinkedinQualifier.toVCardPath(qualifier, vcardsDir)
    And then
           linkedInId = LinkedinQualifier.asLinkedInId(vcardPath)
    """

    @staticmethod
    def toVCardPath(qualifier: str, vcardsDir: str) -> Optional[Path]:
        """
        """
        assert qualifier
        assert vcardsDir

        vcardsDirPath = Path(vcardsDir)
        # if not vcardsDirPath.exists():
        # raise b.exception.badUsage()

        vcardPath = None

        # LinkedInUrl -- Check if the input is a URL
        try:
            result = urlparse(qualifier)
            if all([result.scheme, result.netloc]):
                id = LinkedinId.fromUrl(qualifier)
                vcardPath = LinkedinId.toPath(id, vcardsDirPath)
                if vcardPath is not None:
                    return vcardPath
                vcardPath = VCard.create_extra_vcard(vcardsDirPath, id)
                if vcardPath is not None:
                    return vcardPath
                else:
                    logger.error(f"VCard.create_extra_vcard failed for {id}")
                    return None

        except Exception:
            pass

        # Check if the input is a file path
        qualifierPath = Path(qualifier)

        # LinkedInVCardAbsPath
        if qualifierPath.is_absolute():
            if qualifierPath.exists():
                return qualifierPath
            else:
                logger.info(f"Missing {qualifierPath}")
                id =  LinkedinQualifier.asLinkedInId(qualifierPath)
                vcardPath = VCard.create_extra_vcard(vcardsDirPath, id)
                if vcardPath is not None:
                    return vcardPath
                else:
                    logger.error(f"VCard.create_extra_vcard failed for {id}")
                    return None

        # LinkedInVCardBasename
        if qualifierPath.suffix == '.vcf':
            vcardPath = vcardsDir  / qualifierPath
            if vcardPath.exists():
                return vcardPath
            else:
                logger.info(f"Missing {vcardPath}")
                id =  LinkedinQualifier.asLinkedInId(qualifierPath)
                vcardPath = VCard.create_extra_vcard(vcardsDirPath, id)
                if vcardPath is not None:
                    return vcardPath
                else:
                    logger.error(f"VCard.create_extra_vcard failed for {id}")
                    return None

        # LinkedInId
        vcardPath = LinkedinId.toPath(qualifier, vcardsDirPath)
        if vcardPath is not None:
            return vcardPath
        vcardPath = VCard.create_extra_vcard(vcardsDirPath, qualifier)
        if vcardPath is not None:
            return vcardPath
        else:
            logger.error(f"VCard.create_extra_vcard failed for {qualifier}")
            return None


    @staticmethod
    def asLinkedInId(vcardPath: Path) -> str:
        """
        """
        stem = vcardPath.stem
        return stem


class VCard:
    """
    Utility functions for handling vCards and LinkedIn data files.
    """

    @staticmethod
    def read_csv(file_path: Path) -> List[Dict[str, str]]:
        """
        Read a CSV file and return the rows as a list of dictionaries.
        """
        if not file_path.exists():
            raise FileNotFoundError(f"{file_path} does not exist.")

        with file_path.open('r', encoding='utf-8') as f:
            return list(csv.DictReader(f))

    @staticmethod
    def write_vcard(vcard, vcard_path: Path) -> None:
        """
        Write the vCard object to a file.
        """
        with vcard_path.open('w', encoding='utf-8') as vcard_file:
            vcard_file.write(vcard.serialize())

    @staticmethod
    def read_vcard(vcard_path: Path):
        """
        Read a vCard from a file and return the vCard object.
        """
        with vcard_path.open('r', encoding='utf-8') as vcard_file:
            return vobject.readOne(vcard_file.read())

    @staticmethod
    def create_extra_vcard(vcard_dir: Path, uid: str) -> Optional[Path]:
        """
        Create a new vCard file corresponding to the LinkedIn ID (UID) in the directory.
        Assume that the LinkedinId is in the form of first-last-uniqId
        Create a blank vcard using vobject.
        Add to it:
            - firstname (from uid)
            - lastname (from uid)
            - linkinedUrl (based on uid)
        Write the created vcard using vobject.
        Return Path to created vcard.
        """
        vcard_path = vcard_dir / f"EXTRA_{uid}.vcf"
        if vcard_path.exists():
            return vcard_path
        # Split the UID to extract first and last names
        parts = uid.split('-')
        if len(parts) < 2:
            logger.error(f"Invalid UID format: {uid}")
            return None

        first_name, last_name = parts[0], parts[1]

        # Create a new vCard
        vcard = vobject.vCard()
        vcard.add('fn').value = f"{first_name} {last_name}"
        vcard.add('n').value = vobject.vcard.Name(family=last_name, given=first_name)
        vcard.add('url').value = LinkedinId.toUrl(uid)

        # Write the vCard to a file
        VCard.write_vcard(vcard, vcard_path)
        logger.info(f"Created extra vCard at: {vcard_path}")

        return vcard_path


    @staticmethod
    def find_vcard(vcard_dir: Path, uid: str) -> Optional[Path]:
        """
        Find the vCard file corresponding to the LinkedIn ID (UID) in the directory.
        """
        vcard_path = vcard_dir / f"{uid}.vcf"
        if vcard_path.exists():
            return vcard_path
        return None

    @staticmethod
    def needs_update(vcardPath: Path) -> bool:
        """
        Find the vCard file corresponding to the LinkedIn ID (UID) in the directory.
        """

        vcardStr  = vcardPath.read_text(encoding="utf-8").strip()
        vcard = vobject.readOne(vcardStr)

        field = "x-date"
        if hasattr(vcard, field):
            value = vcard.contents[field][0].value
            logger.info(f"vcardPath={vcardPath} -- {field} = {value} -- Skipped")
            return False
        
        field = "email"
        if hasattr(vcard, field):
            value = vcard.contents[field][0].value
            logger.info(f"vcardPath={vcardPath} -- {field} = {value} -- Skipped")
            return False

        return True

    @staticmethod
    def update_or_add_custom_field(card, field_name, value):
        # Check if the field exists
        existing_field = next((comp for comp in card.contents.get(field_name, [])), None)

        if existing_field:
            # If the field exists, replace its value
            existing_field.value = value
        else:
            # If the field does not exist, add it
            custom_field = card.add(field_name)
            custom_field.value = value


    @staticmethod
    def augment_vcard_with_contact_info(vcard_path: Path, contact_info: Dict[str, Optional[str]]) -> None:
        """
        Augments an existing vCard file with extracted LinkedIn contact info.
        """
        logger.info(f"Augmenting vCard at: {vcard_path}")

        if not vcard_path.exists():
            logger.error(f"vCard not found: {vcard_path}")
            return

        vcard_str = vcard_path.read_text(encoding="utf-8").strip()
        vcard = vobject.readOne(vcard_str)

        field_mapping = {
            "email": ("email", "INTERNET"),
            "phone": ("tel", "CELL"),
            "website": ("url", None),
            "twitter": ("x-twitter", None),
            "address": ("adr", None),
            "birthday": ("bday", None),
            "profile_url": ("x-linkedin", None),
        }

        for key, (field, type_param) in field_mapping.items():
            value = contact_info.get(key)
            if value:
                if hasattr(vcard, field):
                    vcard.contents[field][0].value = value
                else:
                    new_field = vcard.add(field)
                    new_field.value = value
                    if type_param:
                        new_field.type_param = type_param
                logger.debug(f"Updated {field} with: {value}")

        VCard.update_or_add_custom_field(vcard, 'x-date', datetime.now().strftime("%Y%m%d%H%M%S"))
        # vcard.add('x-date').value = datetime.now().strftime("%Y%m%d%H%M%S")
                
        vcard_path.write_text(vcard.serialize(), encoding="utf-8")
        logger.info("vCard updated.")


class Common:

    @staticmethod
    def unzip_file(zip_path: Path, extract_to: Path) -> None:
        """Unzips a .zip file to the specified directory using pathlib.
        Use it like so: unzip_file(Path("LinkedInDataExport.zip"), Path("unzipped"))
        """
        logger.info(f"Unzipping {zip_path} to {extract_to}")
        extract_to.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
