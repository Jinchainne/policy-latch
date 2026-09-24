"""PolicyLatch: consensus-backed semantic condition primitive."""
from genlayer import *
import hashlib
import json


class PolicyLatch(gl.Contract):
    policies: TreeMap[str, str]
    policy_ids: DynArray[str]

    def __init__(self):
        pass

    @gl.public.write
    def create_policy(self, policy_id: str, policy_text: str, source_url: str) -> None:
        key = policy_id.strip().upper()
        if not key or key in self.policies:
            raise gl.vm.UserError("Policy ID is invalid or already exists")
        text = policy_text.strip()
        if len(text) < 40 or len(text) > 4000:
            raise gl.vm.UserError("Policy text must be 40-4000 characters")
        if not source_url.startswith("https://"):
            raise gl.vm.UserError("Source must use HTTPS")
        record = {"id": key, "text": text, "source_url": source_url.strip(),
                  "policy_digest": hashlib.sha256(text.encode()).hexdigest(),
                  "state": "PENDING", "decision": "", "reasoning": "", "evidence_digest": ""}
        self.policies[key] = json.dumps(record, sort_keys=True, separators=(",", ":"))
        self.policy_ids.append(key)

    @gl.public.write
    def evaluate(self, policy_id: str, evidence_url: str) -> str:
        key = policy_id.strip().upper()
        raw = self.policies.get(key, "")
        if not raw:
            raise gl.vm.UserError("Policy not found")
        record = json.loads(raw)
        if record["state"] == "ACCEPTED":
            raise gl.vm.UserError("Policy is already finalized")

        def assess():
            evidence = str(gl.nondet.web.render(evidence_url, mode="text"))[:6000]
            if len(evidence.strip()) < 20:
                return {"decision": "INDETERMINATE", "reasoning": "Evidence was unavailable or too short.",
                        "evidence_digest": hashlib.sha256(evidence.encode()).hexdigest()}
            prompt = f"""Evaluate this policy against the evidence. Return JSON with exactly decision (PASS|FAIL|INDETERMINATE), reasoning (>=20 chars), evidence_digest (64 hex chars). Policy: {record['text']} Evidence: {evidence}"""
            result = gl.nondet.exec_prompt(prompt, response_format="json")
            if isinstance(result, str):
                result = json.loads(result)
            if set(result) != {"decision", "reasoning", "evidence_digest"}:
                raise gl.vm.UserError("Invalid decision schema")
            if result["decision"] not in ("PASS", "FAIL", "INDETERMINATE"):
                raise gl.vm.UserError("Invalid decision")
            if len(str(result["reasoning"]).strip()) < 20:
                raise gl.vm.UserError("Reasoning is too short")
            expected = hashlib.sha256(evidence.encode()).hexdigest()
            if result["evidence_digest"] != expected:
                raise gl.vm.UserError("Evidence digest does not match fetched evidence")
            return result

        def agree(leader_result):
            if not isinstance(leader_result, gl.vm.Return):
                return False
            validator = assess()
            leader = leader_result.calldata
            return leader == validator

        result = gl.vm.run_nondet_unsafe(assess, agree)
        record.update(state="ACCEPTED", decision=result["decision"], reasoning=result["reasoning"], evidence_digest=result["evidence_digest"])
        self.policies[key] = json.dumps(record, sort_keys=True, separators=(",", ":"))
        return result["decision"]

    @gl.public.view
    def get_policy(self, policy_id: str) -> str:
        return self.policies.get(policy_id.strip().upper(), "")

    @gl.public.view
    def list_policy_ids(self) -> list[str]:
        return [item for item in self.policy_ids]
