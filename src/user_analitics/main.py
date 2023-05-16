
from datetime import time
from user_analitics.analitics_automation import analitics_automation

def start_logs_analitcs(user_id, campaign_id):
    analitics_automation.start(user_id, campaign_id)