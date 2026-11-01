# ChatGPT review: product decisions after the mockup review

Reviewed PR #33 at `53279d64db954cd718d71e52b2f89e8226d79b36` on 1 November 2026.

**Verdict: approve this decision record. No must-fix finding for this PR. It does not approve an M6 implementation or network-security design.**

The logo-only identity, controls on the phone, computer-side service interfaces, explicitly labelled emulator demo and removal of the vault form a consistent direction. M4 remains unchanged and loopback-only, and the new Wi-Fi/API work explicitly waits for M6's reviewed security design. The existing no-real-phone rule and owner-controlled flashing remain in force.

**Should fix / carry into M6, in priority order:**

1. **Define the AI proposal stage precisely.** Existing M3 §4c chooses the largest fitting catalog model deterministically; §5 only lets the model explain that result. The new visible-decision requirement therefore needs an explicit integration contract, not an assumption that this already exists. Define what a model may propose, how evidence is checked, and how a fresh validated plan and matching Assistant manifest reach the builder. Model output must not overwrite measured facts, promote unknowns to confirmed, bypass a refusal or directly modify an image. Demonstrate a real accepted proposal's effect; retain SIMULATED labels on demo profiles rather than presenting them as measurements from a handset.

2. **Resolve the networking and permission contract before building M6.** M4c's local APK currently has no permissions, whereas Android's [INTERNET permission enables network sockets](https://developer.android.com/reference/android/Manifest.permission#INTERNET). A phone-side HTTP API requires an explicit permission-contract revision or a separate transport component; “local inference” and “no networking permission” are different promises. Specify authenticated pairing/revocation, TLS trust, exposed endpoints/interfaces, and negative tests for unpaired clients. Define network-off behavior with and without a cable, closing existing LAN sessions and explaining unavailable cloud mode. Keep provider keys and existing call budgets protected. Prove the actual emulator/host transport; an emulator boot alone is not home-Wi-Fi proof. If this misses the time budget, retain the working cable demo and label Wi-Fi unfinished.

3. **Tighten the wording and scope.** The supplied rubric rewards creative, substantive Meta use; it does not say tooling scores count *only* when a model visibly decides. Present that as the owner's demo requirement. Among the two proposed models, Spark Open is the eligible open-weight option; the guide also names Glimmer. Update the PR description to include the logo exception. M6 should distinguish an app-drawn home header from changing Android SystemUI, and avoid expanding into an updater or privileged reboot implementation merely to match a mockup.

Reviewed documents and their dependencies against the approved M3/M4/M4c contracts and supplied judging excerpts. No product code, builds, devices or live model calls were tested.
