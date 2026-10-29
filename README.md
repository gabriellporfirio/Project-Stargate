# Project StarGate: plan and design

StarGate turns an old Android phone into a private home server. A guided app on your computer scans the phone, researches what it can run, lets you pick services (Files, Assistant, VPN, Vault, Home), and builds a minimal **StarGate OS** image for that exact phone. Meta Llama powers the research and explanations. Built for the Meta hackathon; submissions are due Wed 4 Nov 2026, 9:00 PM.

**This repo holds the plan, not the code.** Meta's Muse CLI writes the product code in a separate repo. Claude and ChatGPT plan and review here.

| Path | What it is |
|---|---|
| [plan/master-plan.md](plan/master-plan.md) | The single source of truth: vision, rules, open questions, milestones, schedule |
| [plan/review-workflow.md](plan/review-workflow.md) | How Claude, ChatGPT and you review and approve changes |
| [design/](design) | Mockups of StarGate OS (phone) and the StarGate app (computer) |
| [docs/architecture-reference.md](docs/architecture-reference.md) | Earlier architecture draft, for reference |
| [reviews/](reviews) | Saved review notes, one file per review |

**How changes happen:** every change is a pull request, reviews go in `reviews/`, and merging means the owner has approved it.

The previous contents of this repo (Pixel Media Checker) are preserved in history and under the tag `archive/pixel-media-checker`.
