import csv
import re
from collections import namedtuple
from io import StringIO
from itertools import zip_longest
from operator import getitem, itemgetter
from pathlib import Path

from attr import attrib, attrs, Factory
from requests import get

from pytest_bdd.model.feature import (
    DataCell,
    DataColumn,
    DataTable,
    ExampleTable,
    Feature,
    GherkinYamlModel,
    Rule,
    Scenario,
    Step,
    StepParameter,
    Tag,
)
from pytest_bdd.model.keyword import Keyword


KeywordData = namedtuple('KeywordData', ['keyword', 'payload'])


@attrs
class Builder:
    context = attrib(kw_only=True, default=Factory(dict))

    def build(self, data: KeywordData):
        raise NotImplementedError


def getitemdefault(obj, key, **kwargs):
    try:
        return obj[key]
    except KeyError as e:
        try:
            return kwargs['default']
        except KeyError:
            raise e


def get_item_with_key_by_group(obj, key_group, **kwargs) -> KeywordData:
    for key in key_group:
        try:
            return KeywordData(key, getitem(obj, key))
        except KeyError:
            continue
    try:
        return KeywordData(None, kwargs['default'])
    except KeyError:
        raise KeyError(f'Keys from key_group {key_group} are not present in object from {obj}')


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class GherkinYamlModelBuilder(Builder):
    def build(self, data: KeywordData):
        gherkin_yaml_raw_data = data.payload
        features = [*map(
            lambda value: FeatureBuilder(context=self.context).build(get_item_with_key_by_group(
                value,
                Keyword.Feature.all
            )),
            gherkin_yaml_raw_data)]
        return GherkinYamlModel(features=features)


@attrs
class CompositeBuilder(Builder):
    Buildable = attrib(kw_only=True, default=None)  # type: type

    def build(self, data: KeywordData):
        _, name = get_item_with_key_by_group(data.payload, [Keyword.FeatureNode.NAME])

        # description_data = get_item_with_key_by_group(data.payload, Keyword.Description.all, default=None)
        # description = DescriptionBuilder(context=self.context).build(description_data)

        tags_data = get_item_with_key_by_group(data.payload, Keyword.Tags.all, default=[])
        tags = TagBuilder(context=self.context).build(tags_data)

        backgrounds_data = get_item_with_key_by_group(data.payload, Keyword.Backgrounds.all, default=[])
        backgrounds = BackgroundsBuilder(context=self.context).build(backgrounds_data)

        scenarios_data = get_item_with_key_by_group(data.payload, Keyword.Scenarios.all, default=[])
        scenarios = ScenariosBuilder(context=self.context).build(scenarios_data)

        examples_data = get_item_with_key_by_group(data.payload, Keyword.Examples.all, default=[])
        examples = ExamplesBuilder(context=self.context).build(examples_data)

        return self.Buildable(
            name=name,
            # description=description,
            tags=tags,
            backgrounds=backgrounds,
            scenarios=scenarios,
            examples=examples,
        )


@attrs
class FeatureBuilder(CompositeBuilder):
    Buildable = attrib(default=Feature, kw_only=True)


@attrs
class RuleBuilder(CompositeBuilder):
    Buildable = attrib(default=Rule, kw_only=True)


@attrs
class DescriptionBuilder(Builder):
    # TODO
    def build(self, data):
        raise NotImplementedError


@attrs
class ScenarioCollectionBuilder(Builder):
    def build(self, data):
        collection_data = data.payload
        scenarios = []
        for background_data in collection_data:
            # Supporting python > 3.5 so not using pattern matching

            try:
                scenario_data = get_item_with_key_by_group(background_data, Keyword.ExecutableNode.Scenario.all)
            except KeyError:
                pass
            else:
                scenario = ScenarioBuilder(context=self.context).build(scenario_data)
                scenarios.append(scenario)
                continue

            try:
                rule_data = get_item_with_key_by_group(background_data, Keyword.ExecutableNode.Rule.all)
            except KeyError:
                pass
            else:
                rule = RuleBuilder(context=self.context).build(rule_data)
                scenarios.append(rule)
                continue

        return scenarios


class BackgroundsBuilder(ScenarioCollectionBuilder):
    pass


class ScenariosBuilder(ScenarioCollectionBuilder):
    pass


@attrs
class ScenarioBuilder(Builder):
    def build(self, data: KeywordData):
        _, name = get_item_with_key_by_group(data.payload, [Keyword.FeatureNode.NAME])

        # description_data = get_item_with_key_by_group(data.payload, Keyword.Description.all, default=None)
        # description = DescriptionBuilder(context=self.context).build(description_data)

        tags_data = get_item_with_key_by_group(data.payload, Keyword.Tags.all, default=[])
        tags = TagBuilder(context=self.context).build(tags_data)

        steps_data = get_item_with_key_by_group(data.payload, Keyword.Steps.all, default=[])
        steps = StepsBuilder(context=self.context).build(steps_data)

        examples_data = get_item_with_key_by_group(data.payload, Keyword.Examples.all, default=[])
        examples = ExamplesBuilder(context=self.context).build(examples_data)

        return Scenario(
            name=name,
            # description=description,
            tags=tags,
            examples=examples,
            steps=steps,
        )


class StepBuilder(Builder):
    def build(self, data: KeywordData):
        if isinstance(data.payload, str):
            step_name = data.payload
            keyword = Keyword.Step.Key.AND
            data_tables = []

        elif isinstance(data.payload, dict):
            keyword, step_data = get_item_with_key_by_group(data.payload, Keyword.Step.Key.all)
            if isinstance(step_data, str):
                step_name = step_data
                data_tables = []
            else:
                step_name = step_data['Step']
                data_tables_data = get_item_with_key_by_group(step_data, [Keyword.Examples.DATA_TABLES], default=[])
                data_tables = ExamplesBuilder(context=self.context).build(data_tables_data)
        else:
            # TODO
            raise RuntimeError
        parameters = StepParametersBuilder(context=self.context).build(
            KeywordData('StepParameterSource', step_name)
        )
        return Step(keyword=keyword, parameters=parameters, datatables=data_tables)


class StepParametersBuilder(Builder):
    @classmethod
    def get_step_param_names_from_definition(cls, step_definition):
        return re.findall(cls.STEP_PARAM_RE, step_definition)

    def build(self, data):
        return [
            StepParameter(name=parameter_name)
            for parameter_name
            in self.get_step_param_names_from_definition(data.payload)
        ]

    STEP_PARAM_RE = re.compile(r"<(.+?)>")


class StepsBuilder(Builder):
    def build(self, data: KeywordData):
        steps = []
        for step_data in data.payload:
            steps.append(StepBuilder(context=self.context).build(KeywordData('Step', step_data)))
        return steps


class ExamplesBuilder(Builder):
    def build(self, data: KeywordData):
        examples = []
        for raw_example_data in data.payload:
            try:
                example_data = get_item_with_key_by_group(raw_example_data, Keyword.Examples.Table.all)
            except KeyError:
                # TODO add logging here
                continue
            else:
                examples.append(ExampleBuilder(context=self.context).build(example_data))

        built_examples = [*map(lambda value: ExampleTable(keyword=data.keyword, datatable=value), examples)]

        return built_examples


class ExampleBuilder(Builder):
    def build(self, data):
        try:
            _, content = get_item_with_key_by_group(data.payload, Keyword.Examples.Loader.Embeded.all)
        except KeyError:
            pass
        else:
            if isinstance(content, dict):
                return RawEmbeddedExampleBuilder(context=self.context).build(data)
            else:
                return EmbeddedExampleBuilder(context=self.context).build(data)

        try:
            get_item_with_key_by_group(data.payload, Keyword.Examples.Loader.File.all)
        except KeyError:
            pass
        else:
            return PathExampleBuilder(context=self.context).build(data)

        try:
            get_item_with_key_by_group(data.payload, Keyword.Examples.Loader.URI.all)
        except KeyError:
            pass
        else:
            return URIExampleBuilder(context=self.context).build(data)


class CSVParser:
    class Default:
        delimiter = ','
        doublequote = True
        escapechar = None
        lineterminator = '\r\n'
        quotechar = '"'
        skipinitialspace = True
        strict = True

    @classmethod
    def parse(cls, data, data_meta=None):
        if data_meta is None:
            data_meta = {}
        file_like_data = StringIO(data)

        delimiter = getitemdefault(data_meta, 'Delimiter', default=cls.Default.delimiter)
        doublequote = getitemdefault(data_meta, 'Doublequote', default=cls.Default.doublequote)
        escapechar = getitemdefault(data_meta, 'EscapeChar', default=cls.Default.escapechar)
        lineterminator = getitemdefault(data_meta, 'LineTerminator', default=cls.Default.lineterminator)
        quotechar = getitemdefault(data_meta, 'QuoteChar', default=cls.Default.quotechar)
        skipinitialspace = getitemdefault(data_meta, 'SkipInitialSpace', default=cls.Default.skipinitialspace)
        strict = getitemdefault(data_meta, 'Strict', default=cls.Default.strict)

        parsed_data = iter(csv.reader(
            file_like_data,
            delimiter=delimiter,
            doublequote=doublequote,
            escapechar=escapechar,
            lineterminator=lineterminator,
            quotechar=quotechar,
            skipinitialspace=skipinitialspace,
            strict=strict,
        ))

        headers = next(parsed_data)
        rows = [*parsed_data]
        return {'headers': headers, 'rows': rows}


@attrs
class ParsersRegistry(metaclass=Singleton):
    parser_by_content_type = attrib(default={
        'text/csv': CSVParser
    })


class RawEmbeddedExampleBuilder(Builder):
    def build(self, data: KeywordData):

        content = data.payload['Content']
        try:
            _, headers = get_item_with_key_by_group(content, ['Headers'])
        except KeyError:
            # TODO Maybe raise some Error here
            return None

        try:
            _, rows_data = get_item_with_key_by_group(content, ['Rows'])
        except KeyError:
            try:
                _, columns_data = get_item_with_key_by_group(content, ['Columns'])
            except KeyError:
                # TODO Maybe raise some Error here
                return None
            else:
                rows_data = zip_longest(columns_data)

        rows = zip(*zip_longest(headers, *rows_data, fillvalue=None))

        filled_headers = next(rows)
        columns = list(zip(*rows))

        return DataTableBuilder(context=self.context).build(
            KeywordData(Keyword.Examples.Table.TABLE,
                        {'Headers': filled_headers,
                         'Columns': columns})
        )


class DataTableBuilder(Builder):
    def build(self, data: KeywordData):
        columns = []
        for header, column in zip(*itemgetter('Headers', 'Columns')(data.payload)):
            columns.append(
                DataColumnBuilder(context=self.context).build(
                    KeywordData('Column', {
                        'Header': header,
                        'ColumnData': column
                    })
                )
            )
        return DataTable(columns=columns)


class DataColumnBuilder(Builder):
    def build(self, data: KeywordData) -> DataColumn:
        name = DataCellBuilder(context=self.context).build(KeywordData('Value', data.payload['Header']))
        data = [*map(
            lambda value: DataCellBuilder(context=self.context).build(KeywordData('Value', value)),
            data.payload['ColumnData']
        )]
        return DataColumn(name=name, data=data)


class DataCellBuilder(Builder):
    def build(self, data: KeywordData) -> DataCell:
        return DataCell(value=data.payload)


class EmbeddedExampleBuilder(Builder):
    DEFAULT_CONTENT_TYPE = 'text/csv'

    def build(self, data: KeywordData):
        try:
            content_type = data.payload['ContentType']
        except KeyError:
            content_type = self.DEFAULT_CONTENT_TYPE

        try:
            content_meta = data.payload['ContentMeta']
        except KeyError:
            content_meta = {}

        _, parsable_data = get_item_with_key_by_group(data.payload, Keyword.Examples.Loader.Embeded.all)

        parsed_data = (
            ParsersRegistry()
                .parser_by_content_type[content_type]
                .parse(parsable_data, content_meta)
        )

        raw_example_builder_payload = {
            'Content': {
                'Name': getitemdefault(data.payload, 'Name', default=None),
                'Headers': parsed_data['headers'],
                'Rows': parsed_data['rows']
            }
        }

        return RawEmbeddedExampleBuilder(context=self.context).build(
            KeywordData('Table', raw_example_builder_payload)
        )


@attrs
class URIExampleBuilder(Builder):
    def build(self, data: KeywordData):
        raw_uri = data.payload['URI']
        if isinstance(raw_uri, str):
            uri = raw_uri
            request_params = {}
        else:
            uri = raw_uri['Path']
            raw_request_params = getitemdefault(raw_uri, 'RequestParams', default={})
            request_params = raw_request_params or {}

        uri_data = get(uri, request_params).text

        example_builder_payload = {
            'Name': getitemdefault(data.payload, 'Name', default=None),
            'Content': uri_data,
        }

        content_meta = getitemdefault(data.payload, 'ContentMeta', default=None)
        if content_meta:
            example_builder_payload.update(ContentMeta=content_meta)

        if 'ContentType' in data.payload.keys():
            example_builder_payload.update(ContentType=data.payload['ContentType'])

        return EmbeddedExampleBuilder(context=self.context).build(
            KeywordData('Table', example_builder_payload))


@attrs
class PathExampleBuilder(Builder):
    def build(self, data: KeywordData):
        raw_path = data.payload[Keyword.Examples.Loader.File.PATH]
        if isinstance(raw_path, str):
            path = Path(raw_path)
            path_resolver = Keyword.Examples.Loader.File.Resolver.DOCUMENT
        else:
            path = Path(raw_path[Keyword.Examples.Loader.File.PATH])
            raw_path_resolver = getitemdefault(
                raw_path,
                Keyword.Examples.Loader.File.Resolver.Type.TYPE,
                default=Keyword.Examples.Loader.File.Resolver.DOCUMENT
            )
            path_resolver = raw_path_resolver or Keyword.Examples.Loader.File.Resolver.DOCUMENT

        if path_resolver is Keyword.Examples.Loader.File.Resolver.CWD:
            root_path = Path.cwd()
        else:
            root_path = Path(
                getitemdefault(self.context, 'DocumentPath', default=Path.cwd())
            ).parent.resolve()

        example_path = root_path / path

        with example_path.open(mode='r', encoding='utf-8') as example_file:
            example_data = example_file.read().strip()

        example_builder_payload = {
            'Name': getitemdefault(data.payload, 'Name', default=None),
            'Content': example_data,
        }
        content_meta = getitemdefault(data.payload, 'ContentMeta', default=None)
        if content_meta:
            example_builder_payload.update(ContentMeta=content_meta)

        if 'ContentType' in data.payload.keys():
            example_builder_payload.update(ContentType=data.payload['ContentType'])

        return EmbeddedExampleBuilder(context=self.context).build(
            KeywordData('Table', example_builder_payload))


@attrs
class TagBuilder(Builder):
    def build(self, data):
        tag_names = data.payload
        return [Tag(name=name) for name in tag_names]
