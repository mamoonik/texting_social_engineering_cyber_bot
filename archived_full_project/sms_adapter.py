# # ghosteye/sms_adapter.py
# from __future__ import annotations
# import os, uuid
# from twilio.rest import Client

from __future__ import annotations
import os, uuid
from twilio.rest import Client
# class TwilioAdapter:
#     def __init__(self):
#         self.mock = os.getenv("MOCK_TWILIO", "").lower() == "true"
#         if not self.mock:
#             sid = os.getenv("TWILIO_ACCOUNT_SID")
#             token = os.getenv("TWILIO_AUTH_TOKEN")
#             if not (sid and token):
#                 raise RuntimeError("Missing Twilio credentials")
#             self.client = Client(sid, token)

#     def send_sms(self, from_number: str, to_number: str, body: str) -> str:
#         if self.mock:
#             sid = f"MOCK-{uuid.uuid4().hex[:10]}"
#             print(f"[MOCK SEND] {from_number} → {to_number}: {body}  (sid={sid})")
#             return sid
#         msg = self.client.messages.create(from_=from_number, to=to_number, body=body)
#         return msg.sid
class TwilioAdapter:
    def __init__(self):
        self.mock = os.getenv("MOCK_TWILIO", "").lower() == "true"
        if not self.mock:
            sid = os.getenv("TWILIO_ACCOUNT_SID")
            token = os.getenv("TWILIO_AUTH_TOKEN")
            if not (sid and token):
                raise RuntimeError("Missing Twilio credentials")
            self.client = Client(sid, token)
        self.status_cb = os.getenv("PUBLIC_BASE_URL")
        if self.status_cb:
            self.status_cb = self.status_cb.rstrip("/") + "/twilio/status"

    def send_sms(self, from_number: str, to_number: str, body: str) -> str:
        if self.mock:
            sid = f"MOCK-{uuid.uuid4().hex[:10]}"
            print(f"[MOCK SEND] {from_number} → {to_number}: {body}  (sid={sid})")
            return sid
        kwargs = dict(from_=from_number, to=to_number, body=body)
        if self.status_cb:
            kwargs["status_callback"] = self.status_cb
        msg = self.client.messages.create(**kwargs)
        return msg.sid