# Night batch item 4: M4a Part 2 result and Part 3 prompt

Reviewed the supplied Part 2 report at `95e25471e11b38adbc924811ecf78739ac9d0b2b`, the Part 3 prompt, and PR #34's owner decision.

**Part 2 verdict: accept the honest PARTIAL result.** The reported 1,138,135,470-byte model exceeds the 305,967,104-byte product partition; declining to improvise partition growth is reasonable. The Files image and its hashes are reported artifacts, not an independently verified boot. The final APK/manifest test failure remains real; the coming merge must resolve it, not skip it.

**Part 3 verdict: changes required before sending.** The owner's “app in image, model after boot” exception is authorized. Do not reopen that decision or require a partition-growth experiment.

**Must fix 1 — make the new delivery contract explicit.** Update M4's affected checks/boot-proof wording, not only §4b: §3, §5, §6 and the result criteria still assume no pushed Route A payload. For `model_delivery=after_boot`, verify the actual external model files' complete names, sizes and hashes against the approved Assistant manifest and M3 handoff before reporting a successful package. Reference immutable verified files or produce a payload bundle; copying expected hashes into build-v1 is not a contents check. Preserve exit 9 for binding errors and 8 for wrong/missing bytes. Test a same-size wrong-hash external payload, missing payload and a Files-only build carrying an unwanted model. The manifest and visible UI must say “apps in image; model added after boot,” and must not claim the image contains the model.

**Must fix 2 — separate artifact readiness from M4 completion.** The prompt ends before the owner-run Mac test, so its report cannot call M4 COMPLETE. Use “build ready, Mac proof pending” plus the existing PARTIAL milestone status. Completion or acceptance of a reduced demo is an owner-recorded outcome after the actual boot, transfer/hash and functional proofs. Make the expected post-boot model copy an explicit recorded exception; no post-boot APK installation.

**Should fix:**
- After merging `e90edfa`, require the whole combined suite to pass, including the formerly failing manifest test. Snapshot the hash-verified local APK into builder-owned storage under the shared lock; do not depend on a mutable sibling `out/assistant.apk`.
- If native-library alignment requires changing/signing the APK, obtain an updated Assistant handoff; do not silently alter the approved APK hash. Account for extracted libraries and inode use.
- Revalidate the retained Files-only artifact/manifest under the new checks without rebuilding it, and retain its original build provenance.
- Correct the Part 2 test totals: “456 tests, 455 pass, 1 skip, 1 failure” is inconsistent.
- The final Mac proof must use the new APK hash and an ordinary model question; an app-generated device-fact reply does not prove inference.

No product builds or Mac commands were run in this review.
