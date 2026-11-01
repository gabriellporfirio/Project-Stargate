# M4a Part 3 prompt v2 re-review

Reviewed the attached prompt against M4 v2.3 at planning commit `d06eaee07bd4897473b25dcd91bc61a699c155c1`.

**Verdict: approve this M4 handoff. No remaining must-fix in its stated scope.** This does not declare M4 complete or approve the pending M5/M6 specifications.

The two previous blockers are addressed:
- Section 4d and the corresponding M4 checks now cover actual model payload snapshots, binding to the approved manifest/M3 handoff, byte/hash verification, exclusion from the image and the visible delivery label. The 9/8 distinction is explicit.
- The report begins “BUILD READY, MAC PROOF PENDING” and reserves completion for the owner-run proof.

The prompt also pins the `e90edfa` merge, snapshots APK `1936549b…` under the shared lock, requires the combined suite to pass, stops if the APK would need modification, accounts for native libraries and inodes, retains the Files-only artifact with provenance, and tests an ordinary model question on the exact new APK.

**Should fix / execution notes:**
- Pin the planning read to this exact reviewed commit or its approved merged revision, rather than consuming a later unreviewed branch tip.
- Correct §4d's capacity wording: 305,967,104 B is the product partition's total size; the Part 2 report says 901,120 B free. The conclusion that the model does not fit is unchanged.
- Keep manifest/handoff metadata mismatches at exit 9 and actual missing/corrupt payload bytes at exit 8.
- If a test still reads the mutable sibling APK, make its artifact input use the verified snapshot while preserving the real hash assertion. Do not report a green immutable baseline while the test quietly depends on another worker's output.
- Record the full Step 1 green commit SHA for M5. It is a baseline checkpoint, not proof of the later Files + Assistant image.

After building, the owner still needs to run the guarded Mac proof, including APK/model hashes, Files transfers and actual offline inference. No build or Mac commands were run in this review.
