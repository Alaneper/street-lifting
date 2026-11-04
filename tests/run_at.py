"""Rejoue un test e2e à une heure imposée (fuseau Europe/Brussels), pour reproduire les bugs qui n'apparaissent qu'à certaines heures
(ex. 00h10 : la date UTC est celle de la veille). Usage : python3 tests/run_at.py 2026-11-04T00:10:00 tests/e2e_v46.py"""
import sys, runpy, datetime
from playwright.sync_api import Browser
quand, script = sys.argv[1], sys.argv[2]
sys.argv = [script]
orig = Browser.new_context
def new_context(self, *a, **kw):
    kw.setdefault("timezone_id", "Europe/Brussels")
    c = orig(self, *a, **kw)
    c.clock.install(time=datetime.datetime.fromisoformat(quand).replace(tzinfo=__import__("zoneinfo").ZoneInfo("Europe/Brussels")))
    return c
Browser.new_context = new_context
runpy.run_path(script, run_name="__main__")
