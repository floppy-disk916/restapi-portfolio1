from __future__ import annotations

from typing import Any

from drogue.core.abstracts import IdentityExtractor


class FixedUserExtractor(IdentityExtractor):
    """Extract rate limit key by authenticated user ID. Fixed"""

    def __init__(self, user_id_key: str = "user_id", anonymous_value: str = "anonymous") -> None:
        self.user_id_key = user_id_key
        self.anonymous_value = anonymous_value

    async def extract(self, context: dict[str, Any]) -> str:
        # Check user_id in state or directly in context
        user_id = context.get(self.user_id_key)
        if user_id is None:
            state = context.get("state", {})
            # Previously: user_id = state.get(self.user_id_key)
            user_id = getattr(state, self.user_id_key, None)
        if user_id is None:
            request = context.get("request")
            if request is not None:
                state = getattr(request, "state", None)
                if state is not None:
                    user_id = getattr(state, self.user_id_key, None)

        if user_id is not None:
            return str(user_id)
        return self.anonymous_value

