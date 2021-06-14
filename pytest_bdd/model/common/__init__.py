from typing import List

from attr import attrs, attrib, Factory


@attrs
class DataColumn:
    header = attrib(default=None, kw_only=True)  # type: DataCell
    data = attrib(default=Factory(list), kw_only=True)  # type: List[DataCell]


@attrs
class DataCell:
    value = attrib(default=None, kw_only=True)
