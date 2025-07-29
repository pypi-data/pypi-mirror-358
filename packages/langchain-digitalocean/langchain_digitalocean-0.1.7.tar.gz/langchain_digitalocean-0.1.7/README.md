# langchain-digitalocean

This package contains the LangChain integration with Digitalocean

## Installation

```bash
pip install -U langchain-digitalocean
```

And you should configure credentials by setting the following environment variables:

DIGITALOCEAN_MODEL_ACCESS_KEY

## Chat Models

`ChatDigitalocean` class exposes chat models from LangchainDigitalocean.

```python
from langchain_digitalocean import ChatDigitalocean

llm = ChatDigitalocean(
    model="llama3.3-70b-instruct",
    api_key=os.getenv("DIGITALOCEAN_MODEL_ACCESS_KEY"),
    buffer_length=100
)
result = llm.invoke("What is the capital of France?.")
print(result)
```

```

More features coming soon.