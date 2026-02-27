import os

TESLA_URL = "https://www.tesla.com/ko_kr"
DISCORD_WEBHOOK_URL = os.environ.get("DISCORD_WEBHOOK_URL", "")
STATE_FILE = os.path.join(os.path.dirname(__file__), "state.json")
