"""
Listener Line Bee
-----------------
Manages SMS, Voice Calls, and Listener Interactions via Twilio.
Enables "Rally" features and Voicemail-to-Text for the station.
"""

import os

from hive.bees.base_bee import BaseBee

try:
    from twilio.rest import Client

    TWILIO_AVAILABLE = True
except ImportError:
    TWILIO_AVAILABLE = False


class ListenerLineBee(BaseBee):
    """
    Handles Twilio interactions: SMS replies, Voice logs, and Call routing.
    """

    def __init__(self, hive_path, gateway=None):
        super().__init__(hive_path, gateway)

        self.account_sid = os.getenv("TWILIO_ACCOUNT_SID")
        self.auth_token = os.getenv("TWILIO_AUTH_TOKEN")
        self.phone_number = os.getenv("TWILIO_PHONE_NUMBER")

        if TWILIO_AVAILABLE and self.account_sid and self.auth_token:
            try:
                self.client = Client(self.account_sid, self.auth_token)
                self.log("Twilio Client: CONNECTED", level="success")
            except Exception as e:
                self.log(f"Twilio Config Error: {e}", level="error")
                self.client = None
        else:
            self.client = None
            if not TWILIO_AVAILABLE:
                self.log("Twilio Library missing.", level="warning")
            else:
                self.log(
                    "Twilio Credentials missing in .env (TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)",
                    level="warning",
                )

    def work(self, task):
        instruction = task.get("instruction", "").lower()
        args = task.get("args", {})

        if not self.client:
            return {"success": False, "reason": "Twilio not configured"}

        if "sms" in instruction:
            return self.send_sms(args.get("to"), args.get("message"))
        elif "log_calls" in instruction:
            return self.fetch_call_logs(args.get("limit", 10))

        return {"success": False, "reason": "Unknown instruction"}

    def send_sms(self, to_number, message_body):
        """Send an outgoing SMS."""
        try:
            message = self.client.messages.create(
                body=message_body, from_=self.phone_number, to=to_number
            )
            return {"success": True, "sid": message.sid, "status": message.status}
        except Exception as e:
            return {"success": False, "error": str(e)}

    def fetch_call_logs(self, limit=10):
        """Get recent calls to the station."""
        try:
            calls = self.client.calls.list(limit=limit)
            return {
                "success": True,
                "calls": [
                    {"from": c.from_, "status": c.status, "duration": c.duration} for c in calls
                ],
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
