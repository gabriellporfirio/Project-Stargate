# M1: Device profiles and checks (spec)

Status: v1 draft for ChatGPT review. Planned for Fri 30 Oct (after M0). Builds on the M0 product repo (checkpoint `b2144293…`).

## Goal
StarGate can describe a phone honestly. It has a **device profile** format in which every fact says where it came from and how sure we are. It has a **read-only probe** that would collect those facts from a real phone over USB, and four **simulated phones** to test against. M2 (research) and M3 (strategy and fit) take their input from this profile, so it has to carry what they need.

No phone, no adb install and no USB are used in M1. The probe runs only against simulated outputs.

## What gets built

### 1. The device profile format
A versioned JSON format (`profile-v1`), with a schema file and a validator. Each fact is a record:

| Field | Meaning |
|---|---|
| `value` | The value, or `null` |
| `status` | `measured` (read directly), `inferred` (worked out from other facts, with the rule named), `unknown` (couldn't be read), or `conflicting` (two sources disagree, both kept) |
| `source` | The exact probe command and the line it came from, or the inference rule |
| `observed_at` | Time (UTC) |

The profile also has a top-level `simulated: true/false`, and the simulated profile's name. A simulated profile can never be shown or stored as a real one.

**Facts in v1** (grouped by who needs them):
- **Identity (for M2 research):** manufacturer, model, device codename, Android version, SDK level, chip/platform.
- **Boot and unlock (for M3 strategy):** bootloader locked state, OEM unlock supported, verified boot state, A/B slots, dynamic partitions, Treble enabled, VNDK version.
- **Resources (for the M3 fit engine):** total RAM, free storage on `/data`, CPU ABI list (this is what shows a 32-bit-only phone), CPU core count, kernel version.
- **Kernel features (for M3):** TUN, overlayfs, ext4/exFAT. These are `unknown` unless the phone exposes its kernel config. They must never be guessed.

Muse must check every Android property name it uses against official Android documentation or AOSP source, and record the source next to each probe in `docs/probes.md`. Where a property is missing on some phones, the fact becomes `unknown`, never a default value.

### 2. The read-only probe
- A fixed **allowlist** of exact commands, each reading one named property or file (for example a single `getprop <name>`, or `cat /proc/meminfo`). There is no full `getprop` dump, because that includes the serial number.
- A **denylist test**: anything that writes, reboots, flashes, installs, changes settings or uses root (`reboot`, `fastboot`, `setprop`, `pm`, `am`, `rm`, `su`, `dd` and so on), and any shell metacharacters (`;`, `|`, `&`, `>`, backticks, `$(`), is refused before it runs, and the test proves it.
- **Privacy:** it never reads serial numbers, IMEI, phone numbers, accounts, Wi-Fi details or user files.
- **Bounds:** a timeout and an output size limit per command. Malformed or hostile output becomes `unknown`, never a crash.
- The probe talks to a **transport** interface. M1 ships only a simulated transport that replays canned outputs. The real adb transport is a stub that refuses to run and says why ("real devices are not enabled in M1").

### 3. Four simulated phones
Each one is a folder of canned command outputs, labelled SIMULATED, invented for the purpose (no real serials, no outputs copied from your phones):

| Name | What it's there to test |
|---|---|
| `budget` | Low RAM, small storage, some properties missing (so `unknown` shows up) |
| `flagship` | Modern 64-bit, A/B + dynamic partitions, Treble, plenty of RAM |
| `old32` | 32-bit-only ABI list, old Android, no A/B |
| `locked` | Bootloader locked and OEM unlock not allowed |

Plus one test-only case where two sources disagree, to prove `conflicting` works.

Rule: any phone-related fact that M1 code relies on must come from the probe output, not from the fixture's name.

### 4. `stargate scan`
- `stargate scan --sim <name>` prints a plain-English phone report, grouped like the list above. Unknowns are shown as unknown, with the reason. It ends with a short "what this means" section, for example "Bootloader locked: OS replacement isn't possible on this phone as it stands", using only deterministic rules, no AI.
- `--json` prints the validated profile instead.
- `stargate scan` without `--sim` exits non-zero with "real devices are not enabled in M1".
- No Meta call in M1. Meta models come in at M2.

### 5. Housekeeping from the M0 review
Move the Meta client and secret redaction out of `doctor.py` into their own modules (M2 reuses them). `stargate doctor` must still pass live and offline.

## Done when
- [ ] `stargate scan --sim budget`, `flagship`, `old32` and `locked` each print a readable report. The four reports clearly differ, and `budget` shows at least one `unknown`.
- [ ] `stargate scan --sim <name> --json` output validates against the `profile-v1` schema, and says `simulated: true`.
- [ ] `stargate scan` without `--sim` refuses, with a non-zero exit.
- [ ] Tests prove: every denylisted command and metacharacter is refused, a `conflicting` fact keeps both sources, hostile/oversized output becomes `unknown`, and no serial-like value ever appears in a profile.
- [ ] `docs/probes.md` lists each probe with its official source.
- [ ] `stargate doctor` still passes, and all tests pass offline (count above zero).
- [ ] `INSTALL-LOG.md` shows no new installs (none are expected), there's one checkpoint commit, and nothing is pushed without your OK.

## Out of scope
Real phones, adb, USB, research, strategy, ranking, UI, emulator, images, and any Meta call.

## Open questions this milestone answers
None from the plan list. It does produce the property list M2 and M3 depend on, and any property that turns out to be undocumented is flagged in `docs/probes.md`.

## Demo (under 5 minutes)
```
.venv/bin/stargate scan --sim budget
.venv/bin/stargate scan --sim locked
.venv/bin/stargate scan --sim old32 --json | head -40
.venv/bin/stargate scan; echo "exit $?"
.venv/bin/python -m unittest 2>&1 | tail -3
```
