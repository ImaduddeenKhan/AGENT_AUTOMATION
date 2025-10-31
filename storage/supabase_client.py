import os
import logging
from supabase import create_client, Client
from typing import List, Dict, Any, Optional
from datetime import datetime
from models.event_models import Event, RankedEvent

logger = logging.getLogger(__name__)


class DatabaseManager:
    def __init__(self):
        try:
            supabase_url = os.getenv("SUPABASE_URL")
            supabase_key = os.getenv("SUPABASE_KEY")

            if not supabase_url or not supabase_key:
                raise ValueError("Supabase URL and Key must be set in environment variables")

            self.supabase: Client = create_client(supabase_url, supabase_key)
            logger.info("✅ Supabase client initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            raise

    async def save_events(self, events: List[Event]) -> List[str]:
        """Save events to database, skip duplicates"""
        event_ids = []

        for event in events:
            try:
                # Check if event already exists
                existing = self.supabase.table("events") \
                    .select("id") \
                    .eq("source_url", event.source_url) \
                    .execute()

                if existing.data:
                    logger.info(f"⚠️ Event already exists: {event.title}")
                    event_ids.append(existing.data[0]['id'])
                    continue

                # Insert new event
                event_data = {
                    "title": event.title,
                    "description": event.description,
                    "event_date": event.date.isoformat(),
                    "venue": event.venue,
                    "city": event.city,
                    "source_url": event.source_url,
                    "source_platform": event.source_platform,
                    "price": event.price,
                    "created_at": datetime.now().isoformat()
                }

                result = self.supabase.table("events").insert(event_data).execute()

                if result.data:
                    event_ids.append(result.data[0]['id'])
                    logger.info(f"✅ Saved event: {event.title}")
                else:
                    logger.error(f"❌ Failed to save event: {event.title}")

            except Exception as e:
                logger.error(f"❌ Error saving event {event.title}: {e}")
                continue

        return event_ids

    async def update_event_ranking(self, ranked_event: RankedEvent, event_id: str):
        """Update event with relevance score and keywords"""
        try:
            update_data = {
                "relevance_score": ranked_event.relevance_score,
                "keywords_matched": ranked_event.matched_keywords,
                "updated_at": datetime.now().isoformat()
            }

            self.supabase.table("events") \
                .update(update_data) \
                .eq("id", event_id) \
                .execute()

            logger.info(f"✅ Updated ranking for event: {ranked_event.event.title}")
        except Exception as e:
            logger.error(f"❌ Error updating event ranking: {e}")

    async def save_registration(self, registration_data: Dict[str, Any]) -> Optional[str]:
        """Save registration details to database"""
        try:
            result = self.supabase.table("event_registrations") \
                .insert(registration_data) \
                .execute()

            if result.data:
                reg_id = result.data[0]['id']
                logger.info(f"✅ Saved registration: {reg_id}")
                return reg_id
            return None
        except Exception as e:
            logger.error(f"❌ Error saving registration: {e}")
            return None

    async def mark_event_registered(self, event_id: str, confirmation_data: Dict[str, Any]):
        """Mark event as registered and save confirmation"""
        try:
            update_data = {
                "is_registered": True,
                "registration_confirmation": confirmation_data,
                "updated_at": datetime.now().isoformat()
            }

            self.supabase.table("events") \
                .update(update_data) \
                .eq("id", event_id) \
                .execute()

            logger.info(f"✅ Marked event as registered: {event_id}")
        except Exception as e:
            logger.error(f"❌ Error marking event as registered: {e}")