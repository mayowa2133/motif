#!/usr/bin/env python3
"""Local, opt-in experiment decisions. Standard library only; never changes production."""
import argparse
import copy
import hashlib
import json
import re
from pathlib import Path

GUARDS = {"clarity", "factual_causality", "mascot_style", "phone_readability",
          "contact", "technical_reliability"}
VERDICTS = {"positive", "negative", "inconclusive", "unassessed"}
SHA = re.compile(r"[0-9a-f]{64}\Z")


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False).encode()).hexdigest()


def valid_sha(value):
    return isinstance(value, str) and bool(SHA.fullmatch(value))


def load(path):
    return json.loads(Path(path).read_text())


def save(path, value):
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(path.name + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")
    temporary.replace(path)


def verify_ref(root, ref, expected=None):
    """Only explicitly named evidence files, contained within the allocated evidence root."""
    if not isinstance(ref, dict) or not valid_sha(ref.get("sha256")):
        raise ValueError("missing evidence hash")
    if not isinstance(ref.get("path"), str):
        raise ValueError("missing evidence path")
    relative = Path(ref["path"])
    if relative.is_absolute() or ".." in relative.parts or not relative.parts:
        raise ValueError("evidence path must be relative and contained")
    root = Path(root).resolve()
    path = (root / relative).resolve()
    if not path.is_relative_to(root) or not path.is_file():
        raise ValueError("missing or escaped evidence file: " + str(relative))
    if expected is not None and ref["sha256"] != expected:
        raise ValueError("evidence identity mismatch: " + str(relative))
    actual = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            actual.update(block)
    if actual.hexdigest() != ref["sha256"]:
        raise ValueError("stale evidence: " + str(relative))
    return path


def validate_registry(registry, policy):
    if registry.get("schema_version") != 1 or policy.get("schema_version") != 1:
        raise ValueError("unsupported registry or policy version")
    if set(policy["criteria"]) != GUARDS:
        raise ValueError("all six guardrails are required")
    candidates = registry["candidates"]
    if len({c["id"] for c in candidates}) != len(candidates):
        raise ValueError("duplicate candidate IDs")
    for candidate in candidates:
        if candidate.get("verdict") not in VERDICTS:
            raise ValueError("invalid candidate verdict")
        for key in ("evidence_scope", "baseline_sha256", "artifact_sha256",
                    "component_sha256", "known_regressions", "dependencies",
                    "rollback_target", "evidence", "eligible_scopes", "optional", "effect_domains"):
            if key not in candidate:
                raise ValueError(candidate["id"] + ": missing " + key)
    return {c["id"]: c for c in candidates}


def eligibility(candidate, scope):
    reasons = []
    if candidate["optional"] is not True:
        reasons.append("candidate must be optional")
    if candidate["verdict"] != "positive":
        reasons.append("verdict is " + candidate["verdict"])
    if scope not in candidate["eligible_scopes"]:
        reasons.append("evidence does not support this scope")
    for key in ("baseline_sha256", "artifact_sha256", "component_sha256"):
        if not valid_sha(candidate[key]):
            reasons.append("missing exact " + key)
    if not candidate["evidence"] or any(not valid_sha(e.get("sha256"))
                                          for e in candidate["evidence"]):
        reasons.append("missing hashed research evidence")
    if not candidate["rollback_target"]:
        reasons.append("missing rollback target")
    if any(scope in r.get("scopes", [scope]) for r in candidate["known_regressions"]):
        reasons.append("known regression applies in this scope")
    return reasons


def plan_trial(registry, policy, context, previous=None, requested=(), blocked=()):
    """Freeze a single incremental stage. Empty requests retain current behavior."""
    candidates = validate_registry(registry, policy)
    previous = copy.deepcopy(previous or {
        "artifact_sha256": context.get("baseline_artifact_sha256"), "enabled": []})
    trial = {"schema_version": 1, "context": copy.deepcopy(context),
             "registry_sha256": digest(registry), "policy_sha256": digest(policy),
             "previous": previous, "enabled": copy.deepcopy(previous["enabled"]),
             "addition": None, "ready": False, "rejections": [],
             "blocked_combination_keys": sorted(b["combination_sha256"] for b in blocked)}
    scope = context.get("scope")
    if scope not in policy["scopes"]:
        trial["rejections"].append("unknown trial scope")
    for field in ("brief_sha256", "baseline_artifact_sha256"):
        if not valid_sha(context.get(field)):
            trial["rejections"].append("missing same-brief " + field)
    commit = context.get("baseline_git_commit")
    if not isinstance(commit, str) or not re.fullmatch(r"[0-9a-f]{40}", commit):
        trial["rejections"].append("missing baseline Git commit")
    if not valid_sha(previous.get("artifact_sha256")):
        trial["rejections"].append("missing last-good artifact")
    if not context.get("claims") or any(c not in policy["claims"]
                                        for c in context.get("claims", [])):
        trial["rejections"].append("missing or unsupported claim scope")
    prior_ids = [v["id"] for v in previous["enabled"]]
    if len(set(prior_ids)) != len(prior_ids):
        trial["rejections"].append("duplicate last-good candidate")
    for version in previous["enabled"]:
        candidate = candidates.get(version["id"])
        if not candidate or candidate["component_sha256"] != version["component_sha256"]:
            trial["rejections"].append("last-good version is not in frozen registry")
        elif (scope not in candidate["eligible_scopes"]
              or not set(candidate["effect_domains"]).issubset(set(context.get("claims", [])))):
            trial["rejections"].append("last-good candidate cannot be expanded into this scope")
    requested = list(requested)
    if len(requested) != len(set(requested)) or len(requested) > 1:
        trial["rejections"].append("add at most one candidate per stage")
    for candidate_id in requested:
        candidate = candidates.get(candidate_id)
        if not candidate:
            trial["rejections"].append("unknown candidate: " + candidate_id)
            continue
        trial["rejections"].extend(candidate_id + ": " + r
                                   for r in eligibility(candidate, scope))
        if candidate_id in prior_ids:
            trial["rejections"].append("candidate is already enabled")
        if not set(candidate["dependencies"]).issubset(set(prior_ids)):
            trial["rejections"].append(candidate_id + ": missing accepted dependency")
        if not set(candidate["effect_domains"]).issubset(set(context.get("claims", []))):
            trial["rejections"].append(candidate_id + ": declared effects exceed trial claim/evidence scope")
    if requested and not trial["rejections"]:
        candidate = candidates[requested[0]]
        proposed = trial["enabled"] + [{"id": candidate["id"],
                                        "component_sha256": candidate["component_sha256"]}]
        key = digest({"context": context, "enabled": proposed})
        if key in trial["blocked_combination_keys"]:
            trial["rejections"].append("this exact combination/context has a recorded hard regression")
        else:
            trial["addition"] = candidate["id"]
            trial["enabled"] = proposed
            trial["ready"] = True
    trial["status"] = "ready_for_trial" if trial["ready"] else "no_ready_addition"
    return trial


def complete_absence_coverage(trial, check, report_path, target_sha, trial_sha):
    event = trial["context"].get("events", {}).get(check.get("absence_event"))
    if not event:
        return False
    report = load(report_path)
    report = report.get("event_coverage", {}).get(check.get("absence_event"), report)
    if (report.get("complete_review") is not True
            or report.get("baseline_artifact_sha256") != target_sha
            or report.get("trial_artifact_sha256") != trial_sha):
        return False
    for arm in ("baseline", "trial"):
        bounds = event.get(arm)
        if (not isinstance(bounds, list) or len(bounds) != 2
                or not all(type(v) is int and v >= 0 for v in bounds)
                or bounds[1] < bounds[0]
                or report.get(arm + "_frame_indices") != list(range(bounds[0], bounds[1] + 1))):
            return False
    return True


def assess_trial(registry, policy, trial, result, evidence_root):
    candidates = validate_registry(registry, policy)
    decision = {"trial_sha256": digest(trial), "result_sha256": digest(result),
                "action": "hold", "verdict": "unassessed", "reasons": [],
                "promotion_ready": False, "accepted_scope": None,
                "rollback_target": copy.deepcopy(trial["previous"])}
    reasons = decision["reasons"]
    if not trial.get("ready"):
        reasons.append("trial has no eligible addition")
        return decision
    if (trial["registry_sha256"] != digest(registry)
            or trial["policy_sha256"] != digest(policy)
            or result.get("trial_sha256") != digest(trial)):
        reasons.append("preregistered registry, criteria or trial changed")
        return decision
    # Recompute the plan rather than trusting caller-supplied 'ready' or enabled flags.
    if plan_trial(registry, policy, trial["context"], trial["previous"],
                  [trial["addition"]], [{"combination_sha256": k}
                                       for k in trial["blocked_combination_keys"]]) != trial:
        reasons.append("trial is not the reproducible eligible plan")
        return decision
    context = trial["context"]
    artifacts = result.get("artifacts", {})
    try:
        verify_ref(evidence_root, artifacts.get("brief"), context["brief_sha256"])
        verify_ref(evidence_root, artifacts.get("original"), context["baseline_artifact_sha256"])
        verify_ref(evidence_root, artifacts.get("previous"), trial["previous"]["artifact_sha256"])
        verify_ref(evidence_root, artifacts.get("trial"))
        for version in trial["enabled"]:
            verify_ref(evidence_root, artifacts.get("components", {}).get(version["id"]),
                       version["component_sha256"])
        for entry in candidates[trial["addition"]]["evidence"]:
            verify_ref(evidence_root, result.get("research_evidence", {}).get(entry["sha256"]),
                       entry["sha256"])
    except (ValueError, OSError) as error:
        reasons.append(str(error))
        return decision
    output_sha = artifacts["trial"]["sha256"]
    targets = {context["baseline_artifact_sha256"], trial["previous"]["artifact_sha256"]}
    comparisons = result.get("comparisons", [])
    incomplete = False
    if len(comparisons) != len(targets) or {c.get("against_sha256") for c in comparisons} != targets:
        reasons.append("must compare with both original and last good")
        incomplete = True
    uncertain = False
    playback_required = bool(set(context["claims"]) & {"timing", "motion", "audio"})
    hard_regressions = []
    for comparison in comparisons:
        target = comparison["against_sha256"]
        if target not in targets:
            continue
        checks = comparison.get("checks", {})
        if set(checks) != GUARDS:
            reasons.append("all six criteria required against " + target)
            incomplete = True
        improved = False
        for criterion, check in sorted(checks.items()):
            if criterion not in GUARDS:
                incomplete = True
                continue
            relation = check.get("result")
            if relation not in {"improved", "unchanged", "regressed", "inconclusive", "unassessed"}:
                incomplete = True
                reasons.append("invalid assessment: " + criterion)
                continue
            try:
                report_path = verify_ref(evidence_root, check.get("report"))
                report = load(report_path)
                recorded = {k: v for k, v in check.items() if k != "report"}
                if (report.get("trial_sha256") != digest(trial)
                        or report.get("against_sha256") != target
                        or report.get("trial_artifact_sha256") != output_sha
                        or report.get("criteria", {}).get(criterion) != recorded):
                    raise ValueError("review report is not bound to this frozen trial/pair/assessment")
                for supporting in check.get("supporting_evidence", []):
                    verify_ref(evidence_root, supporting)
            except (ValueError, OSError) as error:
                incomplete = True
                reasons.append(criterion + ": " + str(error))
                continue
            kind = check.get("kind")
            playback_required = playback_required or kind == "full_speed_playback"
            permitted = policy["scopes"][context["scope"]][criterion]
            if kind == "byte_identity":
                supported = (target == output_sha and relation == "unchanged"
                             and context.get("artifact_type") in {"encoded_picture", "encoded_av"}
                             and set(context["claims"]).issubset({"output_preserving_refactor", "reliability"}))
            else:
                supported = kind in permitted
            if not supported or not check.get("observation"):
                incomplete = True
                reasons.append(criterion + ": evidence kind or observation inadequate")
                continue
            if (check.get("finding_type") == "absence" or check.get("absence_event")) and not complete_absence_coverage(
                    trial, check, report_path, target, output_sha):
                uncertain = True
                reasons.append(criterion + ": absence interval not completely reviewed")
                continue
            if check.get("reviewer_disagreement") is True:
                uncertain = True
                reasons.append(criterion + ": reviewer disagreement")
                continue
            if (criterion == "contact" and relation in {"improved", "unchanged"}
                    and context["scope"] in {"production", "output_preserving_refactor"}
                    and kind == "continuous_event_interval"):
                events = context.get("events", {})
                if not events or not all(complete_absence_coverage(
                        trial, {"absence_event": event}, report_path, target, output_sha)
                        for event in events):
                    incomplete = True
                    reasons.append("contact: complete preregistered event coverage required")
                    continue
            if relation == "regressed":
                if (check.get("reproduced") is True
                        and check.get("finding_type") in {"observed", "absence"}):
                    hard_regressions.append({"criterion": criterion, "against_sha256": target,
                                             "evidence": check["report"], "observation": check["observation"]})
                else:
                    uncertain = True
                    reasons.append(criterion + ": regression type or reproduction not established")
            elif relation in {"inconclusive", "unassessed"}:
                uncertain = True
                reasons.append(criterion + ": " + relation)
            elif relation == "improved":
                improved = True
        if not improved:
            uncertain = True
            reasons.append("no incremental demonstrated gain against " + target)
    if hard_regressions:
        decision.update(action="rollback", verdict="negative", regressions=hard_regressions)
        reasons.append("reproducible hard regression; restore last good in this combination")
        return decision
    # Stills and dense frame strips never certify playback, audio or timing quality.
    if playback_required:
        playback = result.get("playback", {})
        try:
            path = verify_ref(evidence_root, playback.get("report"))
            report = load(path)
            if (report.get("trial_sha256") != digest(trial)
                    or report.get("full_speed_picture_watched") is not True
                    or report.get("audio_listened") is not True
                    or set(report.get("artifact_sha256", [])) != targets | {output_sha}):
                raise ValueError("playback report lacks complete paired picture/listening coverage")
        except (ValueError, OSError) as error:
            incomplete = True
            reasons.append("timing/motion/audio claim: " + str(error))
    if incomplete or uncertain:
        decision["verdict"] = "unassessed" if incomplete else "inconclusive"
        return decision
    decision.update(action="accept_in_trial", verdict="positive", accepted_scope=context["scope"],
                    promotion_ready=context["scope"] in {"production", "output_preserving_refactor"})
    return decision


def apply_decision(state, trial, result, decision):
    """Write-ready state transition. Logs exact versions; no deletion or Git operation."""
    if decision["trial_sha256"] != digest(trial) or decision["result_sha256"] != digest(result):
        raise ValueError("decision is not bound to trial/result")
    event_id = digest({"trial": trial, "result": result, "decision": decision})
    if any(e["event_id"] == event_id for e in state.get("history", [])):
        return copy.deepcopy(state)
    if state["last_good"] != trial["previous"]:
        raise ValueError("state changed since trial was declared")
    output = copy.deepcopy(state)
    if decision["action"] == "accept_in_trial":
        output["last_good"] = {"artifact_sha256": result["artifacts"]["trial"]["sha256"],
                               "enabled": copy.deepcopy(trial["enabled"]), "accepted_trial_sha256": digest(trial)}
    output["active"] = copy.deepcopy(output["last_good"])
    event = {"event_id": event_id, "decision": decision, "enabled_versions": trial["enabled"],
             "addition": trial["addition"], "original_artifact_sha256": trial["context"].get("baseline_artifact_sha256"),
             "previous": trial["previous"], "tested_artifact": result.get("artifacts", {}).get("trial"),
             "registry_sha256": trial["registry_sha256"], "policy_sha256": trial["policy_sha256"]}
    output.setdefault("history", []).append(copy.deepcopy(event))
    # A negative verdict belongs to this exact combination/brief; candidate records survive.
    if decision["action"] == "rollback":
        output.setdefault("blocked_combinations", []).append(copy.deepcopy({"event_id": event_id,
            "brief_sha256": trial["context"]["brief_sha256"], "enabled": trial["enabled"],
            "combination_sha256": digest({"context": trial["context"], "enabled": trial["enabled"]}),
            "regressions": decision["regressions"]}))
    return output


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=["plan", "assess"])
    for name in ("registry", "policy", "output"):
        parser.add_argument("--" + name, required=True)
    for name in ("context", "state", "state-out", "trial", "result", "evidence-root"):
        parser.add_argument("--" + name)
    parser.add_argument("--candidate", action="append", default=[])
    args = parser.parse_args()
    registry, policy = load(args.registry), load(args.policy)
    state = load(args.state) if args.state else None
    if args.command == "plan":
        if not args.context:
            parser.error("plan requires --context")
        outcome = plan_trial(registry, policy, load(args.context),
                             state["last_good"] if state else None, args.candidate,
                             state.get("blocked_combinations", []) if state else [])
    else:
        if not all((args.trial, args.result, args.evidence_root)):
            parser.error("assess requires --trial, --result and --evidence-root")
        trial, result = load(args.trial), load(args.result)
        outcome = assess_trial(registry, policy, trial, result, args.evidence_root)
        if args.state_out:
            if not state:
                parser.error("--state-out requires --state")
            save(args.state_out, apply_decision(state, trial, result, outcome))
    save(args.output, outcome)
    print(json.dumps({k: outcome[k] for k in ("status", "action", "verdict", "reasons", "rejections")
                      if k in outcome}, sort_keys=True))


if __name__ == "__main__":
    main()
