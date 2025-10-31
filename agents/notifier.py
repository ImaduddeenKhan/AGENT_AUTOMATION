import os
import logging
import smtplib
from email.mime.text import MIMEText  # ✅ Corrected import
from email.mime.multipart import MIMEMultipart  # ✅ Corrected import
from typing import List
from agno.agent import Agent
from models.event_models import RankedEvent, RegistrationResult, DigestEvent

logger = logging.getLogger(__name__)


class NotifierAgent(Agent):
    def __init__(self):
        super().__init__(
            name="NotifierAgent",
            instructions="""
            Send curated event digests and registration confirmations.
            Format information clearly for both Telegram and Email.
            Include all relevant details and links.
            """,
        )

        # Initialize Telegram bot if token is available
        self.telegram_bot = None
        telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
        if telegram_token:
            try:
                import telegram
                self.telegram_bot = telegram.Bot(token=telegram_token)
                logger.info("✅ Telegram bot initialized")
            except ImportError:
                logger.warning("⚠️ python-telegram-bot not installed, Telegram disabled")
            except Exception as e:
                logger.warning(f"⚠️ Telegram bot initialization failed: {e}")

    async def send_weekly_digest(self, ranked_events: List[RankedEvent]) -> bool:
        """Send weekly curated digest"""
        try:
            # Convert to digest format
            digest_events = []
            for ranked_event in ranked_events[:10]:  # Top 10 events
                digest_event = DigestEvent(
                    title=ranked_event.event.title,
                    date=ranked_event.event.date.strftime("%Y-%m-%d %H:%M"),
                    venue=ranked_event.event.venue,
                    description=(ranked_event.event.description[:200] + "..."
                                 if len(ranked_event.event.description) > 200
                                 else ranked_event.event.description),
                    source_link=ranked_event.event.source_url,
                    relevance_score=ranked_event.relevance_score,
                    registration_status="✅ Auto-registered" if ranked_event.relevance_score >= 0.8 else "⏸️ Manual review"
                )
                digest_events.append(digest_event)

            # Send notifications
            telegram_success = True
            email_success = True

            if self.telegram_bot:
                telegram_success = await self._send_telegram_digest(digest_events)
            else:
                logger.info("ℹ️ Telegram not configured, skipping Telegram notification")

            if os.getenv("EMAIL_USERNAME"):
                email_success = await self._send_email_digest(digest_events)
            else:
                logger.info("ℹ️ Email not configured, skipping email notification")

            overall_success = telegram_success or email_success  # At least one successful
            logger.info(f"📊 Digest sent - Telegram: {telegram_success}, Email: {email_success}")

            return overall_success

        except Exception as e:
            logger.error(f"❌ Error sending weekly digest: {e}")
            return False

    async def send_registration_confirmation(self, results: List[RegistrationResult]):
        """Send registration confirmations"""
        successful_registrations = [r for r in results if r.success]

        if not successful_registrations:
            logger.info("ℹ️ No successful registrations to confirm")
            return

        for result in successful_registrations:
            message = self._format_registration_message(result)

            # Send Telegram message
            if self.telegram_bot:
                await self._send_telegram_message(message)

            # Log to console
            logger.info(f"✅ Registration confirmation: {result.event.event.title}")

    async def _send_telegram_digest(self, events: List[DigestEvent]) -> bool:
        """Send digest to Telegram channel"""
        try:
            message = "🚀 **Raptor Event Scout - Weekly Digest**\n\n"
            message += f"📅 **Curated events for this week:** {len(events)} events found\n\n"

            for i, event in enumerate(events, 1):
                message += f"**{i}. {event.title}**\n"
                message += f"   📍 {event.venue} | 🕐 {event.date}\n"
                message += f"   ⭐ Relevance: {event.relevance_score}/1.0\n"
                message += f"   📝 {event.description}\n"
                message += f"   🔗 [Event Link]({event.source_link})\n"
                message += f"   🎫 {event.registration_status}\n\n"

            message += "---\n"
            message += "*Powered by Raptor AI Event Scout*"

            await self.telegram_bot.send_message(
                chat_id=os.getenv("TELEGRAM_CHAT_ID"),
                text=message,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )

            logger.info("✅ Telegram digest sent successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send Telegram digest: {e}")
            return False

    async def _send_email_digest(self, events: List[DigestEvent]) -> bool:
        """Send digest via email"""
        try:
            smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            email_user = os.getenv("EMAIL_USERNAME")
            email_password = os.getenv("EMAIL_PASSWORD")
            to_email = os.getenv("CONTACT_EMAIL", email_user)  # Fallback to sender email

            if not email_user or not email_password:
                logger.warning("⚠️ Email credentials not fully configured")
                return False

            # Create message
            msg = MIMEMultipart()  # ✅ Corrected class name
            msg['From'] = email_user
            msg['To'] = to_email
            msg['Subject'] = "🚀 Raptor Event Scout - Weekly Event Digest"

            # Create HTML content
            html_content = self._generate_email_html(events, len(events))
            msg.attach(MIMEText(html_content, 'html'))  # ✅ Corrected class name

            # Send email
            with smtplib.SMTP(smtp_server, smtp_port) as server:
                server.starttls()
                server.login(email_user, email_password)
                server.send_message(msg)

            logger.info("✅ Email digest sent successfully")
            return True

        except Exception as e:
            logger.error(f"❌ Failed to send email digest: {e}")
            return False

    def _generate_email_html(self, events: List[DigestEvent], total_events: int) -> str:
        """Generate HTML email content"""
        events_html = ""
        for i, event in enumerate(events, 1):
            status_class = "registered" if "Auto" in event.registration_status else "pending"
            status_text = "Auto-registered" if "Auto" in event.registration_status else "Needs review"

            events_html += f"""
            <div class="event">
                <div class="event-title">{i}. {event.title}</div>
                <div class="event-meta">
                    📍 {event.venue} | 🕐 {event.date}<br>
                    ⭐ Relevance: <span class="relevance-score">{event.relevance_score}/1.0</span>
                </div>
                <p class="event-description">{event.description}</p>
                <div class="event-links">
                    <a href="{event.source_link}" class="event-link">Event Details & Registration</a>
                    <span class="registration-status {status_class}">{status_text}</span>
                </div>
            </div>
            """

        html = f"""
        <html>
            <head>
                <style>
                    body {{ 
                        font-family: 'Segoe UI', Arial, sans-serif; 
                        line-height: 1.6; 
                        color: #333; 
                        max-width: 800px; 
                        margin: 0 auto; 
                        padding: 20px;
                    }}
                    .header {{ 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                        padding: 30px;
                        border-radius: 10px;
                        text-align: center;
                        margin-bottom: 30px;
                    }}
                    .event {{ 
                        border: 1px solid #e1e8ed; 
                        padding: 20px; 
                        margin: 15px 0; 
                        border-radius: 8px;
                        background: #fafbfc;
                    }}
                    .event-title {{ 
                        font-size: 18px; 
                        font-weight: bold; 
                        color: #2c3e50; 
                        margin-bottom: 10px;
                    }}
                    .event-meta {{ 
                        color: #7f8c8d; 
                        font-size: 14px; 
                        margin-bottom: 10px;
                    }}
                    .relevance-score {{ 
                        color: #27ae60; 
                        font-weight: bold; 
                    }}
                    .event-description {{
                        color: #34495e;
                        margin: 10px 0;
                        font-size: 14px;
                    }}
                    .event-links {{
                        display: flex;
                        justify-content: space-between;
                        align-items: center;
                        margin-top: 15px;
                    }}
                    .event-link {{
                        color: #3498db;
                        text-decoration: none;
                        font-weight: 500;
                    }}
                    .event-link:hover {{
                        text-decoration: underline;
                    }}
                    .registration-status {{
                        padding: 4px 12px;
                        border-radius: 20px;
                        font-size: 12px;
                        font-weight: bold;
                    }}
                    .registered {{
                        background-color: #27ae60;
                        color: white;
                    }}
                    .pending {{
                        background-color: #f39c12;
                        color: white;
                    }}
                    .footer {{
                        text-align: center;
                        margin-top: 30px;
                        color: #7f8c8d;
                        font-size: 12px;
                    }}
                </style>
            </head>
            <body>
                <div class="header">
                    <h1>🚀 Raptor Event Scout</h1>
                    <h2>Weekly Event Digest</h2>
                    <p>Found {total_events} relevant events for this week</p>
                </div>

                {events_html}

                <div class="footer">
                    <p>This digest was automatically generated by Raptor AI Event Scout</p>
                    <p>💼 {os.getenv('COMPANY_NAME', 'Raptor AI Inc.')}</p>
                </div>
            </body>
        </html>
        """

        return html

    def _format_registration_message(self, result: RegistrationResult) -> str:
        """Format registration confirmation message"""
        event = result.event.event

        message = f"""
    ✅ **Successfully Registered for Event**

    📅 **Event:** {event.title}
    🏢 **Venue:** {event.venue}, {event.city}
    📅 **Date:** {event.date.strftime('%Y-%m-%d %H:%M')}
    🔗 **Link:** {event.source_url}

    🎫 **Confirmation:** {result.confirmation_data.get('status', 'confirmed')}
    ⭐ **Relevance Score:** {result.event.relevance_score}/1.0

    *Registration completed automatically by Raptor Event Scout*
        """

        return message.strip()

    async def _send_telegram_message(self, message: str):
        """Send simple message to Telegram"""
        try:
            if self.telegram_bot:
                await self.telegram_bot.send_message(
                    chat_id=os.getenv("TELEGRAM_CHAT_ID"),
                    text=message,
                    parse_mode='Markdown'
                )
        except Exception as e:
            logger.error(f"❌ Failed to send Telegram message: {e}")