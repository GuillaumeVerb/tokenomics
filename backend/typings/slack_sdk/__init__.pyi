"""Type stubs for slack_sdk."""
from typing import Any, Dict, List, Optional, Union

class WebClient:
    def __init__(self, token: Optional[str] = None, base_url: str = "https://www.slack.com/api/") -> None: ...
    
    def chat_postMessage(
        self,
        channel: str,
        text: Optional[str] = None,
        blocks: Optional[List[Dict[str, Any]]] = None,
        thread_ts: Optional[str] = None,
        reply_broadcast: Optional[bool] = None,
        unfurl_links: Optional[bool] = None,
        unfurl_media: Optional[bool] = None,
        username: Optional[str] = None,
        as_user: Optional[bool] = None,
        icon_emoji: Optional[str] = None,
        icon_url: Optional[str] = None,
        mrkdwn: Optional[bool] = None,
        link_names: Optional[bool] = None,
        attachments: Optional[List[Dict[str, Any]]] = None,
        metadata: Optional[Dict[str, Any]] = None,
        parse: Optional[str] = None,
    ) -> Dict[str, Any]: ...
    
    def files_upload(
        self,
        channels: Optional[Union[str, List[str]]] = None,
        content: Optional[str] = None,
        file: Optional[Union[str, bytes]] = None,
        filename: Optional[str] = None,
        filetype: Optional[str] = None,
        initial_comment: Optional[str] = None,
        thread_ts: Optional[str] = None,
        title: Optional[str] = None,
    ) -> Dict[str, Any]: ...
    
    def conversations_list(
        self,
        cursor: Optional[str] = None,
        exclude_archived: Optional[bool] = None,
        limit: Optional[int] = None,
        team_id: Optional[str] = None,
        types: Optional[List[str]] = None,
    ) -> Dict[str, Any]: ...
    
    def users_list(
        self,
        cursor: Optional[str] = None,
        limit: Optional[int] = None,
        team_id: Optional[str] = None,
    ) -> Dict[str, Any]: ... 