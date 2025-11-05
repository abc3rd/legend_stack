"""
Transcriber Service - Converts text input into JSON formats for AI communication
Supports multiple AI providers: OpenAI, Anthropic, Ollama, Google AI, and more
"""

from typing import Dict, List, Any, Optional
from datetime import datetime
import json


class TranscriberService:
    """Service for converting text to various AI provider JSON formats"""

    SUPPORTED_PROVIDERS = [
        "openai",
        "anthropic",
        "ollama",
        "google",
        "cohere",
        "huggingface",
        "generic"
    ]

    @staticmethod
    def text_to_openai(
        text: str,
        model: str = "gpt-4",
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Convert text to OpenAI API format"""
        messages = []

        if system_message:
            messages.append({
                "role": "system",
                "content": system_message
            })

        messages.append({
            "role": "user",
            "content": text
        })

        payload = {
            "model": model,
            "messages": messages,
            "temperature": temperature
        }

        if max_tokens:
            payload["max_tokens"] = max_tokens

        return payload

    @staticmethod
    def text_to_anthropic(
        text: str,
        model: str = "claude-3-5-sonnet-20241022",
        system_message: Optional[str] = None,
        temperature: float = 1.0,
        max_tokens: int = 1024
    ) -> Dict[str, Any]:
        """Convert text to Anthropic Claude API format"""
        payload = {
            "model": model,
            "max_tokens": max_tokens,
            "temperature": temperature,
            "messages": [
                {
                    "role": "user",
                    "content": text
                }
            ]
        }

        if system_message:
            payload["system"] = system_message

        return payload

    @staticmethod
    def text_to_ollama(
        text: str,
        model: str = "llama2",
        system_message: Optional[str] = None,
        stream: bool = False
    ) -> Dict[str, Any]:
        """Convert text to Ollama API format"""
        payload = {
            "model": model,
            "prompt": text,
            "stream": stream
        }

        if system_message:
            payload["system"] = system_message

        return payload

    @staticmethod
    def text_to_google(
        text: str,
        model: str = "gemini-pro",
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Convert text to Google AI (Gemini) API format"""
        contents = []

        if system_message:
            contents.append({
                "role": "user",
                "parts": [{"text": system_message}]
            })

        contents.append({
            "role": "user",
            "parts": [{"text": text}]
        })

        payload = {
            "contents": contents,
            "generationConfig": {
                "temperature": temperature,
            }
        }

        if max_tokens:
            payload["generationConfig"]["maxOutputTokens"] = max_tokens

        return payload

    @staticmethod
    def text_to_cohere(
        text: str,
        model: str = "command",
        system_message: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: Optional[int] = None
    ) -> Dict[str, Any]:
        """Convert text to Cohere API format"""
        payload = {
            "model": model,
            "message": text,
            "temperature": temperature
        }

        if system_message:
            payload["preamble"] = system_message

        if max_tokens:
            payload["max_tokens"] = max_tokens

        return payload

    @staticmethod
    def text_to_huggingface(
        text: str,
        model: str = "gpt2",
        parameters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convert text to HuggingFace API format"""
        payload = {
            "inputs": text,
        }

        if parameters:
            payload["parameters"] = parameters
        else:
            payload["parameters"] = {
                "max_new_tokens": 250,
                "temperature": 0.7,
                "return_full_text": False
            }

        return payload

    @staticmethod
    def text_to_generic(
        text: str,
        model: str = "default",
        additional_params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Convert text to a generic AI API format"""
        payload = {
            "model": model,
            "input": text,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if additional_params:
            payload.update(additional_params)

        return payload

    @classmethod
    def convert(
        cls,
        text: str,
        provider: str = "generic",
        **kwargs
    ) -> Dict[str, Any]:
        """
        Universal conversion method

        Args:
            text: The input text to convert
            provider: The AI provider (openai, anthropic, ollama, google, cohere, huggingface, generic)
            **kwargs: Additional parameters specific to each provider

        Returns:
            Dictionary containing the JSON payload for the specified provider
        """
        provider = provider.lower()

        if provider not in cls.SUPPORTED_PROVIDERS:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Supported providers: {', '.join(cls.SUPPORTED_PROVIDERS)}"
            )

        if provider == "openai":
            return cls.text_to_openai(text, **kwargs)
        elif provider == "anthropic":
            return cls.text_to_anthropic(text, **kwargs)
        elif provider == "ollama":
            return cls.text_to_ollama(text, **kwargs)
        elif provider == "google":
            return cls.text_to_google(text, **kwargs)
        elif provider == "cohere":
            return cls.text_to_cohere(text, **kwargs)
        elif provider == "huggingface":
            return cls.text_to_huggingface(text, **kwargs)
        else:  # generic
            return cls.text_to_generic(text, **kwargs)

    @classmethod
    def convert_batch(
        cls,
        text: str,
        providers: List[str],
        **kwargs
    ) -> Dict[str, Dict[str, Any]]:
        """
        Convert text to multiple provider formats at once

        Args:
            text: The input text to convert
            providers: List of provider names
            **kwargs: Additional parameters (applied to all providers)

        Returns:
            Dictionary mapping provider names to their JSON payloads
        """
        results = {}

        for provider in providers:
            try:
                results[provider] = cls.convert(text, provider, **kwargs)
            except Exception as e:
                results[provider] = {"error": str(e)}

        return results

    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """Get list of supported AI providers"""
        return cls.SUPPORTED_PROVIDERS.copy()

    @staticmethod
    def format_json(data: Dict[str, Any], indent: int = 2) -> str:
        """Pretty print JSON data"""
        return json.dumps(data, indent=indent, ensure_ascii=False)
