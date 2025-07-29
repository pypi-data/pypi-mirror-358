from typing import List, Dict, Union, Optional, Any
import re
import json
import os
import base64
from pathlib import Path
from urllib.parse import urlparse
import requests

from sendlayer.base import BaseClient
from sendlayer.exceptions import SendLayerError, SendLayerAPIError, SendLayerAuthenticationError, SendLayerValidationError

class Emails:
    """Client for sending emails through SendLayer."""

    def __init__(self, client: BaseClient):
        self.client = client
    
    def _validate_email(self, email: str) -> bool:
        """Validate email address format."""
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, email))
    
    def _read_attachment(self, file_path: str) -> str:
        """Read a file and encode it in base64."""

        # Check if the path is a URL first
        parsed = urlparse(file_path)
        is_url = bool(parsed.scheme and parsed.netloc)

        if is_url:
            # Handle remote file
            try:
                timeout = getattr(self.client, 'attachment_url_timeout', 30000) / 1000  # Convert to seconds
                response = requests.get(file_path, timeout=timeout)
                response.raise_for_status()
                file_content = response.content
                encoded_content = base64.b64encode(file_content).decode("utf-8")
                return encoded_content
            except requests.exceptions.RequestException as e:
                raise SendLayerError(f'Error fetching remote file: {str(e)}')
            except Exception as e:
                raise SendLayerValidationError(f"Error reading attachment: {str(e)}")

        # Handle local files
        path_obj = Path(file_path)
        
        # Check if file exists and is readable
        if not path_obj.exists():
            raise SendLayerError(f"Attachment file does not exist: {file_path}")
        
        if not path_obj.is_file():
            raise SendLayerError(f"Path is not a file: {file_path}")
            
        if not os.access(path_obj, os.R_OK):
            raise SendLayerError(f"File is not readable: {file_path}")

        # Get Absolute path
        absolute_path = os.path.abspath(file_path)
        relative_path = os.path.join(os.getcwd(), file_path)  # Relative to current working directory
 
        try:
           # Try the original path first
            if os.path.exists(file_path):
                with open(file_path, "rb") as file:
                    file_content = file.read()
            
            elif os.path.exists(absolute_path):
                with open(absolute_path, "rb") as file:
                    file_content = file.read()

            elif os.path.exists(relative_path):
                with open(relative_path, "rb") as file:
                    file_content = file.read()
            else:
                raise FileNotFoundError(f"Attachment file not found: {file_path}")
                
            # encoded content to base64
            encoded_content = base64.b64encode(file_content).decode("utf-8")
            return encoded_content
                
        except FileNotFoundError:
            raise SendLayerError(f"Attachment file not found: {file_path}")
        except Exception as e:
            raise SendLayerValidationError(f"Error reading attachment: {str(e)}")
        
    
    def _validate_attachment(self, attachment: Dict[str, str]) -> None:
        """Validate attachment format."""
        if not attachment.get("path"):
            raise SendLayerValidationError("Attachment path is required")
        if not attachment.get("type"):
            raise SendLayerValidationError("Attachment type is required")
    
    def send(
        self,
        sender: Union[str, Dict[str, Optional[str]], List[Union[str, Dict[str, Optional[str]]]]],
        to: Union[str, Dict[str, Optional[str]], List[Union[str, Dict[str, Optional[str]]]]],
        subject: str,
        text: Optional[str] = None,
        html: Optional[str] = None,
        cc: Optional[Union[str, Dict[str, Optional[str]], List[Union[str, Dict[str, Optional[str]]]]]] = None,
        bcc: Optional[Union[str, Dict[str, Optional[str]], List[Union[str, Dict[str, Optional[str]]]]]] = None,
        reply_to: Optional[Union[str, Dict[str, Optional[str]], List[Union[str, Dict[str, Optional[str]]]]]] = None,
        attachments: Optional[List[Dict[str, str]]] = None,
        headers: Optional[Dict[str, str]] = None,
        tags: Optional[List[str]] = None,
    ) -> Dict[str, str]:
        """Send an email through SendLayer."""
        if not text and not html:
            raise SendLayerValidationError("Either 'text' or 'html' content must be provided.")
        
        # Validate email addresses
        def validate_recipient(recipient: Union[str, Dict[str, Optional[str]]], recipient_type: str = "recipient") -> Dict[str, Optional[str]]:
            if isinstance(recipient, str):
                if not self._validate_email(recipient):
                    raise SendLayerValidationError(f"Invalid {recipient_type} email address: {recipient}")
                return {"email": recipient}
            if not self._validate_email(recipient['email']):
                raise SendLayerValidationError(f"Invalid {recipient_type} email address: {recipient['email']}")
            return recipient
        
        from_details = validate_recipient(sender, "sender")
            
        to_list = [validate_recipient(r, "recipient") for r in (to if isinstance(to, list) else [to])]

        
        payload = {
            "From": from_details,
            "To": to_list,
            "Subject": subject,
            "ContentType": "HTML" if html else "Text",
            "HTMLContent" if html else "PlainContent": html or text
        }
        
        if cc:
            cc_list = [validate_recipient(r, "cc") for r in (cc if isinstance(cc, list) else [cc])]
            payload["CC"] = cc_list

        if bcc:
            bcc_list = [validate_recipient(r, "bcc") for r in (bcc if isinstance(bcc, list) else [bcc])]
            payload["BCC"] = bcc_list

        if reply_to:
            reply_to_list = [validate_recipient(r, "reply_to") for r in (reply_to if isinstance(reply_to, list) else [reply_to])]
            payload["ReplyTo"] = reply_to_list

        if attachments:
            # Validate and transform attachments
            payload["Attachments"] = []
            for attachment in attachments:
                self._validate_attachment(attachment)
                encoded_content = self._read_attachment(attachment["path"])
                
                payload["Attachments"].append({
                    "Content": encoded_content,
                    "Type": attachment["type"],
                    "Filename": os.path.basename(attachment["path"]),
                    "Disposition": "attachment",
                    "ContentId": int(hash(attachment["path"]))  # Using a unique identifier
                })
                
        if headers:
            payload["Headers"] = headers
        if tags:
            if not isinstance(tags, list) or not all(isinstance(tag, str) for tag in tags):
                raise SendLayerValidationError("Tags must be a list of strings.")
            payload["Tags"] = tags
            
        return self.client._make_request("POST", "email", json=payload) 