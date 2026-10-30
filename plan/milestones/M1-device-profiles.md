# M1: Device profiles and checks (spec)

Status: v2.1, which folds in [the follow-up review](../../reviews/2026-10-30-chatgpt-m1-device-profiles-v2.md) and [ChatGPT's review](../../reviews/2026-10-30-chatgpt-m1-device-profiles.md) (all six points). Planned for Fri 30 Oct, after M0. Builds on the M0 product repo at the accepted checkpoint: fixup commit `1673b97fb97d2612f42fa28c6fe07caa2a937bb3` on top of `b214429`. The M1 prompt carries this full SHA, and Muse stops if HEAD doesn't match it.

## Goal
StarGate can describe a phone honestly. It has a **device profile** format in which every fact says where it came from and how sure we are. It has a **read-only probe** that would collect those facts from a real phone over USB, and four **simulated phones** to test against. M2 (research) and M3 (strategy and fit) take their input from this profile, so the format has to be exact enough that they can't read it two ways.

No phone, no adb install and no USB are used in M1. The probe runs only against simulated outputs.

## 1. The device profile format (`profile-v1`)

A JSON Schema file plus a validator. The top level holds `schema_version: "profile-v1"`, `simulated` (boolean), `fixture_name` (string or null), `created_at` (UTC, ISO 8601) and `facts` (an object keyed by fact ID).

### 1a. One fact record
| Field | Type | Rule |
|---|---|---|
| `status` | `measured` / `inferred` / `unknown` / `conflicting` | Required |
| `value` | The fact's declared type (table 1c) | Required. Must be `null` when `unknown` or `conflicting` |
| `unit` | `bytes`, `count` or `null` | Fixed per fact (table 1c). Sizes are always whole bytes |
| `evidence` | List of evidence items (1b) | At least one for `measured`. For `conflicting`, the evidence lives on each candidate instead |
| `unknown_reason` | `not_exposed`, `property_missing`, `permission_denied`, `timeout`, `output_too_large`, `malformed_output`, `not_probed_in_m1` or `deferred` | Required when `unknown`, otherwise absent |
| `inference` | `{ "rule_id": string, "inputs": [fact IDs] }` | Required when `inferred`, otherwise absent. Each rule ID is listed in `docs/inference-rules.md` |
| `candidates` | List of `{ "value", "evidence" }` | Required when `conflicting`, otherwise absent. At least two candidates, each typed like `value` and each with at least one evidence item, and the candidate **values must be distinct** (no two equal after normalising the unit) |

### 1b. One evidence item
`{ "probe_id": string, "command": string (exactly as in the allowlist), "excerpt": string (the line used, max 200 characters, after redaction), "observed_at": UTC time }`

### 1c. Facts in v1
| Fact ID | Type, unit | Needed by | Notes |
|---|---|---|---|
| `identity.manufacturer`, `identity.model`, `identity.device_codename` | string | M2 | |
| `identity.android_release` | string | M2 | e.g. "13" |
| `identity.sdk_level` | integer | M2, M3 | |
| `identity.platform` | string | M2 | Chip/platform name as the phone reports it |
| `boot.bootloader_locked` | boolean | M3 | The **current** lock state |
| `boot.oem_unlock_supported` | boolean | M3 | Whether this **build** supports OEM unlocking (`ro.oem_unlock_supported`) |
| `boot.oem_unlock_allowed` | boolean | M3 | Whether unlocking is **currently permitted** (the user toggle and/or carrier). Often unreadable without privileges. Then it's `unknown` with a reason, never a guess |
| `boot.verified_boot_state` | `green` / `yellow` / `orange` / `red` | M3 | |
| `boot.ab_slots` | boolean | M3 | |
| `boot.dynamic_partitions` | boolean | M3 | |
| `boot.treble_enabled` | boolean | M3 | |
| `boot.vndk_version` | string | M3 | A missing property is `unknown` (`property_missing`), **never** "no VNDK": from Android 15, VNDK properties are removed for some builds |
| `resources.ram_total` | integer, bytes | M3 | |
| `resources.data_free` | integer, bytes | M3 | Free space for **user data only** (1d) |
| `resources.cpu_abis` | list of strings | M3 | This is what shows a 32-bit-only phone |
| `resources.cpu_cores` | integer, count | M3 | |
| `kernel.release` | string | M2, M3 | |
| `kernel.config.<feature>` for `tun`, `overlay_fs`, `ext4`, `exfat` | `built_in` / `module` / `disabled` | M3 | `unknown` (`not_exposed`) unless the kernel config is readable. Says what the kernel was **built** with (1d) |
| `capacity.system_image_max` | integer, bytes | M3 | Reserved. Always `unknown` (`deferred`) in M1 |
| `runtime.<feature>_usable` | boolean | M3 | Reserved. Always `unknown` (`not_probed_in_m1`) in M1 |

### 1d. What these facts do **not** prove
- `resources.data_free` says nothing about whether an OS image fits. With dynamic partitions, system and other images live inside a `super` partition with its own size limits. Nothing in M1 may print or store a "fits" or "doesn't fit" conclusion. That's M3's job, and it needs `capacity.*` facts M1 doesn't collect.
- `kernel.config.*` describes how the kernel was **built**. Whether a service can actually **use** a feature (for example TUN also needs device access and the right privileges) is the separate `runtime.*` fact, `unknown` in M1.
- A locked bootloader (`boot.bootloader_locked: true`) is not proof that a phone can never be unlocked. Only `boot.oem_unlock_supported` and `boot.oem_unlock_allowed` speak to that.

### 1e. Examples
`schemas/examples/` holds at least: a valid measured fact, a valid unknown fact with a reason, a valid inferred fact, a valid conflicting fact with two candidates, and invalid ones (unknown with a value, conflicting with one candidate, conflicting with two equal values, measured with no evidence, a size given as "2 GB" instead of bytes). Tests run the validator over all of them.

Muse checks every Android property name against official Android documentation or AOSP source, and lists each probe with its source in `docs/probes.md`.

## 2. The read-only probe
- **Allowlist:** a fixed list of exact commands, each reading one named property or file (for example a single `getprop <name>`, or `cat /proc/meminfo`). There's no full `getprop` dump, because that includes the serial number.
- **Refused before the transport is called:** any command not on the allowlist exactly, including anything that writes, reboots, flashes, installs, changes settings or uses root (`reboot`, `fastboot`, `setprop`, `pm`, `am`, `rm`, `su`, `dd` and so on), and any shell metacharacters (`;`, `|`, `&`, `>`, `<`, backticks, `$(`, newlines).
- **Limits (numeric):** 5 seconds per command, 64 KiB of output per command, and a 60-second total per scan. If `/proc/config.gz` is read in future, it gets a 1 MiB limit on the **decompressed** size. A limit hit gives `unknown` with `timeout` or `output_too_large`.
- **Privacy:** it never reads serial numbers, IMEI, phone numbers, accounts, Wi-Fi details or user files. Redaction runs on values, evidence excerpts **and** error messages.
- **Transport:** an interface. M1 ships only a simulated transport that replays canned outputs. The real adb transport is a stub that refuses ("real devices are not enabled in M1") without starting any process.

## 3. Four simulated phones
Each one is a folder of canned command outputs, labelled SIMULATED and invented for the purpose: no real serials, and nothing copied from your phones.

| Name | What it's there to test |
|---|---|
| `budget` | Low RAM, small storage, some properties missing (so `unknown` with reasons shows up) |
| `flagship` | Modern 64-bit, A/B plus dynamic partitions, Treble, kernel config readable |
| `old32` | 32-bit-only ABI list, old Android, no A/B |
| `locked` | Bootloader locked, `oem_unlock_supported: true`, `oem_unlock_allowed: unknown` (`permission_denied`) |

Plus test-only cases: a conflicting fact, unlock **not supported** by the build, a property that times out, and oversized output.

Rule: any phone-related fact M1 code relies on must come from the probe output, never from the fixture's name.

## 4. `stargate scan`
- `stargate scan --sim <name>` prints a plain-English phone report, grouped as in 1c, with unknowns shown as unknown plus their reason. It ends with a short "what this means" section built from deterministic rules only, for example "Bootloader is locked. Whether it can be unlocked: build supports it, permission unknown." No fit conclusions (1d) and no AI.
- `--json` prints the complete validated profile.
- `stargate scan` without `--sim` exits with code 3 and "real devices are not enabled in M1".
- Scans and all automated tests are offline. They make no network calls.
- While building, Muse **may** read documentation and source code online (Android docs, AOSP source, the pinned plan repo) to check property names. That's read-only research. The product itself makes no calls.

## 5. Allowed network use, and housekeeping
- The only network call allowed in M1 is **one** `stargate doctor` regression run at the end, to show M0 still works live. Nothing else calls Meta.
- **Optional, only if it doesn't put the schedule at risk:** move the Meta client and secret redaction out of `doctor.py` into their own modules for M2. If it's skipped, say so in the report.

## Done when
- [ ] `stargate scan --sim` works for `budget`, `flagship`, `old32` and `locked`. The four reports clearly differ, `budget` shows at least one `unknown` with a reason, and `locked` shows the three unlock facts separately.
- [ ] The complete `--json` output of all four validates against `profile-v1`, with `simulated: true`.
- [ ] The schema examples (1e) pass and fail exactly as labelled.
- [ ] `stargate scan` without `--sim` exits 3, and no process is started.
- [ ] Tests prove: every non-allowlisted command and metacharacter is refused before the transport is called, timeout and oversize become `unknown` with the right reason, `conflicting` keeps both candidates with evidence, no serial-like value appears in values, evidence or errors, and nothing prints a fit conclusion.
- [ ] `docs/probes.md` lists each probe with its official source, and `docs/inference-rules.md` lists each rule ID.
- [ ] One live `stargate doctor` run passes, and all tests pass offline (count above zero).
- [ ] `INSTALL-LOG.md` shows no new installs, there's one checkpoint commit, and nothing is pushed without your OK.

## Out of scope
Real phones, adb, USB, fastboot, research, strategy, fit conclusions, UI, emulator, images, and any Meta call except the single doctor run.

## Demo (under 5 minutes)
```
.venv/bin/stargate scan --sim budget
.venv/bin/stargate scan --sim locked
for p in budget flagship old32 locked; do .venv/bin/stargate scan --sim $p --json > /tmp/$p.json && .venv/bin/python -m stargate.profile validate /tmp/$p.json; done
.venv/bin/stargate scan; test $? -eq 3 && echo "refused as expected"
.venv/bin/python -m unittest -v
```
The exact validate command can differ; Muse documents the one it builds.
