"""
Shared pieces for every scripts/match_*_registers.py: one name normaliser, one grading
table, one fetcher, one row schema. Written 20 Sep 2026 after the world pass showed each
matcher inventing its own (three grading tables, one TLS bypass, one cap overrun).

    from crosswalklib import names, grading, fetch, rows

A matcher must not define its own norm/jaccard/grade or open a socket outside fetch.Fetcher.
"""
