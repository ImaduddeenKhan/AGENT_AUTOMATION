import logging
from typing import List
from agno.agent import Agent
from agno.models.groq import Groq
from models.event_models import Event, RankedEvent

logger = logging.getLogger(__name__)


class EventRankerAgent(Agent):
    def __init__(self):
        super().__init__(
            name="EventRankerAgent",
            model=Groq(id="llama-3.3-70b-versatile"),
            instructions="""
            You are an event relevance analyzer for a tech company.
            Analyze events based on their relevance to business development, partnerships, and client acquisition.

            Focus on these keywords and themes:
            - AI, artificial intelligence, machine learning
            - Startup, entrepreneurship, venture capital  
            - HR tech, hiring, recruitment
            - Business, networking, partnerships
            - Technology, innovation, digital transformation
            - Expat, international business

            Score events from 0.0 to 1.0 based on:
            1. Direct keyword matches (40%)
            2. Semantic relevance to tech business (30%)
            3. Potential for partnerships/client acquisition (20%)
            4. Location suitability (10%)

            Be strict - only high-quality events should score above 0.7.
            """,
        )
        self.relevance_keywords = [
            "startup", "AI", "artificial intelligence", "HR tech", "expat",
            "business", "innovation", "hiring", "tech", "technology",
            "entrepreneur", "venture", "funding", "networking", "machine learning",
            "digital transformation", "partnership", "client", "investment"
        ]

    async def rank_events(self, events: List[Event]) -> List[RankedEvent]:
        """Rank events by relevance using Groq for analysis"""
        ranked_events = []

        logger.info(f"🔍 Ranking {len(events)} events by relevance...")

        for event in events:
            try:
                ranked_event = await self._calculate_relevance_score(event)
                if ranked_event.relevance_score >= 0.6:  # Minimum threshold
                    ranked_events.append(ranked_event)
                    logger.info(f"⭐ {event.title} - Score: {ranked_event.relevance_score}")
            except Exception as e:
                logger.error(f"❌ Error ranking event {event.title}: {e}")
                continue

        # Sort by relevance score (highest first)
        ranked_events.sort(key=lambda x: x.relevance_score, reverse=True)

        logger.info(f"✅ Ranked {len(ranked_events)} relevant events")
        return ranked_events

    async def _calculate_relevance_score(self, event: Event) -> RankedEvent:
        """Calculate comprehensive relevance score"""
        # Keyword matching
        keyword_matches = self._find_keyword_matches(event)
        keyword_score = min(1.0, len(keyword_matches) * 0.2)  # Max 1.0 for 5+ matches

        # Semantic analysis using Groq
        semantic_score = await self._get_semantic_score(event)

        # Location score (preference for our target cities)
        location_score = 1.0 if event.city in ["Osaka", "Kobe", "Kyoto"] else 0.3

        # Final weighted score
        final_score = (
                keyword_score * 0.4 +
                semantic_score * 0.3 +
                location_score * 0.2 +
                0.1  # Base score for all events
        )

        # Ensure score is between 0 and 1
        final_score = max(0.0, min(1.0, final_score))

        return RankedEvent(
            event=event,
            relevance_score=round(final_score, 2),
            matched_keywords=keyword_matches,
            confidence=semantic_score
        )

    def _find_keyword_matches(self, event: Event) -> List[str]:
        """Find matching keywords in event content"""
        text = f"{event.title} {event.description}".lower()
        matches = []

        for keyword in self.relevance_keywords:
            if keyword.lower() in text:
                matches.append(keyword)

        return matches

    async def _get_semantic_score(self, event: Event) -> float:
        """Use Groq to analyze semantic relevance"""
        try:
            prompt = f"""
            Analyze this event for relevance to a tech company (Raptor AI Inc.) that wants to:
            - Find business partners
            - Acquire new clients  
            - Network with startups and investors
            - Stay updated on AI and tech trends

            Event Title: {event.title}
            Event Description: {event.description[:500]}
            City: {event.city}

            Consider:
            - How relevant is this event for business development?
            - Does it attract our target audience (tech companies, startups, investors)?
            - Is the topic aligned with AI, HR tech, or business innovation?

            Provide a relevance score from 0.0 to 1.0, where:
            0.0 = Completely irrelevant
            0.3 = Slightly relevant
            0.6 = Moderately relevant  
            0.8 = Highly relevant
            1.0 = Perfect match

            Return ONLY the numeric score, no other text.
            """

            # Fixed: Use the agent directly without await on run()
            response = self.run(prompt)
            score_text = response.content.strip()

            # Extract numeric score
            try:
                score = float(score_text)
                return max(0.0, min(1.0, score))  # Clamp between 0-1
            except ValueError:
                logger.warning(f"⚠️ Could not parse score from Groq: {score_text}")
                return 0.5  # Default score

        except Exception as e:
            logger.error(f"❌ Groq analysis failed for {event.title}: {e}")
            return 0.5  # Default score on error