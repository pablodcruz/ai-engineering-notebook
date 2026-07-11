# Glossary

## AI And LLM Terms

- Agent: an application pattern where a model can choose tools or actions to complete a goal.
- Agent harness: the runtime around a model that manages context, tools, permissions, execution loops, and computer or service access.
- Chunking: splitting source documents into smaller pieces for retrieval.
- Context window: the amount of input and output a model can consider at once.
- Embedding: a numeric representation of text used for similarity search.
- Evaluation: measuring whether outputs meet expected quality, safety, and task requirements.
- Evaluation runner: a system that applies fixed inputs and checks to candidate outputs; unlike an agent harness, it does not give a model tools or computer access.
- Fine-tuning: training a model further on examples to shape behavior or task performance.
- Foundation model: a broadly trained model that can be adapted to many tasks.
- Grounding: providing source context so an answer is based on supplied information.
- Hallucination: an unsupported or false model output.
- Inference: generating an output from a model.
- Prompt: the instructions and input sent to a model.
- Prompt regression: a behavior that becomes worse after a prompt changes, detected by rerunning fixed evaluation cases.
- RAG: retrieval-augmented generation, a pattern that retrieves relevant context before generation.
- Temperature: a setting that influences output randomness.
- Token: a text unit processed by a model.
- Tool calling: allowing a model-driven app to request specific external functions.
- Vector database: a store optimized for similarity search over embeddings.
