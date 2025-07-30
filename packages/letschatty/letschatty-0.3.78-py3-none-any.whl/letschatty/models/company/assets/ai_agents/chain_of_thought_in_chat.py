from pydantic import Field
from ....base_models import CompanyAssetModel
from ....utils.types.identifier import StrObjectId
from enum import StrEnum
from .chatty_ai_agent import ChattyAIAgent
from ....base_models.chatty_asset_model import ChattyAssetPreview
from typing import ClassVar, Type, Any

class ChainOfThoughtInChatTrigger(StrEnum):
    """Trigger for the chain of thought in chat"""
    USER_MESSAGE = "user_message"
    FOLLOW_UP = "follow_up"


class ChainOfThoughtInChatPreview(ChattyAssetPreview):
    """Preview of the chain of thought in chat"""
    chat_id : StrObjectId
    trigger: ChainOfThoughtInChatTrigger
    trigger_id : str = Field(description="The id of the trigger which could be a message_id or a workflow assigned to chat link id")
    chain_of_thought : str = Field(description="The chain of thought")
    name: str = Field(description="A title for the chain of thought", alias="title")

    @classmethod
    def get_projection(cls) -> dict[str, Any]:
        return super().get_projection() | {"chat_id": 1, "trigger": 1, "trigger_id": 1, "chain_of_thought": 1, "name": 1}

class ChainOfThoughtInChat(CompanyAssetModel):
    """Chain of thought in chat"""
    chat_id : StrObjectId
    trigger: ChainOfThoughtInChatTrigger
    trigger_id : str = Field(description="The id of the trigger which could be a message_id or a workflow assigned to chat link id")
    chatty_ai_agent : ChattyAIAgent = Field(description="The chatty ai agent at the moment of triggering the chain of thought")
    chain_of_thought : str = Field(description="The chain of thought")
    name: str = Field(description="A title for the chain of thought", alias="title")
    preview_class: ClassVar[Type[ChattyAssetPreview]] = ChainOfThoughtInChatPreview

