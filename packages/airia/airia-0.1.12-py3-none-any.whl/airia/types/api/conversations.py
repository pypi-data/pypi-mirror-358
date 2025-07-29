from typing import Optional

from pydantic import BaseModel, Field


class CreateConversationResponse(BaseModel):
    user_id: str = Field(alias="userId")
    conversation_id: str = Field(alias="conversationId")
    websocket_url: str = Field(alias="websocketUrl")
    deployment_id: str = Field(alias="deploymentId")
    icon_id: Optional[str] = Field(None, alias="iconId")
    icon_url: Optional[str] = Field(None, alias="iconUrl")
    description: Optional[str] = None
    space_name: Optional[str] = Field(None, alias="spaceName")
