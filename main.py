#!/usr/bin/env python3
"""
Raptor Event Scout - Main Orchestrator
Autonomous AI agent system for discovering business and tech events in Osaka, Kobe, and Kyoto.
"""

import asyncio
import os
import logging
from dotenv import load_dotenv
from datetime import datetime

from agents import EventFinderAgent, EventRankerAgent, EventRegistrarAgent, NotifierAgent
from storage.supabase_client import DatabaseManager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('raptor_scout.log', encoding='utf-8')
    ]
)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class RaptorEventScout:
    def __init__(self):
        """Initialize the Raptor Event Scout system"""
        logger.info("🚀 Initializing Raptor Event Scout...")

        # Initialize agents
        self.finder = EventFinderAgent()
        self.ranker = EventRankerAgent()
        self.registrar = EventRegistrarAgent()
        self.notifier = NotifierAgent()
        self.db = DatabaseManager()

        logger.info("✅ All agents initialized successfully")

    async def run_weekly_scout(self):
        """Main workflow to run weekly event discovery"""
        logger.info(f"🎯 Starting Raptor Event Scout - {datetime.now()}")

        try:
            # Step 1: Discover events from multiple platforms
            logger.info("🔍 Phase 1: Discovering events...")
            events = await self.finder.discover_events()

            if not events:
                logger.warning("⚠️ No events discovered")
                return False

            # Step 2: Save raw events to database
            event_ids = await self.db.save_events(events)
            logger.info(f"💾 Saved {len(event_ids)} events to database")

            # Step 3: Rank and filter events by relevance
            logger.info("🎯 Phase 2: Ranking events by relevance...")
            ranked_events = await self.ranker.rank_events(events)

            if not ranked_events:
                logger.warning("⚠️ No relevant events found after filtering")
                return False

            # Update events with relevance scores in database
            for ranked_event in ranked_events:
                # Log the ranked events
                logger.info(f"⭐ {ranked_event.event.title} - Score: {ranked_event.relevance_score}")

            # Step 4: Auto-register for top events
            logger.info("🎫 Phase 3: Registering for events...")
            registration_results = await self.registrar.register_for_events(ranked_events)

            successful_registrations = [r for r in registration_results if r.success]
            logger.info(f"✅ Successfully registered for {len(successful_registrations)} events")

            # Step 5: Save registration details
            for result in successful_registrations:
                registration_data = {
                    "event_id": None,  # Would link to actual event ID in production
                    "status": "confirmed",
                    "confirmation_data": result.confirmation_data
                }
                await self.db.save_registration(registration_data)

            # Step 6: Send weekly digest and confirmations
            logger.info("📢 Phase 4: Sending notifications...")
            digest_sent = await self.notifier.send_weekly_digest(ranked_events)

            if successful_registrations:
                await self.notifier.send_registration_confirmation(successful_registrations)

            # Summary
            logger.info(f"""
    🎉 Raptor Event Scout completed successfully!
    📊 Summary:
       - Discovered: {len(events)} events
       - Relevant: {len(ranked_events)} events  
       - Registered: {len(successful_registrations)} events
       - Notifications: {'Sent' if digest_sent else 'Failed'}
            """)

            return True

        except Exception as e:
            logger.error(f"❌ Error in Raptor Event Scout: {e}")
            import traceback
            logger.error(f"❌ Stack trace: {traceback.format_exc()}")

            # Send error notification if possible
            try:
                error_message = f"❌ Raptor Event Scout failed: {str(e)}"
                if hasattr(self.notifier, '_send_telegram_message'):
                    await self.notifier._send_telemetry_message(error_message)
            except:
                pass  # Don't let notification errors hide the original error

            return False


async def main():
    """Main function to run the Raptor Event Scout"""
    print("🚀 Starting Raptor Event Scout...")
    print("💡 Make sure you have:")
    print("   - Groq API key in .env file")
    print("   - Supabase credentials in .env file")
    print("   - Optional: Telegram bot token and email settings")
    print()

    # Check essential environment variables
    required_vars = ['GROQ_API_KEY', 'SUPABASE_URL', 'SUPABASE_KEY']
    missing_vars = [var for var in required_vars if not os.getenv(var)]

    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n📝 Please check your .env file")
        return

    # Initialize and run the scout
    scout = RaptorEventScout()

    # Check if running in immediate mode
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == '--now':
        print("⏰ Running immediate scan...")
        success = await scout.run_weekly_scout()

        if success:
            print("✅ Raptor Event Scout completed successfully!")
        else:
            print("❌ Raptor Event Scout encountered errors")
            print("📋 Check raptor_scout.log for details")
    else:
        print("ℹ️ To run immediately, use: python main.py --now")
        print("📅 For scheduled runs, use the scheduler version")


if __name__ == "__main__":
    # Run the application
    asyncio.run(main())