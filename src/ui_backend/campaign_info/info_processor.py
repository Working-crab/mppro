from kafka_dir.topics import Topics
from ui_backend.campaign_info.capaign_processor import Capaign_processor

async def process_campaign(campaign_processing):
    await Capaign_processor.go_campaign_processing(campaign_processing)
