import os
import re
import unicodedata

# Burada istediyiniz kanallari deyise bilersiniz.
# Sol terefde kanalin adi, sagda siyahida ola bilecek yazilislari
# (kicik herflerle: e=e, i=i, s=s, u=u).
WANTED = {
    "Xezer TV": ["xezer tv", "khazar tv"],
    "ATV": ["atv"],
    "ARB": ["arb"],
    "Ictimai TV": ["ictimai tv", "ictimai", "itv"],
    "Space TV": ["space tv"],
    "CBC Sport": ["cbc sport", "cbc sport hd"],
    "Az TV": ["az tv", "aztv"],
    "Real TV": ["real tv"],
    "Baku TV": ["baku tv"],
    "Xezer TV": ["xezer tv"],
    "APA Tv": ["apa tv"],
    "Show TV": ["show tv", "show turk"],
    "TV8": ["tv8", "tv 8"],
    "Star TV": ["star tv"],
    "Kanal 7": ["kanal 7"],
    "FOX / NOW": ["fox", "fox tv", "now", "now tv"],
    "TRT Spor": ["trt spor"],
}

# Sira vacibdir: evvelki yuksek prioritetdir.
SOURCES = ["az.m3u", "tr.m3u", "free-az.m3u", "free-tr.m3u"]
CUSTOM = "custom.m3u"  # istege bagli: oz kanallarinizi bura yaza bilersiniz


def norm(text):
    text = text.replace("ə", "e").replace("Ə", "e").replace("ı", "i").replace("İ", "i")
    text = unicodedata.normalize("NFKD", text.casefold())
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = re.sub(r"[^a-z0-9]+", " ", text)
    return text.strip()


def clean_title(extinf):
    title = extinf.rsplit(",", 1)[-1]
    title = re.sub(r"[\u24B6-\u24E9]", "", title)
    title = re.sub(r"\(.*?\)|\[.*?\]", "", title)
    return norm(title)


def read_blocks(path):
    blocks = []
    cur = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f.read().splitlines():
            if line.startswith("#EXTINF"):
                cur = [line]
                blocks.append(cur)
            elif cur is not None and line.strip():
                cur.append(line)
    return blocks


alias_to_channel = {}
for channel, aliases in WANTED.items():
    for a in aliases:
        alias_to_channel[norm(a)] = channel
found = {}
out = ["#EXTM3U"]

# 1) Sizin oz linkleriniz (custom.m3u) - birinci prioritet
if os.path.exists(CUSTOM):
    for block in read_blocks(CUSTOM):
        out.extend(block)
        ch = alias_to_channel.get(clean_title(block[0]))
        if ch:
            found[ch] = found.get(ch, 0) + 1

# 2) Siyahilar: her kanaldan yalniz BIR link, yalniz yuxaridan tapilmayibsa
for src in SOURCES:
    if not os.path.exists(src):
        continue
    for block in read_blocks(src):
        ch = alias_to_channel.get(clean_title(block[0]))
        if ch and ch not in found:
            out.extend(block)
            found[ch] = 1

with open("az-tr.m3u", "w", encoding="utf-8") as f:
    f.write("\n".join(out) + "\n")

with open("report.txt", "w", encoding="utf-8") as f:
    f.write("TAPILAN kanallar:\n")
    for ch in WANTED:
        if ch in found:
            f.write(f"  + {ch}\n")
    f.write("\nTAPILMAYAN kanallar (siyahida yoxdur):\n")
    for ch in WANTED:
        if ch not in found:
            f.write(f"  - {ch}\n")
print(open("report.txt", encoding="utf-8").read())
