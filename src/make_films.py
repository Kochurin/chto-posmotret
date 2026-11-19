"""films_raw.json -> ../films.json: настроения, тип, отбор по рейтингу"""
import json, re, sys
sys.stdout.reconfigure(encoding="utf-8")
MOODS = [
  ("laugh", "Посмеяться", r"комед|ситком|сатир"),
  ("thrill", "Пощекотать нервы", r"триллер|ужас|тайн|загадк|детектив|нуар|мистик"),
  ("crime", "Криминал", r"криминал|гангстер"),
  ("action", "Экшен и приключения", r"боевик|приключен|экшен|супергеро|военн|эпическ|вестерн|спортивн"),
  ("fantasy", "Фантастика и фэнтези", r"фантаст|фэнтез|антиутоп|киберпанк"),
  ("drama", "Подумать о жизни", r"драм|биограф|историческ"),
  ("love", "Про любовь", r"мелодрам|романтич|любов"),
  ("family", "С семьёй", r"семейн|детск|мультфильм|анимац|мультсериал"),
  ("anime", "Аниме", r"аниме|манга"),
]
raw = json.load(open("films_raw.json", encoding="utf-8"))
out = []
for x in raw:
    if not x.get("kp") or x["kp"] < 6.8 or (x.get("votes") or 0) < 3000:
        continue
    text = " ".join(x["genres"]).lower()
    series = x["type"] == "tv-series" or (x["type"] is None and re.search(r"сериал|телесериал|ситком|аниме", text + " " + (x.get("desc") or "").lower()))
    moods = [k for k, _, rx in MOODS if re.search(rx, text)]
    genres = sorted({re.sub(r"(ий|ый|ой)? ?(фильм|телесериал|сериал)$|^(фильм|телесериал)-", "", g).strip() or g for g in x["genres"]})[:3]
    out.append({"n": x["name"], "y": x["year"], "r": round(x["kp"], 1), "v": x.get("votes"), "s": bool(series), "ru": x["ru"],
                "m": moods, "g": x["genres"][:3], "d": x.get("desc"), "dir": x.get("director"), "t": x.get("dur"), "kp": x.get("kpid")})
out.sort(key=lambda f: -f["r"])
json.dump({"moods": [[k, t] for k, t, _ in MOODS], "films": out}, open("../films.json", "w", encoding="utf-8"), ensure_ascii=False, separators=(",", ":"))
import collections
print(len(out), "сериалов", sum(f["s"] for f in out), "без настроения", sum(1 for f in out if not f["m"]))
print(collections.Counter(m for f in out for m in f["m"]))
