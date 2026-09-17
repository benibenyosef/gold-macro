#!/usr/bin/env python3
"""
Gold Macro auto updater
- 100% free endpoints only
- No API keys
- Uses Python standard library only
"""

from __future__ import annotations
import csv
import io
import json
import math
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data.json"
IL = ZoneInfo("Asia/Jerusalem")

MM_URL = "https://nfs.faireconomy.media/mm_calendar_thisweek.json"
FF_URL = "https://nfs.faireconomy.media/ff_calendar_thisweek.json"
FRED_10Y = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS10"
FRED_2Y = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=DGS2"
STOOQ_DXY = "https://stooq.com/q/l/?s=dx.f&i=d"

UA = "Mozilla/5.0 gold-macro-dashboard/1.0"

RELEVANT = [
    "fomc", "federal funds", "fed chair", "powell", "fed speaks", "fomc member",
    "cpi", "consumer price", "pce", "ppi", "producer price", "inflation",
    "nonfarm", "non-farm", "nfp", "unemployment", "jobless", "employment",
    "average hourly", "adp", "jolts", "retail sales", "gdp",
    "ism manufacturing", "ism services", "consumer confidence",
    "consumer sentiment", "inflation expectations",
    "treasury", "building permits", "housing starts",
    "industrial production", "capacity utilization",
    "boe", "bank of england", "boj", "bank of japan", "ecb", "lagarde"
]

CRITICAL = [
    "fomc", "federal funds", "fed chair", "cpi", "pce",
    "nonfarm", "non-farm", "nfp", "unemployment rate"
]

IMPORTANT = [
    "ppi", "jobless", "unemployment claims", "average hourly", "adp", "jolts",
    "retail sales", "gdp", "ism", "consumer confidence", "consumer sentiment",
    "inflation expectations", "industrial production", "boe", "boj", "ecb"
]

TRANSLATIONS = [
    ("FOMC Rate Decision", "החלטת ריבית הפד"),
    ("Federal Funds Rate", "ריבית הפד"),
    ("FOMC Statement", "הודעת ה-FOMC"),
    ("Fed Chair", "יו״ר הפד"),
    ("Core CPI", "מדד המחירים לצרכן ליבה"),
    ("CPI", "מדד המחירים לצרכן"),
    ("Core PCE", "מדד PCE ליבה"),
    ("PCE Price Index", "מדד המחירים PCE"),
    ("Core PPI", "מדד מחירי היצרן ליבה"),
    ("PPI", "מדד מחירי היצרן"),
    ("Non-Farm", "דוח תעסוקה NFP"),
    ("Nonfarm", "דוח תעסוקה NFP"),
    ("Unemployment Rate", "שיעור האבטלה"),
    ("Unemployment Claims", "תביעות אבטלה"),
    ("Jobless Claims", "תביעות אבטלה"),
    ("Average Hourly Earnings", "שכר ממוצע לשעה"),
    ("ADP", "תעסוקה ADP"),
    ("JOLTS", "משרות פנויות JOLTS"),
    ("Retail Sales", "מכירות קמעונאיות"),
    ("GDP", "תוצר מקומי גולמי"),
    ("ISM Manufacturing PMI", "מדד ISM לייצור"),
    ("ISM Services PMI", "מדד ISM לשירותים"),
    ("Consumer Confidence", "אמון הצרכנים"),
    ("Consumer Sentiment", "סנטימנט הצרכנים"),
    ("Inflation Expectations", "ציפיות אינפלציה"),
    ("Industrial Production", "ייצור תעשייתי"),
    ("Building Permits", "היתרי בנייה"),
    ("Housing Starts", "התחלות בנייה"),
    ("BOE", "בנק אנגליה"),
    ("Bank of England", "בנק אנגליה"),
    ("BOJ", "בנק יפן"),
    ("Bank of Japan", "בנק יפן"),
    ("ECB", "הבנק המרכזי האירופי"),
]

def get_text(url: str, timeout: int = 25) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode("utf-8", "replace")

def get_json(url: str):
    return json.loads(get_text(url))

def parse_dt(value: str) -> datetime:
    s = str(value).strip()
    if s.endswith("Z"):
        s = s[:-1] + "+00:00"
    dt = datetime.fromisoformat(s)
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(IL)

def translate(title: str) -> str:
    out = title
    for en, he in TRANSLATIONS:
        if en.lower() in title.lower():
            return he
    return out

def importance(title: str, source_impact: str = "") -> str:
    t = title.lower()
    if any(k in t for k in CRITICAL):
        return "critical"
    if any(k in t for k in IMPORTANT):
        return "important"
    imp = str(source_impact).lower()
    if "high" in imp:
        return "important"
    return "medium"

def why(title: str) -> str:
    t = title.lower()
    if any(k in t for k in ["cpi", "pce", "ppi", "inflation"]):
        return "משפיע על ציפיות האינפלציה והריבית. נתון חם מהצפי עשוי להעלות תשואות וללחוץ על הזהב; נתון חלש עשוי לפעול הפוך."
    if any(k in t for k in ["nonfarm", "nfp", "unemployment", "jobless", "employment", "adp", "jolts", "average hourly"]):
        return "משפיע על הערכת עוצמת שוק העבודה ועל ציפיות הריבית. שוק עבודה חזק נוטה לתמוך בדולר ובתשואות; חולשה יכולה לתמוך בזהב."
    if any(k in t for k in ["fomc", "federal funds", "fed chair", "fed speaks", "fomc member"]):
        return "מדיניות הפד היא מהגורמים המרכזיים לזהב. מסר ניצי וריבית גבוהה יותר נוטים ללחוץ על הזהב; מסר יוני נוטה לתמוך בו."
    if any(k in t for k in ["retail sales", "gdp", "ism", "consumer confidence", "consumer sentiment", "industrial production"]):
        return "מודד את עוצמת הכלכלה. נתון חזק יכול לחזק ציפיות לריבית גבוהה יותר; נתון חלש יכול להפחית אותן."
    if any(k in t for k in ["boe", "bank of england", "boj", "bank of japan", "ecb"]):
        return "עשוי להשפיע בעקיפין על הדולר ועל תנועות מטבע גלובליות, ולכן גם על חוזי הזהב."
    return "אירוע מאקרו שעשוי להשפיע על הדולר, התשואות או ציפיות הריבית — שלושת הצירים המרכזיים לחוזי הזהב."

def relevant_item(item: dict) -> bool:
    title = str(item.get("title", ""))
    country = str(item.get("country", "")).upper()
    t = title.lower()
    if any(k in t for k in RELEVANT):
        return True
    if country in {"USD", "US"} and str(item.get("impact", "")).lower() in {"high", "medium"}:
        return True
    return False

def load_calendar():
    errors = []
    for url, src in [(MM_URL, "Metals Mine"), (FF_URL, "Forex Factory")]:
        try:
            raw = get_json(url)
            if isinstance(raw, list) and raw:
                return raw, src
        except Exception as e:
            errors.append(f"{src}: {e}")
    raise RuntimeError("Calendar sources failed: " + " | ".join(errors))

def build_events(raw):
    out = []
    seen = set()
    for item in raw:
        if not isinstance(item, dict) or not relevant_item(item):
            continue
        try:
            dt = parse_dt(item.get("date"))
        except Exception:
            continue
        title = str(item.get("title", "")).strip()
        key = (dt.isoformat(), title)
        if key in seen:
            continue
        seen.add(key)
        out.append({
            "id": re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")[:48] + "-" + dt.strftime("%m%d%H%M"),
            "dateISO": dt.isoformat(),
            "dateKey": dt.strftime("%Y-%m-%d"),
            "timeLabel": dt.strftime("%H:%M"),
            "nameHe": translate(title),
            "nameEn": title,
            "country": str(item.get("country") or ""),
            "importance": importance(title, item.get("impact", "")),
            "forecast": str(item.get("forecast") or "—"),
            "previous": str(item.get("previous") or "—"),
            "actual": item.get("actual"),
            "whyHe": why(title)
        })
    out.sort(key=lambda e: e["dateISO"])
    return out

def fred_latest(url: str):
    text = get_text(url)
    rows = list(csv.DictReader(io.StringIO(text)))
    vals = []
    for row in rows:
        date = row.get("DATE") or row.get("observation_date")
        value = next((v for k, v in row.items() if k not in {"DATE", "observation_date"}), None)
        if value and value not in {".", "NA"}:
            try:
                vals.append((date, float(value)))
            except ValueError:
                pass
    if not vals:
        return {"value": None, "direction": "unknown", "date": None, "change": None}
    latest = vals[-1]
    prev = vals[-2] if len(vals) > 1 else latest
    change = latest[1] - prev[1]
    direction = "up" if change > 0.001 else "down" if change < -0.001 else "flat"
    return {"value": latest[1], "direction": direction, "date": latest[0], "change": round(change, 4)}

def stooq_dxy():
    try:
        text = get_text(STOOQ_DXY)
        rows = list(csv.reader(io.StringIO(text)))
        # Common output: Symbol,Date,Time,Open,High,Low,Close,Volume
        if len(rows) >= 2:
            hdr = [x.strip().lower() for x in rows[0]]
            data = rows[-1]
            close_i = hdr.index("close")
            date_i = hdr.index("date") if "date" in hdr else None
            value = float(data[close_i])
            return {"value": value, "direction": "unknown", "date": data[date_i] if date_i is not None else None, "change": None}
    except Exception:
        pass
    return {"value": None, "direction": "unknown", "date": None, "change": None}

def macro_summary(market):
    y10 = market["us10y"].get("direction")
    y2 = market["us2y"].get("direction")
    dx = market["dxy"].get("direction")

    negatives = sum(x == "up" for x in [y10, y2, dx])
    positives = sum(x == "down" for x in [y10, y2, dx])

    if negatives >= 2:
        return {
            "status": "negative",
            "title": "סביבה מאקרו לוחצת על הזהב",
            "summary": "רוב גורמי המאקרו הזמינים — בעיקר תשואות ו/או דולר — נעים בכיוון שבדרך כלל מקשה על חוזי GC/MGC."
        }
    if positives >= 2:
        return {
            "status": "positive",
            "title": "סביבה מאקרו תומכת בזהב",
            "summary": "רוב גורמי המאקרו הזמינים — בעיקר תשואות ו/או דולר — נעים בכיוון שבדרך כלל תומך בחוזי GC/MGC."
        }
    return {
        "status": "mixed",
        "title": "תמונת המאקרו מעורבת",
        "summary": "האותות מהדולר ומהתשואות אינם אחידים כרגע. מומלץ לתת משקל גבוה לאירוע המאקרו הקרוב ולתגובת התשואות לאחר הפרסום."
    }

def main():
    raw, calendar_source = load_calendar()
    events = build_events(raw)

    market = {
        "us10y": fred_latest(FRED_10Y),
        "us2y": fred_latest(FRED_2Y),
        "dxy": stooq_dxy()
    }

    data = {
        "updated": datetime.now(IL).isoformat(timespec="seconds"),
        "events": events,
        "market": market,
        "macro": macro_summary(market),
        "sources": [
            f"{calendar_source} / Fair Economy calendar export",
            "Federal Reserve / FRED (DGS10, DGS2)",
            "Stooq free delayed data (DXY fallback)"
        ]
    }

    OUT.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Updated {OUT} with {len(events)} relevant events")

if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        sys.exit(1)
