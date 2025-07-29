from pydantic import BaseModel, Field, field_validator
from typing import List, Any
from .context_item import ContextItem
from .faq import FAQ
from .chat_example import ChatExample
from ....base_models import CompanyAssetModel
from ....base_models.chatty_asset_model import ChattyAssetPreview
from .chatty_ai_mode import ChattyAIMode
from ....utils.custom_exceptions import NotFoundError
from ....utils.types.identifier import StrObjectId

class ChattyAIAgent(CompanyAssetModel):
    """AI Agent configuration model"""
    # Basic Information
    name: str = Field(..., description="Name of the AI agent")
    personality: str = Field(..., description="Detailed personality description of the agent")
    general_objective: str = Field(..., description="General objective/goal of the agent")
    # Configuration
    contexts: List[ContextItem] = Field(default_factory=list, description="List of context items")
    unbreakable_rules: List[str] = Field(default_factory=list, description="List of unbreakable rules")
    examples: List[ChatExample] = Field(default_factory=list, description="Training examples")
    faqs: List[FAQ] = Field(default_factory=list, description="Frequently asked questions")
    follow_up_strategy: str = Field(default="", description="Follow-up approach description")
    control_triggers: List[str] = Field(default_factory=list, description="Triggers for human handoff")
    allowed_integration_ids : List[StrObjectId] = Field(default_factory=list, description="Allowed integration users ids")
    mode: ChattyAIMode = Field(default=ChattyAIMode.OFF)


    @field_validator('personality')
    @classmethod
    def validate_personality_not_empty(cls, v):
        if not v.strip():
            raise ValueError("Personality cannot be empty")
        return v.strip()

    @field_validator('general_objective')
    @classmethod
    def validate_objective_not_empty(cls, v):
        if not v.strip():
            raise ValueError("General objective cannot be empty")
        return v.strip()

    @field_validator('contexts')
    @classmethod
    def validate_contexts_order(cls, v):
        # Sort contexts by order
        return sorted(v, key=lambda x: x.order)

    def get_context_by_title(self, title: str) -> ContextItem:
        """Get context item by title"""
        context = next((context for context in self.contexts if context.title.lower() == title.lower()), None)
        if context is None:
            raise NotFoundError(f"Context with title {title} not found")
        return context

class ChattyAIAgentPreview(ChattyAssetPreview):
    """Preview of the Chatty AI Agent"""
    general_objective: str = Field(..., description="General objective of the AI agent")

    @classmethod
    def get_projection(cls) -> dict[str, Any]:
        return super().get_projection() | {"general_objective": 1}

