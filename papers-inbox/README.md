# Question paper inbox

Drop CSIR NET Mathematical Sciences question-paper PDFs here, exactly as downloaded,
then ask for them to be solved by file name.

Naming: `YYYY-MM-DD-<subject>-shift<N>.pdf`, for example
`2025-03-02-mathematical-sciences-shift1.pdf`.

A PDF stays in this folder permanently once processed — it is the archived source
for every solution published from it.

**Why the PDF has to be committed rather than linked.** Outbound access to
`drive.google.com` and similar hosts is blocked by the build environment's egress
policy, so a shared cloud link cannot be opened. A file inside the repository is read
straight from disk.

**Papers whose questions are page images.** Many official preview papers store each
question as a rendered image with no text layer. Those are still fine — the pages are
read visually and transcribed into MathJax. It is slower, which is why such a paper is
published in instalments.
