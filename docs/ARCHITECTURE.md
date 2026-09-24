# PolicyLatch architecture

Policy text is snapshotted and hashed before evaluation. The write path then fetches evidence and runs semantic evaluation inside `run_nondet_unsafe`. Deterministic validation rejects malformed schemas; validators compare the complete result and evidence digest. The finalized record is immutable through the public API.
