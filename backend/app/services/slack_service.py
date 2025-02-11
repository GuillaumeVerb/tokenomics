from typing import Optional

from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError

from app.core.config import settings
from app.core.logger import logger


class SlackService:
    def __init__(self):
        self._client: Optional[WebClient] = None

    @property
    def client(self) -> WebClient:
        """
        Lazy initialization of Slack client to avoid unnecessary API token validation
        when Slack integration is not used.
        """
        if self._client is None:
            if not settings.is_slack_configured:
                raise ValueError(
                    "Slack API token is not configured. Please set SLACK_API_TOKEN in your .env file."
                )
            self._client = WebClient(token=settings.SLACK_API_TOKEN)
        return self._client

    async def send_message(self, channel: str, text: str) -> bool:
        """
        Send a message to a Slack channel

        Args:
            channel: The channel to send the message to (e.g. "#general")
            text: The message text

        Returns:
            bool: True if message was sent successfully, False otherwise
        """
        try:
            response = self.client.chat_postMessage(channel=channel, text=text)
            return response["ok"]
        except SlackApiError as e:
            logger.error(f"Error sending message to Slack: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error when sending Slack message: {str(e)}")
            return False

    async def send_notification(self, message: str) -> bool:
        """
        Send a notification to the default notification channel

        Args:
            message: The notification message

        Returns:
            bool: True if notification was sent successfully, False otherwise
        """
        # You can configure a default channel for notifications
        default_channel = "#notifications"
        return await self.send_message(default_channel, message)


# Create a global instance of the Slack service
slack_service = SlackService()
