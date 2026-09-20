"""python3 -m unittest scripts/crosswalklib/test_lib.py  (run from the repo root)"""
import http.server
import ssl
import threading
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from crosswalklib import fetch, grading, names, rows
from crosswalklib.grading import Evidence


class Names(unittest.TestCase):
    def test_strips_suffix_and_generic(self):
        self.assertEqual(names.tokens("Distillerie de la Haute-Loue SARL"), frozenset({"haute", "loue"}))
        self.assertEqual(names.tokens("株式会社ベンチャーウイスキー Venture Whisky Co., Ltd."), frozenset({"venture"}))

    def test_exact_keeps_generic_words(self):
        self.assertTrue(names.exact("Yoichi Distillery", "YOICHI DISTILLERY LTD"))
        self.assertFalse(names.exact("Yoichi Distillery", "Yoichi Beer LLC"))

    def test_all_generic_name_keeps_its_words(self):
        self.assertEqual(names.tokens("CHATEAU DE COGNAC"), frozenset({"chateau", "cognac"}))
        self.assertTrue(names.exact("Château de Cognac", "CHATEAU DE COGNAC SAS"))

    def test_exact_tolerates_a_missing_generic_word(self):
        self.assertTrue(names.exact("Distillerie L'Officine", "L'OFFICINE"))
        self.assertFalse(names.exact("Yoichi Distillery", "Yoichi Beer LLC"))

    def test_signal(self):
        self.assertTrue(names.has_signal("Lake Country Libare Distilling, LLC"))
        self.assertFalse(names.has_signal("KMH Enterprises LLC"))


class Grading(unittest.TestCase):
    def test_exact_strong_active_is_high(self):
        self.assertEqual(grading.grade(Evidence(1.0, True, "strong")), "high")

    def test_inactive_caps_medium(self):
        self.assertEqual(grading.grade(Evidence(1.0, True, "strong", active=False)), "medium")

    def test_partial_without_location_is_nothing(self):
        self.assertIsNone(grading.grade(Evidence(0.65, False, "none")))

    def test_generic_pin_needs_a_strong_location(self):
        self.assertFalse(names.distinctive("La Distillerie"))
        self.assertFalse(names.distinctive("Craft Spirits Co"))
        self.assertTrue(names.distinctive("Dusty Barrel Distillery"))
        self.assertTrue(names.distinctive("Yoichi Distillery"))
        self.assertIsNone(grading.grade(Evidence(1.0, True, "none", distinctive=False)))
        self.assertEqual(grading.grade(Evidence(1.0, True, "weak", distinctive=False)), "low")
        self.assertEqual(grading.grade(Evidence(1.0, True, "strong", distinctive=False)), "medium")

    def test_name_alone_without_signal_is_nothing(self):
        self.assertIsNone(grading.grade(Evidence(1.0, True, "none", signal=False)))
        self.assertEqual(grading.grade(Evidence(1.0, True, "none", signal=True)), "high")

    def test_weak_location_needs_signal_for_high(self):
        self.assertEqual(grading.grade(Evidence(1.0, True, "weak", signal=False)), "medium")
        self.assertEqual(grading.grade(Evidence(1.0, True, "weak", signal=True)), "high")

    def test_guard_ambiguous_highs(self):
        mk = lambda n: {"slug": "niagara", "relation": "self", "match_method": "m", "company_number": n,
                        "confidence": "high", "distillery_name": "Niagara Distillery", "company_name": "Niagara " + n, "note": "", "registry": "r"}
        rs = [mk("1"), mk("2")]
        grading.apply_guards(rs, [])
        self.assertEqual({r["confidence"] for r in rs}, {"medium"})

    def test_conflict_never_high(self):
        self.assertEqual(grading.grade(Evidence(1.0, True, "conflict")), "medium")

    def test_guard_group_run_site(self):
        hand = [{"slug": "yoichi", "registry": "r", "relation": "operator", "match_method": "hand", "company_number": "1",
                 "confidence": "high", "distillery_name": "Yoichi Distillery", "company_name": "Nikka", "note": ""}]
        auto = [{"slug": "yoichi", "registry": "r", "relation": "self", "match_method": "romaji", "company_number": "2",
                 "confidence": "high", "distillery_name": "Yoichi Distillery", "company_name": "Yoichi Beer", "note": ""}]
        grading.apply_guards(auto, hand)
        self.assertEqual(auto[0]["confidence"], "low")

    def test_guard_premises_only(self):
        r = [{"slug": "x", "registry": "r", "relation": "self", "match_method": "ttb-premises", "company_number": "1",
              "confidence": "medium", "distillery_name": "Old Prentice Distillery", "company_name": "Four Roses Distillery LLC", "note": ""}]
        grading.apply_guards(r, [])
        self.assertEqual(r[0]["confidence"], "low")

    def test_guard_no_number(self):
        r = [{"slug": "x", "registry": "r", "relation": "self", "match_method": "hand", "company_number": "",
              "confidence": "high", "distillery_name": "A", "company_name": "A Ltd", "note": ""}]
        grading.apply_guards(r, [])
        self.assertEqual(r[0]["confidence"], "low")


class Rows(unittest.TestCase):
    def test_validate_shapes(self):
        r = rows.make("s", "D", "France", "fr-sirene", "12345678", "D SAS", "self", "m", "high", "u", "")
        self.assertTrue(any("wrong shape" in p for p in rows.validate([r])))
        r["company_number"] = "123456789"
        self.assertEqual(rows.validate([r]), [])

    def test_write_refuses_bad(self):
        with TemporaryDirectory() as d:
            r = rows.make("s", "D", "X", "r", "1", "D", "self", "m", "high", "u", "")
            r["verified"] = "2026-01-01"
            with self.assertRaises(SystemExit):
                rows.write(Path(d) / "x.csv", [r])


class Fetch(unittest.TestCase):
    def test_no_way_to_disable_tls(self):
        with TemporaryDirectory() as d:
            f = fetch.Fetcher(Path(d), allow=False)
            self.assertEqual(f._ctx.verify_mode, ssl.CERT_REQUIRED)
            self.assertTrue(f._ctx.check_hostname)

    def test_not_allowed_never_fetches(self):
        with TemporaryDirectory() as d:
            f = fetch.Fetcher(Path(d), allow=False)
            self.assertIsNone(f.get("http://127.0.0.1:9/never"))
            self.assertEqual(f.made, 0)

    def test_cap_and_log_before_request(self):
        class H(http.server.BaseHTTPRequestHandler):
            def do_GET(self):
                self.send_response(200); self.end_headers(); self.wfile.write(b"ok")
            def log_message(self, *a): pass
        srv = http.server.HTTPServer(("127.0.0.1", 0), H)
        t = threading.Thread(target=srv.serve_forever, daemon=True); t.start()
        try:
            with TemporaryDirectory() as d:
                f = fetch.Fetcher(Path(d), allow=True, cap=2, delay=0)
                base = f"http://127.0.0.1:{srv.server_port}/"
                self.assertEqual(f.get(base + "a"), b"ok")
                self.assertEqual(f.get(base + "b"), b"ok")
                self.assertIsNone(f.get(base + "c"))       # cap
                self.assertEqual(f.get(base + "a"), b"ok")  # cache, no request
                log = (Path(d) / "requests.log").read_text()
                self.assertEqual(log.count("REQ "), 2)
                f2 = fetch.Fetcher(Path(d), allow=True, cap=2, delay=0)
                self.assertEqual(f2.made, 2)                # a new run inherits the log's count
        finally:
            srv.shutdown()


if __name__ == "__main__":
    unittest.main()
