# Troubleshooting Drills

Practice these as timed scenarios. The goal is to diagnose clearly and build debugging reflexes.

## Drill Format

1. State the symptom.
2. Ask one clarifying question.
3. Check the fastest likely cause.
4. Explain what you are doing out loud.
5. Apply the fix.
6. Summarize the takeaway.

## Drills

| Scenario | Practice Response |
| --- | --- |
| API key missing | Check environment variable, shell session, and credential name. |
| Wrong Python environment | Confirm interpreter, virtual environment, and installed packages. |
| Dependency install fails | Check package name, network, permissions, and version compatibility. |
| Model returns unsupported format | Inspect raw output, adjust prompt, add schema or parser guard. |
| RAG retrieves irrelevant chunks | Inspect query, chunk text, metadata, and similarity results. |
| Local app works, deployed app fails | Compare environment variables, runtime versions, network access, and logs. |
| Broad product question interrupts debugging | Record the question, finish the technical diagnosis, then return to product implications. |
| Tool-using agent loops | Stop execution, inspect state, add loop limit and clearer stopping condition. |

## Builder Angle

When discussing troubleshooting, emphasize:

- Calm process.
- Visible reasoning.
- Fast isolation of variables.
- Knowing when to use a workaround to preserve the experiment.
