import asyncio
import httpx
import logging
from typing import List, Dict, Optional
from datetime import datetime, timedelta
from agno.agent import Agent
from models.event_models import Event, EventPlatform

logger = logging.getLogger(__name__)


class EventFinderAgent(Agent):
    def __init__(self):
        super().__init__(
            name="EventFinderAgent",
            role="Discover business and tech events in Osaka, Kobe, and Kyoto",
            instructions="""
            Your task is to discover relevant events from multiple Japanese platforms.
            Focus on cities: Osaka, Kobe, Kyoto.
            Look for tech, startup, business, and innovation events.
            """,
        )
        self.cities = ["Osaka", "Kobe", "Kyoto"]
        self.platforms = [EventPlatform.CONNPASS, EventPlatform.PEATIX, EventPlatform.MEETUP]
        self.http_client = httpx.AsyncClient(timeout=30.0)

    async def discover_events(self) -> List[Event]:
        """Main method to discover events from all sources"""
        all_events = []

        try:
            tasks = []
            for city in self.cities:
                for platform in self.platforms:
                    task = self._search_platform(platform, city)
                    tasks.append(task)

            # Run all searches concurrently
            results = await asyncio.gather(*tasks, return_exceptions=True)

            for result in results:
                if isinstance(result, Exception):
                    logger.error(f"Search error: {result}")
                    continue
                if result:
                    all_events.extend(result)

            logger.info(f"✅ Discovered {len(all_events)} total events")
            return all_events

        except Exception as e:
            logger.error(f"❌ Error in event discovery: {e}")
            return []
        finally:
            await self.http_client.aclose()

    async def _search_platform(self, platform: EventPlatform, city: str) -> List[Event]:
        """Search specific platform for events"""
        try:
            if platform == EventPlatform.CONNPASS:
                return await self._search_connpass(city)
            elif platform == EventPlatform.PEATIX:
                return await self._search_peatix(city)
            elif platform == EventPlatform.MEETUP:
                return await self._search_meetup(city)
            else:
                return []
        except Exception as e:
            logger.error(f"❌ Error searching {platform} in {city}: {e}")
            return []

    async def _search_connpass(self, city: str) -> List[Event]:
        """Search Connpass for events with proper headers"""
        try:
            # Connpass API endpoint
            url = "https://connpass.com/api/v1/event/"
            params = {
                'keyword': city,
                'count': 20,  # Reduced count
                'order': 2  # Order by update time
            }

            # Add proper headers to avoid 403
            headers = {
                'User-Agent': 'RaptorEventScout/1.0 (+https://raptorai.co)',
                'Accept': 'application/json',
                'Accept-Language': 'en-US,en;q=0.9',
            }

            response = await self.http_client.get(url, params=params, headers=headers, timeout=10.0)

            if response.status_code == 403:
                logger.warning(f"⚠️ Connpass API blocked request for {city}. Using mock data instead.")
                return await self._get_connpass_mock_events(city)

            response.raise_for_status()

            data = response.json()
            events = data.get('events', [])

            parsed_events = []
            for event in events[:5]:  # Limit to 5 events per city
                try:
                    # Convert Japanese city names
                    jp_city = self._convert_city_name(city, event.get('address', ''))

                    # Parse date safely
                    event_date = datetime.now()
                    if event.get('started_at'):
                        try:
                            event_date = datetime.fromisoformat(event['started_at'].replace('Z', '+00:00'))
                        except ValueError:
                            event_date = datetime.now() + timedelta(days=7)

                    parsed_event = Event(
                        title=event.get('title', 'No Title'),
                        description=event.get('description', 'No Description')[:500],
                        date=event_date,
                        venue=event.get('place', 'Unknown Venue'),
                        city=jp_city,
                        source_url=event.get('event_url', ''),
                        source_platform=EventPlatform.CONNPASS,
                        price="Free" if event.get('fee', '0') == '0' else f"¥{event.get('fee', '0')}",
                        registration_required=True
                    )
                    parsed_events.append(parsed_event)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to parse Connpass event: {e}")
                    continue

            logger.info(f"✅ Found {len(parsed_events)} events from Connpass in {city}")
            return parsed_events

        except Exception as e:
            logger.warning(f"⚠️ Connpass API unavailable for {city}: {e}. Using mock data.")
            return await self._get_connpass_mock_events(city)

    async def _get_connpass_mock_events(self, city: str) -> List[Event]:
        """Provide mock Connpass events when API is unavailable"""
        mock_events = [
            Event(
                title=f"Tech Community Meetup {city}",
                description=f"Join the local tech community in {city} for networking and knowledge sharing. Great opportunity to connect with developers and startups.",
                date=datetime.now() + timedelta(days=10),
                venue=f"{city} Community Center",
                city=city,
                source_url=f"https://connpass.com/event/{city.lower()}-tech-{datetime.now().timestamp()}",
                source_platform=EventPlatform.CONNPASS,
                price="Free",
                registration_required=True
            )
        ]
        return mock_events

    async def _search_peatix(self, city: str) -> List[Event]:
        """Search Peatix for events (mock implementation)"""
        try:
            # Note: Peatix doesn't have a public API, so we'll use mock data
            # In production, you'd need to use web scraping (with proper permissions)

            mock_events = [
                Event(
                    title=f"AI & Startup Networking in {city}",
                    description=f"Join us for an exciting networking event with AI startups and investors in {city}. Great opportunity for partnerships and business development.",
                    date=datetime.now() + timedelta(days=7),
                    venue=f"{city} Business Center",
                    city=city,
                    source_url=f"https://peatix.com/event/{city}-ai-{datetime.now().timestamp()}",
                    source_platform=EventPlatform.PEATIX,
                    price="Free",
                    registration_required=True
                )
            ]

            logger.info(f"✅ Found {len(mock_events)} mock events from Peatix in {city}")
            return mock_events

        except Exception as e:
            logger.error(f"❌ Peatix search error for {city}: {e}")
            return []

    async def _search_meetup(self, city: str) -> List[Event]:
        """Search Meetup for events (mock implementation)"""
        try:
            # Note: Meetup API requires authentication
            # Using mock data for demonstration

            mock_events = [
                Event(
                    title=f"Tech Innovation Meetup {city}",
                    description=f"Monthly tech meetup featuring the latest innovations in AI, HR tech, and business development in {city}.",
                    date=datetime.now() + timedelta(days=14),
                    venue=f"{city} Tech Hub",
                    city=city,
                    source_url=f"https://meetup.com/tech-{city}-{datetime.now().timestamp()}",
                    source_platform=EventPlatform.MEETUP,
                    price="Free",
                    registration_required=True
                )
            ]

            logger.info(f"✅ Found {len(mock_events)} mock events from Meetup in {city}")
            return mock_events

        except Exception as e:
            logger.error(f"❌ Meetup search error for {city}: {e}")
            return []

    def _convert_city_name(self, english_city: str, japanese_address: str) -> str:
        """Convert between English and Japanese city names"""
        city_mapping = {
            'Osaka': ['大阪', 'ōsaka', 'osaka'],
            'Kobe': ['神戸', 'kōbe', 'kobe'],
            'Kyoto': ['京都', 'kyōto', 'kyoto']
        }

        for eng_city, jp_names in city_mapping.items():
            if any(name in japanese_address.lower() for name in jp_names):
                return eng_city

        return english_city  # Return original if no match