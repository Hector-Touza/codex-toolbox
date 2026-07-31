---
name: app-qa
description: Run a native three-critic quality-assurance workflow on an app, site, dashboard, page, interactive tool, or product feature, then consolidate feedback, rework the artifact, and re-check it. Use when the user asks to build or change an app and requests QA, quality review, self-review, critique, polish, validation with app-QA, or independent agents to assess the result.
---

# App QA

Run quality assurance as a bounded native multi-agent workflow. Treat QA as broader than formal correctness: assess whether the work is useful, coherent, clear, polished, resilient, and faithful to the user's intent. Use objective checks when they illuminate quality, but do not reduce the workflow to tests alone.

Keep the main thread accountable for the artifact and the final judgment. Critics supply independent perspectives; they do not replace the main thread's understanding.

## Execution topology gate

Run this workflow only from a first-class user-created Work thread.

Before implementation or QA begins, verify all of the following:

- the current thread is the top-level conversation the user opened;
- the current thread, not a delegated agent, will implement, edit, test, adjudicate, deploy, and report;
- the three required critics can be created as direct children of the current thread.

Do not spawn an implementation, coordinator, or QA-orchestrator subagent. Do not run the workflow from a task-details subagent or create a nested implementation layer. Critics must remain leaf reviewers and must not spawn their own agents.

If the current context is a subagent, or direct-child topology cannot be established with confidence, stop before changing the artifact and return:

`APP_QA_REQUIRES_FIRST_CLASS_THREAD`

Ask the user to open a fresh Work chat and invoke `app-qa` there. Never silently continue with a nested substitute.

## Required critics

Run exactly these three independent critics:

1. **Product & Intent Critic**
   Assess requirement fidelity, target-user value, scope, domain coherence, assumptions, missing capabilities, contradictions, and whether the result solves the intended problem.
2. **Experience & Communication Critic**
   Assess usability, interaction flow, information hierarchy, visual quality, copy, discoverability, accessibility, responsive behavior, and loading, empty, error, and edge states. For a visual app or site, inspect the rendered experience instead of reviewing source alone.
3. **Engineering & Operational Critic**
   Assess architecture, maintainability, state and data integrity, error handling, runtime behavior, performance, security appropriate to scope, regressions, and the adequacy of focused checks.

Read [references/critic-prompts.md](references/critic-prompts.md) before spawning the critics.

## Workflow

### 1. Establish the quality brief

Before review, write a compact brief containing:

- the user's intended outcome and target user;
- the artifact and scope being reviewed;
- non-negotiable requirements and constraints;
- important qualitative aspirations such as simplicity, clarity, credibility, or visual polish;
- how to run or inspect the result;
- known uncertainties, without defending implementation choices.

Build or finish a coherent candidate before launching QA. Do not make critics review a half-written artifact unless the user explicitly asks for an early design review.

### 2. Prepare independent review packets

Give every critic the original request, the quality brief, the reviewable artifact or exact changed-file scope, and run/inspection instructions.

Do not include:

- the main thread's self-assessment;
- another critic's findings;
- persuasive implementation rationale that could anchor the reviewer;
- instructions to edit files.

Critics are read-only. The main thread remains the sole editor. Spawn the three critics as fresh direct-child threads of the current first-class thread, in parallel when capacity permits. Record their thread identities so re-checks return to those same critics. If capacity requires sequential execution, keep their contexts independent and never reveal earlier findings.

### 3. Require actionable findings

Each critic must return:

- a one-paragraph overall assessment;
- the strongest qualities worth preserving;
- a short, prioritized set of findings;
- questions or uncertainties that materially affect the judgment.

Every finding must include:

- stable ID;
- severity: `blocker`, `high`, `medium`, or `low`;
- concrete evidence and location;
- the quality expectation at stake;
- recommended action or design direction;
- confidence: `high`, `medium`, or `low`.

Critics may make qualitative judgments, but must ground them in something observable. They must distinguish a defect, a risk, and a preference. Avoid generic praise, style trivia, speculative feature wish lists, and unsupported claims.

### 4. Consolidate without delegating understanding

The main thread must read the artifact and every finding itself. Deduplicate related findings, preserve meaningful disagreement, and assign each item one disposition:

- **Accept** — incorporate it now.
- **Reject** — explain why it does not improve the stated goal or is based on incorrect evidence.
- **Defer** — useful but outside the present scope; name the tradeoff.

Do not decide by majority vote and do not paste critic output directly into the final answer. Investigate material disagreements. Prioritize blockers and high-impact improvements, but keep valuable qualities that the critics identified.

### 5. Rework and re-check

Have the main thread implement accepted changes. Then send the relevant original critic thread a focused follow-up containing:

- the accepted finding IDs;
- the changed artifact or diff;
- the specific question to re-check.

Do not spawn replacement critics for re-checks and do not delegate rework.

Use at most two rework/re-check cycles unless the user asks for more. Run final checks appropriate to the artifact. If a blocker or high-severity concern remains, disclose it instead of claiming that QA passed.

### 6. Preserve detail in a findings report

Create one Markdown artifact named `app-qa-findings.md`. Save it to the user's persistent file surface when available and link it from the final response.

Include:

- the quality brief and reviewed scope;
- first-class thread and direct-child critic topology;
- each critic's assessment and preserved strengths;
- every deduplicated finding with ID, evidence, confidence, severity, disposition, rationale, rework, and re-check outcome;
- validation evidence and open risks.

Map severities in user-facing output as:

- `P0` = blocker;
- `P1` = high;
- `P2` = medium;
- `P3` = low.

### 7. Return a lean final response

Keep the main thread's final response screenshot-friendly: no process narration, critic biographies, topology explanation, long prose, or duplicated findings. Use exactly this structure:

```markdown
Implemented
- [two to five minimal feature bullets]

Deployment: [production URL and access state, when applicable]
Validations: [short dot-separated list of checks actually run]
QA findings: [P0/P1/P2/P3 counts; always show P0, omit trailing zero categories]
Accepted and implemented: [count] · Rejected: [count] · Deferred: [count]
Findings report: [app-qa-findings.md](...)
```

Add one final `Open risks:` line only when a material limitation remains. Do not claim validation or re-check coverage that did not occur. If a critic could not run or inspect required evidence, state that on the `Validations` or `Open risks` line. Do not use “QA passed” when unresolved P0 or P1 findings remain.

## Boundaries

- Do not let parallel critics edit shared files.
- Do not let critics spawn further agents.
- Do not move implementation, adjudication, rework, testing, deployment, or the final report out of the first-class thread.
- Do not expand the product merely because a critic suggested an attractive unrelated feature.
- Do not mistake more feedback for better feedback; favor a few consequential findings.
- Do not imply formal verification, medical validity, security certification, or production readiness unless the task and evidence justify those claims.
- If the artifact is not visual, adapt the Experience & Communication Critic to the relevant interaction or communication surface rather than inventing UI issues.
