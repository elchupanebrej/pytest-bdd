from functools import reduce
from itertools import product, chain
from operator import attrgetter
from typing import Iterable

from pytest_bdd.model.common import DataColumn, DataCell
from pytest_bdd.model.executable import (
    CombinedParametersTable,
    FeatureExecutablePlan,
    ParametrizedScenario,
    ScenarioFlow,
)
from pytest_bdd.model.feature import GherkinYamlModel, Feature, CompositeScenario, Scenario


class ExecutablePlanBuilder:
    def build(self, source: GherkinYamlModel):
        feature_executable_plans = []
        for feature in source.features:
            feature_executable_plans.append(
                FeatureExecutablePlanBuilder().build(feature)
            )


class FeatureExecutablePlanBuilder:
    def build(self, source: Feature):
        return FeatureExecutablePlan(executable_scenarios=ParametrizedScenariosBuilder().build(source))


class ParametrizedScenariosBuilder:
    def build(self, source: [CompositeScenario, Scenario]) -> Iterable[ParametrizedScenario]:
        if isinstance(source, CompositeScenario):
            yield from self._build_from_composite_scenario(source)
        if isinstance(source, Scenario):
            yield from self._build_from_scenario(source)

    def _build_from_composite_scenario(self, source: CompositeScenario) -> Iterable[ParametrizedScenario]:
        for background_scenario in chain(*map(self.build, source.backgrounds)):
            for scenario in chain(*map(self.build, source.scenarios)):
                yield from self._combine_background_with_scenario_and_feature_node(
                    background_scenario,
                    scenario,
                    source,
                )

    def _combine_background_with_scenario_and_feature_node(self, background_scenario, scenario, feature_node):
        for example_table in feature_node.examples or [None]:
            try:
                yield ParametrizedScenario(
                    scenario_flow=ScenarioFlow(
                        steps=[*background_scenario.scenario_flow.steps, *scenario.scenario_flow.steps],
                        tags=[*background_scenario.scenario_flow.tags, *scenario.scenario_flow.tags, *feature_node.tags]
                    ),
                    combined_parameters_table=reduce(self._combine_parameters_tables, [
                        background_scenario.combined_parameters_table,
                        scenario.combined_parameters_table,
                        CombinedParametersTable(
                            tags=[*getattr(example_table, 'tags', []), *feature_node.tags],
                            columns=example_table.datatable.columns
                        ),
                    ]))
            except self.OverlappingTableParameterError as e:
                # TODO log
                continue

    def _combine_background_with_scenario_and_node_parameter_table(
        self,
        background_scenario,
        scenario,
        node_parameter_table,
    ) -> ParametrizedScenario:
        return ParametrizedScenario(
            scenario_flow=ScenarioFlow(
                steps=[*background_scenario.scenario_flow.steps, *scenario.scenario_flow.steps],
                tags=[*background_scenario.scenario_flow.tags, *scenario.scenario_flow.tags]
            ),
            combined_parameters_table=reduce(self._combine_parameters_tables, [
                background_scenario.combined_parameters_table,
                scenario.combined_parameters_table,
                node_parameter_table
            ]))

    class OverlappingTableParameterError(RuntimeError):
        pass

    def _combine_parameters_tables(
        self,
        first_table: CombinedParametersTable,
        second_table: CombinedParametersTable
    ) -> CombinedParametersTable:
        if first_table is None:
            return second_table
        if second_table is None:
            return first_table

        first_table_rows = zip(*map(attrgetter('data'), first_table.columns))
        first_table_headers = set(map(attrgetter('header.value'), first_table.columns))
        second_table_rows = zip(*map(attrgetter('data'), second_table.columns))
        second_table_headers = set(map(attrgetter('header.value'), second_table.columns))
        common_headers = first_table_headers & second_table_headers
        if common_headers:
            raise self.OverlappingTableParameterError(
                f'Both tables contain {common_headers} headers; Unable to process'
            )
        combined_table_rows = map(lambda v: chain(*v), product(first_table_rows, second_table_rows))
        combined_table_data_columns = zip(*combined_table_rows)
        data_columns = []

        for column_header, column_data in zip(chain(map(attrgetter('header.value'), first_table.columns),
                                                    map(attrgetter('header.value'), second_table.columns)),
                                              combined_table_data_columns):
            data_columns.append(DataColumn(header=DataCell(value=column_header),
                                           data=[*map(lambda value: DataCell(value=value), column_data)]))
        return CombinedParametersTable(
            columns=data_columns,
            tags=[*first_table.tags, *second_table.tags]
        )

    def _build_from_scenario(self, source: Scenario) -> Iterable[ParametrizedScenario]:
        scenario_flow = ScenarioFlow(steps=source.steps, tags=source.tags)

        if source.examples:
            for example_table in source.examples:
                combined_parameters_table = CombinedParametersTable(
                    tags=[*example_table.tags, *source.tags],
                    columns=example_table.datatable.columns
                )
                yield ParametrizedScenario(scenario_flow=scenario_flow,
                                           combined_parameters_table=combined_parameters_table)
        else:
            yield ParametrizedScenario(scenario_flow=scenario_flow)
