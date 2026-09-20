#!/usr/bin/env python3
"""
Match the map's Japanese distilleries against the National Tax Agency corporate-number
register (法人番号公表サイト) and the NTA's new-liquor-manufacturing-licence lists, and write
candidate rows for human review.

Registers and lists (research: docs/data-quality/japan-registers-2026-09-20.md):
  jp-houjin-bangou   NTA Corporate Number Publication Site bulk CSV (全件データ, one zip per
                     prefecture, CSV Unicode, month-end snapshot). Licence: 公共データ利用規約
                     第1.0版 (PDL1.0, CC BY 4.0 compatible). Only fetched with --fetch-nta;
                     each prefecture zip is cached so reruns are offline. The Web-API needs
                     an application ID (2-4 weeks to issue) and is NOT used.
  Licence layer      NTA 酒類等製造免許の新規取得者名等一覧, yearly Excel files 2014 - Jun 2026
                     (new manufacturing licences only; rows from 2016 on carry the 法人番号,
                     the legal name, a trading name and the manufacturing-site address).
                     Only fetched with --fetch-licences. Rows go to japan-licences.csv,
                     registry nta-seizo-menkyo, same schema.
  gBizINFO is NOT used: its REST API and bulk download both need a registered token
  (an unauthenticated probe on 20 Sep 2026 got an error body, not data; gBizINFO's own
  API page confirms a prior application and emailed token are required).

Run (offline, from cached files):
  python3 scripts/match_japan_registers.py --cache /path/to/cache
Fetch (<= 1 request/second; one POST per prefecture zip, one GET per yearly Excel):
  python3 scripts/match_japan_registers.py --cache /path/to/cache --fetch-nta --fetch-licences

Cache layout: <cache>/nta/<pref-kanji>.zip (register), <cache>/nta-licence/<year>.xlsx.
Missing files are skipped with a warning. Idempotent: same inputs -> same outputs.

Name bridging: pins mostly carry romanised names while the register holds kanji. Bridges used,
in order of strength: (1) kanji pin name == kanji register name after normalisation;
(2) the licence list's 法人番号 + trading name (kanji or full-width Latin) + site address;
(3) register English name / katakana furigana (romanised here) containing a distinctive pin
or website-domain token, with prefecture or postcode agreement; (4) same 7-digit postcode as
the pin and a drinks word in the company name. Hand rows carry the group operator for the
well-known group-run sites; their 法人番号 is resolved from the register by kanji legal name.
"""
from __future__ import annotations

import argparse
import csv
import html
import io
import json
import re
import sys
import time
import unicodedata
import urllib.parse
import urllib.request
import zipfile
from collections import defaultdict
from http.cookiejar import CookieJar
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GEO = ROOT / "public" / "data" / "distilleries.geojson"
OUT_DIR = ROOT / "data" / "company-crosswalk"
OUT_CANDIDATES = OUT_DIR / "japan-candidates.csv"
OUT_LICENCES = OUT_DIR / "japan-licences.csv"
FIELDS = ["slug", "distillery_name", "country", "registry", "company_number", "company_name",
          "relation", "match_method", "confidence", "verified", "source", "note"]

SRC_NTA = "https://www.houjin-bangou.nta.go.jp/download/zenken/"
SRC_NTA_LICENCE = "https://www.nta.go.jp/taxes/sake/menkyo/shinki/seizo/02/zenkoku.htm"
NTA_ZENKEN_POST = "https://www.houjin-bangou.nta.go.jp/download/zenken/index.html"
NTA_LICENCE_FILES = [  # (path under .../shinki/seizo/, tag)
    ("02/h26.xlsx", "h26"), ("02/h27.xlsx", "h27"), ("02/h28.xlsx", "h28"), ("02/h29.xlsx", "h29"),
    ("02/h30/12/h30.xlsx", "h30"), ("02/r01/10/r01.xlsx", "r01"), ("02/r02/02/r02.xlsx", "r02"),
    ("02/r03/01/r03.xlsx", "r03"), ("02/r04/01/r04.xlsx", "r04"), ("02/r05/01/r05.xlsx", "r05"),
    ("02/r06/12/r06.xlsx", "r06"), ("02/r07/01/r01.xlsx", "r07"), ("02/r08/01/r08.xlsx", "r08"),
]
UA = "Mozilla/5.0 (distillery-map crosswalk; stdlib urllib)"

# 47 prefectures: kanji, romanised, JIS code
PREFS = [
    ("北海道", "Hokkaido", "01"), ("青森県", "Aomori", "02"), ("岩手県", "Iwate", "03"), ("宮城県", "Miyagi", "04"),
    ("秋田県", "Akita", "05"), ("山形県", "Yamagata", "06"), ("福島県", "Fukushima", "07"), ("茨城県", "Ibaraki", "08"),
    ("栃木県", "Tochigi", "09"), ("群馬県", "Gunma", "10"), ("埼玉県", "Saitama", "11"), ("千葉県", "Chiba", "12"),
    ("東京都", "Tokyo", "13"), ("神奈川県", "Kanagawa", "14"), ("新潟県", "Niigata", "15"), ("富山県", "Toyama", "16"),
    ("石川県", "Ishikawa", "17"), ("福井県", "Fukui", "18"), ("山梨県", "Yamanashi", "19"), ("長野県", "Nagano", "20"),
    ("岐阜県", "Gifu", "21"), ("静岡県", "Shizuoka", "22"), ("愛知県", "Aichi", "23"), ("三重県", "Mie", "24"),
    ("滋賀県", "Shiga", "25"), ("京都府", "Kyoto", "26"), ("大阪府", "Osaka", "27"), ("兵庫県", "Hyogo", "28"),
    ("奈良県", "Nara", "29"), ("和歌山県", "Wakayama", "30"), ("鳥取県", "Tottori", "31"), ("島根県", "Shimane", "32"),
    ("岡山県", "Okayama", "33"), ("広島県", "Hiroshima", "34"), ("山口県", "Yamaguchi", "35"), ("徳島県", "Tokushima", "36"),
    ("香川県", "Kagawa", "37"), ("愛媛県", "Ehime", "38"), ("高知県", "Kochi", "39"), ("福岡県", "Fukuoka", "40"),
    ("佐賀県", "Saga", "41"), ("長崎県", "Nagasaki", "42"), ("熊本県", "Kumamoto", "43"), ("大分県", "Oita", "44"),
    ("宮崎県", "Miyazaki", "45"), ("鹿児島県", "Kagoshima", "46"), ("沖縄県", "Okinawa", "47"),
]
PREF_BY_EN = {en.lower(): k for k, en, _ in PREFS}
PREF_SHORT = {k.rstrip("都道府県") if k != "北海道" else "北海道": k for k, _, _ in PREFS}
PREF_EN = {k: en for k, en, _ in PREFS}

# Pins whose address has no prefecture: prefecture from the pin description / website.
PIN_PREF = {
    "distillery-japan-2": "宮崎県",   # Kirishima Shuzo, Miyakonojo
    "distillery-japan-3": "鹿児島県",  # Machida Shuzo, Amami Oshima
    "distillery-japan-4": "鳥取県",   # 中井酒造, Kurayoshi (sanin-sake.jp)
    "distillery-japan-7": "福島県",   # Nekka, Tadami
    "distillery-japan-12": "鹿児島県",  # 三岳酒造, Yakushima
    "tagohinke-brewery-products": "岡山県",  # Tsuyama
    "distillery-japan-13": "京都府",  # The Kyoto Distillery
    "distillery-japan-21": "鹿児島県",  # Satsuma Musou
    "distillery-japan-26": "長崎県",  # Takara Shuzo Shimabara plant
    "distillery-japan-29": "鹿児島県",  # 奄美大島酒造
    "distillery-japan-33": "宮崎県",  # Miyakonojo Shuzo
}

# Legal-entity suffixes and generic words dropped from kanji names before comparison
KANJI_SUFFIX = ["株式会社", "有限会社", "合同会社", "合資会社", "合名会社", "一般社団法人", "(株)", "(有)", "㈱", "㈲"]
KANJI_GENERIC = ["蒸溜所", "蒸留所", "醸造所", "製造場", "ディスティラリー", "ディスティラリー", "distillery"]
# Drinks signal words in a kanji register name
KANJI_SIGNAL = ["酒造", "醸造", "蒸溜", "蒸留", "酒類", "ウイスキー", "ウヰスキー", "ウィスキー", "ディスティラリー",
                "ディスティリング", "スピリッツ", "焼酎", "泡盛", "ブルワリー", "ブルーイング", "ビール", "麦酒",
                "ワイン", "リカー", "酒"]
DISTILLED = {"ウイスキー", "スピリッツ", "リキュール", "単式蒸留焼酎", "単式蒸留しょうちゅう", "連続式蒸留焼酎",
             "連続式蒸留しょうちゅう", "ブランデー", "原料用アルコール", "雑酒"}
COMPANY_KINDS = {"301", "302", "303", "304", "305"}  # 株式会社 有限会社 合名 合資 合同
NON_COMPANY = re.compile(r"商工会議所|協同組合|組合|信用金庫|税理士|学院|学校|法人|協会|財産区|教会|病院|医院")
# Latin tokens too generic to bridge on
STOP_LATIN = {"distillery", "distilleries", "distill", "distilling", "distillers", "whisky", "whiskey", "shuzo",
              "shuzou", "syuzou", "jozo", "jyozo", "brewery", "brewing", "beer", "sake", "spirits", "gin", "craft",
              "japan", "japanese", "the", "and", "co", "ltd", "inc", "www", "com", "jp", "shop", "pro", "net",
              "org", "html", "index", "factory", "company", "kura", "tokyo", "kyoto", "osaka", "kagoshima",
              "okinawa", "hokkaido", "nagasaki", "miyazaki", "kumamoto", "shizuoka", "nagano", "niigata", "chiba",
              "saitama", "yamagata", "fukushima", "aichi", "gifu", "saga", "iwate", "aomori", "toyama", "shiga",
              "hyogo", "ibaraki", "kanagawa", "yokohama", "yamanashi", "hiroshima", "yamaguchi", "ishikawa",
              "tochigi", "oita", "amami", "goto", "onsen", "tsunuki", "komagatake", "products", "botanical",
              "restaurant", "cafe", "bar", "salon", "head", "office", "limited", "non", "alcoholic", "mars",
              "instagram", "nifty", "homepage3", "base", "thebase", "age", "verification", "pages", "contents",
              "eng", "company", "visiting", "experience", "open", "home"}
COMMON_DOMAIN = {"instagram.com", "tabelog.com", "shop-pro.jp", "thebase.in", "nifty.com"}

# Hand rows: group operators for group-run sites, plus operating companies whose legal name
# differs from the pin name. company_number is resolved from the register by kanji name
# (unique hit in the named prefecture); blank if not found.
# slug -> [(kanji legal name, prefecture, relation, confidence, note[, city substring])]
HAND = {
    "yamazaki-distillery": [("サントリー株式会社", "大阪府", "operator", "high",
                             "Suntory's operating company (Suntory Spirits/Beer/Wine merged 2022); Yamazaki is a Suntory malt distillery, Shimamoto, Osaka"),
                            ("サントリーホールディングス株式会社", "大阪府", "group", "high", "Suntory group parent")],
    "hakushu-distillery": [("サントリー株式会社", "大阪府", "operator", "high",
                            "Suntory's operating company; Hakushu is a Suntory malt distillery, Hokuto, Yamanashi"),
                           ("サントリーホールディングス株式会社", "大阪府", "group", "high", "Suntory group parent")],
    "chita-distillery": [("サングレイン株式会社", "愛知県", "operator", "high",
                          "Sungrain Ltd, Suntory subsidiary that runs the Chita grain distillery (Kitahama-machi, Chita)", "知多市"),
                         ("サントリーホールディングス株式会社", "大阪府", "group", "high", "Suntory group parent")],
    "yoichi-distillery": [("ニッカウヰスキー株式会社", "東京都", "operator", "high",
                           "Nikka Whisky Distilling Co.; Yoichi is Nikka's first distillery (Hokkaido)"),
                          ("アサヒグループホールディングス株式会社", "東京都", "group", "high", "Asahi Group, Nikka's parent")],
    "miyagikyo-distillery": [("ニッカウヰスキー株式会社", "東京都", "operator", "high",
                              "Nikka Whisky Distilling Co.; Miyagikyo is Nikka's second distillery (Sendai)"),
                             ("アサヒグループホールディングス株式会社", "東京都", "group", "high", "Asahi Group, Nikka's parent")],
    "nikka-whiskey-distillery-kashiwa-factory": [("ニッカウヰスキー株式会社", "東京都", "operator", "high",
                                                  "Nikka Whisky Distilling Co.; Kashiwa is a Nikka blending/bottling plant (Chiba)")],
    "kirin-fuji-gotemba-distillery": [("キリンディスティラリー株式会社", "静岡県", "operator", "high",
                                       "Kirin Distillery Co., Gotemba; runs the Fuji Gotemba distillery", "御殿場市"),
                                      ("キリンホールディングス株式会社", "東京都", "group", "high", "Kirin group parent")],
    "mars-komagatake-distillery": [("本坊酒造株式会社", "鹿児島県", "operator", "high",
                                    "Hombo Shuzo, Kagoshima; Mars Shinshu (Komagatake) is its Nagano distillery")],
    "mars-tsunuki-distillery": [("本坊酒造株式会社", "鹿児島県", "operator", "high",
                                 "Hombo Shuzo, Kagoshima; Mars Tsunuki is its Minamisatsuma distillery")],
    "distillery-japan-8": [("本坊酒造株式会社", "鹿児島県", "operator", "high",
                            "Hombo Shuzo; Yakushima Denshogura is its shochu/whisky ageing site on Yakushima")],
    "chichibu-distillery": [("株式会社ベンチャーウイスキー", "埼玉県", "self", "high",
                             "Venture Whisky Ltd (Ichiro Akuto), Chichibu, Saitama; runs Chichibu distillery")],
    "hanyu-distillery": [("東亜酒造株式会社", "埼玉県", "self", "high",
                          "Toa Shuzo Co., Hanyu, Saitama; pin website toashuzo.com")],
    "asaka-distillery": [("笹の川酒造株式会社", "福島県", "operator", "high",
                          "Sasanokawa Shuzo, Koriyama; Asaka distillery is its whisky site; pin website sasanokawa.co.jp")],
    "kenten": [("堅展実業株式会社", "東京都", "operator", "high",
                "Kenten Jitsugyo Co. (Tokyo) owns and runs Akkeshi distillery, Hokkaido; pin website akkeshi-distillery.com")],
    "distillery-japan": [("ガイアフローディスティリング株式会社", "静岡県", "self", "high",
                          "Gaiaflow Distilling Co., operating company of Shizuoka distillery (Ochiai, Aoi-ku)"),
                         ("ガイアフロー株式会社", "静岡県", "group", "high", "Gaiaflow Co., parent/importer; pin website gaiaflow.co.jp")],
    "distillery-japan-20": [("小正嘉之助蒸溜所株式会社", "鹿児島県", "self", "high",
                             "Komasa Kanosuke Distillery Co.; pin website kanosuke.com"),
                            ("小正醸造株式会社", "鹿児島県", "group", "high", "Komasa Jyozo, parent shochu house (Hioki)")],
    "distillery-japan-19": [("小正醸造株式会社", "鹿児島県", "self", "high",
                             "Komasa Jyozo Co., Hioki; the Hioki distillery is its main shochu site; pin website komasa.co.jp")],
    "eigashima-whiskey-distillery-white-oak-distillery": [("江井ケ嶋酒造株式会社", "兵庫県", "self", "high",
                                                           "Eigashima Shuzo Co. (register spelling 江井ケ嶋), Akashi; White Oak distillery; pin website ei-sake.jp")],
    "saburomaru-distillery": [("若鶴酒造株式会社", "富山県", "operator", "high",
                               "Wakatsuru Shuzo Co., Tonami; Saburomaru is its whisky distillery; pin website wakatsuru.co.jp")],
    "nagahama-distillery": [("長浜浪漫ビール株式会社", "滋賀県", "operator", "high",
                             "Nagahama Roman Beer Co.; Nagahama distillery sits in its brewpub; pin website romanbeer.com")],
    "distillery-japan-32": [("株式会社金龍", "山形県", "operator", "high",
                             "Kinryu Co. (Yamagata sake/shochu house) built and runs Yuza distillery; pin website yuza-disty.jp")],
    "niseko-distillery-co-ltd": [("株式会社ニセコ蒸溜所", "北海道", "self", "high",
                                  "Niseko Distillery Co.; licensed for whisky and spirits 2021 (NTA list)"),
                                 ("八海醸造株式会社", "新潟県", "group", "high", "Hakkaisan Brewery, Niseko Distillery's parent")],
    "distillery-japan-13": [("株式会社京都蒸溜所", "京都府", "self", "high",
                             "The Kyoto Distillery Co. (KI NO BI gin); pin website kinobigin.com; NTA spirits licence 2016 at 南区吉祥院", "中京区")],
    "tokyo-riverside-distillery": [("エシカル・スピリッツ株式会社", "東京都", "self", "high",
                                    "Ethical Spirits & Co.; Tokyo Riverside distillery, Kuramae (NTA licence 2021)")],
    "yasato-distillery": [("木内酒造株式会社", "茨城県", "operator", "high",
                           "Kiuchi Brewery (Hitachino Nest); Yasato distillery is its whisky site, Ishioka; pin website kiuchibrewery.co.jp")],
    "hitachino-brewing-tokyo-distillery": [("木内酒造株式会社", "茨城県", "operator", "high",
                                            "Kiuchi Brewery; Hitachino Brewing Lab Tokyo distillery, Akihabara")],
    "distillery-japan-2": [("霧島酒造株式会社", "宮崎県", "self", "high", "Kirishima Shuzo Co., Miyakonojo; pin website kirishima.co.jp")],
    "distillery-japan-26": [("宝酒造株式会社", "京都府", "operator", "high",
                             "Takara Shuzo Co. (Kyoto HQ) runs the Shimabara plant, Nagasaki"),
                            ("宝ホールディングス株式会社", "京都府", "group", "high", "Takara Holdings, parent")],
    "distillery-japan-22": [("薩摩酒造株式会社", "鹿児島県", "operator", "high",
                             "Satsuma Shuzo, Makurazaki; Hinokami distillery licensed for whisky 2021 (NTA list)")],
    "distillery-japan-28": [("薩摩酒造株式会社", "鹿児島県", "operator", "high", "Satsuma Shuzo, Makurazaki; Kedogawa distillery (Meijigura)")],
    "distillery-japan-30": [("濵田酒造株式会社", "鹿児島県", "group", "high", "Hamada Shuzo (濵田酒造), Ichikikushikino; Satsuma Kinzangura is its gold-mine site, run through 薩摩金山蔵株式会社 (kanji-name row)")],
    "distillery-japan-25": [("濵田酒造株式会社", "鹿児島県", "self", "high", "Hamada Shuzo Co. (register spelling 濵田), Ichikikushikino (Denbee-gura); pin website hamadasyuzou.co.jp")],
    "the-ontake-distillery": [("西酒造株式会社", "鹿児島県", "operator", "high", "Nishi Shuzo Co., Hioki; Ontake distillery is its whisky site, Kagoshima city")],
    "distillery-japan-18": [("西酒造株式会社", "鹿児島県", "self", "high", "Nishi Shuzo Co., Hioki; pin website nishi-shuzo.co.jp")],
    "suntory-osumi-distillery": [("大隅酒造株式会社", "鹿児島県", "self", "high",
                                  "Osumi Shuzo Co., Soo; Suntory shochu subsidiary; pin website osumishuzo.co.jp"),
                                 ("サントリーホールディングス株式会社", "大阪府", "group", "high", "Suntory group parent")],
    "iichiko-hita-distillery": [("三和酒類株式会社", "大分県", "operator", "high", "Sanwa Shurui Co., Usa; iichiko Hita distillery is its shochu site; pin website iichiko.co.jp")],
    "takahashi-shuzo-co-ltd-taragi-distillery": [("高橋酒造株式会社", "熊本県", "self", "high", "Takahashi Shuzo Co. (Hakutake), Hitoyoshi; Taragi distillery; pin website hakutake.co.jp")],
    "helios-distillery-co-ltd-sawauchi-jozosho": [("ヘリオス酒造株式会社", "沖縄県", "operator", "high", "Helios Shuzo Co., Nago, Okinawa; Sawauchi Jozosho (Iwate) is its beer site")],
    "zuisen-distillery-co-ltd-head-office": [("瑞泉酒造株式会社", "沖縄県", "self", "high", "Zuisen Shuzo Co., Shuri, Naha; pin website zuisen.co.jp")],
    "distillery-japan-10": [("有限会社比嘉酒造", "沖縄県", "self", "high", "Higa Shuzo (Zanpa awamori), Yomitan; pin website zanpa.co.jp")],
    "amamioshima-kaiun-distillery": [("奄美大島開運酒造株式会社", "鹿児島県", "self", "high", "Amami Oshima Kaiun Shuzo, Uken; pin website lento.co.jp")],
    "distillery-japan-29": [("奄美大島酒造株式会社", "鹿児島県", "self", "high", "Amami Oshima Shuzo (Jougo); pin website jougo.co.jp")],
    "distillery-japan-3": [("町田酒造株式会社", "鹿児島県", "self", "high", "Machida Shuzo (Sato no Akebono), Amami")],
    "distillery-japan-12": [("三岳酒造株式会社", "鹿児島県", "self", "high", "Mitake Shuzo, Yakushima; pin website mitake-shochu.com")],
    "distillery-japan-21": [("さつま無双株式会社", "鹿児島県", "self", "high", "Satsuma Musou Co., Kagoshima city; pin website satsumamusou.co.jp")],
    "distillery-japan-33": [("都城酒造株式会社", "宮崎県", "self", "high", "Miyakonojo Shuzo Co.; pin website ms-c.co.jp")],
    "distillery-japan-23": [("有限会社佐多宗二商店", "鹿児島県", "self", "high", "Sata Soji Shoten (Akayane), Minamikyushu; pin website akayane.co.jp")],
    "distillery-japan-4": [("中井酒造株式会社", "鳥取県", "self", "high", "Nakai Shuzo Co., Kurayoshi (sanin-sake.jp)")],
    "distillery-japan-14": [("二世古酒造株式会社", "北海道", "self", "high", "Niseko Shuzo Co., Kutchan; pin website niseko-shuzo.com")],
    "tagohinke-brewery-products": [("多胡本家酒造場", "岡山県", "self", "medium", "Tago Honke Shuzojo (Tsuyama beer); wikidata row already holds 6260003000981")],
    "hikari-distillery-limited": [("光ディスティラリー株式会社", "埼玉県", "self", "high", "Hikari Distillery Ltd, Konosu; register furigana ヒカリディスティラリー, same postcode as the pin")],
    "fukano-shuzo-distillery": [("深野酒造株式会社", "熊本県", "self", "high", "Fukano Shuzo Co., Hitoyoshi; pin website fukanowhisky.com")],
    "mori-izo-distillery": [("森伊蔵酒造有限会社", "鹿児島県", "self", "high", "Mori Izo Shuzo, Tarumizu; pin website moriizo.com")],
    "komaki-distillery": [("小牧醸造株式会社", "鹿児島県", "self", "high", "Komaki Jozo Co., Satsuma; pin website komakijozo.co.jp")],
    "ishigura-museum-shirakane-distillery": [("白金酒造株式会社", "鹿児島県", "self", "high", "Shirakane Shuzo Co., Aira; Ishigura; pin website shirakane.jp")],
    "nishihira-shuzo-kokuto-shochu-distillery": [("西平酒造株式会社", "鹿児島県", "self", "high", "Nishihira Shuzo Co., Amami; pin website nishihira-shuzo.com")],
    "furusawa-distillery": [("古澤醸造合名会社", "宮崎県", "self", "medium", "Furusawa Jozo (Yaezakura), Nichinan; pin website nichinan-yaezakura.jp; number left to the register lookup")],
    "nanbubijin-distillery": [("株式会社南部美人", "岩手県", "self", "high", "Nanbu Bijin Co., Ninohe; spirits licence 2021 (NTA list); pin website nanbubijin.co.jp")],
    "togari-onsen-distillery": [("きよかわ株式会社", "長野県", "self", "high", "Kiyokawa Co., Iiyama; Iiyama distillery spirits licence 2021 (NTA list); pin website kiyokawa-sake.co.jp")],
    "kyoto-whisky-distillery": [("京都酒造株式会社", "京都府", "self", "high", "Kyoto Shuzo Co., Kyotamba; pin website kyotoshuzo.com")],
    "ikawa-distillery": [("株式会社十山", "静岡県", "self", "high", "Juzan Co. (Tokai Pulp group), Ikawa distillery; pin website juzan.co.jp")],
    "setouchi-distillery": [("株式会社三宅本店", "広島県", "operator", "high", "Miyake Honten (Sempuku sake), Kure; Setouchi distillery whisky licence 2021 (NTA list)")],
    "yokohama-gin-distillery": [("横浜ベイブルーイング株式会社", "神奈川県", "self", "high", "Yokohama Bay Brewing Co.; pin website yokohamabaybrewing.jp")],
    "hekinan-distillery-aioi-unibio-co-ltd": [("相生ユニビオ株式会社", "愛知県", "self", "high", "Aioi Unibio Co., Hekinan; pin website unibio.jp")],
    "distillery-japan-31": [("株式会社楯の川酒造", "山形県", "operator", "high", "Tatenokawa Shuzo, Sakata; Gakkogawa distillery (Yuza) is its gin/whisky site; pin website gakkogawa.com")],
    "echigo-yakuso-distillery": [("株式会社越後薬草", "新潟県", "self", "high", "Echigo Yakuso Co., Joetsu (YASO gin); pin website yaso80gin.jp")],
    "amanokawashuzo-or-amanokawa-distillery": [("天の川酒造株式会社", "長崎県", "self", "high", "Amanokawa Shuzo Co., Iki; pin website amanokawashuzo.com")],
    "ikinokura-distillery-co-ltd": [("壱岐の蔵酒造株式会社", "長崎県", "self", "high", "Ikinokura Shuzo Co., Iki; pin website ikinokura.co.jp")],
    "muhyo-distillery": [("霧氷酒造株式会社", "長崎県", "self", "high", "Muhyo Shuzo Co.; register address 長崎市神浦夏井町391 = pin address; pin website nagasaki-muhyou.com")],
    "goto-retto-distillery-inc": [("五島列島酒造株式会社", "長崎県", "self", "high", "Goto Retto Shuzo Co.; pin website gotoretto.jp")],
    "sakimoto-sake-distillery": [("合名会社崎元酒造所", "沖縄県", "self", "high", "Sakimoto Shuzosho, Yonaguni; pin website sakimotoshuzo.com")],
    "donan-distillery": [("株式会社どなん酒造", "沖縄県", "self", "high", "Donan Shuzo, Yonaguni; register furigana ドナンシュゾウ, same postcode as the pin; pin website donan.thebase.in")],
    "yanbaru-distillery-inc": [("やんばる酒造株式会社", "沖縄県", "self", "high", "Yanbaru Shuzo Co., Ogimi (Maruta awamori); pin website takazato-maruta.jp")],
    "sakimoto-awamori-distillery": [("咲元酒造株式会社", "沖縄県", "self", "high", "Sakimoto Shuzo Co., Onna; pin website sakimoto-awamori.com")],
    "yamaga-distillery": [("山鹿蒸溜所株式会社", "熊本県", "self", "high", "Yamaga Distillery Co.; pin website yamagadistillery.co.jp")],
    "fugaku-distillery-sasakawa-whisky-co-ltd": [("SASAKAWA WHISKY株式会社", "山梨県", "self", "high", "Sasakawa Whisky Co., Fujiyoshida; NTA whisky licence 2023 at 富士吉田市上吉田4918-1 = pin address; pin website sasakawa-whisky.jp")],
    "hida-takayama-distillery": [("株式会社舩坂酒造店", "岐阜県", "operator", "medium", "Funasaka Shuzoten, Takayama; Hida Takayama distillery; pin website whisky-hida.com")],
    "shinobu-distillery": [("新潟小規模蒸溜所株式会社", "新潟県", "self", "high", "Niigata Micro Distillery Co. (Shinobu), Nishikan; pin website shinobudistillery.com")],
    "shirahama-distillery": [("南アルプスワインアンドビバレッジ株式会社", "山梨県", "operator", "medium", "Shirahama distillery (Shimoda) is run by Minami Alps Wine & Beverage (whisky licence 2021, NTA list); check")],
    "tokyo-hachioji-distillery": [("石川酒造株式会社", "東京都", "operator", "low", "Hachioji distillery; operator unconfirmed; pin website hachioji-distillery.jp")],
    "fukagawa-distillery": [("株式会社深川蒸留所", "東京都", "self", "high", "Fukagawa Distillery Co., Koto-ku Hirano 2-3-15 = pin address; pin website fukagawa-distillery.tokyo", "江東区")],
    "mitosaya-botanical-distillery": [("株式会社mitosaya", "千葉県", "self", "high", "mitosaya Co., Otaki; pin website mitosaya.com")],
    "tl-pearce-distillery": [("TL Enterprises株式会社", "千葉県", "self", "high", "TL Enterprises Co.; NTA spirits licence 2022, trading name TL Pearce Distillery, site 野田市七光台181-6 = pin address")],
    "iseya-distillery": [("伊勢屋酒造株式会社", "神奈川県", "self", "high", "Iseya Shuzo, Sagamihara; pin website iseyashuzo.com")],
    "alembic-distillery": [("株式会社Alembic", "石川県", "self", "high", "Alembic Co., Kanazawa; NTA spirits licence 2022, site 金沢市大野町4丁目ハ17 = pin address; pin website alembic.jp")],
    "yoshida-denzai-distillery": [("吉田電材工業株式会社", "新潟県", "operator", "high", "Yoshida Denzai Kogyo (electrical parts maker) built the Murakami grain distillery; pin website yoshidadenzai-distillery.com")],
    "tenkyo-distillery": [("天鏡ホールディングス株式会社", "福島県", "operator", "medium", "Tenkyo Holdings, Bandai (register address 磐梯町更科字天鏡, same postcode as the pin); pin website tenkyo.jp")],
    "dewa-distillery": [("出羽蒸留所株式会社", "山形県", "self", "high", "Dewa Distillery Co., Oguni; register address 小国町小坂町40-1 = pin address; pin website dewadistillery.com")],
    "di-tripper-distillery": [("株式会社BEHIND THE CASK", "北海道", "self", "high", "Behind the Cask Co.; NTA whisky licence 2023, trading name ディ・トリッパー蒸留所, site 函館市元町31-20 = pin address")],
    "tankyu-distillery": [("丹丘蒸留所株式会社", "北海道", "self", "high", "Tankyu Distillery Co., Higashikawa; pin name carries the kanji legal name")],
    "whisky-student": [("株式会社Whisky Student", "北海道", "self", "high", "Whisky Student Co., Tobetsu distillery; pin name carries ㈱Whisky Student")],
    "kyotango-mairingen-distillery": [("株式会社丹後王国", "京都府", "operator", "low", "Mairingen distillery, Kyotango; operator unconfirmed; pin website mairingen.jp")],
    "okumikawa-distillery": [("奥三河蒸留研究所有限会社", "愛知県", "self", "high", "Okumikawa Distillation Laboratory; register furigana オクミカワジョウリュウケンキュウジョ, Shinshiro; pin website valoreland.com")],
    "blue-rabbit-distillery": [("合同会社Blue Rabbit Distillery", "東京都", "self", "high", "Blue Rabbit Distillery LLC; NTA spirits licence 2022, site 大田区田園調布本町57-2 = pin address")],
    "neo-blue-distillery": [("株式会社Neo Blue Distillery", "山口県", "self", "high", "Neo Blue Distillery Co.; NTA spirits licence 2019, site 長門市油谷新別名960-7 = pin address")],
    "three-aroma-distillery": [("株式会社ACRO", "東京都", "operator", "medium", "ACRO Inc. (THREE cosmetics brand, POLA ORBIS group) runs the Yobuko aroma distillery, Karatsu; register row chosen by the 西五反田 head office", "品川区")],
    "sicx-gin-distillery-cafe-bar": [("株式会社FEC", "京都府", "operator", "high", "FEC Co.; NTA spirits licence 2022, trading name SiCX京都東山, site 東山区下堀詰町234 = pin address")],
    "naturadistill": [("株式会社Kokage", "福島県", "operator", "high", "Kokage Co.; NTA spirits licence 2024, trading name naturadistill, site 川内村上川内字町分396-2 = pin address")],
    "shibataya-brewery-distillery": [("株式会社柴田屋酒店", "東京都", "operator", "medium", "Shibataya (sake retailer/brewer, sake-ya-japan.com) runs the Sayama brewery-distillery; number left to the register lookup")],
    "number-eight-distillery": [("株式会社HUGE", "東京都", "operator", "high", "HUGE Co. (restaurant group) runs Number Eight distillery at Quays Pacific Grill, Yokohama Hammerhead; NTA beer licence 2019 names 法人番号7013201012145; pin website huge.co.jp", "神宮前")],
    "rikashitsu-distillery-utsunomiya": [("株式会社リカシツ", "東京都", "self", "medium", "Rikashitsu (laboratory glassware shop) distillery, Utsunomiya; pin website rikashitsu.jp; number left to the register lookup")],
    "distillery-japan-5": [("株式会社FLAVOUR", "静岡県", "self", "high", "FLAVOUR Co.; NTA spirits licence 2020, trading name 株式会社FLAVOUR沼津蒸留所, site 沼津市上土町8 = pin address; pin website flavour.jp")],
    "distillery-japan-7": [("合同会社ねっか", "福島県", "self", "high", "Nekka LLC, Tadami; pin website nekka.jp")],
    "sugimoto-shochu-distillery": [("杉本酒造株式会社", "鹿児島県", "self", "high", "Sugimoto Shuzo Co., Nagashima; instagram-only pin website")],
    "ishigaki-distillery": [("石垣ディスティラリー株式会社", "沖縄県", "self", "high", "Ishigaki Distillery Co.; register address 石垣市字崎枝530-5 = pin address; pin website ishigaki-distillery.com")],
    "nozawa-onsen-distillery": [("Nozawa Onsen Distillery株式会社", "長野県", "self", "high", "Nozawa Onsen Distillery Co.; NTA spirits licence 2022, site 野沢温泉村豊郷9394 = pin address")],
    "toranomon-distillery": [("株式会社虎ノ門蒸留所", "東京都", "self", "high", "Toranomon Distillery Co.; register furigana トラノモンジョウリュウジョ, Minato-ku")],
    "osuzuyama-distillery": [("株式会社尾鈴山蒸留所", "宮崎県", "self", "high", "Osuzuyama Distillery Co.; register address 木城町石河内, same postcode as the pin"),
                             ("株式会社黒木本店", "宮崎県", "group", "high", "Kuroki Honten, Takanabe; Osuzuyama distillery is its mountain site (Kijo)")],
    "komoro-distillery": [("軽井沢蒸留酒製造株式会社", "長野県", "self", "high", "Karuizawa Distillers Inc., Komoro; pin website komorodistillery.com"),
                          ("合同会社小諸蒸留所", "長野県", "self", "medium", "Komoro Distillery LLC; register furigana コモロジョウリュウジョ, same postcode as the pin")],
    "distillery-japan-24": [("紅櫻蒸溜所株式会社", "北海道", "self", "high", "Benizakura Distillery Co.; register address 札幌市南区澄川389-6 = pin address; pin website hlwhisky.co.jp (Hokkaido Liberty Whisky brand)")],
    "shochu-distillery-museum-toji-no-sato-kasasa": [("株式会社杜氏の里笠沙", "鹿児島県", "self", "high", "Toji no Sato Kasasa Co.; register furigana トウジノサトカササ, same postcode as the pin; pin website toujinosato.co.jp")],
    "ixey-non-alcoholic-spirits-kyoto-distillery-salon": [],
    "nameless-distillery": [],
}


# ------------------------------------------------------------ normalisation --
def nfkc(s: str) -> str:
    return unicodedata.normalize("NFKC", s or "").replace("　", " ").strip()


def kanji_norm(s: str) -> str:
    """Kanji company/pin name -> comparison key: NFKC, drop legal suffixes, generic words,
    spaces and punctuation, lower-case any Latin."""
    s = nfkc(s)
    for w in KANJI_SUFFIX + KANJI_GENERIC:
        s = s.replace(w, "")
    s = re.sub(r"[\s・･·／/()（）「」【】、,.\-‐－—–'\"]+", "", s)
    return s.lower()


def suffix_strip(s: str) -> str:
    s = nfkc(s)
    for w in KANJI_SUFFIX:
        s = s.replace(w, "")
    return re.sub(r"\s+", "", s)


def is_cjk(s: str) -> bool:
    return any("぀" <= c <= "ヿ" or "一" <= c <= "鿿" for c in s or "")


def latin_norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return re.sub(r"[^a-z0-9 ]+", " ", s)


def romaji_key(s: str) -> str:
    """Collapse Hepburn spelling variants so 'shuzou', 'shuzo', 'syuzo' compare equal."""
    s = latin_norm(s).replace(" ", "")
    s = re.sub(r"(ou|oo|oh|uu|ū|ō)", lambda m: m.group(1)[0], s)
    s = s.replace("m", "n").replace("tsu", "tu").replace("shi", "si").replace("chi", "ti").replace("sh", "sy") \
        .replace("ch", "ty").replace("ji", "zi").replace("j", "zy").replace("fu", "hu").replace("wi", "i").replace("we", "e")
    s = re.sub(r"(.)\1", r"\1", s)  # double consonants / vowels
    return s


ROMAJI_GENERIC = ["syuzozyo", "syuzo", "disutiringu", "zyoryukenkyuzyo", "zyozosyo", "zyozo", "zyoryusyo", "zyoryuzyo", "zyoryusyu", "zyoryu", "uisuki",
                  "disutirari", "disuteirari", "supiritu", "buruwari", "buruingu", "biru", "syurui", "syoten",
                  "honten", "saketen", "syotyu", "awanori", "wain", "rika", "seizosyo", "kenkyuzyo", "kenkyusyo",
                  "sisyo", "nihon", "nipon", "kabusikigaisya", "yugengaisya", "godogaisya", "gosigaisya", "gomeigaisya"]
EN_GENERIC = ["distillery", "distilling", "distillers", "brewery", "brewing", "corporation", "company", "holdings",
              "limited", "japan", "inc", "ltd", "co", "kk", "the", "and"]


def romaji_core(r: str) -> str:
    for w in ROMAJI_GENERIC:
        r = r.replace(w, "")
    return r


def en_core(r: str) -> str:
    for w in EN_GENERIC:
        r = r.replace(romaji_key(w), "")
    return r


KATA = {
    "ア": "a", "イ": "i", "ウ": "u", "エ": "e", "オ": "o", "カ": "ka", "キ": "ki", "ク": "ku", "ケ": "ke", "コ": "ko",
    "サ": "sa", "シ": "shi", "ス": "su", "セ": "se", "ソ": "so", "タ": "ta", "チ": "chi", "ツ": "tsu", "テ": "te", "ト": "to",
    "ナ": "na", "ニ": "ni", "ヌ": "nu", "ネ": "ne", "ノ": "no", "ハ": "ha", "ヒ": "hi", "フ": "fu", "ヘ": "he", "ホ": "ho",
    "マ": "ma", "ミ": "mi", "ム": "mu", "メ": "me", "モ": "mo", "ヤ": "ya", "ユ": "yu", "ヨ": "yo",
    "ラ": "ra", "リ": "ri", "ル": "ru", "レ": "re", "ロ": "ro", "ワ": "wa", "ヲ": "o", "ン": "n", "ヰ": "i", "ヱ": "e",
    "ガ": "ga", "ギ": "gi", "グ": "gu", "ゲ": "ge", "ゴ": "go", "ザ": "za", "ジ": "ji", "ズ": "zu", "ゼ": "ze", "ゾ": "zo",
    "ダ": "da", "ヂ": "ji", "ヅ": "zu", "デ": "de", "ド": "do", "バ": "ba", "ビ": "bi", "ブ": "bu", "ベ": "be", "ボ": "bo",
    "パ": "pa", "ピ": "pi", "プ": "pu", "ペ": "pe", "ポ": "po", "ヴ": "vu",
    "ァ": "a", "ィ": "i", "ゥ": "u", "ェ": "e", "ォ": "o", "ャ": "ya", "ュ": "yu", "ョ": "yo", "ヮ": "wa",
}
SMALL_Y = {"ャ": "ya", "ュ": "yu", "ョ": "yo"}
SMALL_V = {"ァ": "a", "ィ": "i", "ゥ": "u", "ェ": "e", "ォ": "o"}


def kana_to_romaji(s: str) -> str:
    """Katakana furigana -> rough Hepburn. Hiragana is folded to katakana first."""
    s = nfkc(s)
    s = "".join(chr(ord(c) + 0x60) if "ぁ" <= c <= "ゖ" else c for c in s)
    out, i = [], 0
    while i < len(s):
        c = s[i]
        nxt = s[i + 1] if i + 1 < len(s) else ""
        if c == "ッ":
            if nxt in KATA:
                out.append(KATA[nxt][0])
            i += 1
            continue
        if c == "ー":
            i += 1
            continue
        if c in KATA:
            r = KATA[c]
            if nxt in SMALL_Y and r.endswith("i"):
                r = r[:-1] + ("" if r[:-1] in ("sh", "ch", "j") else "y") + SMALL_Y[nxt][1]
                i += 1
            elif nxt in SMALL_V and c in ("フ", "ヴ", "ウ", "テ", "デ", "ト", "ド", "ツ"):
                r = r[0] + SMALL_V[nxt]
                i += 1
            out.append(r)
        elif c.isascii() and c.isalnum():
            out.append(c.lower())
        i += 1
    return "".join(out)


def latin_tokens(s: str) -> list[str]:
    return [t for t in latin_norm(s).split() if len(t) >= 4 and t not in STOP_LATIN and not t.isdigit()]


def domain_tokens(url: str) -> list[str]:
    """Distinctive tokens from the website host (second-level label split on hyphens)."""
    if not url:
        return []
    host = urllib.parse.urlparse(url if "://" in url else "http://" + url).netloc.lower()
    host = host.split(":")[0]
    if not host or any(host.endswith(d) for d in COMMON_DOMAIN):
        return []
    labels = [l for l in host.split(".") if l not in ("www", "shop", "co", "ne", "or", "jp", "com", "net", "info", "tokyo", "in")]
    toks = []
    for l in labels[:1]:
        toks.append(l.replace("-", ""))
        toks.extend(p for p in l.split("-") if len(p) >= 4)
    return [t for t in toks if len(t) >= 4 and t not in STOP_LATIN]


# ------------------------------------------------------------------- pins ----
def pin_prefecture(addr: str, slug: str) -> str:
    if slug in PIN_PREF:
        return PIN_PREF[slug]
    a = addr or ""
    for k, _, _ in PREFS:
        if k in a:
            return k
    pc = re.search(r"\d{3}-\d{4}", a)
    hits = [(m.start(), PREF_BY_EN[m.group(1).lower()])
            for m in re.finditer(r"\b(" + "|".join(en for _, en, _ in PREFS) + r")\b", a, flags=re.I)]
    if not hits:
        return ""
    if pc:
        before = [h for h in hits if h[0] < pc.start()]
        if before:
            return before[-1][1]
        after = [h for h in hits if h[0] > pc.start()]
        if after:
            return after[0][1]
    return hits[-1][1]


def load_pins():
    feats = json.loads(GEO.read_text())["features"]
    pins = []
    for f in feats:
        p = f["properties"]
        if p.get("country") != "Japan":
            continue
        addr = p.get("address") or ""
        name = p.get("name") or ""
        pc = re.search(r"\d{3}-\d{4}", addr)
        kanji_parts = [x for x in re.split(r"[/／()（）_、,]|\s{2,}| (?=[A-Za-z])", nfkc(name)) if is_cjk(x)]
        toks = set(latin_tokens(name)) | set(domain_tokens(p.get("website") or ""))
        pins.append({"slug": p["slug"], "name": name, "website": p.get("website") or "", "addr": addr,
                     "pref": pin_prefecture(addr, p["slug"]), "postcode": pc.group(0).replace("-", "") if pc else "",
                     "kanji": [kanji_norm(x) for x in kanji_parts if kanji_norm(x)],
                     "kanji_raw": [x for x in kanji_parts if kanji_norm(x)],
                     "domain": set(domain_tokens(p.get("website") or "")),
                     "toks": {romaji_key(t) for t in toks if len(romaji_key(t)) >= 4},
                     "raw_toks": toks})
    return pins


# ----------------------------------------------------------- NTA register ----
def fetch_nta(cache: Path, prefs: set[str], log: dict):
    """Download the CSV-Unicode 全件 zip for each prefecture not yet cached. One GET for the
    page (form token + cookies), then one POST per zip, >= 1 s apart."""
    ntadir = cache / "nta"
    ntadir.mkdir(parents=True, exist_ok=True)
    need = [k for k in sorted(prefs) if k and not (ntadir / f"{k}.zip").exists()]
    if not need:
        return
    jar = CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(jar))
    opener.addheaders = [("User-Agent", UA)]
    page = opener.open(SRC_NTA, timeout=60).read().decode("utf-8", "replace")
    log["nta-zenken-page"] = log.get("nta-zenken-page", 0) + 1
    token = re.search(r'CNSFWTokenProcessor\.request\.token" value="([^"]+)"', page).group(1)
    sec = re.split(r'<h2 class="title" id="(csv-sjis|csv-unicode|xml-unicode)">', page)
    body = sec[sec.index("csv-unicode") + 1]
    files = {}
    for m in re.finditer(r'<dt class="mb05">([^<]+)</dt>\s*<dd>(.*?)</dd>', body, flags=re.S):
        files[m.group(1).strip()] = re.findall(r"doDownload\((\d+)\);\">([^<]*)zip ([\d.]+[MK]B)", m.group(2))
    stamp = re.search(r"CSV形式・Unicode\s*</h2>\s*<p[^>]*>([^<]*更新)", body)
    print(f"nta: zenken page {stamp.group(1) if stamp else ''}; {len(files)} regions listed", file=sys.stderr)
    for k in need:
        if k not in files:
            print(f"warn: {k} not on the zenken page", file=sys.stderr)
            continue
        parts = []
        for fileno, label, size in files[k]:
            time.sleep(1.0)
            data = urllib.parse.urlencode({
                "jp.go.nta.houjin_bangou.framework.web.common.CNSFWTokenProcessor.request.token": token,
                "event": "download", "selDlFileNo": fileno}).encode()
            req = urllib.request.Request(NTA_ZENKEN_POST, data=data, headers={"Referer": SRC_NTA})
            blob = opener.open(req, timeout=600).read()
            log["nta-zenken-download"] = log.get("nta-zenken-download", 0) + 1
            parts.append(blob)
            print(f"nta: {k} {label.strip() or 'zip'} {size} -> {len(blob):,} bytes", file=sys.stderr)
        if len(parts) == 1:
            (ntadir / f"{k}.zip").write_bytes(parts[0])
        else:  # Tokyo comes split; merge the CSV members into one zip
            with zipfile.ZipFile(ntadir / f"{k}.zip", "w", zipfile.ZIP_DEFLATED) as zout:
                for i, blob in enumerate(parts):
                    with zipfile.ZipFile(io.BytesIO(blob)) as zin:
                        for n in zin.namelist():
                            if n.endswith(".csv"):
                                zout.writestr(f"{i}_{n}", zin.read(n))


def iter_register(cache: Path, pref: str):
    """Yield register rows (as lists) from the cached prefecture zip. Columns per the NTA
    resource definition: 1 法人番号, 6 name, 8 kind, 9 pref, 10 city, 11 street, 15 postcode,
    18 closure date, 19 closure reason, 22 assignment date, 24 English name, 26 English
    address, 28 furigana."""
    path = cache / "nta" / f"{pref}.zip"
    if not path.exists():
        print(f"warn: missing {path}", file=sys.stderr)
        return
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if not n.endswith(".csv"):
                continue
            with z.open(n) as fh:
                for row in csv.reader(io.TextIOWrapper(fh, encoding="utf-8", newline="")):
                    if len(row) >= 28:
                        yield row


def has_kanji_signal(name: str) -> bool:
    return any(w in name for w in KANJI_SIGNAL)


def load_register(cache: Path, prefs: set[str], pins, wanted_numbers: set[str], hand_names: set[str]):
    """Stream the prefecture files and keep only rows that could matter: postcode of a pin,
    kanji name of a pin or a hand row, a licence 法人番号, or a drinks word in the name."""
    postcodes = {p["postcode"] for p in pins if p["postcode"]}
    pin_kanji = {k for p in pins for k in p["kanji"]}
    hand_keys = {kanji_norm(n) for n in hand_names}
    pin_tokens = {t for p in pins for t in p["toks"] if len(t) >= 5}
    keep, by_number, by_key, by_pc = [], {}, defaultdict(list), defaultdict(list)
    n_rows, n_furi, n_en = 0, 0, 0
    for pref in sorted(prefs):
        for r in iter_register(cache, pref):
            n_rows += 1
            name = nfkc(r[6])
            key = kanji_norm(name)
            if r[28]:
                n_furi += 1
            if r[24]:
                n_en += 1
            romaji = romaji_key(kana_to_romaji(r[28])) if r[28] else ""
            en_key = romaji_key(r[24]) if r[24] else ""
            if not (r[15] in postcodes or key in pin_kanji or key in hand_keys or r[1] in wanted_numbers
                    or has_kanji_signal(name)
                    or any(t in romaji or t in en_key for t in pin_tokens)):
                continue
            rec = {"number": r[1], "name": name, "kind": r[8], "pref": r[9], "city": r[10], "street": r[11],
                   "postcode": r[15], "closed": r[18], "closed_reason": r[19], "assigned": r[22],
                   "en": nfkc(r[24]), "en_addr": nfkc(r[26]), "furigana": r[28], "key": key,
                   "romaji": romaji, "en_key": en_key}
            keep.append(rec)
            by_number[rec["number"]] = rec
            by_key[key].append(rec)
            if rec["postcode"]:
                by_pc[rec["postcode"]].append(rec)
    print(f"register: {n_rows:,} rows read from {len(prefs)} prefecture files; {len(keep):,} kept; "
          f"{n_furi:,} with furigana, {n_en:,} with English name", file=sys.stderr)
    return keep, by_number, by_key, by_pc


# ------------------------------------------------------------ licence list ---
def fetch_licences(cache: Path, log: dict):
    d = cache / "nta-licence"
    d.mkdir(parents=True, exist_ok=True)
    for path, tag in NTA_LICENCE_FILES:
        out = d / f"{tag}.xlsx"
        if out.exists():
            continue
        time.sleep(1.0)
        req = urllib.request.Request("https://www.nta.go.jp/taxes/sake/menkyo/shinki/seizo/" + path,
                                     headers={"User-Agent": UA})
        out.write_bytes(urllib.request.urlopen(req, timeout=60).read())
        log["nta-licence-xlsx"] = log.get("nta-licence-xlsx", 0) + 1
        print(f"licence: {tag}.xlsx {out.stat().st_size:,} bytes", file=sys.stderr)


def read_xlsx_rows(path: Path):
    """Minimal .xlsx reader (stdlib): shared strings with ruby (<rPh>) stripped, sheet1 cells."""
    with zipfile.ZipFile(path) as z:
        ss = z.read("xl/sharedStrings.xml").decode()
        strings = []
        for si in re.findall(r"<si>(.*?)</si>", ss, flags=re.S):
            si = re.sub(r"<rPh\b.*?</rPh>", "", si, flags=re.S)
            strings.append(html.unescape(re.sub(r"<[^>]+>", "", si)))
        sheet = z.read("xl/worksheets/sheet1.xml").decode()
    for r in re.findall(r"<row\b[^>]*>(.*?)</row>", sheet, flags=re.S):
        cells = {}
        for m in re.finditer(r'<c r="([A-Z]+)\d+"([^>]*)>(.*?)</c>', r, flags=re.S):
            col, attrs, inner = m.groups()
            v = re.search(r"<v>(.*?)</v>", inner, flags=re.S)
            if not v:
                continue
            cells[col] = strings[int(v.group(1))] if 't="s"' in attrs else v.group(1)
        yield cells


def load_licences(cache: Path):
    rows = []
    for _, tag in NTA_LICENCE_FILES:
        path = cache / "nta-licence" / f"{tag}.xlsx"
        if not path.exists():
            print(f"warn: missing {path}", file=sys.stderr)
            continue
        hdr = None
        for cells in read_xlsx_rows(path):
            if "税務署名" in cells.values():
                hdr = {v: k for k, v in cells.items()}
                continue
            if not hdr or not cells.get(hdr["製造者氏名又は名称"]):
                continue
            g = lambda k: nfkc(cells.get(hdr.get(k, ""), ""))
            lines = [nfkc(x) for x in re.split(r"\r?\n", cells[hdr["製造者氏名又は名称"]]) if x.strip()]
            number = ""
            if lines and lines[0].startswith("法人番号"):
                number = re.sub(r"\D", "", lines[0])
                lines = lines[1:]
            legal = lines[0] if lines else ""
            trade = " / ".join(lines[1:])
            pref = PREF_SHORT.get(g("都道府県名"), g("都道府県名"))
            rows.append({"year": tag, "pref": pref, "office": g("税務署名"), "date": g("免許等年月日"),
                         "number": number, "legal": legal, "trade": trade, "site": g("製造場所在地"),
                         "cls": g("免許等区分"), "product": g("品目"), "process": g("処理区分"),
                         "legal_key": kanji_norm(legal), "trade_key": kanji_norm(trade),
                         "latin": set(latin_tokens(legal + " " + trade))})
    print(f"licence: {len(rows)} rows, {sum(1 for r in rows if r['number'])} with 法人番号", file=sys.stderr)
    return rows


# --------------------------------------------------------------- matching ----
def status_note(rec: dict) -> str:
    if rec["closed"]:
        return f"register record closed {rec['closed']} (reason code {rec['closed_reason']})"
    return f"register record open; number assigned {rec['assigned']}"


def loc_note(rec: dict) -> str:
    return f"{rec['pref']}{rec['city']}{rec['street']}" + (f" 〒{rec['postcode']}" if rec["postcode"] else "")


def downgrade(g: str) -> str:
    return {"high": "medium", "medium": "low", "low": "low"}[g]


def row(pin, registry, number, name, relation, method, conf, source, note):
    return {"slug": pin["slug"], "distillery_name": pin["name"], "country": "Japan", "registry": registry,
            "company_number": number, "company_name": name, "relation": relation, "match_method": method,
            "confidence": conf, "verified": "", "source": source, "note": note}


def match_register(pins, keep, by_key, by_pc, licences):
    """Automatic register matches, one list per pin. Returns (candidates, licence_rows)."""
    cands, lic_rows = [], []
    lic_by_legal = defaultdict(list)
    lic_by_trade = defaultdict(list)
    for L in licences:
        if L["legal_key"]:
            lic_by_legal[L["legal_key"]].append(L)
        if L["trade_key"]:
            lic_by_trade[L["trade_key"]].append(L)
    for pin in pins:
        seen = set()

        def add(rec, method, conf, relation, why):
            if rec["number"] in seen:
                return
            seen.add(rec["number"])
            if rec["closed"]:
                conf = downgrade(conf)
            if pin["pref"] and rec["pref"] != pin["pref"] and method != "kanji-name":
                conf = downgrade(conf)
                why += f"; prefecture differs (pin {pin['pref']}, register {rec['pref']})"
            cands.append(row(pin, "jp-houjin-bangou", rec["number"], rec["name"], relation, method, conf, SRC_NTA,
                             f"{why}; {loc_note(rec)}; {status_note(rec)}"))

        # 1. kanji name equality: exact once legal suffixes go = high; equal only after generic
        #    words (蒸溜所 etc) go = medium; another prefecture = low
        for k, raw in zip(pin["kanji"], pin["kanji_raw"]):
            for rec in by_key.get(k, []):
                exact = suffix_strip(rec["name"]) == suffix_strip(raw)
                if pin["pref"] and rec["pref"] != pin["pref"]:
                    add(rec, "kanji-name", "low", "self", f"kanji name equal after normalisation ({k}) but in another prefecture")
                else:
                    add(rec, "kanji-name", "high" if exact else "medium", "self",
                        f"kanji name {'equal once legal suffixes are removed' if exact else 'equal after dropping generic words'} ({k})")
        # 2. licence list bridge: pin kanji == licence legal/trade name, or Latin tokens in trade name
        lic_hits = []
        for k in pin["kanji"]:
            lic_hits += lic_by_legal.get(k, []) + lic_by_trade.get(k, [])
        for L in licences:
            shared = L["latin"] & pin["raw_toks"]
            if shared and L["product"] in DISTILLED and (len(shared) >= 2 or shared & pin["domain"]
                                                         or max(len(t) for t in shared) >= 6):
                lic_hits.append(L)
            elif pin["kanji"] and L["trade_key"] and any(len(k) >= 3 and k in L["trade_key"] for k in pin["kanji"]):
                lic_hits.append(L)
        for L in lic_hits:
            conf = "high" if (not pin["pref"] or L["pref"] == pin["pref"]) else "low"
            lic_rows.append(row(pin, "nta-seizo-menkyo", L["number"], L["legal"], "self", "licence-name", conf,
                                SRC_NTA_LICENCE,
                                f"{L['year']} list: {L['cls']} {L['product']} {L['process']} {L['date']}, "
                                f"office {L['office']}, site {L['site']}; trading name '{L['trade']}'"))
            if L["number"]:
                for rec in [r for r in keep if r["number"] == L["number"]]:
                    add(rec, "licence-houjin", conf, "self",
                        f"法人番号 from NTA licence list {L['year']} ({L['product']}, site {L['site']}, trading name '{L['trade']}')")
        # 3. romanised bridge: register furigana / English name, with generic drinks words
        #    removed, equals (high) or barely exceeds (medium) a distinctive pin/domain token
        if pin["toks"]:
            for rec in keep:
                if not (rec["romaji"] or rec["en_key"]):
                    continue
                if pin["pref"] and rec["pref"] != pin["pref"]:
                    continue
                if rec["kind"] not in COMPANY_KINDS or NON_COMPANY.search(rec["name"]):
                    continue
                best = None
                for core, label in ((romaji_core(rec["romaji"]), "furigana " + rec["furigana"]),
                                    (en_core(rec["en_key"]), "English name " + repr(rec["en"]))):
                    if len(core) < 4:
                        continue
                    for t in sorted(pin["toks"]):
                        if len(t) < 4 or t not in core:
                            continue
                        same_pc = bool(pin["postcode"]) and rec["postcode"] == pin["postcode"]
                        signal = has_kanji_signal(rec["name"]) or bool(re.search(r"distill|whisk|spirit|brew|sake|shuzo|liquor", rec["en"], re.I))
                        equal = core == t or core in {a + b for a in pin["toks"] for b in pin["toks"] if a != b}
                        if len(t) < 5:
                            continue
                        if equal and (signal or same_pc):
                            conf, why = "high", f"register {label} equals pin/domain token '{t}' once drinks words are removed" + ("; same postcode" if same_pc else "; drinks word in name")
                        elif same_pc and len(t) >= 5 and signal:
                            conf, why = "high", f"pin/domain token '{t}' in register {label}; same postcode; drinks word in name"
                        elif same_pc:
                            conf, why = "low", f"pin/domain token '{t}' in register {label}; same postcode but no drinks word (lead only)"
                        elif len(core) <= len(t) + 3 and signal and len(t) >= 5:
                            conf, why = "medium", f"pin/domain token '{t}' in register {label} (core '{core}'); drinks word in name"
                        elif equal and len(t) >= 5:
                            conf, why = "low", f"register {label} equals pin/domain token '{t}' but no drinks word and no postcode agreement (lead only)"
                        else:
                            continue
                        rank = {"high": 3, "medium": 2, "low": 1}
                        if not best or rank[conf] > rank[best[0]]:
                            best = (conf, why)
                if best:
                    add(rec, "romaji-bridge", best[0], "self", best[1])
        # 4. postcode + drinks word
        if pin["postcode"]:
            for rec in by_pc.get(pin["postcode"], []):
                if has_kanji_signal(rec["name"]):
                    add(rec, "postcode-signal", "medium", "self",
                        f"same 7-digit postcode as the pin and a drinks word in the name")
    return cands, lic_rows


def hand_rows(pins, by_key):
    out = []
    for pin in pins:
        for legal, pref, relation, conf, note, *city in HAND.get(pin["slug"], []):
            key = kanji_norm(legal)
            hits = [r for r in by_key.get(key, []) if r["pref"] == pref] or by_key.get(key, [])
            if city:
                hits = [r for r in hits if city[0] in r["city"] + r["street"]] or hits
            exact = [r for r in hits if r["name"] == nfkc(legal)]
            if len(exact) == 1 and len(hits) > 1:
                hits = exact
            hits_open = [r for r in hits if not r["closed"]] or hits
            if len(hits_open) == 1:
                r = hits_open[0]
                out.append(row(pin, "jp-houjin-bangou", r["number"], r["name"], relation, "hand", conf, SRC_NTA,
                               f"{note}; register-checked 20 Sep 2026: {loc_note(r)}; {status_note(r)}"))
            elif len(hits_open) > 1:
                r = hits_open[0]
                out.append(row(pin, "jp-houjin-bangou", "", legal, relation, "hand", downgrade(conf), SRC_NTA,
                               f"{note}; {len(hits_open)} register rows share this name in {pref}, number not resolved"))
            else:
                out.append(row(pin, "jp-houjin-bangou", "", legal, relation, "hand", downgrade(conf), SRC_NTA,
                               f"{note}; not found in the {pref} register file by this kanji name"))
    return out


def write_csv(path: Path, rows: list[dict]):
    rows = sorted(rows, key=lambda r: (r["slug"], {"high": 0, "medium": 1, "low": 2}[r["confidence"]],
                                       r["relation"], r["company_number"]))
    with path.open("w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=FIELDS)
        w.writeheader()
        for r in rows:
            w.writerow(r)


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--cache", required=True, type=Path)
    ap.add_argument("--fetch-nta", action="store_true", help="download missing prefecture zips from the NTA site")
    ap.add_argument("--fetch-licences", action="store_true", help="download the yearly NTA licence Excel files")
    ap.add_argument("--summary", type=Path, help="write a JSON summary (counts, request log) here")
    args = ap.parse_args()
    log = {}

    pins = load_pins()
    prefs = {p["pref"] for p in pins if p["pref"]} | {pref for rows_ in HAND.values() for _, pref, *_ in rows_}
    print(f"pins: {len(pins)} Japan; {sum(1 for p in pins if p['pref'])} with prefecture; "
          f"{sum(1 for p in pins if p['postcode'])} with postcode; {len(prefs)} prefectures needed", file=sys.stderr)
    if args.fetch_licences:
        fetch_licences(args.cache, log)
    if args.fetch_nta:
        fetch_nta(args.cache, prefs, log)

    licences = load_licences(args.cache)
    lic_numbers = {L["number"] for L in licences if L["number"]}
    hand_names = {legal for rows_ in HAND.values() for legal, *_ in rows_}
    keep, by_number, by_key, by_pc = load_register(args.cache, prefs, pins, lic_numbers, hand_names)

    auto, lic_rows = match_register(pins, keep, by_key, by_pc, licences)
    hand = hand_rows(pins, by_key)
    # a hand row for the same slug+number supersedes the automatic row
    hand_keys = {(r["slug"], r["company_number"]) for r in hand if r["company_number"]}
    auto = [r for r in auto if (r["slug"], r["company_number"]) not in hand_keys]
    # a kanji legal name already produced by hand (number unresolved) also drops the auto duplicate
    # Two grading guards, 20 Sep. A postcode neighbour with a sake or liquor word is a lead,
    # not a match: liquor shops, a clinic and a union came through at medium. And where a hand
    # row names the group or operator of a site, machine rows for that site are town-name
    # collisions (Yoichi Beer for Yoichi Distillery), so they become leads too.
    operated = {r["slug"] for r in hand if r["relation"] in ("operator", "group")}
    for r in auto:
        if r["match_method"] == "postcode-signal" and r["confidence"] != "low":
            r["confidence"] = "low"
            r["note"] = "postcode neighbour only; " + r["note"]
        elif r["slug"] in operated and r["confidence"] != "low":
            r["confidence"] = "low"
            r["note"] = "site is group-run per the hand row; name match is a lead; " + r["note"]
    write_csv(OUT_CANDIDATES, auto + hand)
    write_csv(OUT_LICENCES, lic_rows)

    matched = defaultdict(lambda: "")
    order = {"high": 3, "medium": 2, "low": 1, "": 0}
    for r in auto + hand:
        if r["company_number"] and order[r["confidence"]] > order[matched[r["slug"]]]:
            matched[r["slug"]] = r["confidence"]
    per_pref = defaultdict(lambda: {"pins": 0, "high": 0, "medium": 0, "low": 0, "unmatched": 0})
    for p in pins:
        d = per_pref[p["pref"] or "(no prefecture)"]
        d["pins"] += 1
        d[matched[p["slug"]] or "unmatched"] += 1
    summary = {"pins": len(pins), "candidates": len(auto + hand), "licence_rows": len(lic_rows),
               "per_prefecture": {PREF_EN.get(k, k): v for k, v in sorted(per_pref.items())},
               "unmatched": sorted(p["slug"] for p in pins if not matched[p["slug"]]),
               "requests": log}
    print(json.dumps(summary, ensure_ascii=False, indent=1), file=sys.stderr)
    if args.summary:
        args.summary.write_text(json.dumps(summary, ensure_ascii=False, indent=1))
    print(f"wrote {OUT_CANDIDATES} ({len(auto + hand)} rows) and {OUT_LICENCES} ({len(lic_rows)} rows)")


if __name__ == "__main__":
    main()
