# PolicyLatch

## Intelligent Contract

PolicyLatch is a reusable GenLayer primitive that snapshots a policy and turns independently fetched evidence into a consensus-backed `PASS`, `FAIL`, or `INDETERMINATE` decision. Validators compare the complete typed result and the SHA-256 digest of the evidence they independently fetched.

### Why GenLayer

`gl.nondet.web.render` and `gl.nondet.exec_prompt` handle evidence retrieval and semantic evaluation. `gl.vm.run_nondet_unsafe` rejects divergent decisions, reasoning, and evidence digests before state is finalized. Deterministic code owns policy snapshotting, schema validation, and one-time finalization.

### Public API

- `create_policy(policy_id, policy_text, source_url)` snapshots policy content and its digest.
- `evaluate(policy_id, evidence_url)` runs validator consensus and stores the final decision.
- `get_policy(policy_id)` returns the canonical record.
- `list_policy_ids()` lists registered policies.

### Verification

```bash
python -m py_compile contracts/policy_latch.py
```

This repository is an Intelligent Contract primitive, not medical, legal, financial, or safety advice.
