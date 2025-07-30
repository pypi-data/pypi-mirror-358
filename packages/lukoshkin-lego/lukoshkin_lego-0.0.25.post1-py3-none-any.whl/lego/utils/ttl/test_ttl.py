import pytest

from lego.utils.ttl.ttl import ExpireTime


def test_expiration_time_parsing():
    with pytest.raises(ValueError, match="Invalid time format"):
        ExpireTime.from_str("DAY")

    assert ExpireTime.from_str("13") == 13
    assert ExpireTime.from_str("3s") == 3
    assert ExpireTime.from_str("3m") == 180
    assert ExpireTime.from_str("2h") == 7200
    assert ExpireTime.from_str("2d") == 172800
    assert ExpireTime.from_str("1w") == 604800

    assert ExpireTime.parse(None) is None
    assert ExpireTime.parse("-1") == -1
    assert ExpireTime.parse("0") == 0
    assert ExpireTime.parse("1") == 1
    assert ExpireTime.parse(0) == 0
    assert ExpireTime.parse(1) == 1
    assert ExpireTime.parse("1m") == 60
