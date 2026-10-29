# M0 review addendum: clean slate and cloud execution

29 Oct 2026 · Owner's new direction after [PR #18](https://github.com/gabriellporfirio/Project-Stargate/pull/18) spec v2 (`bd137803b1a80d1b235def1f36c0f2a2c0847e49`).

**Changes requested before the implementation prompt.** Claude reconciled the earlier review; this addendum records a subsequent scope change. No Mac cleanup, installation or cloud provisioning has been performed here.

## Owner's direction

Discard the earlier Muse hackathon implementation. Prefer development in the cloud, with no new software on the Mac by default. Any proposed Mac install must be shown and explicitly approved first, including project-local dependencies. Existing private StarGate/VPN work remains outside scope.

## Required reconciliation

1. **Must fix — replace the local reset.** Separate a small Mac cleanup/inventory step from cloud bootstrap. Trash only verified old Muse hackathon directories, reversibly; do not empty Trash or import that code into the fresh workspace. Do not remove shared/system packages merely because they are installed. Produce a targeted uninstall proposal from evidence first. The [cleanup and install-approval prompt](../plan/prompts/muse-clean-slate-and-install-guard.md) makes this concrete.

2. **Must fix — install control.** Show host, tool/version/source, exact command, paths, privileges, purpose, footprint/cost and rollback before any Mac install. Keep Muse's command approvals and sandbox enabled. Cloud setup should have one reviewable, bounded bootstrap plan; extra installs outside that plan need approval. Never fall back to Mac installation. No Mac folder mounts or credential-store copies into the cloud.

3. **Must fix — specify cloud M0.** Propose provider, access method, machine, storage, estimated costs, spending cap, idle shutdown and persistence/export policy before provisioning. The product repository is currently empty: document how a fresh workspace starts without an unintended repository publication. Verify Muse runs with its safeguards enabled, pin the approved planning commit, create the Python environment remotely using the actual selected interpreter path, and retain offline tests plus a real Meta inference check. Use cloud secrets/runtime environment variables rather than Mac Keychain; distinguish Muse CLI authentication from the product API credential. Use model-compatible bounded inference limits.

4. **Must fix — reconcile the master plan too.** Record the decision in section 7. Update M0 and the Mac-specific M4/M6/Q7/Q8 assumptions. Preserve selection-driven image construction and boot validation; choose and validate a remote emulator/build host rather than silently restoring Mac installs. Physical USB testing stays deferred.

## Candidate, not a provisioned environment

**Should fix:** assess browser-based [GitHub Codespaces](https://docs.github.com/en/codespaces/about-codespaces/what-are-codespaces) for M0–M3; [Muse supports Linux](https://dev.meta.ai/docs/muse-code). Verify actual compatibility and remaining [included usage/budget](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces). Stopped workspaces still consume storage.

A full [AOSP source build](https://source.android.com/docs/setup/start/requirements) calls for x86-64 Linux, 64 GB RAM and 400 GB free disk; Codespaces currently tops out at 128 GB storage. Later image construction and [emulator acceleration](https://developer.android.com/studio/run/emulator-acceleration) therefore need their own feasibility check. Do not assume a generic cloud VM supports the required acceleration, or that Baseten/Modal credits fund this workspace.

## Reconciliation (Claude, 29 Oct 2026)

- **Must fix 1 (replace the local reset):** accepted. M0 Part A is the Mac cleanup using your prompt unchanged.
- **Must fix 2 (install control):** accepted. Master plan rule 3 is rewritten around the INSTALL APPROVAL REQUIRED block, with one reviewed cloud bootstrap.
- **Must fix 3 (specify cloud M0):** accepted. Part B1 is a proposal table (provider, blank-template start so nothing gets published, machine, cost, $0 cap, idle shutdown, persistence, secrets, Muse login kept separate) to approve before anything is created. B3 moves the credential to an env-var secret, with no Keychain.
- **Must fix 4 (master plan):** accepted. Section 7 entry added, and M0/M4/Q8 updated, with new Q9 (Muse sign-in in the cloud), Q10 (repo visibility) and Q11 (emulator host).
- **One point raised for the owner rather than settled here:** Codespaces doesn't provide the hardware virtualization the Android Emulator needs. So M4's boot step needs either one approved Mac install (the official emulator runs natively on Apple Silicon) or a paid cloud VM with virtualization. Claude recommends the approved Mac install, given the deadline. The owner decides (Q11).
