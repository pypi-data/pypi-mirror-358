

import boto3
from typing import Optional
import os
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import mimetypes


class SesEmailClient:
    def __init__(self, region_name: str, aws_access_key_id: Optional[str] = None, aws_secret_access_key: Optional[str] = None, aws_session_token: Optional[str] = None):
        self.client = boto3.client(
            'ses',
            region_name=region_name,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            aws_session_token=aws_session_token
        )

    def send_email(self, source: str, to_addresses: list[str], subject: str, body: str, body_html: Optional[str] = None, attachments: Optional[list[str | bytes]] = None) -> dict:
        if attachments:
            # Create a multipart/mixed parent container.
            msg = MIMEMultipart('mixed')
            msg['Subject'] = subject
            msg['From'] = source
            msg['To'] = ', '.join(to_addresses)

            # Create a multipart/alternative child container for body text/html
            msg_body = MIMEMultipart('alternative')
            if body:
                text_part = MIMEText(body, 'plain')
                msg_body.attach(text_part)
            if body_html:
                html_part = MIMEText(body_html, 'html')
                msg_body.attach(html_part)
            msg.attach(msg_body)

            # Attach files
            self._attach_files(msg, attachments)

            response = self.client.send_raw_email(
                Source=source,
                Destinations=to_addresses,
                RawMessage={"Data": msg.as_string()}
            )
            return response
        else:
            message = {
                'Subject': {'Data': subject},
                'Body': {}
            }
            if body_html:
                message['Body']['Html'] = {'Data': body_html}
            if body:
                message['Body']['Text'] = {'Data': body}

            response = self.client.send_email(
                Source=source,
                Destination={'ToAddresses': to_addresses},
                Message=message
            )
            return response

    def _attach_files(self, msg: MIMEMultipart, attachments: list[str | bytes]) -> None:
        for attachment in attachments:
            if isinstance(attachment, str):
                filename = os.path.basename(attachment)
                ctype, encoding = mimetypes.guess_type(attachment)
                if ctype is None or encoding is not None:
                    ctype = 'application/octet-stream'
                maintype, subtype = ctype.split('/', 1)
                with open(attachment, 'rb') as f:
                    part = MIMEBase(maintype, subtype)
                    part.set_payload(f.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition',
                                    'attachment', filename=filename)
                    msg.attach(part)
            else:
                filename = getattr(attachment, 'name', 'attachment')
                content = attachment.read()
                ctype, encoding = mimetypes.guess_type(filename)
                if ctype is None or encoding is not None:
                    ctype = 'application/octet-stream'
                maintype, subtype = ctype.split('/', 1)
                part = MIMEBase(maintype, subtype)
                part.set_payload(content)
                encoders.encode_base64(part)
                part.add_header('Content-Disposition', 'attachment',
                                filename=os.path.basename(filename))
                msg.attach(part)
