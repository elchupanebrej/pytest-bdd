from attr import attrs, attrib, Factory
from typing import List, Any, Optional


@attrs
class GherkinYamlModel:
    features = attrib(default=Factory(list), kw_only=True)  # type: List[Feature]


@attrs
class FeatureNode:
    keyword = attrib(default=None, kw_only=True)  # type: str
    name = attrib(default=None, kw_only=True)  # type: str
    uri = attrib(default=None, kw_only=True)  # type: URI
    description = attrib(default=None, kw_only=True)  # type: Description
    attachments = attrib(default=Factory(list), kw_only=True)  # type: List[Attachment]


@attrs
class Tagable:
    tags = attrib(default=Factory(list), kw_only=True)  # type: List[Tag]


@attrs
class Feature(FeatureNode, Tagable):
    scenarios = attrib(default=Factory(list), kw_only=True)  # type: List[Scenario]
    rules = attrib(default=Factory(list), kw_only=True)  # type: List[Rule]
    backgrounds = attrib(default=Factory(list), kw_only=True)  # type: List[Background]
    examples = attrib(default=Factory(list), kw_only=True)  # type: List[ExampleTable]


@attrs
class Scenario(FeatureNode, Tagable):
    examples = attrib(default=Factory(list), kw_only=True)  # type: List[ExampleTable]
    steps = attrib(default=Factory(list), kw_only=True)  # type: List[Step]


@attrs
class Rule(FeatureNode, Tagable):
    backgrounds = attrib(default=Factory(list), kw_only=True)  # type: List[Background]
    scenarios = attrib(default=Factory(list), kw_only=True)  # type: List[Scenario]
    examples = attrib(default=Factory(list), kw_only=True)  # type: List[ExampleTable]
    rules = attrib(default=Factory(list), kw_only=True)  # type: List[Rule]


@attrs
class Background(FeatureNode, Tagable):
    examples = attrib(default=Factory(list), kw_only=True)  # type: List[ExampleTable]
    steps = attrib(default=Factory(list), kw_only=True)  # type: List[Step]


@attrs
class Step(FeatureNode):
    parameters = attrib(default=Factory(list), kw_only=True)  # type: List[StepParameter]
    datatables = attrib(default=Factory(list), kw_only=True)  # type: List[DataTable]


@attrs
class StepParameter:
    name = attrib(default=Factory(list), kw_only=True)  # type: str


@attrs
class ExampleTable(FeatureNode):
    datatable = attrib(default=Factory(list), kw_only=True)  # type: DataTable


@attrs
class DataTable:
    columns = attrib(default=Factory(list), kw_only=True)  # type: List[DataColumn]


@attrs
class DataColumn:
    name = attrib(default=Factory(list), kw_only=True)  # type: DataCell
    data = attrib(default=Factory(list), kw_only=True)  # type: List[DataCell]


@attrs
class DataCell:
    value = attrib(default=None, kw_only=True)  # type: List[Any]


@attrs
class DataTableProvider:
    converter = attrib(default=None, kw_only=True)
    attachment = attrib(default=None, kw_only=True)  # type: Attachment

    def provide(self) -> DataTable:
        raise NotImplementedError


@attrs
class AttachmentResolver:
    # TODO
    pass


@attrs
class Attachment:
    content = attrib(default=None, kw_only=True)  # type: bytes
    contentType = attrib(default=None, kw_only=True)  # type: str


@attrs
class Attachable:
    contentType = attrib(default=None, kw_only=True)  # type: str


@attrs
class AttachmentProvider(Attachable):
    contentType = attrib(default=None, kw_only=True)  # type: Optional[str]

    def provide(self) -> Attachment:
        raise NotImplementedError


@attrs
class URIAttachmentProvider(AttachmentProvider):
    uri = attrib(default=None, kw_only=True)  # type: URI

    # TODO
    def provide(self) -> Attachment:
        raise NotImplementedError


@attrs
class PathAttachmentProvider(AttachmentProvider):
    path = attrib(default=None, kw_only=True)  # type: str

    # TODO
    def provide(self) -> Attachment:
        raise NotImplementedError


class Description(Attachment):
    pass


@attrs
class URI:
    name = attrib(default=None, kw_only=True)  # type: str


@attrs
class RelativePath:
    name = attrib(default=None, kw_only=True)  # type: str


@attrs
class Tag:
    name = attrib(default=None, kw_only=True)  # type: str

    @name.validator
    def name_validator(self, attribute, value):
        if not isinstance(value, str):
            raise ValueError('Tag name has to be string')
