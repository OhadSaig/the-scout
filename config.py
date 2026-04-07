import os
from dotenv import load_dotenv

load_dotenv()

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
SCOUT_MODEL = "claude-opus-4-6"

# GDPR retention windows (months)
TRACKING_RETENTION_MONTHS = 24
ALERT_RETENTION_MONTHS = 12

# Data health thresholds
HEALTH_SCORE_VERIFIED = 80.0
HEALTH_SCORE_PARTIAL = 50.0
