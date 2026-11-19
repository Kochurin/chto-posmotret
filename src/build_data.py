"""Собирает films.json: список из кэша кино-бота + жанры, описание, длительность и id Кинопоиска из Wikidata (без ключей)"""
import json, sys, time, urllib.request, urllib.parse
sys.stdout.reconfigure(encoding="utf-8")
CACHE = r"C:/Users/phoen/Desktop/claude/work/movie/kp_cache.json"
d = json.load(open(CACHE, encoding="utf-8"))
items = {}
for k, v in d.items():
    q = json.loads(k)
    typ = q.get("type")
    ru = q.get("countries.name") == "Россия" or q.get("countries.name") == ["Россия"]
    for x in v.get("docs", []):
        imdb = (x.get("externalId") or {}).get("imdb")
        if not imdb or not x.get("name"):
            continue
        it = items.setdefault(imdb, {"imdb": imdb, "name": x["name"], "year": x.get("year"),
                                     "kp": (x.get("rating") or {}).get("kp"), "votes": (x.get("votes") or {}).get("kp"),
                                     "type": typ, "ru": ru})
        if typ and not it["type"]:
            it["type"] = typ
print("из кэша:", len(items))

def sparql(ids):
    vals = " ".join(f'"{i}"' for i in ids)
    q = f"""SELECT ?imdb ?item ?kpid ?dur ?desc (GROUP_CONCAT(DISTINCT ?gl; separator="|") AS ?genres) (SAMPLE(?dl) AS ?director) WHERE {{
      VALUES ?imdb {{ {vals} }}
      ?item wdt:P345 ?imdb .
      OPTIONAL {{ ?item wdt:P2603 ?kpid }}
      OPTIONAL {{ ?item wdt:P2047 ?dur }}
      OPTIONAL {{ ?item schema:description ?desc FILTER(lang(?desc)="ru") }}
      OPTIONAL {{ ?item wdt:P136 ?g . ?g rdfs:label ?gl FILTER(lang(?gl)="ru") }}
      OPTIONAL {{ ?item wdt:P57 ?d . ?d rdfs:label ?dl FILTER(lang(?dl)="ru") }}
    }} GROUP BY ?imdb ?item ?kpid ?dur ?desc"""
    url = "https://query.wikidata.org/sparql?" + urllib.parse.urlencode({"query": q, "format": "json"})
    req = urllib.request.Request(url, headers={"User-Agent": "kino-site-builder/1.0 (static site data)"})
    return json.load(urllib.request.urlopen(req, timeout=90))["results"]["bindings"]

ids = list(items)
for i in range(0, len(ids), 80):
    for b in sparql(ids[i:i+80]):
        it = items[b["imdb"]["value"]]
        g = b.get("genres", {}).get("value", "")
        it.setdefault("genres", set()).update(x for x in g.split("|") if x)
        for key, src in (("kpid", "kpid"), ("desc", "desc"), ("director", "director")):
            if src in b and not it.get(key):
                it[key] = b[src]["value"]
        if "dur" in b and not it.get("dur"):
            try: it["dur"] = round(float(b["dur"]["value"]))
            except ValueError: pass
    print("wikidata", i + 80)
    time.sleep(1)

out = []
for it in items.values():
    it["genres"] = sorted(it.get("genres", []))
    out.append(it)
json.dump(out, open("films_raw.json", "w", encoding="utf-8"), ensure_ascii=False, indent=0)
print("итого", len(out), "с жанрами", sum(1 for x in out if x["genres"]), "с kp id", sum(1 for x in out if x.get("kpid")))
