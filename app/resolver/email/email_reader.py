# App/Resolver/Email/email_reader.py

from pathlib import Path
from email import policy
from email.parser import BytesParser
from bs4 import BeautifulSoup
import re
import html

class EmlEmailReader:


    INPUT_DIR = r"D:\AD Automation\DataMail"

    def _html_to_text(self, html_content: str) -> str:

        soup = BeautifulSoup(
            html_content,
            "html.parser"
        )

        text = soup.get_text(
            separator="\n",
            strip=True
        )

        return text

    
    def read_folder(self) -> list[dict]:

        input_path = Path(self.INPUT_DIR)
        if not input_path.exists():
            raise FileNotFoundError(
                f"Input folder not found: {self.INPUT_DIR}"
            )

        eml_files = sorted(input_path.glob("*.eml"))

        emails = []

        for eml_file in eml_files:
            emails.append(
                self.read_file(eml_file)
            )

        return emails

    def read_file(self, file_path: Path) -> dict:

        with open(file_path, "rb") as f:
            message = BytesParser(
                policy=policy.default
            ).parse(f)

        return {
            "source_file": str(file_path),
            "file_name": file_path.name,
            "message_id": message.get("Message-ID", ""),
            "subject": message.get("Subject", ""),
            "sender": message.get("From", ""),
            "received_date": message.get("Date", ""),
            "body": self._extract_body(message)
        }
    def html_to_text(html_content: str) -> str:

        if not html_content:
            return ""

        text = html_content

        # Decode HTML entities
        text = html.unescape(text)

        # BR -> newline
        text = re.sub(
            r"(?i)<br\s*/?>",
            "\n",
            text
        )

        # đóng thẻ block -> newline
        text = re.sub(
            r"(?i)</(p|div|tr|table|li)>",
            "\n",
            text
        )

        # bỏ toàn bộ tag
        text = re.sub(
            r"<[^>]+>",
            " ",
            text
        )

        # dọn khoảng trắng
        text = re.sub(r"\r", "", text)
        text = re.sub(r"\t", " ", text)
        text = re.sub(r" +", " ", text)
        text = re.sub(r"\n{2,}", "\n", text)

        return text.strip()
    def _extract_body(self, message) -> str:

        if message.is_multipart():

            # Ưu tiên text/plain
           
            for part in message.walk():

                if part.get_content_type() == "text/plain":

                    try:
                        return str(part.get_content())
                    except Exception:
                        pass
            # Fallback text/html
            for part in message.walk():

               if part.get_content_type() == "text/html":

                    try:
                        html_content = str(part.get_content())
                        return self._html_to_text(html_content)

                    except Exception:
                        pass

            return ""

        try:
            content = str(message.get_content())

            if message.get_content_type() == "text/html":
                return self.html_to_text(content)

            return content

        except Exception:
            return ""