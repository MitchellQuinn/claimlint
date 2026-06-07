# Verdict Rules

## supported

Use when the selected corpus contains strong evidence matching the claim and no major required evidence is missing.

## partially_supported

Use when the selected corpus contains some relevant evidence, but important evidence is missing, incomplete, indirect, or inconveniently discoverable.

Example: training logs or a metric file exist, but the released checkpoint or evaluation command is missing.

## unsupported

Use when no meaningful supporting evidence is found in the selected corpus.

## ambiguous

Use when the claim itself is unclear, vague, or too underspecified to decide what evidence would support it.

## overclaimed

Use when the repository contains some evidence, but the claim goes materially beyond that evidence.

Example: synthetic validation evidence exists, but a README implies real-world generalisation and no real-world evidence is present.

## needs_human_review

Use when the claim cannot be reliably judged from static repository evidence alone.

Examples include hardware-dependent runtime claims, external service claims, and claims needing credentials, deployment state, or physical environment.

Do not mark a claim `supported` merely because it sounds plausible.

