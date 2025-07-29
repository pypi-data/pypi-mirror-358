# langchain-digitalocean

This package contains the LangChain integration with Digitalocean

## Installation

```bash
pip install -U langchain-digitalocean
```

And you should configure credentials by setting the following environment variables:

export DIGITALOCEAN_MODEL_ACCESS_KEY=<DigitalOcean_Model_Access_Key>

## Chat Models

`ChatDigitalocean` class exposes chat models from langchain-digitalocean.

### Invoke

```python
from langchain_digitalocean import ChatDigitalocean

llm = ChatDigitalocean(
    model="llama3.3-70b-instruct",
    api_key=os.getenv("DIGITALOCEAN_MODEL_ACCESS_KEY")
)

result = llm.invoke("What is the capital of France?.")
print(result)
```

### Stream

```python
from langchain_digitalocean import ChatDigitalocean

llm = ChatDigitalocean(
    model="llama3.3-70b-instruct",
    api_key=os.getenv("DIGITALOCEAN_MODEL_ACCESS_KEY")
)

for chunk in llm.stream("Tell me what happened to the Dinosaurs?"):
    print(chunk.content, end="", flush=True)

```

More features coming soon.