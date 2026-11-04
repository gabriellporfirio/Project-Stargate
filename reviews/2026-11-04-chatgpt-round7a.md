# StarGate round 7a review

Reviewed 4 November 2026. Line references below are to the supplied `Pasted text(5).txt` (R7, 124 lines). Baseline: [round 6](2026-11-04-chatgpt-round6.md). M5 checked against v2.2 at planning commit `6e96bff39c5b33fc6e066f5524779ebc012a8b37`.

Only the instruction attachment arrived for this round. The available five media files are the previous round's copies; no newer set was found. Consequently this review checks 8f's instructions, not their claimed completion. The 5l/5m results and the three new audit reports are also not supplied. No product task, CLI, build, device operation or live call was run.

| Item | Verdict |
|---|---|
| 1. 8f / media after Grok round 6 | 8f GO; revised media approval HOLD until the five actual files arrive. |
| 2m. Preflight | GO as a preliminary, read-only check. |
| 2n. Release audit | NO-GO as written for the merge probes and an unqualified release clearance; static, redacted inspection can continue. |
| 2o. Shot readiness | GO for static inspection; HOLD project CLI/replay execution until its source and write behaviour are checked. |
| 3. 8g submission draft | GO for a draft; the final submission still needs proof-state and owner checks. |
| 4. 5n live-run draft | GO as a draft; execution HOLD for reviewed 5l output, the exact commands and the owner's fresh go. |
| 5. Revised cut-down times | GO as an owner proposal, keeping the freeze and submission target fixed. |

R7:4 says four read-only Muse prompts but supplies three: 2m, 2n and 2o. No fourth prompt is approved implicitly.

## 1. Media / 8f — instructions GO, artifact review HOLD

**Must fix for approval:** R7:1–3 refers to five revised attachments, but only the instruction file is present. Supply the post-round-6 `script.md`, `captions.md`, `x-post.md`, `shot-capture-list.md` and `claims-check.md`. The earlier must-fix remains open pending inspection of those outputs; issuing a correct prompt does not establish that the files implement it.

R7:14 correctly preserves the visible **SIMULATED phone profile** label on all profile-derived shots and a retained caption if 0:12 is removed. R7:15 correctly separates Muse Code CLI from the models. R7:16 has the four correct diagram/credit starts **when the profile shot is retained**.

**Should fix/check in the files:** if 0:12 is also removed, subtract a further 18 seconds from subsequent starts. Ensure every caption follows the actual edit, not merely the diagram and credit cards. Recount the new files; the previous round's counts are not verification of this version.

**Optional:** none.

## 2m. Preflight — GO, preliminary only

**Must fix:** none in this read-only inspection prompt. R7:22–33 clearly makes the embedded live-proof job an object to inspect, not a job to execute.

**Should fix / check in its report:**
- R7:25–27: cite full source commit IDs. The output-path survey at `5a9c7e6` covers that base only. Label inherited 5m paths and the eventual merged tree unverified until the reviewed 5m tip exists; do not call the post-merge suite safe from the base-only survey.
- R7:28: timestamp disk/inode observations and use exact bytes for a fit calculation. Finishing another build does not automatically free its retained outputs. This is a forecast, not permission to build; the live job must repeat its check under the lock.
- R7:29: the two-hunk comparison proves the builder-side change only. It does not prove that the future 5m merge has no additional conflicts.
- R7:26,30: missing flags, entry points or path overrides must be WRONG/UNKNOWN with an implementation requirement, not invented APIs. Confirm the command list contains no attempt to run the embedded build.

**Optional:** report the survey's file coverage so “every inherited script” is auditable. Use bytecode-disabled Python for any project imports, although this task can inspect source without importing it.

## 2n. Release audit — corrections required

**Must fix:**
1. **R7:78,81 — the merge probe is not strictly read-only.** `git merge-tree --write-tree` can create Git objects even though it leaves the working tree and index alone ([Git documentation](https://git-scm.com/docs/git-merge-tree)). It violates this task's one-report-only write boundary. Defer actual merge probes to the later integration task; here mark conflicts unverified and use read-only changed-path overlap as a warning, never as proof of a clean merge. Do not substitute the deprecated trivial-merge mode as equivalent. If a probe already ran, record it; do not delete Git objects to undo it.
2. **R7:82–83 — scan privately and cover publication history.** Never send raw `git log -p`, matching lines or key-containing stderr to the terminal/Muse transcript. A scanner may inspect committed/tracked bytes internally, returning only locations and classifications; it must not open environment/authentication stores. Pin the intended publication refs and scan their reachable historical blobs, including deleted files and merge-only content, rather than relying solely on a patch log/current tree or commits ahead of `origin/main`. Check the previously reported removed APK blob `9266cb7` for reachability. Apply the private-VPN-content check to history too. Report any unscanned blobs as incomplete, not clean.
3. **R7:80–81 — correct the publication premise and status claims.** GitHub currently reports [the product repository](https://github.com/gabriellporfirio/Project-StarGate-Meta-Hackathon) as **public**, consistent with master-plan Q10. Any push is publication; there is no later visibility switch protecting it. Offline remote-tracking refs cannot prove the current server state. Report “contained/not contained in locally known remote refs; current push status unknown,” with the pinned tip and local baseline.

**Should fix/check:** take a start/end ref and dirty-state inventory; distinguish committed coverage from changing worktree observations. A later release needs the final exact tips checked. Stream unique blobs and report size/coverage, avoiding a huge raw-diff dump or full test/build work. Separate dummy strings, public endpoints and public-key/test fixtures from confirmed private material; a heuristic hit alone is not a confirmed leak.

**Optional:** none. This preliminary audit is not push authorization.

## 2o. Shot readiness — static GO, execution HOLD

**Must fix before running project commands — R7:91,93,97:** “offline” does not establish “writes nothing.” Resolve the exact source and inspect the command's code path first. Do not import a moving `/workspaces/m5` while 5l edits it; `git rev-parse HEAD` does not make `PYTHONPATH=/workspaces/m5` use committed bytes. Keep this pass to pinned source and saved-file inspection where the worktree is dirty or changing.

For any permitted execution, disable bytecode writes (`PYTHONDONTWRITEBYTECODE=1` or `-B`; [Python documentation](https://docs.python.org/3/using/cmdline.html)), prove stdout-only output, no cache/report/default JSON writes, no key lookup and no live fallback. The old report's replay examples contain `--json-out`, so copying them would violate this task's boundary. If a safe invocation cannot be established, report the command with **ran: no / output: unknown**.

**Should fix/check in the report:**
- R7:94–97: record full commit IDs, dirty-state observations and hashes of the saved traces/manifests used. An older trace rejected as unsupported by v2.2 is a missing usable shot, not a successful replay.
- R7:98–99: a Mac-step document proves instructions exist, not that boot/answer footage exists. Mark owner-local recordings unavailable to the codespace as unknown. Line counts estimate readability; only the actual chosen viewport/footage proves it.
- The frozen M4 proof and current M5 output must remain distinguishable; no old answer presented as a run of a newly built APK.

**Optional:** none.

## 3. 8g submission draft — GO

**Must fix:** none for this one-file draft task (R7:104–111). It does not authorize posting.

**Should fix/check in the resulting file:**
- R7:108–109: apply [IF A]/[IF B] to dependent claims throughout the title/tagline and every section, not just the 150-word description. Produce a coherent final version for each proof state; unproved successes cannot become unconditional in “How we built it” or “Challenges.”
- Preserve the M5 limitation, “install-routing proposal, not a validated install procedure,” alongside simulated profiles and emulator-only proof. “What's next” must clearly describe future work.
- R7:107,110: keep the title descriptive until the owner chooses it. List human contributors separately from AI tools and their roles; fill every [NAME] before submission.
- Check against the actual final media/proof records. Neither this prompt nor earlier conditional copy establishes A/B success.

**Optional:** word counts can accompany the draft; final field-length compliance depends on the actual submission form.

## 4. Box 5n — draft GO, execution HOLD

**Must fix in the proposed limits:** none. R7:118 correctly requires reviewed 5l evidence and a fresh owner go. R7:121 keeps 8192, top-level low reasoning, one 180-second run deadline, two intended live runs, aggregate 6 Meta sends / 4 page requests including retries/redirects, and no favourable-result reruns. The unchanged spec also caps each run at 3 sends and 2 page requests. The flagship exit-6 stop is preserved.

**Should fix before making the final runnable copy:**
- R7:121: verify all planned `-v3` outputs are absent before starting; never overwrite previous evidence. Stop dependent commands if a preparatory scan/plan fails or an input is missing, rather than interpreting “eight commands exactly once” as unconditional execution. Capture each exit explicitly; expected M5 exits 5/7/10 must not disappear behind blanket shell `set -e`.
- R7:122: report the numeric exit separately from the semantic result and include exit **2** (missing key) and exit **7**. Mark unsent calls and unavailable usage/finish reasons as not applicable/unknown. Do not invent an excerpt hash when extraction failed.
- Keep the full commit ID, report section and exact eight commands together for the 7b review. Check the replay and output paths against the new code; they are not available in this attachment.

**Optional:** a small command/exit/Meta-count/page-count table will make the batch ceiling easy to audit. No live-run approval is given here.

## 5. Revised cut-down checks — GO as a proposal

**Must fix:** none, provided these remain decisions to cut scope rather than automatic extensions for unfinished work.

**Should fix — R7:7:** write the timezone and dates explicitly: **15:00 / 18:00 / 19:00 Wednesday 4 November, Europe/London; code freeze 20:00; submission target 00:30 Thursday 5 November**. The owner-supplied guide in the repo records a 02:00 GMT deadline on 5 November, so that target retains 90 minutes of buffer; this is not a new independent certification of contest rules.

Suggested decisions: at 15:00 choose the minimum proven demo; at 18:00 drop integrations without a bounded path to proof; at 19:00 choose the A/B cut from evidence actually obtained and lock its claims. Keep the 20:00 freeze on exact release commits/APKs; later work is capture, edit, accessibility checks and submission. An unfinished proof uses the already-written fallback, rather than moving freeze. This remains the owner's decision; no schedule or automation was changed.

**Optional:** none.

## Review boundaries and history

The round-6 media blocker is still evidence-pending, not newly disproven. 8f addresses it correctly in instructions. 5l/5m prompt approvals remain intact; their implementation reviews belong to round 7b. The earlier failed runs and prompt versions remain on record. The new findings concern these new audit prompts and the missing new media outputs, not a claim that any running Muse has already leaked data, modified a worktree or failed its task.
