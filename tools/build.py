#!/usr/bin/env python3
"""Build the solved-paper pages and the papers index from data/papers/*.json.

Every solved paper on this site is generated, never hand-written. Drop a JSON
file in data/papers/, run  python3 tools/build.py , and the matching page in
papers/ plus the papers index are rewritten. See HOW-TO-ADD-A-PAPER.md.
"""

import html
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "papers"
OUT = ROOT / "papers"
SITE = "https://nrstatlab.github.io/CSIR-NET-MATHEMATICS"

HUB_BAR = (
    '<div class="nrstatlab-bar"><div class="nrstatlab-inner">'
    '<a class="nrstatlab-brand" href="https://nrstatlab.github.io/planning-for-future/">NRSTATLAB</a>'
    '<span class="nrstatlab-sep">&rsaquo;</span>'
    '<a class="nrstatlab-brand" style="border-bottom-color:transparent" href="{up}index.html">CSIR NET Mathematics</a>'
    '<span class="nrstatlab-sep">&rsaquo;</span>'
    '<span class="nrstatlab-here">{here}</span>'
    '<a class="nrstatlab-topics" href="{up}syllabus.html">Syllabus &amp; pattern</a>'
    "</div></div>"
)

MATHJAX = """<script>
window.MathJax = {
  tex: {
    inlineMath: [['$','$'], ['\\\\(','\\\\)']],
    displayMath: [['$$','$$'], ['\\\\[','\\\\]']],
    processEscapes: true,
    processEnvironments: true,
    packages: {'[+]': ['ams', 'noerrors', 'noundefined']}
  },
  loader: { load: ['[tex]/ams', '[tex]/noerrors', '[tex]/noundefined'] },
  options: { skipHtmlTags: ['script','noscript','style','textarea','pre','code','annotation','annotation-xml'] },
  svg: { fontCache: 'global' }
};
</script>
<script src="https://cdn.jsdelivr.net/npm/mathjax@3/es5/tex-mml-chtml.js" id="MathJax-script" async></script>"""


def head(title, description, canonical, up, here, extra=""):
    t, d = html.escape(title), html.escape(description)
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{t}</title>
<meta name="description" content="{d}">
<meta property="og:title" content="{t}">
<meta property="og:description" content="{d}">
<meta property="og:type" content="article">
<meta property="og:site_name" content="NRSTATLAB">
<meta property="og:url" content="{canonical}">
<meta name="twitter:card" content="summary">
<meta name="theme-color" content="#1e3a8a">
<link rel="canonical" href="{canonical}">
<link rel="stylesheet" href="{up}assets/styles.css">
{MATHJAX}
{extra}
</head>
<body>
{HUB_BAR.format(up=up, here=html.escape(here))}
"""


def topnav(up, active=""):
    items = [
        ("index.html", "Home", "home"),
        ("syllabus.html", "Syllabus &amp; Pattern", ""),
        ("papers/index.html", "Solved Papers", ""),
        ("strategy.html", "Exam Strategy", ""),
    ]
    out = ['<nav class="topnav">']
    for href, label, cls in items:
        c = f' class="{cls}"' if cls else ""
        style = ' style="background:#1e3a8a;color:#fff;"' if href == active else ""
        out.append(f'<a href="{up}{href}"{c}{style}>{label}</a>')
    out.append("</nav>")
    return "\n".join(out)


FOOTER = """<footer class="site-footer">
  <p><strong>NRSTATLAB</strong> &middot; CSIR NET Mathematical Sciences &middot; Free study material for aspirants.</p>
  <p>Question papers belong to CSIR-HRDG / NTA and are reproduced here only for educational discussion. Solutions are our own.</p>
</footer>
</body>
</html>
"""

REVEAL_JS = """<script>
(function () {
  var root = document.getElementById('paper');
  if (!root) return;
  var all = function () { return Array.prototype.slice.call(root.querySelectorAll('details')); };
  var set = function (open) { all().forEach(function (d) { d.open = open; }); };
  var openAll = document.getElementById('open-all');
  var shutAll = document.getElementById('shut-all');
  if (openAll) openAll.addEventListener('click', function () { set(true); });
  if (shutAll) shutAll.addEventListener('click', function () { set(false); });

  var filter = document.getElementById('topic-filter');
  if (filter) {
    filter.addEventListener('change', function () {
      var want = filter.value;
      root.querySelectorAll('.mcq').forEach(function (q) {
        q.hidden = !(want === 'all' || (q.dataset.topic || '') === want);
      });
      root.querySelectorAll('.part-head').forEach(function (h) {
        var n = 0, el = h.nextElementSibling;
        while (el && !el.classList.contains('part-head')) {
          if (el.classList.contains('mcq') && !el.hidden) n++;
          el = el.nextElementSibling;
        }
        h.hidden = n === 0;
      });
    });
  }
})();
</script>"""


def render_steps(q):
    bits = []
    if q.get("given"):
        bits.append(f'<div class="concept"><b>What is given.</b> {q["given"]}</div>')
    if q.get("concept"):
        bits.append(f'<div class="concept"><b>Idea used.</b> {q["concept"]}</div>')
    steps = q.get("steps") or []
    if steps:
        bits.append('<ol class="steps">')
        bits.extend(f"<li>{s}</li>" for s in steps)
        bits.append("</ol>")
    if q.get("conclusion"):
        bits.append(f"<p>{q['conclusion']}</p>")
    if q.get("pitfall"):
        bits.append(f'<div class="pitfall"><b>Common slip.</b> {q["pitfall"]}</div>')
    return "\n".join(bits)


def answer_label(q):
    ans = q.get("answer") or []
    if not ans:
        return "Answer not yet settled"
    names = ", ".join(f"({i})" for i in ans)
    opts = q.get("options") or []
    if len(ans) == 1 and 1 <= ans[0] <= len(opts):
        return f"Answer: {names}"
    return f"Answer: {names}"


def render_question(q):
    solved = bool(q.get("body")) and bool(q.get("answer"))
    if not solved:
        return ""
    ans = set(q.get("answer") or [])
    topic = q.get("topic", "")
    o = [f'<div class="mcq" id="q{q["n"]}" data-topic="{html.escape(topic)}">']
    qid = f'<span class="qid">ID {html.escape(str(q.get("qid","")))}</span>' if q.get("qid") else ""
    o.append(f'<div class="q">{qid}<span class="qn">Q{q["n"]}.</span> {q["body"]}</div>')
    if q.get("options"):
        o.append('<ol class="options">')
        for i, opt in enumerate(q["options"], 1):
            cls = ' class="correct"' if i in ans else ""
            o.append(f"<li{cls}>{opt}</li>")
        o.append("</ol>")
    o.append("<details><summary>Show step-by-step solution</summary>")
    o.append(f'<p class="verdict"><b>{answer_label(q)}</b></p>')
    o.append(render_steps(q))
    o.append("</details>")
    tags = [t for t in [topic, q.get("subtopic")] if t]
    if tags:
        o.append('<p class="tags">' + "".join(f'<span class="tag">{html.escape(t)}</span>' for t in tags) + "</p>")
    o.append("</div>")
    return "\n".join(o)


def topic_chart(paper, solved):
    counts = {}
    for q in solved:
        counts[q.get("topic", "Unclassified")] = counts.get(q.get("topic", "Unclassified"), 0) + 1
    if not counts:
        return ""
    top = max(counts.values())
    rows = []
    for topic, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0])):
        rows.append(
            f'<div class="chart-row"><span class="chart-label">{html.escape(topic)}</span>'
            f'<span class="chart-track"><span class="chart-bar" style="width:{n / top * 100:.1f}%">{n}</span></span></div>'
        )
    return (
        '<div class="chartbox"><h3>Topic distribution</h3>'
        '<p class="chart-note">How the solved questions of this paper split across the syllabus. '
        "Use it to decide what to revise first — bars are scaled to the largest topic.</p>"
        + "".join(rows)
        + "</div>"
    )


def build_paper(paper):
    total = len(paper["questions"])
    solved = [q for q in paper["questions"] if q.get("body") and q.get("answer")]
    pct = 100.0 * len(solved) / total if total else 0.0
    slug = paper["slug"]
    canonical = f"{SITE}/papers/{slug}.html"
    desc = f'{paper["subject"]} (Code {paper["code"]}) · {paper["exam_date"]} · {total} questions with step-by-step solutions'

    parts = ""
    for part in paper["parts"]:
        qs = [q for q in solved if q["part"] == part["id"]]
        parts += (
            f'<div class="part-head" id="part{part["id"].lower()}"><h2>{html.escape(part["name"])}</h2>'
            f'<p>{part["note"]}</p></div>\n'
        )
        if qs:
            parts += "\n".join(render_question(q) for q in qs) + "\n"
        else:
            parts += (
                '<div class="note"><strong>Not transcribed yet.</strong> '
                f'Questions {part["from"]}&ndash;{part["to"]} of this paper are still being extracted from the '
                "source PDF and worked out. They appear here as soon as each solution is checked.</div>\n"
            )

    topics = sorted({q.get("topic", "") for q in solved if q.get("topic")})
    options = "".join(f'<option value="{html.escape(t)}">{html.escape(t)}</option>' for t in topics)

    body = f"""{head(paper["title"], desc, canonical, "../", paper["short_title"])}
{topnav("../", "papers/index.html")}

<header class="site-header">
  <h1>{html.escape(paper["short_title"])}</h1>
  <p>{html.escape(paper["subject"])} (Code {html.escape(paper["code"])}) &middot; {html.escape(paper["exam_date"])} &middot; {html.escape(paper["shift"])}</p>
  <span class="badge">{total} questions &middot; every step shown</span>
</header>

<main class="container">

  <div class="coverage">
    <h3>Solutions ready: {len(solved)} of {total}</h3>
    <span class="cov-track"><span class="cov-bar" style="width:{max(pct, 6):.1f}%">{pct:.0f}%</span></span>
    <p class="cov-note">{html.escape(paper.get("coverage_note", ""))}</p>
  </div>

  {topic_chart(paper, solved)}

  <div class="qtools">
    <button type="button" id="open-all">Reveal every solution</button>
    <button type="button" id="shut-all">Hide every solution</button>
    <span class="spacer"></span>
    <label for="topic-filter">Show topic</label>
    <select id="topic-filter"><option value="all">All topics</option>{options}</select>
  </div>

  <div id="paper">
{parts}
  </div>

</main>

{REVEAL_JS}
{FOOTER}"""
    (OUT / f"{slug}.html").write_text(body, encoding="utf-8")
    return len(solved), total


def build_index(papers):
    cards = []
    for paper, solved, total in papers:
        pct = 100.0 * solved / total if total else 0.0
        if solved == 0:
            status = '<span class="status queued">Queued</span>'
        elif solved < total:
            status = f'<span class="status wip">{solved}/{total} solved</span>'
        else:
            status = '<span class="status done">Fully solved</span>'
        cards.append(f"""      <a class="paper-card" href="{paper['slug']}.html">
        <span class="meta">{html.escape(paper['exam_date'])} &middot; {html.escape(paper['shift'])}</span>
        <h3>{html.escape(paper['short_title'])}</h3>
        <p>{html.escape(paper['blurb'])}</p>
        <span class="foot"><span>{total} questions &middot; {pct:.0f}% worked</span>{status}</span>
      </a>""")

    canonical = f"{SITE}/papers/index.html"
    body = f"""{head("CSIR NET Mathematics — Solved Question Papers", "Previous-year CSIR NET Mathematical Sciences papers with every question worked out step by step.", canonical, "../", "Solved Papers")}
{topnav("../", "papers/index.html")}

<header class="site-header">
  <h1>Solved Question Papers</h1>
  <p>Previous-year CSIR NET Mathematical Sciences papers, worked out question by question</p>
  <span class="badge">{len(papers)} paper{'s' if len(papers) != 1 else ''} in the collection</span>
</header>

<main class="container">
  <section class="unit-content">
    <h2>How these papers are written up</h2>
    <p>Every question is reproduced in full, typeset with MathJax rather than pasted as a
    screenshot, so it stays readable on a phone and can be searched. Under each question a
    single click opens the worked solution: what the question gives you, the idea the setter
    is testing, then the algebra one numbered step at a time, and finally the trap that makes
    aspirants pick the wrong option.</p>
    <p>Nothing is guessed. A question is published only after its solution has been worked
    through independently, so a paper often appears here in instalments rather than all at once.</p>
  </section>

  <div class="unit-grid">
{chr(10).join(cards)}
  </div>

  <section class="unit-content" style="margin-top:2rem;">
    <h2>Want a particular paper solved?</h2>
    <p>Upload the question paper PDF to the <code>papers-inbox/</code> folder of this repository
    and it joins the queue. The full procedure is in
    <a href="../HOW-TO-ADD-A-PAPER.html">How to add a paper</a>.</p>
  </section>
</main>

{FOOTER}"""
    (OUT / "index.html").write_text(body, encoding="utf-8")


def main():
    OUT.mkdir(exist_ok=True)
    files = sorted(DATA.glob("*.json"), reverse=True)
    if not files:
        print("no papers in data/papers/", file=sys.stderr)
        return 1
    built = []
    for f in files:
        paper = json.loads(f.read_text(encoding="utf-8"))
        solved, total = build_paper(paper)
        built.append((paper, solved, total))
        print(f"built papers/{paper['slug']}.html  ({solved}/{total} solved)")
    build_index(built)
    print(f"built papers/index.html  ({len(built)} paper(s))")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
