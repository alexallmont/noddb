import pytest
from noddb.path import split_path


def test_split_path():
    path = 'this.th_at[0][1].et0c'
    split = split_path(path)
    assert len(split) == 5
    assert split[0] == 'this'
    assert split[1] == 'th_at'
    assert split[2] == 0
    assert split[3] == 1
    assert split[4] == 'et0c'

    with pytest.raises(ValueError) as excinfo:
        _ = split_path('good.0bad')
    assert str(excinfo.value) == "invalid literal for int() with base 10: '0bad'"
