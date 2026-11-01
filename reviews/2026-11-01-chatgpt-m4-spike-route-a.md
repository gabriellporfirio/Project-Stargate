# ChatGPT re-review: Route A confirmation and M4b fixup 3

Reviewed PR #32 at `245beee2c1ad01b1734c8163f3fee12f51f18a1e` on 1 November 2026, including commits `84683ef` and `6626453`.

**Verdict: request changes for two prompt corrections. The Path A evidence is now accepted.**

The owner-run confirmation records the verified image hash, intended AVD, `boot_ok=1`, `sys.boot_completed=1` and the matching marker in one run. This closes the boot-evidence finding and supports Route A. The missing final empty device inventory is honestly labelled; it does not invalidate the boot/marker proof.

The FULL/PARTIAL branch now carries through artifacts, Mac instructions and the report. The schema, manifest-defined payload and early disk-check clarifications are resolved. Part 1 remains route-independent and approved.

**Must fix 1 — reject every unexpected device** (`m4a-part2-route-a.md:63`; `m4b-fixup-3.md:21–26`). The proposed guard counts only rows containing the state `device`. I ran it in zsh against a fake adb: one expected emulator plus a physical device marked `unauthorized` or `offline` both incorrectly returned ALLOW. Parse all device rows from one successful inventory; require exactly one row, the exact expected emulator serial, state `device`, and the expected AVD name. Reject any extra row regardless of state. Apply that guard to M4b's commands too, including the root/push/chown fallback, and revalidate after adbd reconnects. Test those rejected inventories and the valid single-emulator case.

**Must fix 2 — separate stopping from token display** (`m4b-fixup-3.md:6,15,19,28`). The screenshot proves a visible control token, not failed EOS stopping or an absent length cap. In [ExecuTorch 1.5.1's generator](https://github.com/pytorch/executorch/blob/3b60683923245cf472b7323426920e15623ba361/extension/llm/runner/text_token_generator.h#L172), the text callback runs before the EOS check. Thus stopping can work while the UI still prints `<|eot_id|>`. Correct the diagnosis, inspect the installed runner/model's EOS handling, and explicitly require hiding control-token text from the answer as well as terminating generation. Test both independently, including a callback that delivers the terminating token. Keep the sourced chat format and 256-new-token requirement.

**Should fix — preserve both model paths** (`m4b-fixup-3.md:18,22–25`). Scope folder creation and repair to Route B; retain Route A's manifest-defined read-only path, opened in place without copying. Also, `mkdirs` does not repair an existing shell-owned folder: check creation/readability failures rather than promising it is “always” app-owned.

I inspected the screenshot and primary runtime source, and tested only the guard with synthetic inventories. Product implementation, rebuilt APK, model hash matching and fresh Mac Assistant proof remain to be reviewed; no devices, builds or inference calls were run.
