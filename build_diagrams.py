"""Generate the architecture diagrams as theme-aware SVG (stdlib only).

    python build_diagrams.py        # writes ./assets/*.svg (light and dark)

Each diagram shows facts that are written in the matching case study. System fonts only: an SVG
shown through <img> on GitHub cannot load web fonts.
"""
from pathlib import Path
from xml.sax.saxutils import escape

OUT = Path(__file__).resolve().parent / "assets"
SERIF = "Georgia, 'Times New Roman', serif"
SANS = "Segoe UI, system-ui, -apple-system, Arial, sans-serif"
T = {
    "light": dict(bg="#F7F8FA", box="#FFFFFF", line="#CBD2DC", ink="#101828", mute="#3B455A", faint="#667085",
                  blue="#2347D6", soft="#EEF2FF", warn="#9A5B00", ok="#1B7F4B", grid="#E6E9F0"),
    "dark": dict(bg="#0D1117", box="#161B22", line="#30363D", ink="#E6EDF3", mute="#B4BDC9", faint="#8B949E",
                 blue="#6E8BFF", soft="#1B2340", warn="#E3B341", ok="#56D364", grid="#171C24"),
}


class Canvas:
    def __init__(self, t, w, h, label):
        self.c, self.w, self.h, self.label, self.parts = T[t], w, h, label, []
        self.parts.append(f'<defs><marker id="a" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                          f'orient="auto-start-reverse"><path d="M0 0L10 5L0 10z" fill="{self.c["faint"]}"/></marker>'
                          f'<pattern id="g" width="40" height="40" patternUnits="userSpaceOnUse"><path d="M40 0H0V40" fill="none" '
                          f'stroke="{self.c["grid"]}" stroke-width="1"/></pattern></defs>')
        self.parts.append(f'<rect width="{w}" height="{h}" fill="{self.c["bg"]}"/><rect width="{w}" height="{h}" fill="url(#g)"/>')

    def box(self, x, y, w, h, title, sub=(), kind="plain"):
        c = self.c
        fill = c["soft"] if kind == "accent" else c["box"]
        stroke = c["blue"] if kind == "accent" else c["line"]
        sw = 2.5 if kind == "accent" else 1.5
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="10" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')
        ty = y + 32
        self.parts.append(f'<text x="{x + w / 2}" y="{ty}" text-anchor="middle" font-family="{SANS}" font-size="22" '
                          f'font-weight="700" fill="{c["ink"]}">{escape(title)}</text>')
        for i, line in enumerate(sub):
            self.parts.append(f'<text x="{x + w / 2}" y="{ty + 26 + i * 22}" text-anchor="middle" font-family="{SANS}" '
                              f'font-size="17" fill="{c["mute"]}">{escape(line)}</text>')

    def zone(self, x, y, w, h, title):
        c = self.c
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="none" stroke="{c["warn"]}" '
                          f'stroke-width="2" stroke-dasharray="8 6"/>')
        self.parts.append(f'<text x="{x + 16}" y="{y + 26}" font-family="{SANS}" font-size="17" font-weight="700" fill="{c["warn"]}">{escape(title)}</text>')

    def arrow(self, x1, y1, x2, y2, label="", dashed=False):
        c = self.c
        d = ' stroke-dasharray="7 6"' if dashed else ""
        self.parts.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{c["faint"]}" stroke-width="2"{d} marker-end="url(#a)"/>')
        if label:
            self.parts.append(f'<text x="{(x1 + x2) / 2 + 8}" y="{(y1 + y2) / 2 - 6}" font-family="{SANS}" font-size="15" fill="{c["faint"]}">{escape(label)}</text>')

    def note(self, x, y, text, anchor="start", size=17, color=None):
        self.parts.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{SANS}" font-size="{size}" '
                          f'fill="{color or self.c["mute"]}">{escape(text)}</text>')

    def svg(self):
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" viewBox="0 0 {self.w} {self.h}" '
                f'role="img" aria-label="{escape(self.label)}">\n' + "\n".join(self.parts) + "\n</svg>\n")


def rankwant(t):
    s = Canvas(t, 1200, 520, "RankWant today: one host, a default network and an internal judge network")
    s.box(40, 24, 300, 96, "Web", ("Next.js, React 19, SSR", "10 locales"), "accent")
    s.box(450, 24, 330, 96, "API", ("Django 5.2 LTS + DRF", "REST /api/v1, OpenAPI"), "accent")
    s.box(890, 24, 270, 96, "Worker", ("Celery: results,", "rejudge, ratings"))
    s.arrow(340, 72, 450, 72, "REST")
    s.arrow(780, 72, 890, 72)
    s.box(40, 190, 250, 90, "PostgreSQL", ("metadata, standings",))
    s.box(340, 190, 250, 90, "Redis", ("session, Celery",))
    s.box(640, 190, 250, 90, "MinIO (S3)", ("statements, test data",))
    s.box(940, 190, 220, 90, "judge-queue", ("separate Redis",), "accent")
    s.arrow(560, 120, 165, 190)
    s.arrow(615, 120, 465, 190)
    s.arrow(680, 120, 765, 190)
    s.arrow(1000, 120, 1050, 190)
    s.zone(40, 320, 1120, 180, "judge-net (internal: true): no route to the internet or to postgres:5432 and api:8000")
    s.box(70, 356, 400, 86, "judge (Go + nsjail)", ("pulls jobs, no DATABASE_URL",))
    s.box(500, 356, 300, 86, "Preflight", ("connects to postgres/api;", "success = exit 1"))
    s.box(830, 356, 300, 86, "judge-ro (MinIO user)", ("read-only on test data",))
    s.arrow(1050, 280, 1050, 320, "queue", dashed=True)
    s.note(70, 478, "Measured gap that led here (2026-09-24): from the judge, postgres:5432 and 1.1.1.1:443 were open.", size=16)
    return s.svg()


def tg_solver(t):
    s = Canvas(t, 1200, 420, "tg-solver pipeline: from a group message to a sent reply or a held draft")
    xs = [30, 260, 490, 720, 950]
    s.box(xs[0], 24, 220, 100, "Group message", ("text and photos",))
    s.box(xs[1], 24, 220, 100, "Listener", ("every 15 s, no LLM",))
    s.box(xs[2], 24, 220, 100, "Batch", ("45 s of quiet,", "one request"))
    s.box(xs[3], 24, 220, 100, "Triage", ("small model:", "task or not"), "accent")
    s.box(xs[4], 24, 220, 100, "Solve", ("large model,", "JSON only"), "accent")
    for a, b in zip(xs, xs[1:]):
        s.arrow(a + 220, 74, b, 74)
    s.box(30, 190, 220, 100, "Lint", ("phone-width rules,", "one reformat pass"))
    s.box(290, 190, 270, 100, "Verify", ("independent re-solve,", "compares every number"), "accent")
    s.box(600, 190, 270, 100, "Code gates", ("statement matches,", "no earlier contradiction"))
    s.box(960, 190, 210, 46, "Send", ("",))
    s.box(960, 252, 210, 46, "Hold as draft", ("",))
    s.arrow(1060, 124, 140, 190)
    s.arrow(250, 240, 290, 240)
    s.arrow(560, 240, 600, 240)
    s.arrow(870, 224, 960, 213)
    s.note(880, 198, "pass", size=15, color=s.c["faint"])
    s.arrow(870, 256, 960, 275)
    s.note(880, 300, "any gate fails", size=15, color=s.c["faint"])
    s.note(30, 345, "The model has no tools and returns JSON only; Python alone sends.", size=20, color=s.c["ink"])
    s.note(30, 375, "A reply that fails a gate or the verifier is held for the owner instead of being sent.")
    return s.svg()


def attendance(t):
    s = Canvas(t, 1200, 360, "Attendance system pipeline: camera, detection, embedding, matching, local buffer, outbound sync")
    xs = [20, 215, 410, 605, 800, 995]
    labels = [("RTSP camera", ("entry, optional exit",)), ("Detect", ("YOLOv11n-face",)),
              ("Embed", ("ArcFace R50,", "512-dim")), ("Match", ("cosine search,", "FAISS in RAM")),
              ("Local buffer", ("SQLite, temporary",)), ("Outbound sync", ("HTTPS POST to the", "client system"))]
    for x, (title, sub) in zip(xs, labels):
        s.box(x, 40, 185, 112, title, sub, "accent" if title in ("Detect", "Embed", "Match") else "plain")
    for a, b in zip(xs, xs[1:]):
        s.arrow(a + 185, 96, b, 96)
    s.note(20, 215, "Headless workers; the integration is outbound-only.", size=20, color=s.c["ink"])
    s.note(20, 248, "Events are deleted from the local database after a successful sync: it is a buffer, not a history.")
    s.note(20, 278, "Delivered as one archive: unzip, edit .env, run. Only the NVIDIA driver is needed on the machine.")
    return s.svg()


def project_alpha(t):
    s = Canvas(t, 1200, 470, "Project Alpha: the ten-stage documentation pipeline")
    s.box(30, 24, 260, 84, "Idea intake", ("evaluation, selection",))
    s.note(310, 72, "gateway before stage 01; stages then run in order 01 to 10, left to right, row by row", color=s.c["faint"])
    names = [("01", "Vision"), ("02", "Problem"), ("03", "Market"), ("04", "PRD"), ("05", "Domain model"),
             ("06", "Architecture"), ("07", "ADR"), ("08", "Technical spec"), ("09", "Plan"), ("10", "Operations")]
    for i, (n, name) in enumerate(names):
        x = 30 + (i % 5) * 232
        y = 140 + (i // 5) * 100
        s.box(x, y, 212, 64, f"{n} {name}", (), "accent" if n in ("04", "06", "07") else "plain")
    for i in range(4):
        x = 30 + i * 232 + 212
        s.arrow(x, 172, x + 20, 172)
        s.arrow(x, 272, x + 20, 272)
    s.arrow(1100, 204, 140, 240)
    s.box(30, 350, 360, 60, "Global audit", ("",))
    s.box(430, 350, 360, 60, "Production ready", ("",))
    s.arrow(390, 380, 430, 380)
    s.note(820, 372, "Stage states: NOT_STARTED, IN_PROGRESS,", size=15, color=s.c["ink"])
    s.note(820, 394, "REVIEW, PASSED. BLOCKED goes back to IN_PROGRESS.", size=15, color=s.c["ink"])
    return s.svg()


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    made = 0
    for t in T:
        for name, fn in (("rankwant-architecture", rankwant), ("tg-solver-pipeline", tg_solver),
                         ("attendance-pipeline", attendance), ("project-alpha-stages", project_alpha)):
            (OUT / f"{name}-{t}.svg").write_text(fn(t), encoding="utf-8")
            made += 1
    print(f"{made} diagrams -> {OUT}")


if __name__ == "__main__":
    main()
