"""LLM adapters used by runner.py.

get_llm() picks, in order:
  1. FakeLLM        when RUNNER_FAKE_LLM=1 (tests, dry runs; echoes a stub or uses a callable)
  2. AnthropicLLM   when ANTHROPIC_API_KEY is set and `pip install anthropic` was done
Set ANTHROPIC_MODEL to choose the model; the default below is the current Sonnet-class model.
"""
import os

DEFAULT_MODEL = "claude-sonnet-5-5"


class LLMNotConfigured(RuntimeError):
    pass


class FakeLLM:
    """Deterministic stand-in. `responder` may be a str, a list (popped in order) or a callable(prompt)->str."""

    def __init__(self, responder="{}"):
        self.responder = responder
        self.calls = []

    def complete(self, prompt, system=None, max_tokens=4096):
        self.calls.append({"prompt": prompt, "system": system})
        if callable(self.responder):
            return self.responder(prompt)
        if isinstance(self.responder, list):
            return self.responder.pop(0) if len(self.responder) > 1 else self.responder[0]
        return self.responder


class AnthropicLLM:
    def __init__(self, model=None):
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover
            raise LLMNotConfigured("Install the SDK first: pip install anthropic") from exc
        self.client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY
        self.model = model or os.getenv("ANTHROPIC_MODEL", DEFAULT_MODEL)

    def complete(self, prompt, system=None, max_tokens=4096):
        kwargs = {"model": self.model, "max_tokens": max_tokens,
                  "messages": [{"role": "user", "content": prompt}]}
        if system:
            kwargs["system"] = system
        message = self.client.messages.create(**kwargs)
        return "".join(block.text for block in message.content if getattr(block, "type", "") == "text")


def get_llm():
    if os.getenv("RUNNER_FAKE_LLM") == "1":
        return FakeLLM()
    if os.getenv("ANTHROPIC_API_KEY"):
        return AnthropicLLM()
    raise LLMNotConfigured("No LLM configured: set ANTHROPIC_API_KEY (and pip install anthropic), or RUNNER_FAKE_LLM=1 for a dry run.")
