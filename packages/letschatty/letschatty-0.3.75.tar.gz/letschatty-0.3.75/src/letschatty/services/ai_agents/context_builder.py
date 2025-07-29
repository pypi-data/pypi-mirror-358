from letschatty.models.company.assets.ai_agents.chatty_ai_agent import ChattyAIAgent
from letschatty.models.company.assets.ai_agents.chatty_ai_mode import ChattyAIMode
from letschatty.models.company.empresa import EmpresaModel
from datetime import datetime
from zoneinfo import ZoneInfo

class ContextBuilder:
    @staticmethod
    def build_context(agent: ChattyAIAgent, mode_in_chat: ChattyAIMode, company_info:EmpresaModel) -> str:
        if agent.mode == ChattyAIMode.OFF:
            raise ValueError("Agent is in OFF mode, so it can't be used to build context")
        context = f"You are a WhatsApp AI Agent for the company {company_info.name}."
        context += f"\nThe current time is {datetime.now(ZoneInfo('UTC')).strftime('%Y-%m-%d %H:%M:%S')}"
        context += f"\nYour answers should be in the same lenguage as the user's messages. Default lenguage is Spanish."
        context += f"\nHere's your desired behavior and personality: {agent.personality}"
        context += f"\nHere's your objective: {agent.general_objective}"
        context += f"\n\n{ChattyAIMode.get_context_for_mode(mode_in_chat)}"
        context += f"\n\nHere are the context items that will be your knowledge base:"
        for context_item in agent.contexts:
            context += f"\n\n{context_item.title}: {context_item.content}"
        context += f"\n\nHere are the FAQ:"
        for faq_index, faq in enumerate(agent.faqs):
            context += f"\n{faq_index + 1}. user: {faq.question}\nAI: {faq.answer}"
        context += f"\n\nHere are the examples of how you should behave. You can also use them as FAQ. \nNote that the user might be spliting its interaction into multiple messages, so you should be able to handle that and to act the same way, so it resembles a real human conversation."
        for example_index, example in enumerate(agent.examples):
            context += f"\n{example_index + 1}. {example.title}\n"
            for message in example.messages:
                if message.is_incoming_message:
                    context += f"\nuser: {message.content.get_body_or_caption()}\n"
                else:
                    context += f"\nAI: {message.content.get_body_or_caption()}\n"
        context += f"\n\nHere are the unbreakable rules you must follow at all times. You can't break them under any circumstances:"
        for rule in agent.unbreakable_rules:
            context += f"\n{rule}"
        context += f"\n\nHere are the control triggers you must follow. If you identify any of these situations, you must call the human_handover tool:"
        for trigger in agent.control_triggers:
            context += f"\n{trigger}"
        context += f"\n\nRemember that {ChattyAIMode.get_context_for_mode(mode_in_chat)}"
        return context