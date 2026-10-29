# Claude + ChatGPT: how they work together on StarGate

Neither assistant writes product code. Muse does that (hackathon rule). Their job is the plan, the milestone specs, and checking Muse's work.

## Recommended setup: one shared plan folder on GitHub

1. This repo (`Project-Stargate`) holds only documents: the master plan, milestone specs, mockups, and review notes. Muse's product code lives in a separate repo.
2. **Claude** (this thread) writes and updates the plan files and opens a pull request for each change, so you see a clear diff of what changed.
3. **ChatGPT** reads the same repo through its GitHub connector, if your plan includes it. Otherwise, upload the file to the chat. It reviews with the prompt below.
4. You paste ChatGPT's review into this thread. Claude reconciles both views, updates the PR, and lists anything the two disagree on for you to decide.
5. **You merge** the pull request. Merged means approved.
6. **Muse** gets the merged milestone spec plus the one prompt for it. Muse's code lives in its own repo, separate from the plan.

Why GitHub: all three tools see the same file, every change has a history, and "approved" is a single unambiguous action (the merge).

## Simpler alternative: no repo

Download the plan from this thread, upload it to ChatGPT with the prompt below, then paste its answer back here. It works, but versions are easier to mix up.

## ChatGPT reviewer prompt (paste with the document)

```
You are reviewing the plan for StarGate, a Meta hackathon project. Another AI (Claude) wrote it; the code will be written by a third AI (Meta's Muse CLI). The owner is not a full-time developer and wants clarity over cleverness.

Review the attached document critically. Do not rewrite it. Give me:
1. Wrong or unverified technical claims (Android boot/signing, fastboot, emulator, build requirements, model sizing), each with what is actually true and a source if you can.
2. Hidden assumptions: anything the plan treats as known that isn't.
3. Gaps: steps that are missing, or a milestone whose "demo" doesn't prove what it claims.
4. Risks to the owner's production phone or laptop that the plan doesn't handle.
5. Scope: what to cut to make the hackathon deadline, if anything.
6. Your top 3 changes, in priority order.

Keep it under 500 words. Mark each point as Must fix / Should fix / Optional.
```

## Reviewing Muse's output (after each milestone)

Paste Muse's final report into this thread and into ChatGPT with: "Check this report against the milestone's done-when list. What is proven, what is only claimed, and what should I run myself to confirm?"
