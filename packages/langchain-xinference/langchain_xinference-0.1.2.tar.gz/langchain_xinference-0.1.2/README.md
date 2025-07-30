# 💻 langchain-xinference

This package contains the LangChain integration with Xinference

## 🤝 Support

- [x] Chat
- [x] Generate
- [x] Embeddings
- [x] Reranks
- [x] Tools Call

## 🚀 Installation

```bash
pip install -U langchain-xinference
```

## ☕ Chat Models

`ChatXinference` class exposes chat models from Xinference.

```python
from langchain_xinference.chat_models import ChatXinference
from langchain.prompts import PromptTemplate

llm = ChatXinference(
  server_url="http://0.0.0.0:9997",  # replace your xinference server url
  model_uid={model_uid}  # replace model_uid with the model UID return from launching the model
         )
prompt = PromptTemplate(input=["country"], template="Q: where can we visit in the capital of {country}? A:")
chain = prompt | llm

chain.invoke(input={"country": "France"})

ai_res = chain.stream(input={"country": "France"})
for chunk in ai_res:
    print(chunk.content)
```

## ☕ Generate
`Xinference` class exposes LLMs from Xinference.

```python
from langchain_xinference.llms import Xinference
from langchain.prompts import PromptTemplate

llm = Xinference(
    server_url="http://0.0.0.0:9997",  # replace your xinference server url
    model_uid={model_uid}  # replace model_uid with the model UID return from launching the model
 )
prompt = PromptTemplate(input=["country"], template="Q: where can we visit in the capital of {country}? A:")
chain = prompt | llm
chain.invoke(input={"country": "France"})

ai_res = chain.stream(input={"country": "France"})
for chunk in ai_res:
    print(chunk)
```
