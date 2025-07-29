"""LangchainDigitalocean chat models."""

from typing import Any, Dict, Iterator, List, Optional
import os
import httpx

from langchain_core.callbacks import (
    CallbackManagerForLLMRun,
)
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import (
    AIMessage,
    AIMessageChunk,
    BaseMessage,
)
from langchain_core.messages.ai import UsageMetadata
from langchain_core.outputs import ChatGeneration, ChatGenerationChunk, ChatResult
from pydantic import Field


class ChatDigitalOcean(BaseChatModel):
    # TODO: Replace all TODOs in docstring. See example docstring:
    # https://github.com/langchain-ai/langchain/blob/7ff05357bac6eaedf5058a2af88f23a1817d40fe/libs/partners/openai/langchain_openai/chat_models/base.py#L1120
    """LangchainDigitalocean chat model integration.

    The default implementation echoes the first `buffer_length` characters of the input.

    Setup:
        Install ``langchain-digitalocean`` and set environment variable ``DIGITALOCEAN_MODEL_ACCESS_KEY``.

        .. code-block:: bash

            pip install -U langchain-digitalocean
            export DIGITALOCEAN_MODEL_ACCESS_KEY="your-api-key"

    Key init args — completion params:
        model: str
            Name of LangchainDigitalocean model to use.
        temperature: float
            Sampling temperature.
        max_tokens: Optional[int]
            Max number of tokens to generate.

    Key init args — client params:
        timeout: Optional[float]
            Timeout for requests.
        max_retries: int
            Max number of retries.
        api_key: Optional[str]
            LangchainDigitalocean API key. If not passed in will be read from env var DIGITALOCEAN_MODEL_ACCESS_KEY.

    See full list of supported init args and their descriptions in the params section.

    Instantiate:
        .. code-block:: python

            from langchain_digitalocean import ChatDigitalOcean

            llm = ChatDigitalOcean(
                model="...",
                temperature=0,
                max_tokens=None,
                timeout=None,
                max_retries=2,
                # api_key="...",
                # other params...
            )

    Invoke:
        .. code-block:: python

            messages = [
                ("system", "You are a helpful translator. Translate the user sentence to French."),
                ("human", "I love programming."),
            ]
            llm.invoke(messages)

        .. code-block:: python

            # TODO: Example output.

    # TODO: Delete if token-level streaming isn't supported.
    Stream:
        .. code-block:: python

            for chunk in llm.stream(messages):
                print(chunk.text(), end="")

        .. code-block:: python

            # TODO: Example output.

        .. code-block:: python

            stream = llm.stream(messages)
            full = next(stream)
            for chunk in stream:
                full += chunk
            full

        .. code-block:: python

            # TODO: Example output.

    # TODO: Delete if native async isn't supported.
    Async:
        .. code-block:: python

            await llm.ainvoke(messages)

            # stream:
            # async for chunk in (await llm.astream(messages))

            # batch:
            # await llm.abatch([messages])

        .. code-block:: python

            # TODO: Example output.

    # TODO: Delete if .bind_tools() isn't supported.
    Tool calling:
        .. code-block:: python

            from pydantic import BaseModel, Field

            class GetWeather(BaseModel):
                '''Get the current weather in a given location'''

                location: str = Field(..., description="The city and state, e.g. San Francisco, CA")

            class GetPopulation(BaseModel):
                '''Get the current population in a given location'''

                location: str = Field(..., description="The city and state, e.g. San Francisco, CA")

            llm_with_tools = llm.bind_tools([GetWeather, GetPopulation])
            ai_msg = llm_with_tools.invoke("Which city is hotter today and which is bigger: LA or NY?")
            ai_msg.tool_calls

        .. code-block:: python

              # TODO: Example output.

        See ``ChatDigitalOcean.bind_tools()`` method for more.

    # TODO: Delete if .with_structured_output() isn't supported.
    Structured output:
        .. code-block:: python

            from typing import Optional

            from pydantic import BaseModel, Field

            class Joke(BaseModel):
                '''Joke to tell user.'''

                setup: str = Field(description="The setup of the joke")
                punchline: str = Field(description="The punchline to the joke")
                rating: Optional[int] = Field(description="How funny the joke is, from 1 to 10")

            structured_llm = llm.with_structured_output(Joke)
            structured_llm.invoke("Tell me a joke about cats")

        .. code-block:: python

            # TODO: Example output.

        See ``ChatDigitalOcean.with_structured_output()`` for more.

    # TODO: Delete if JSON mode response format isn't supported.
    JSON mode:
        .. code-block:: python

            # TODO: Replace with appropriate bind arg.
            json_llm = llm.bind(response_format={"type": "json_object"})
            ai_msg = json_llm.invoke("Return a JSON object with key 'random_ints' and a value of 10 random ints in [0-99]")
            ai_msg.content

        .. code-block:: python

            # TODO: Example output.

    # TODO: Delete if image inputs aren't supported.
    Image input:
        .. code-block:: python

            import base64
            import httpx
            from langchain_core.messages import HumanMessage

            image_url = "https://upload.wikimedia.org/wikipedia/commons/thumb/d/dd/Gfp-wisconsin-madison-the-nature-boardwalk.jpg/2560px-Gfp-wisconsin-madison-the-nature-boardwalk.jpg"
            image_data = base64.b64encode(httpx.get(image_url).content).decode("utf-8")
            # TODO: Replace with appropriate message content format.
            message = HumanMessage(
                content=[
                    {"type": "text", "text": "describe the weather in this image"},
                    {
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image_data}"},
                    },
                ],
            )
            ai_msg = llm.invoke([message])
            ai_msg.content

        .. code-block:: python

            # TODO: Example output.

    # TODO: Delete if audio inputs aren't supported.
    Audio input:
        .. code-block:: python

            # TODO: Example input

        .. code-block:: python

            # TODO: Example output

    # TODO: Delete if video inputs aren't supported.
    Video input:
        .. code-block:: python

            # TODO: Example input

        .. code-block:: python

            # TODO: Example output

    # TODO: Delete if token usage metadata isn't supported.
    Token usage:
        .. code-block:: python

            ai_msg = llm.invoke(messages)
            ai_msg.usage_metadata

        .. code-block:: python

            {'input_tokens': 28, 'output_tokens': 5, 'total_tokens': 33}

    # TODO: Delete if logprobs aren't supported.
    Logprobs:
        .. code-block:: python

            # TODO: Replace with appropriate bind arg.
            logprobs_llm = llm.bind(logprobs=True)
            ai_msg = logprobs_llm.invoke(messages)
            ai_msg.response_metadata["logprobs"]

        .. code-block:: python

              # TODO: Example output.

    Response metadata
        .. code-block:: python

            ai_msg = llm.invoke(messages)
            ai_msg.response_metadata

        .. code-block:: python

             # TODO: Example output.

    """  # noqa: E501

    model_name: str = Field(alias="model")
    """The name of the model"""
    buffer_length: int
    """The number of characters from the last message of the prompt to be echoed."""
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    timeout: Optional[int] = None
    stop: Optional[List[str]] = None
    max_retries: int = 2

    @property
    def _llm_type(self) -> str:
        """Return type of chat model."""
        return "chat-digitalocean"

    @property
    def _identifying_params(self) -> Dict[str, Any]:
        """Return a dictionary of identifying parameters.

        This information is used by the LangChain callback system, which
        is used for tracing purposes make it possible to monitor LLMs.
        """
        return {
            # The model name allows users to specify custom token counting
            # rules in LLM monitoring applications (e.g., in LangSmith users
            # can provide per token pricing for their model and monitor
            # costs for the given LLM.)
            "model_name": self.model_name,
        }

    def _get_api_key(self):
        return getattr(self, "api_key", None) or os.environ.get("DIGITALOCEAN_MODEL_ACCESS_KEY")

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        api_key = self._get_api_key()
        if not api_key:
            raise ValueError("DigitalOcean API key not provided. Set DIGITALOCEAN_MODEL_ACCESS_KEY env var or pass api_key param.")

        url = "https://inference.do-ai.run/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        # Convert LangChain messages to OpenAI-style messages
        def convert_message(msg):
            if hasattr(msg, "type"):
                role = {"human": "user", "ai": "assistant", "system": "system"}.get(msg.type, msg.type)
            else:
                role = getattr(msg, "role", "user")
            return {"role": role, "content": msg.content}

        payload = {
            "model": self.model_name,
            "messages": [convert_message(m) for m in messages],
        }
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens
        if stop is not None:
            payload["stop"] = stop

        timeout = self.timeout or 30

        for attempt in range(self.max_retries):
            try:
                response = httpx.post(url, headers=headers, json=payload, timeout=timeout)
                response.raise_for_status()
                data = response.json()
                choice = data["choices"][0]
                content = choice["message"]["content"]
                usage = data.get("usage", {})
                message = AIMessage(
                    content=content,
                    additional_kwargs={},
                    response_metadata={"finish_reason": choice.get("finish_reason")},
                    usage_metadata={
                        "input_tokens": usage.get("prompt_tokens"),
                        "output_tokens": usage.get("completion_tokens"),
                        "total_tokens": usage.get("total_tokens"),
                    },
                )
                generation = ChatGeneration(message=message)
                return ChatResult(generations=[generation])
            except Exception as e:
                if attempt == self.max_retries - 1:
                    raise

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGenerationChunk]:
        """Stream the output of the model using the DigitalOcean API with streaming enabled."""
        api_key = self._get_api_key()
        if not api_key:
            raise ValueError("DigitalOcean API key not provided. Set DIGITALOCEAN_MODEL_ACCESS_KEY env var or pass api_key param.")

        url = "https://inference.do-ai.run/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        }

        def convert_message(msg):
            if hasattr(msg, "type"):
                role = {"human": "user", "ai": "assistant", "system": "system"}.get(msg.type, msg.type)
            else:
                role = getattr(msg, "role", "user")
            return {"role": role, "content": msg.content}

        payload = {
            "model": self.model_name,
            "messages": [convert_message(m) for m in messages],
            "stream": True,  # Enable streaming
        }
        if self.temperature is not None:
            payload["temperature"] = self.temperature
        if self.max_tokens is not None:
            payload["max_tokens"] = self.max_tokens
        if stop is not None:
            payload["stop"] = stop

        timeout = self.timeout or 30

        with httpx.stream("POST", url, headers=headers, json=payload, timeout=timeout) as response:
            response.raise_for_status()
            for line in response.iter_lines():
                if not line:
                    continue
                # The API may send lines like: 'data: { ... }' or 'data: [DONE]'
                if line.strip() == "data: [DONE]":
                    break
                if line.startswith("data:"):
                    line = line[len("data:"):].strip()
                try:
                    data = httpx.Response(200, content=line).json()
                except Exception:
                    continue
                # Parse the streamed chunk
                choice = data.get("choices", [{}])[0]
                delta = choice.get("delta", {})
                content = delta.get("content", "")
                if content:
                    chunk = ChatGenerationChunk(
                        message=AIMessageChunk(content=content)
                    )
                    if run_manager:
                        run_manager.on_llm_new_token(content, chunk=chunk)
                    yield chunk
            # Optionally, handle usage metadata at the end if provided
            # (You may need to adjust this depending on the API's final message)

    # TODO: Implement if ChatDigitalOcean supports async streaming. Otherwise delete.
    # async def _astream(
    #     self,
    #     messages: List[BaseMessage],
    #     stop: Optional[List[str]] = None,
    #     run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
    #     **kwargs: Any,
    # ) -> AsyncIterator[ChatGenerationChunk]:

    # TODO: Implement if ChatDigitalOcean supports async generation. Otherwise delete.
    # async def _agenerate(
    #     self,
    #     messages: List[BaseMessage],
    #     stop: Optional[List[str]] = None,
    #     run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
    #     **kwargs: Any,
    # ) -> ChatResult:

    @property
    def init_from_env_params(self):
        # env_vars, model_params, expected_attrs
        # Map DIGITALOCEAN_MODEL_ACCESS_KEY -> api_key, and require model param
        return (
            {"DIGITALOCEAN_MODEL_ACCESS_KEY": "test-env-key"},
            {"model": "bird-brain-001", "buffer_length": 50},
            {"api_key": "test-env-key", "model_name": "bird-brain-001"},
        )

    @classmethod
    def is_lc_serializable(cls):
        return True

    def __getstate__(self):
        state = self.__dict__.copy()
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
