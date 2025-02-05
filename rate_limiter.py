import time
from telegram.ext import ContextTypes

class RateLimiter:

    def __init__(self, cooldown_seconds=300):
        self.cooldown_seconds = cooldown_seconds

    async def is_allowed(self, context:ContextTypes.DEFAULT_TYPE):
        user_data = context.user_data
        current_time = time.time()

        last_request_time = user_data.get("last_request_time", None)

        if last_request_time:
            elapsed_time = current_time - last_request_time
            if elapsed_time < self.cooldown_seconds:
                wait_time = int(self.cooldown_seconds - elapsed_time)
                return False, f""
        user_data["last_request_time"] = current_time
        return True, "Request allowed."