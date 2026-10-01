"""Generates the animated SVG assets for the GitHub profile README."""
import base64
import json
from pathlib import Path
from html import escape

OUT = Path(__file__).parent / "assets"
OUT.mkdir(exist_ok=True)

# Palette: "night shift in the control room, Kerala sunset on the packets"
VOID = "#05070F"      # background
PANEL = "#0A1024"     # node / card fill
WIRE = "#1E2A55"      # idle edges, borders
SIGNAL = "#2EF2C8"    # teal: live data
PLASMA = "#9D7BFF"    # violet: AI / agents
EMBER = "#FFB54A"     # amber: packets, cursor
TEXT = "#EAF0FF"
MUTED = "#8C98C8"

MONO = "'JetBrains Mono','SFMono-Regular',Consolas,'Liberation Mono',Menlo,monospace"
SANS = "'Segoe UI','Inter',-apple-system,'Helvetica Neue',Arial,sans-serif"

REDUCED = """
@media (prefers-reduced-motion: reduce) { * { animation: none !important; } }
"""


def write(name, svg):
    (OUT / name).write_text(svg.strip() + "\n", encoding="utf-8")
    print(f"{name}: {len(svg)/1024:.1f} KB")


# ---------------------------------------------------------------- header ----
def header():
    W, H = 1200, 420
    nodes = {
        "ingest":    (690, 210, SIGNAL),
        "spark":     (800, 130, SIGNAL),
        "temporal":  (800, 290, SIGNAL),
        "cassandra": (915, 80, SIGNAL),
        "neo4j":     (915, 190, SIGNAL),
        "agents":    (1030, 250, PLASMA),
        "api":       (1120, 160, EMBER),
    }
    edges = [
        ("ingest", "spark"), ("ingest", "temporal"),
        ("spark", "cassandra"), ("spark", "neo4j"),
        ("temporal", "agents"), ("neo4j", "agents"),
        ("agents", "api"), ("cassandra", "api"),
    ]

    def curve(a, b):
        x1, y1, _ = nodes[a]
        x2, y2, _ = nodes[b]
        mx = (x1 + x2) / 2
        return f"M{x1},{y1} C{mx},{y1} {mx},{y2} {x2},{y2}"

    edge_svg, packet_svg = [], []
    for i, (a, b) in enumerate(edges):
        d = curve(a, b)
        pid = f"e{i}"
        edge_svg.append(f'<path id="{pid}" d="{d}" class="wire"/>')
        edge_svg.append(f'<path d="{d}" class="flow" style="animation-delay:-{i*0.4:.1f}s"/>')
        colour = PLASMA if b == "agents" else EMBER
        for k in range(2):
            begin = -(i * 0.35 + k * 1.6)
            packet_svg.append(
                f'<circle r="3.2" fill="{colour}" filter="url(#glow)">'
                f'<animateMotion dur="3.2s" begin="{begin:.2f}s" repeatCount="indefinite" '
                f'keyPoints="0;1" keyTimes="0;1" calcMode="spline" keySplines="0.45 0 0.55 1">'
                f'<mpath href="#{pid}"/></animateMotion></circle>'
            )

    node_svg = []
    for i, (name, (x, y, c)) in enumerate(nodes.items()):
        node_svg.append(
            f'<circle cx="{x}" cy="{y}" r="22" fill="none" stroke="{c}" class="ring" '
            f'style="animation-delay:{i*0.45:.2f}s"/>'
            f'<circle cx="{x}" cy="{y}" r="22" fill="{PANEL}" stroke="{c}" stroke-width="1.5"/>'
            f'<circle cx="{x}" cy="{y}" r="5" fill="{c}" class="core" '
            f'style="animation-delay:{i*0.45:.2f}s"/>'
            f'<text x="{x}" y="{y+42}" class="nlabel">{name}</text>'
        )
    # agents: three orbiting sub-agents
    ax, ay, _ = nodes["agents"]
    orbit = "".join(
        f'<g><circle cx="{ax}" cy="{ay-31}" r="2.6" fill="{PLASMA}"/>'
        f'<animateTransform attributeName="transform" type="rotate" '
        f'from="{a} {ax} {ay}" to="{a+360} {ax} {ay}" dur="6s" repeatCount="indefinite"/></g>'
        for a in (0, 120, 240)
    )

    # typing line: one clip per phrase, chained with SMIL
    phrases = [
        "building GenAI apps on real data",
        "turning questions into SQL with LLMs",
        "grounding LLMs with vector search",
        "wiring multi-agent AI systems",
        "orchestrating distributed pipelines",
        "writing about Python for data engineering",
        "painting when the builds are green",
    ]
    CH = 11.4           # enforced glyph advance via textLength
    TX, TY = 96, 292
    typed, clips, cursor_vals = [], [], []
    n = len(phrases)
    for i, p in enumerate(phrases):
        w = round(len(p) * CH, 1)
        begin = "0s;t%d.end" % (n - 1) if i == 0 else f"t{i-1}.end"
        clips.append(
            f'<clipPath id="c{i}"><rect x="{TX}" y="{TY-22}" height="30" width="0">'
            f'<animate id="t{i}" attributeName="width" begin="{begin}" dur="4.4s" '
            f'values="0;{w};{w};0" keyTimes="0;0.4;0.86;1" fill="remove"/></rect></clipPath>'
        )
        typed.append(
            f'<text x="{TX}" y="{TY}" class="typed" textLength="{w}" lengthAdjust="spacingAndGlyphs" '
            f'clip-path="url(#c{i})">{escape(p)}</text>'
        )
        cursor_vals.append(
            f'<animate attributeName="x" begin="{"0s;t%d.end" % (n-1) if i == 0 else f"t{i-1}.end"}" '
            f'dur="4.4s" values="{TX+2};{TX+w+4};{TX+w+4};{TX+2}" keyTimes="0;0.4;0.86;1" fill="freeze"/>'
        )

    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t d">
<title id="t">Jeevan Varghese</title>
<desc id="d">Senior data and AI engineer working on GenAI, vector search and text-to-SQL. An animated workflow graph shows data moving from ingestion through Spark and Temporal into Cassandra, Neo4j and a group of AI agents.</desc>
<defs>
  <pattern id="dots" width="24" height="24" patternUnits="userSpaceOnUse">
    <circle cx="1" cy="1" r="1" fill="#141C3A"/>
  </pattern>
  <radialGradient id="halo" cx="0.76" cy="0.45" r="0.45">
    <stop offset="0" stop-color="{PLASMA}" stop-opacity="0.16"/>
    <stop offset="1" stop-color="{PLASMA}" stop-opacity="0"/>
  </radialGradient>
  <linearGradient id="scan" x1="0" x2="0" y1="0" y2="1">
    <stop offset="0" stop-color="{SIGNAL}" stop-opacity="0"/>
    <stop offset="0.5" stop-color="{SIGNAL}" stop-opacity="0.07"/>
    <stop offset="1" stop-color="{SIGNAL}" stop-opacity="0"/>
  </linearGradient>
  <filter id="glow" x="-200%" y="-200%" width="500%" height="500%">
    <feGaussianBlur stdDeviation="2.4" result="b"/>
    <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
  </filter>
  {''.join(clips)}
</defs>
<style>
  .wire {{ fill:none; stroke:{WIRE}; stroke-width:1.5; }}
  .flow {{ fill:none; stroke:{SIGNAL}; stroke-width:1.2; stroke-opacity:.45;
          stroke-dasharray:3 11; animation: flow 1.6s linear infinite; }}
  @keyframes flow {{ to {{ stroke-dashoffset:-28; }} }}
  .ring {{ stroke-width:1.2; opacity:0; transform-box:fill-box; transform-origin:center;
          animation: ring 3.2s ease-out infinite; }}
  @keyframes ring {{ 0% {{ opacity:.7; transform:scale(1); }} 70%,100% {{ opacity:0; transform:scale(1.7); }} }}
  .core {{ animation: core 3.2s ease-in-out infinite; }}
  @keyframes core {{ 0%,100% {{ opacity:.45; }} 20% {{ opacity:1; }} }}
  .nlabel {{ font:500 12px {MONO}; fill:{MUTED}; text-anchor:middle; }}
  .prompt {{ font:500 15px {MONO}; fill:{SIGNAL}; }}
  .name {{ font:700 66px {SANS}; fill:{TEXT}; letter-spacing:-1.5px; }}
  .role {{ font:400 22px {SANS}; fill:{MUTED}; }}
  .typed {{ font:500 19px {MONO}; fill:{SIGNAL}; }}
  .caret {{ fill:{EMBER}; animation: blink 1s steps(1) infinite; }}
  @keyframes blink {{ 50% {{ opacity:0; }} }}
  .status {{ font:500 13px {MONO}; fill:#5A6694; }}
  .live {{ fill:{SIGNAL}; animation: core 1.6s ease-in-out infinite; }}
  .sweep {{ animation: sweep 7s linear infinite; }}
  @keyframes sweep {{ from {{ transform:translateY(-140px); }} to {{ transform:translateY(560px); }} }}
  {REDUCED}
</style>

<rect width="{W}" height="{H}" rx="18" fill="{VOID}"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#dots)"/>
<rect width="{W}" height="{H}" rx="18" fill="url(#halo)"/>
<rect class="sweep" x="0" y="0" width="{W}" height="140" fill="url(#scan)"/>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{WIRE}"/>

<text x="64" y="104" class="prompt">~/jeevanvsan $ whoami</text>
<text x="60" y="182" class="name">Jeevan Varghese</text>
<text x="64" y="224" class="role">Senior data and AI engineer</text>

<text x="64" y="{TY}" class="prompt" style="font-size:19px">&gt;</text>
{''.join(typed)}
<rect class="caret" x="{TX+2}" y="{TY-17}" width="10" height="21" rx="1">{''.join(cursor_vals)}</rect>

<line x1="64" y1="340" x2="600" y2="340" stroke="{WIRE}"/>
<circle class="live" cx="70" cy="368" r="4"/>
<text x="84" y="372" class="status">workflow jeevan.run() is live in Alappuzha, Kerala  UTC+05:30</text>

<g>{''.join(edge_svg)}</g>
<g>{''.join(packet_svg)}</g>
<g>{''.join(node_svg)}</g>
{orbit}
</svg>"""
    write("header.svg", svg)


# ----------------------------------------------------------------- stack ----
def stack():
    lanes = [
        ("data and orchestration", SIGNAL,
         ["Python", "Apache Spark", "Cassandra", "Temporal", "PostgreSQL", "Neo4j"]),
        ("genai and retrieval", PLASMA,
         ["LLMs", "RAG", "Vector DBs", "Text-to-SQL", "Embeddings", "LangGraph"]),
        ("backends and ops", EMBER,
         ["FastAPI", "Docker", "Traefik", "GitHub Actions"]),
    ]
    W, H = 1200, 350
    X0, GAP, CW = 260, 26, 8.8
    body, defs = [], []
    for li, (label, colour, tools) in enumerate(lanes):
        y = 82 + li * 100
        widths = [round(len(t) * CW + 38) for t in tools]
        xs, x = [], X0
        for w in widths:
            xs.append(x)
            x += w + GAP
        end = x - GAP
        body.append(f'<text x="48" y="{y+5}" class="lane">{label}</text>')
        body.append(f'<line x1="{X0-20}" y1="{y}" x2="{end+20}" y2="{y}" stroke="{WIRE}" stroke-width="1.5"/>')
        # travelling light
        gid = f"lg{li}"
        defs.append(
            f'<linearGradient id="{gid}" x1="0" x2="1"><stop offset="0" stop-color="{colour}" stop-opacity="0"/>'
            f'<stop offset="0.8" stop-color="{colour}" stop-opacity="0.9"/><stop offset="1" stop-color="{colour}" stop-opacity="0"/></linearGradient>'
        )
        body.append(
            f'<rect y="{y-1.5}" height="3" width="120" fill="url(#{gid})">'
            f'<animate attributeName="x" from="{X0-140}" to="{end+20}" dur="{5+li}s" repeatCount="indefinite"/></rect>'
        )
        for i, (t, w, x) in enumerate(zip(tools, widths, xs)):
            delay = i * (5 + li) / len(tools)
            body.append(
                f'<g><rect x="{x}" y="{y-19}" width="{w}" height="38" rx="19" fill="{PANEL}" stroke="{WIRE}" stroke-width="1.5"/>'
                f'<rect x="{x}" y="{y-19}" width="{w}" height="38" rx="19" fill="none" stroke="{colour}" stroke-width="1.5" class="lit" '
                f'style="animation-duration:{5+li}s;animation-delay:{delay:.2f}s"/>'
                f'<circle cx="{x+17}" cy="{y}" r="3.5" fill="{colour}"/>'
                f'<text x="{x+28}" y="{y+5}" class="tool">{t}</text></g>'
            )
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">Tech stack: Python, Apache Spark, Cassandra, Temporal, PostgreSQL, Neo4j, LLMs, RAG, vector databases, text-to-SQL, embeddings, LangGraph, FastAPI, Docker, Traefik, GitHub Actions</title>
<defs>{''.join(defs)}</defs>
<style>
  .lane {{ font:500 14px {MONO}; fill:{MUTED}; }}
  .tool {{ font:600 15px {SANS}; fill:{TEXT}; }}
  .lit {{ opacity:0; animation-name: lit; animation-iteration-count: infinite; animation-timing-function: ease-out; }}
  @keyframes lit {{ 0%,100% {{ opacity:0; }} 8% {{ opacity:1; }} 30% {{ opacity:0; }} }}
  {REDUCED}
</style>
<rect width="{W}" height="{H}" rx="18" fill="{VOID}"/>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="18" fill="none" stroke="{WIRE}"/>
{''.join(body)}
</svg>"""
    write("stack.svg", svg)


# ----------------------------------------------------------- repo cards -----
def card(fname, name, lines, tag, colour):
    W, H = 580, 190
    desc = "".join(
        f'<text x="32" y="{96 + i*24}" class="desc">{escape(l)}</text>' for i, l in enumerate(lines)
    )
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">{escape(name)}: {escape(' '.join(lines))}</title>
<defs>
  <linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="{colour}" stop-opacity="0"/>
  <stop offset="0.5" stop-color="{colour}"/><stop offset="1" stop-color="{colour}" stop-opacity="0"/></linearGradient>
</defs>
<style>
  .name {{ font:700 26px {SANS}; fill:{TEXT}; }}
  .desc {{ font:400 15.5px {SANS}; fill:{MUTED}; }}
  .tag {{ font:500 13px {MONO}; fill:{colour}; }}
  .live {{ animation: pulse 2s ease-in-out infinite; }}
  @keyframes pulse {{ 0%,100% {{ opacity:.35; }} 50% {{ opacity:1; }} }}
  {REDUCED}
</style>
<rect width="{W}" height="{H}" rx="16" fill="{PANEL}"/>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{WIRE}"/>
<clipPath id="cc"><rect width="{W}" height="{H}" rx="16"/></clipPath>
<rect y="0" height="2" width="200" fill="url(#edge)" clip-path="url(#cc)">
  <animate attributeName="x" from="-200" to="{W}" dur="4.5s" repeatCount="indefinite"/>
</rect>
<text x="32" y="56" class="name">{escape(name)}</text>
<circle class="live" cx="{W-40}" cy="47" r="5" fill="{colour}"/>
{desc}
<circle cx="37" cy="{H-33}" r="5" fill="{colour}"/>
<text x="50" y="{H-28}" class="tag">{escape(tag)}</text>
</svg>"""
    write(fname, svg)


# ------------------------------------------------------------ post cards ----
def post_card(fname, name, lines, tag, colour, photo):
    """Repo-card styling with a photo banner; the photo is embedded because
    GitHub blocks external images inside SVGs."""
    W, BH = 580, 220
    H = BH + 170
    img = base64.b64encode(photo.read_bytes()).decode()
    desc = "".join(
        f'<text x="32" y="{BH + 86 + i*24}" class="desc">{escape(l)}</text>' for i, l in enumerate(lines)
    )
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">{escape(name)}: {escape(' '.join(lines))}</title>
<defs>
  <clipPath id="cc"><rect width="{W}" height="{H}" rx="16"/></clipPath>
  <linearGradient id="fade" x1="0" x2="0" y1="0" y2="1">
    <stop offset="0.55" stop-color="{PANEL}" stop-opacity="0"/><stop offset="1" stop-color="{PANEL}"/>
  </linearGradient>
  <linearGradient id="edge" x1="0" x2="1"><stop offset="0" stop-color="{colour}" stop-opacity="0"/>
  <stop offset="0.5" stop-color="{colour}"/><stop offset="1" stop-color="{colour}" stop-opacity="0"/></linearGradient>
</defs>
<style>
  .name {{ font:700 26px {SANS}; fill:{TEXT}; }}
  .desc {{ font:400 15.5px {SANS}; fill:{MUTED}; }}
  .tag {{ font:500 13px {MONO}; fill:{colour}; }}
</style>
<g clip-path="url(#cc)">
  <rect width="{W}" height="{H}" fill="{PANEL}"/>
  <image href="data:image/jpeg;base64,{img}" width="{W}" height="{BH}" preserveAspectRatio="xMidYMid slice"/>
  <rect width="{W}" height="{BH}" fill="url(#fade)"/>
  <rect y="{BH}" height="2" width="200" fill="url(#edge)">
    <animate attributeName="x" from="-200" to="{W}" dur="4.5s" repeatCount="indefinite"/>
  </rect>
</g>
<rect x="0.5" y="0.5" width="{W-1}" height="{H-1}" rx="16" fill="none" stroke="{WIRE}"/>
<text x="32" y="{BH + 48}" class="name">{escape(name)}</text>
{desc}
<circle cx="37" cy="{H-33}" r="5" fill="{colour}"/>
<text x="50" y="{H-28}" class="tag">{escape(tag)}</text>
</svg>"""
    write(fname, svg)


# ------------------------------------------------------------- buttons ------
def button(fname, label, detail, colour):
    W, H = 280, 64
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">{escape(label)}: {escape(detail)}</title>
<style>
  .l {{ font:700 16px {SANS}; fill:{TEXT}; }}
  .d {{ font:500 12px {MONO}; fill:{MUTED}; }}
</style>
<rect x="1" y="1" width="{W-2}" height="{H-2}" rx="12" fill="{PANEL}" stroke="{colour}" stroke-opacity=".7" stroke-width="1.5"/>
<rect x="1" y="1" width="6" height="{H-2}" rx="3" fill="{colour}"/>
<text x="26" y="28" class="l">{escape(label)}</text>
<text x="26" y="47" class="d">{escape(detail)}</text>
</svg>"""
    write(fname, svg)


# ------------------------------------------------------------ backwaters ----
def footer():
    W, H = 1200, 150

    def wave(amp, length, y):
        n = int((W + 2 * length) / length) + 2
        d = f"M0,{y}"
        for i in range(n):
            x = i * length
            d += f" q{length/4},{-amp} {length/2},0 t{length/2},0"
        d += f" V{H} H0 Z"
        return d

    layers = [
        (14, 400, 78, PLASMA, 0.2, 14),
        (11, 300, 96, SIGNAL, 0.16, 10),
        (8, 240, 114, SIGNAL, 0.28, 7),
    ]
    g = "".join(
        f'<path d="{wave(a, L, y)}" fill="{c}" fill-opacity="{o}" class="w" '
        f'style="animation-duration:{s}s;animation-name:drift{L}"/>'
        for a, L, y, c, o, s in layers
    )
    kf = "".join(f"@keyframes drift{L} {{ to {{ transform: translateX(-{L*2}px); }} }}" for _, L, *_ in layers)
    svg = f"""
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}" role="img" aria-labelledby="t">
<title id="t">Waves of the Alappuzha backwaters</title>
<style>
  .w {{ animation-timing-function: linear; animation-iteration-count: infinite; }}
  {kf}
  .cap {{ font:500 13px {MONO}; fill:{MUTED}; text-anchor:middle; }}
  {REDUCED}
</style>
<rect width="{W}" height="{H}" rx="18" fill="{VOID}"/>
<clipPath id="r"><rect width="{W}" height="{H}" rx="18"/></clipPath>
<g clip-path="url(#r)">{g}</g>
<text x="{W/2}" y="44" class="cap">streaming from the backwaters of Alappuzha</text>
</svg>"""
    write("footer.svg", svg)


if __name__ == "__main__":
    header()
    stack()
    card("card-sharejeeni.svg", "sharejeeni",
         ["Python package that pulls files from SharePoint sites,",
          "authenticating through Azure AD client credentials."],
         "Python  |  pip package", SIGNAL)
    card("card-dviewer.svg", "DViewer",
         ["Data aggregation and query platform: view and query",
          "many data sources from a single interface."],
         "Data platform  |  docs", PLASMA)
    # LinkedIn highlights: add one entry to posts.json per post, then rerun
    for p in json.loads((Path(__file__).parent / "posts.json").read_text(encoding="utf-8")):
        post_card(f"post-{p['slug']}.svg", p["title"], p["lines"], p["tag"], EMBER,
                  OUT / "photos" / f"{p['slug']}.jpg")
    button("btn-linkedin.svg", "LinkedIn", "in/jeevan-varghese-1a5237214", SIGNAL)
    button("btn-blog.svg", "Blog", "jeevan-varghese.blogspot.com", PLASMA)
    button("btn-email.svg", "Email", "jeevanvsan@gmail.com", EMBER)
    footer()
