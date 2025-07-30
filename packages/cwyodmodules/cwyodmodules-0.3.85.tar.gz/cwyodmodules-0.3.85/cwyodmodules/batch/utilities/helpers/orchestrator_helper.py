from typing import List
from ..orchestrator.semantic_kernel_orchestrator import SemanticKernelOrchestrator

__all__ = ["Orchestrator"]


class Orchestrator:
    def __init__(self) -> None:
        self.orchestrator = SemanticKernelOrchestrator()

    async def handle_message(
        self,
        user_message: str,
        chat_history: List[dict],
        conversation_id: str,
        user_info,
        **kwargs: dict,
    ) -> dict:
        return await self.orchestrator.handle_message(
            user_message, chat_history, conversation_id, user_info, **kwargs
        )
