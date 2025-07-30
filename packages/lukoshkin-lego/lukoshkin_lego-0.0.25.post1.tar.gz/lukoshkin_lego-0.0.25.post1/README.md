## Lego

Python utilities initially for ChatBot Development and Cloud Engineering.

## Structure

### The most useful parts

- lego/models.py - base for string enums and base for auto-conversion
  between `camelCase` and `snake_case` styles.
- lego/db - database connectors:
  - redis - async Redis JSON connector,
  - milvus - superb MilvusDB connector.
  - redshift - async calls to the Redshift DB.
- lego/utils/io.py - read/write op-s for JSON files.
- lego/utils/ttl.py - ttl utilities used in Redis and Milvus connectors.
- lego/llm/utils/json\_{compose,mediator}.py - interfaces to use in the
  calls to LLM to get structured response (the answer with JSON).
- lego/llm/utils/parse.py - parser functions for LLM responses;
  includes also streaming responses and responses with thinking blockes.
- lego/settings - settings for the DB connectors above (and more)

### The rest is a bit outdated and should move to `legacy` soon
