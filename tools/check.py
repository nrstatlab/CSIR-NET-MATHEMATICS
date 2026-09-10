#!/usr/bin/env python3
"""Validate the paper data and the generated site before pushing.

Checks, in order:
  1. every JSON question has balanced $ delimiters and no LaTeX outside math mode
  2. answers point at options that exist
  3. every generated page has well-formed tag nesting
  4. every internal link resolves to a file that exists
Exits non-zero on the first category that fails, printing what to fix.
"""

import html.parser
import json
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
problems = []


def text_fields(q):
    for key in ("body", "given", "concept", "conclusion", "pitfall"):
        if q.get(key):
            yield key, q[key]
    for i, opt in enumerate(q.get("options") or []):
        yield f"options[{i}]", opt
    for i, step in enumerate(q.get("steps") or []):
        yield f"steps[{i}]", step


def check_json():
    for f in sorted((ROOT / "data" / "papers").glob("*.json")):
        paper = json.loads(f.read_text(encoding="utf-8"))
        for q in paper["questions"]:
            n = q["n"]
            for key, value in text_fields(q):
                if value.count("$") % 2:
                    problems.append(f"{f.name} Q{n} {key}: unbalanced $")
                outside = re.sub(r"\$\$.*?\$\$", "", value, flags=re.S)
                outside = re.sub(r"\$[^$]*\$", "", outside)
                if "\\" in outside:
                    stray = outside.strip()[:70]
                    problems.append(f"{f.name} Q{n} {key}: LaTeX outside math mode: {stray!r}")
            answer, options = q.get("answer") or [], q.get("options") or []
            if answer and not options:
                problems.append(f"{f.name} Q{n}: answer given but no options")
            for a in answer:
                if not 1 <= a <= len(options):
                    problems.append(f"{f.name} Q{n}: answer {a} is outside 1..{len(options)}")
            if q.get("body") and not answer:
                problems.append(f"{f.name} Q{n}: body transcribed but no answer recorded")
            if q.get("type") == "single" and len(answer) > 1:
                problems.append(f"{f.name} Q{n}: single-answer question has {len(answer)} answers")


class Nesting(html.parser.HTMLParser):
    VOID = {"br", "hr", "img", "meta", "link", "input", "source",
            "col", "area", "base", "embed", "param", "track", "wbr"}

    def __init__(self):
        super().__init__()
        self.stack, self.errors = [], []

    def handle_starttag(self, tag, attrs):
        if tag not in self.VOID:
            self.stack.append(tag)

    def handle_endtag(self, tag):
        if tag in self.VOID:
            return
        if tag in self.stack:
            while self.stack[-1] != tag:
                self.errors.append(f"line {self.getpos()[0]}: <{self.stack.pop()}> never closed")
            self.stack.pop()
        else:
            self.errors.append(f"line {self.getpos()[0]}: stray </{tag}>")


def check_html():
    for f in sorted(ROOT.rglob("*.html")):
        text = f.read_text(encoding="utf-8")
        parser = Nesting()
        parser.feed(text)
        rel = f.relative_to(ROOT)
        for err in parser.errors + [f"<{t}> never closed" for t in parser.stack]:
            problems.append(f"{rel}: {err}")
        for href in re.findall(r'(?:href|src)="([^"]+)"', text):
            if href.startswith(("http", "#", "mailto:", "data:")):
                continue
            if not (f.parent / href.split("#")[0]).resolve().exists():
                problems.append(f"{rel}: broken link to {href}")


def main():
    check_json()
    check_html()
    if problems:
        for p in problems:
            print(p, file=sys.stderr)
        print(f"\n{len(problems)} problem(s)", file=sys.stderr)
        return 1
    print("data and site check out")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
