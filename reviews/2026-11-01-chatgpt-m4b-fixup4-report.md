# Night batch item 2: M4b fixup 4

Reviewed the supplied prompt, Muse report and owner's Mac observations for `53e583661e86df3caf42b6fb746d3751492d92d8`.

**Verdict: approve this fixup checkpoint on the supplied evidence. No must-fix for its stated scope.**

The reported `resetContext()` call before each generation matches the requested change. More importantly, the owner observed `given pos_ 67, num_prompt_tokens 67` for three successive questions on APK `f98a59a5629e30cf29222804900ac12176621a318f53c34297baa031ad520439`. This supports fresh context per question rather than the earlier accumulating positions. The app answered the battery question itself; the reported dispatch returns before invoking the runner. General battery explanations remain allowed.

The 359-test result, method-signature extraction, APK permission inspection and dependency scans are Muse-reported, not independently reproduced here.

**Should fix / retain in the handoff:**
- Describe device-fact protection as coverage of the defined question patterns. A phrase list cannot guarantee detection of every paraphrase or prevent all hallucinations. Keep the general-information counterexamples.
- Token counts and listed EOS IDs support the configuration; EOS IDs alone do not prove every generation terminates correctly. Preserve the separate stopping and display tests.
- This Mac proof belongs to `f98a59a5…`. M4c rebuilt the local APK as `1936549b…`; that artifact still needs the planned final Mac regression. Do not transfer the old APK's proof to the new hash.
- Integrate the owner's chosen `e90edfa`, which contains this fix, rather than combining the old manifest with the overwritten shared APK.

No additional live call, install or product-code change is requested by this review.
