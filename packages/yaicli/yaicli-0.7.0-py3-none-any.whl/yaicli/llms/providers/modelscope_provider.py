from typing import Any, Dict

from .openai_provider import OpenAIProvider


class ModelScopeProvider(OpenAIProvider):
    """ModelScope provider implementation based on openai-compatible API"""

    DEFAULT_BASE_URL = "https://api-inference.modelscope.cn/v1/"

    def get_completion_params(self) -> Dict[str, Any]:
        params = super().get_completion_params()
        if "max_completion_tokens" in params:
            params["max_tokens"] = params.pop("max_completion_tokens")
        return params
