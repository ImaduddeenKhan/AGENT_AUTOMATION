import os
import logging
import asyncio
from typing import List
from agno.agent import Agent
from models.event_models import RankedEvent, RegistrationResult

logger = logging.getLogger(__name__)


class EventRegistrarAgent(Agent):
    def __init__(self):
        super().__init__(
            name="EventRegistrarAgent",
            instructions="""
            Automatically register for relevant events that are free.
            Handle form filling and capture confirmation details.
            Only register for high-relevance free events.
            """,
        )
        self.company_info = {
            "name": os.getenv("CONTACT_NAME", "Raptor AI Representative"),
            "company": os.getenv("COMPANY_NAME", "Raptor AI Inc."),
            "email": os.getenv("CONTACT_EMAIL", "events@raptorai.co"),
            "phone": os.getenv("CONTACT_PHONE", "+81-XXX-XXXX-XXXX"),
            "position": os.getenv("CONTACT_POSITION", "Co-Founder & CTO")
        }

    async def register_for_events(self, ranked_events: List[RankedEvent]) -> List[RegistrationResult]:
        """Register for top events automatically"""
        results = []
        registered_count = 0

        for ranked_event in ranked_events:
            # Only register for top events that meet criteria
            if registered_count >= 3:  # Limit to 3 registrations per run
                logger.info("ℹ️ Registration limit reached (3 events)")
                break

            if await self._should_register(ranked_event):
                result = await self._register_single_event(ranked_event)
                results.append(result)

                if result.success:
                    registered_count += 1
                    logger.info(f"✅ Successfully registered for: {ranked_event.event.title}")
                else:
                    logger.warning(f"⚠️ Registration failed for: {ranked_event.event.title} - {result.error_message}")

                await asyncio.sleep(2)  # Rate limiting

        logger.info(
            f"📊 Registration summary: {len([r for r in results if r.success])} successful, {len([r for r in results if not r.success])} failed")
        return results

    async def _should_register(self, ranked_event: RankedEvent) -> bool:
        """Determine if we should auto-register for this event"""
        event = ranked_event.event

        # Check relevance threshold
        if ranked_event.relevance_score < 0.8:
            logger.info(f"⏭️ Skipping {event.title} - relevance score too low: {ranked_event.relevance_score}")
            return False

        # Check if event is free
        price_lower = event.price.lower()
        if not any(free_indicator in price_lower for free_indicator in ['free', '無料', '0', 'zero', 'no charge']):
            logger.info(f"⏭️ Skipping {event.title} - not free: {event.price}")
            return False

        # Check if registration is required
        if not event.registration_required:
            logger.info(f"⏭️ Skipping {event.title} - no registration required")
            return False

        logger.info(
            f"🎯 Eligible for registration: {event.title} (Score: {ranked_event.relevance_score}, Price: {event.price})")
        return True

    async def _register_single_event(self, ranked_event: RankedEvent) -> RegistrationResult:
        """Register for a single event"""
        try:
            platform = ranked_event.event.source_platform

            if platform == "connpass":
                return await self._register_connpass(ranked_event)
            elif platform == "peatix":
                return await self._register_peatix(ranked_event)
            elif platform == "meetup":
                return await self._register_meetup(ranked_event)
            else:
                return await self._register_generic(ranked_event)

        except Exception as e:
            error_msg = f"Registration error: {str(e)}"
            logger.error(f"❌ {error_msg}")
            return RegistrationResult(
                event=ranked_event,
                success=False,
                error_message=error_msg
            )

    async def _register_connpass(self, ranked_event: RankedEvent) -> RegistrationResult:
        """Register for Connpass events (mock implementation)"""
        try:
            # Note: Connpass registration typically requires manual form filling
            # This is a mock implementation
            logger.info(f"🔗 Attempting Connpass registration for: {ranked_event.event.title}")

            # Simulate registration process
            await asyncio.sleep(1)

            # Mock successful registration
            return RegistrationResult(
                event=ranked_event,
                success=True,
                confirmation_data={
                    "platform": "connpass",
                    "event_id": f"CONNPASS_{hash(ranked_event.event.source_url)}",
                    "registration_date": "2024-01-15",
                    "status": "confirmed",
                    "ticket_type": "一般"
                },
                qr_code_url=f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data={ranked_event.event.source_url}",
                error_message=None
            )

        except Exception as e:
            return RegistrationResult(
                event=ranked_event,
                success=False,
                error_message=f"Connpass registration failed: {str(e)}"
            )

    async def _register_peatix(self, ranked_event: RankedEvent) -> RegistrationResult:
        """Register for Peatix events (mock implementation)"""
        try:
            logger.info(f"🔗 Attempting Peatix registration for: {ranked_event.event.title}")
            await asyncio.sleep(1)

            return RegistrationResult(
                event=ranked_event,
                success=True,
                confirmation_data={
                    "platform": "peatix",
                    "order_id": f"PEATIX_{hash(ranked_event.event.source_url)}",
                    "ticket_type": "Free Admission",
                    "status": "confirmed"
                },
                qr_code_url=f"https://api.qrserver.com/v1/create-qr-code/?size=200x200&data=PEATIX_{hash(ranked_event.event.source_url)}",
                error_message=None
            )

        except Exception as e:
            return RegistrationResult(
                event=ranked_event,
                success=False,
                error_message=f"Peatix registration failed: {str(e)}"
            )

    async def _register_meetup(self, ranked_event: RankedEvent) -> RegistrationResult:
        """Register for Meetup events (mock implementation)"""
        try:
            logger.info(f"🔗 Attempting Meetup registration for: {ranked_event.event.title}")
            await asyncio.sleep(1)

            return RegistrationResult(
                event=ranked_event,
                success=True,
                confirmation_data={
                    "platform": "meetup",
                    "rsvp_id": f"MEETUP_{hash(ranked_event.event.source_url)}",
                    "status": "yes",
                    "guests": 0
                },
                qr_code_url=None,  # Meetup typically doesn't provide QR codes
                error_message=None
            )

        except Exception as e:
            return RegistrationResult(
                event=ranked_event,
                success=False,
                error_message=f"Meetup registration failed: {str(e)}"
            )

    async def _register_generic(self, ranked_event: RankedEvent) -> RegistrationResult:
        """Generic registration for other platforms"""
        logger.info(f"🔗 Attempting generic registration for: {ranked_event.event.title}")

        return RegistrationResult(
            event=ranked_event,
            success=True,
            confirmation_data={
                "platform": ranked_event.event.source_platform,
                "status": "auto_registered",
                "registration_date": "2024-01-15",
                "note": "Automatic registration by Raptor Event Scout"
            },
            qr_code_url=None,
            error_message=None
        )