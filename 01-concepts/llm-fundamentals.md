# LLM Fundamentals

## Why This Matters

Explain what large language models are, how they behave, and why their strengths and limitations matter in real applications.

## Core Explanation

An LLM is a model trained to predict useful continuations of text based on patterns learned from large datasets. It does not retrieve truth by default. It generates responses from learned statistical structure plus the context you provide.

## Concepts To Know

- Tokens: chunks of text the model processes.
- Context window: the amount of input and output the model can consider at once.
- Inference: the process of generating an answer from a prompt.
- Temperature: a control that affects randomness and variety.
- System instructions: higher-priority guidance about behavior, role, and constraints.
- Hallucination: a confident output that is unsupported, wrong, or fabricated.
- Evaluation: testing whether model outputs meet task-specific quality standards.

## Engineering Explanation

Think of the model as a probabilistic text engine wrapped by an API. Your application controls the instructions, input data, tools, retrieval context, validation, and user experience around it.

## Product Explanation

An LLM can help draft, summarize, classify, transform, and reason over language-like information. It is powerful, but it needs clear instructions, good context, and checks for accuracy when decisions matter.

## Common Learner Confusions

- LLMs are not databases.
- More prompt text is not always better.
- Model confidence is not the same as correctness.
- Fine-tuning, RAG, and prompt engineering solve different problems.

## Explain It Back

Explain LLMs in 60 seconds to:

- A software engineer.
- A product manager.
- A curious non-technical friend.
