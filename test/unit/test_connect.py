import pytest

from pyclvm.connect import connect


def test_connect_with_non_existing_instance(capsys):
    data = {"profile": "shako_remote"}
    connect("XXXXX", **data)
    out, _ = capsys.readouterr()
    assert out == "[ERROR] No such instance registered: wrong instance name provided\n"
