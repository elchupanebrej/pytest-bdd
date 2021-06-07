from textwrap import dedent

from pytest_bdd.model.builder import CSVParser
from deepdiff import DeepDiff


def test_trivial_csv_parsing():
    assert not DeepDiff(CSVParser.parse(dedent(
        """\
            header1, header2, header3
            1,       2,       3
        """.strip()
    )), {'headers': ['header1', 'header2', 'header3'], 'rows': [['1', '2', '3']]})
