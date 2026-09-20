#!/usr/bin/env python3
"""Assemble the single-file TCM study app.

Reads src/index.template.html and every data/*.json, injects them as
window.TCM_DATA, writes dist/tcm-study.html (fully self-contained).
"""
import datetime
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parent
TEMPLATE = ROOT / "src" / "index.template.html"
DATA_DIR = ROOT / "data"
OUT = ROOT / "dist" / "tcm-study.html"
# GitHub Pages serves the committed file at repo root; keep it in sync on every build.
ROOT_INDEX = ROOT / "index.html"

REQUIRED = ["curriculum", "theory", "herbs", "formulas", "acupoints", "quiz"]

VALID_CATS = {
    "theory": {"陰陽", "五行", "藏象", "氣血津液", "經絡", "病因", "治則治法"},
    "herbs": {
        "解表藥", "清熱藥", "瀉下藥", "祛風濕藥", "化濕藥", "利水滲濕藥", "溫裡藥",
        "理氣藥", "消食藥", "止血藥", "活血祛瘀藥", "化痰止咳平喘藥", "安神藥",
        "平肝息風藥", "開竅藥", "補虛藥", "收澀藥",
    },
    "formulas": {
        "解表劑", "清熱劑", "瀉下劑", "祛風濕劑", "開竅劑", "理氣劑", "消食劑",
        "止血劑", "理血劑", "化痰止咳平喘劑", "安神劑", "平肝息風劑", "補益劑",
        "固澀劑", "腫瘍劑等其他",
    },
}
VALID_ROLES = {"君", "臣", "佐", "使", "佐使"}


def load(name):
    path = DATA_DIR / f"{name}.json"
    if not path.exists():
        sys.exit(f"missing data file: {path}")
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def validate(data):
    errors = []
    for c in data["theory"]["concepts"]:
        if c["category"] not in VALID_CATS["theory"]:
            errors.append(f"theory {c['id']}: bad category {c['category']}")
    for h in data["herbs"]["herbs"]:
        if h["category"] not in VALID_CATS["herbs"]:
            errors.append(f"herb {h['id']} ({h['name']}): bad category {h['category']}")
    for f in data["formulas"]["formulas"]:
        if f["category"] not in VALID_CATS["formulas"]:
            errors.append(f"formula {f['id']} ({f['name']}): bad category {f['category']}")
        for comp in f["composition"]:
            if comp["role"] not in VALID_ROLES:
                errors.append(f"formula {f['id']} ({f['name']}): bad role {comp['role']}")
    mids = {m["id"] for m in data["acupoints"]["meridians"]}
    for p in data["acupoints"]["points"]:
        if p["meridian"] not in mids:
            errors.append(f"point {p['id']} ({p['name']}): unknown meridian {p['meridian']}")
    for q in data["quiz"]["questions"]:
        if q.get("topic") not in VALID_CATS["theory"]:
            errors.append(f"quiz {q['id']}: bad topic {q.get('topic')}")
        if not (isinstance(q["answer"], int) and 0 <= q["answer"] < len(q["options"])):
            errors.append(f"quiz {q['id']}: answer out of range")
        if len(q["options"]) != 4:
            errors.append(f"quiz {q['id']}: needs exactly 4 options")
    for group in ("herbs", "formulas"):
        ids = [x["id"] for x in data[group][group]]
        if len(ids) != len(set(ids)):
            errors.append(f"{group}: duplicate ids")
    if len(data["acupoints"]["meridians"]) != 14:
        errors.append(f"meridians: expected 14, got {len(data['acupoints']['meridians'])}")
    return errors


def main():
    if not TEMPLATE.exists():
        sys.exit(f"missing template: {TEMPLATE}")
    data = {name: load(name) for name in REQUIRED}
    data["meta"] = {
        "app": "中醫自學",
        "generated": datetime.date.today().isoformat(),
        "counts": {
            "theory": len(data["theory"]["concepts"]),
            "herbs": len(data["herbs"]["herbs"]),
            "formulas": len(data["formulas"]["formulas"]),
            "meridians": len(data["acupoints"]["meridians"]),
            "points": len(data["acupoints"]["points"]),
            "quiz": len(data["quiz"]["questions"]),
        },
    }
    errors = validate(data)
    if errors:
        print("DATA VALIDATION ERRORS:")
        for e in errors:
            print("  -", e)
        sys.exit(1)

    html = TEMPLATE.read_text(encoding="utf-8")
    marker = "/*__TCM_DATA__*/"
    if marker not in html:
        sys.exit(f"template missing marker {marker}")
    payload = json.dumps(data, ensure_ascii=False)
    payload = payload.replace("</", "<\\/")  # keep inline <script> safe
    html = html.replace(marker, payload)
    OUT.parent.mkdir(exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    ROOT_INDEX.write_text(html, encoding="utf-8")
    size_kb = OUT.stat().st_size / 1024
    print(f"OK -> {OUT}")
    print(f"OK -> {ROOT_INDEX} (GitHub Pages) ({size_kb:.0f} KB)")
    print("counts:", json.dumps(data["meta"]["counts"], ensure_ascii=False))


if __name__ == "__main__":
    main()
