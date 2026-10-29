> **Reference only.** This is the earlier v2 architecture draft. Where it differs from [plan/master-plan.md](../plan/master-plan.md), the master plan wins.

# StarGate v2: smart platform architecture (draft)

The goal: plug in any old Android phone and get a stable, custom StarGate OS image built for that exact phone. It decides how to build it from live research and measured hardware, not from a fixed recipe. The checks and safety work from v1 stay as the foundation. v2 adds the intelligence on top.

## The pipeline

```
Probe → Identify → Research → Plan strategies → Size & fit → Compose → Build → Validate → Install → Verify & tune
```

Meta Llama runs the research and planning steps as an agent with tools. Deterministic code checks every fact it brings back before the plan is allowed to use it.

## 1. Deep device probe (read-only)

As well as v1's facts, collect:
- **Partitions and boot:** A/B slots, dynamic partitions and `super` size, partition list by name, boot header version, `ro.boot.verifiedbootstate`, AVB/vbmeta state, `ro.oem_unlock_supported`, and whether OEM unlock is allowed.
- **Treble:** `ro.treble.enabled`, VNDK version, vendor and system API levels.
- **Kernel:** version, `/proc/config.gz` when readable, loaded modules (`/proc/modules`), and features StarGate modules need (TUN, overlayfs, cgroups/namespaces, exFAT/ext4, USB host/OTG, binder).
- **Compute:** CPU cores and clusters, GPU and Vulkan support, DSP/NPU hints (e.g. Hexagon), memory bandwidth class.
- **Peripherals and health:** SD card, USB OTG, battery health and charge limits, thermal zones.

Each fact keeps v1's record: value, source, time, and whether it was observed, inferred, unknown or conflicting.

## 2. Identify the phone

Resolve the codename to a known device identity. This step is the key to everything after it: which images, trees and firmware exist for this phone.

## 3. Research agent (Meta Llama + tools, cached and cited)

| Question | Sources it searches |
|---|---|
| Is there a maintained community OS? | LineageOS device list and wiki, postmarketOS wiki, TWRP, XDA device forums |
| Is there a public device tree, kernel and vendor repo? | GitHub/GitLab orgs for the device and its chip family, LineageOS org |
| Is there stock firmware to extract? | Official vendor factory-image pages; known firmware mirrors (allowlisted) |
| Does a GSI boot here? | Treble compatibility lists, community reports for this codename |
| Which local AI models fit? | Hugging Face API (GGUF/quantised models, sizes, licences), llama.cpp / ExecuTorch / MLC runtime support for this chip |

The rules: every URL must be on an allowlist of domains, every download is hashed and recorded, every claim cites its source, and the agent can never add executable build steps. It proposes, the strategy engine decides.

## 4. Strategy engine: how to build the image

Each strategy is scored on stability, effort, evidence and risk for this specific phone, then ranked.

1. **Community device tree build:** StarGate OS built as a product on top of LineageOS or AOSP with the device's own kernel and vendor trees. This is the most stable option, and it's what worked on the Razer.
2. **GSI over the stock vendor partition:** Treble phones only. A generic system with the phone's own vendor drivers.
3. **Stock firmware rebuild:** extract the stock images, keep the stock boot/vendor/firmware partitions, and replace system/product with a StarGate OS build.
4. **Linux path:** postmarketOS for phones with good support.
5. **Hosted fallback:** no OS replacement. Services run on top of Android. This is a configuration bundle, not an image.

**Signing, stated plainly:** modifying any verified partition breaks its stock signature. Strategies 1–4 all need an unlocked bootloader, plus either verification disabled in vbmeta or re-signing with your own AVB key on phones that support custom keys. That's why "keep signing intact" is really about keeping the stock vendor, boot and firmware untouched. It's the most compatible approach, but it's not the same as passing stock verified boot. The engine must show this per phone and recommend strategy 5 when the bootloader can't be unlocked.

## 5. Size and fit engine

- **Memory:** OS baseline + each module's working set + AI model (parameters × bits/8 + KV cache + runtime overhead) must fit with headroom, otherwise the build is blocked.
- **Storage:** the image must fit the `super`/system partition limits, and user data must fit the chosen location.
- **Kernel:** each module declares the kernel features it needs. A missing feature is either blocked, or fixed by a kernel rebuild when the strategy includes kernel source (strategy 1).
- **AI:** candidate models ranked by fit and expected speed, then **measured** on the phone with a short benchmark before the choice is final.
- **Power and heat:** recommend charge limits and duty cycles from battery and thermal data.

## 6. Compose

The StarGate OS product: launcher, module manager, and the chosen modules (Files, Assistant, VPN, Vault, Home), packaged for the chosen strategy. Android products use makefiles/Soong. The Linux path uses packages. The UI and module manifests from v1 carry over.

## 7. Build farm

Full Android builds need x86-64 Linux, around 400 GB of disk and 64 GB of RAM. So builds run on a **remote Linux builder** (cloud VM or a home server) driven from the app, with source caching, pinned revisions, and a journal of toolchain versions and hashes. Lighter strategies (GSI customisation, postmarketOS) can run locally in a container.

## 8. Validate

Check image formats, partition size fit, `avbtool info_image` output, that the contents match the selection exactly, and the kernel features against module needs. Physical boot, service and recovery checks are a separate, later status.

## 9. Install and recover

Back up first (partition dumps where readable, stock firmware references). Flash over fastboot with explicit confirmation of each step, use the other A/B slot where available, and save a tested restore path. Nothing ever changes the phone without your confirmation on the exact operation.

## 10. Verify and tune

After first boot: health checks for each module, an AI benchmark, and thermal monitoring. The phone's measured results feed back into the knowledge base, so the next phone of the same model gets a better plan.

## What carries over from v1

The read-only adb transport and allowlist, the evidence and manifest model, sanitisation, the deterministic rules pattern, the five service definitions, the module manifests, the StarGate OS UI and preview, the Meta client and its validation, the artifact taxonomy (report → spec → bundle → image → hardware-verified image), and the tests behind them.

## Hackathon slice

The full vision is several months of work. For the demo, prove the "smart" part end to end on one real phone:
1. Deep probe, then identity, then a live research agent finding the device tree, stock firmware and fitting AI models, with citations, shown live in the platform app.
2. The strategy engine ranking strategies for that phone, with reasons and the signing implications.
3. The fit engine choosing an AI model, and the composition changing as you tick services.
4. One real image produced by the most feasible strategy, with validated contents. Flashing only if you choose to on a test phone.
