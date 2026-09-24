# Threat model

- **Policy substitution:** policy content is stored and hashed at creation.
- **Evidence drift:** every validator recomputes and agrees on the evidence digest.
- **Prompt injection:** evidence is supplied as data to the prompt and never as executable instructions.
- **Replay/finalization:** an accepted policy cannot be evaluated again.
- **Source trust:** callers must use authoritative HTTPS sources and independently audit them.
