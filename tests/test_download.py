import pytest

import project0
from project0 import project0

url2 = ("http://normanpd.normanok.gov/content/daily-activity")

def test_list_sanity():
    assert project0.fetchincidents(url2) is not None

def test_list_size():
    assert len(project0.fetchincidents(url2)) == 7

