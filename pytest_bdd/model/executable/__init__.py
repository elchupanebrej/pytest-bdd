from itertools import chain
from operator import attrgetter
from typing import List, Iterable, Optional

from attr import attrs, attrib, Factory

from pytest_bdd.model.common import DataColumn


@attrs
class Tagable:
    tags = attrib(default=Factory(list), kw_only=True)  # type: List[Tag]


@attrs
class ExecutablePlan:
    feature_executable_plans = attrib(default=Factory(list), kw_only=True)  # type: List[FeatureExecutablePlan]


@attrs
class FeatureExecutablePlan:
    executable_scenarios = attrib(default=Factory(list), kw_only=True)  # type: Iterable[ParametrizedScenario]


@attrs
class ParametrizedScenario:
    scenario_flow = attrib(default=None, kw_only=True)  # type: ScenarioFlow
    combined_parameters_table = attrib(default=None, kw_only=True)  # type: Optional[CombinedParametersTable]

    @property
    def flow_defined_parameter_names(self) -> set:
        return set(map(attrgetter("name"), self.scenario_flow.step_parameter_set))

    @property
    def table_defined_parameter_names(self) -> set:
        if self.combined_parameters_table:
            return self.combined_parameters_table.columns_header_names
        else:
            return set()

    @property
    def flow_open_parameter_names(self) -> set:
        return self.flow_defined_parameter_names - self.table_defined_parameter_names

    @property
    def table_open_parameter_names(self) -> set:
        return self.table_defined_parameter_names - self.flow_defined_parameter_names

    class ValidationError(RuntimeError):
        pass

    def validate_there_are_no_open_parameters(self):
        still_open_parameters = self.flow_open_parameter_names | self.table_open_parameter_names
        if still_open_parameters != set():
            raise self.ValidationError(f"There are still open parameters: {still_open_parameters}")


@attrs
class ScenarioFlow(Tagable):
    keyword = attrib(default=None, kw_only=True)  # type: str
    name = attrib(default=None, kw_only=True)  # type: str
    description = attrib(default=None, kw_only=True)  # type: str
    attachments = attrib(default=Factory(list), kw_only=True)
    steps = attrib(default=Factory(list), kw_only=True)  # type: List[Step]

    @property
    def step_parameter_set(self):
        return set(chain(*map(attrgetter("parameters"), self.steps)))


@attrs
class Step:
    keyword = attrib(default=None, kw_only=True)  # type: str
    name = attrib(default=None, kw_only=True)  # type: str
    pararmeters = attrib(default=Factory(list), kw_only=True)  # type: StepParameter


@attrs(frozen=True)
class StepParameter:
    name = attrib(default=None, kw_only=True)  # type: str


@attrs
class CombinedParametersTable:
    columns = attrib(default=Factory(list), kw_only=True)  # type: List[DataColumn]
    tags = attrib(default=Factory(list), kw_only=True)  # type:List[Tag]

    @property
    def columns_header_names(self):
        return set(map(attrgetter("header.value"), self.columns))


@attrs
class Tag:
    name = attrib(default=None, kw_only=True)  # type: str
