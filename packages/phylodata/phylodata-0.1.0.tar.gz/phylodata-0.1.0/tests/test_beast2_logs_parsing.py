from io import BytesIO

import pytest

from phylodata.errors import ValidationError
from phylodata.parsers.parse_files import parse_beast2_logs


def to_bytes_io(text: str):
    bytesio = BytesIO(bytes(text, "ascii"))
    bytesio.name = "Test"
    return bytesio


def test_simple_log_is_ok():
    raw_logs = "state   posterior"
    for s in range(1000):
        raw_logs += f"\n{s}   0"

    file = to_bytes_io(raw_logs)
    parse_beast2_logs(file)


def test_log_file_with_few_lines_fails():
    with pytest.raises(ValidationError):
        raw_logs = "state   posterior"
        for s in range(5):
            raw_logs += f"\n{s} 0"

        file = to_bytes_io(raw_logs)
        parse_beast2_logs(file)


def test_empty_file_fails():
    with pytest.raises(ValidationError):
        file = to_bytes_io("")
        parse_beast2_logs(file)


def test_no_tsv_fails():
    with pytest.raises(ValidationError):
        file = to_bytes_io("""This is some random file:khklhdsf
            asdfsadfsadf""")
        parse_beast2_logs(file)
