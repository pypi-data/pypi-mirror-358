import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from worldbank_api.indicators import get_export, get_import, get_pib

def test_export():
    df = get_export("SN")
    assert not df.empty

def test_import():
    df = get_import("SN")
    assert not df.empty

def test_pib():
    df = get_pib(["SN", "FR"])
    assert not df.empty
