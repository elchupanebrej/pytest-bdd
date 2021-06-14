from pathlib import Path

from yaml import FullLoader, load_all

from pytest_bdd.model.executable import ParametrizedScenario
from pytest_bdd.model.executable.builder import ParametrizedScenariosBuilder
from pytest_bdd.model.feature.builder import GherkinYamlModelBuilder, KeywordData
from pytest import raises


def load_gherkin_model_by_feature_path(path: Path):
    feature_file_yaml_data = path.resolve().read_text()
    feature_file_data = list(load_all(feature_file_yaml_data, Loader=FullLoader))

    gherkin_yaml_model = GherkinYamlModelBuilder(
        context={'DocumentPath': str(path.resolve())}
    ).build(KeywordData('Document', feature_file_data))

    return gherkin_yaml_model


def test_building_from_simple_feature_with_single_scenario(resource_path):
    feature_file_yaml_path = (resource_path / '..' / '..' / 'feature_with_simplest_scenario.feature.yaml')
    gherkin_yaml_model = load_gherkin_model_by_feature_path(feature_file_yaml_path)

    scenario = gherkin_yaml_model.features[0].scenarios[0]
    parametrized_scenarios = list(ParametrizedScenariosBuilder()._build_from_scenario(scenario))

    assert len(parametrized_scenarios) == 1
    assert parametrized_scenarios[0].flow_defined_parameter_names == set()
    assert parametrized_scenarios[0].table_defined_parameter_names == set()
    assert parametrized_scenarios[0].flow_open_parameter_names == set()
    assert parametrized_scenarios[0].table_defined_parameter_names == set()
    # TODO Add more validations


def test_building_from_simple_feature_with_single_parametrized_scenario(resource_path):
    feature_file_yaml_path = (
        resource_path / '..' / '..' / 'feature_with_simplest_scenario_with_single_parameter.feature.yaml'
    )
    gherkin_yaml_model = load_gherkin_model_by_feature_path(feature_file_yaml_path)
    scenario = gherkin_yaml_model.features[0].scenarios[0]
    parametrized_scenarios = list(ParametrizedScenariosBuilder()._build_from_scenario(scenario))

    assert len(gherkin_yaml_model.features) == 1
    assert parametrized_scenarios[0].flow_defined_parameter_names == {'parameter'}
    assert parametrized_scenarios[0].table_defined_parameter_names == {'parameter'}
    assert parametrized_scenarios[0].flow_open_parameter_names == set()
    assert parametrized_scenarios[0].table_open_parameter_names == set()
    try:
        parametrized_scenarios[0].validate_there_are_no_open_parameters()
    except ParametrizedScenario.ValidationError as validation_exc:
        raise AssertionError from validation_exc
    # TODO Add more validations


def test_building_from_simple_feature_with_single_parametrized_scenario_with_unclosed_flow_parameter(resource_path):
    feature_file_yaml_path = (
        resource_path / '..' / '..' / 'feature_with_simplest_scenario_with_single_unclosed_flow_parameter.feature.yaml'
    )
    gherkin_yaml_model = load_gherkin_model_by_feature_path(feature_file_yaml_path)

    scenario = gherkin_yaml_model.features[0].scenarios[0]
    parametrized_scenarios = list(ParametrizedScenariosBuilder()._build_from_scenario(scenario))

    assert len(parametrized_scenarios) == 1
    assert parametrized_scenarios[0].flow_defined_parameter_names == {'parameter'}
    assert parametrized_scenarios[0].table_defined_parameter_names == set()
    assert parametrized_scenarios[0].flow_open_parameter_names == {'parameter'}
    assert parametrized_scenarios[0].table_open_parameter_names == set()
    with raises(ParametrizedScenario.ValidationError):
        parametrized_scenarios[0].validate_there_are_no_open_parameters()
    # TODO Add more validations


def test_building_from_simple_feature_with_single_parametrized_scenario_with_unclosed_table_parameter(resource_path):
    feature_file_yaml_path = (
        resource_path / '..' / '..' / 'feature_with_simplest_scenario_with_single_unclosed_table_parameter.feature.yaml'
    )
    gherkin_yaml_model = load_gherkin_model_by_feature_path(feature_file_yaml_path)
    scenario = gherkin_yaml_model.features[0].scenarios[0]
    parametrized_scenarios = list(ParametrizedScenariosBuilder()._build_from_scenario(scenario))

    assert len(parametrized_scenarios) == 1
    assert parametrized_scenarios[0].flow_defined_parameter_names == set()
    assert parametrized_scenarios[0].table_defined_parameter_names == {'parameter'}
    assert parametrized_scenarios[0].flow_open_parameter_names == set()
    assert parametrized_scenarios[0].table_open_parameter_names == {'parameter'}
    with raises(ParametrizedScenario.ValidationError):
        parametrized_scenarios[0].validate_there_are_no_open_parameters()
    # TODO Add more validations


def test_building_from_simple_feature_with_background_scenario_and_no_usual_scenarios(resource_path):
    feature_file_yaml_path = (
        resource_path / '..' / '..' / 'feature_with_simplest_background_and_no_scenario.feature.yaml'
    )
    gherkin_yaml_model = load_gherkin_model_by_feature_path(feature_file_yaml_path)

    parametrized_scenarios = list(ParametrizedScenariosBuilder().build(gherkin_yaml_model.features[0]))

    assert len(parametrized_scenarios) == 0
    # TODO Add more validations


def test_building_from_simple_feature_with_scenario_containing_multiple_example_tables(resource_path):
    feature_file_yaml_path = (
        resource_path / '..' / '..' / 'feature_with_scenario_with_multiple_example_tables.feature.yaml'
    )
    gherkin_yaml_model = load_gherkin_model_by_feature_path(feature_file_yaml_path)

    scenario = gherkin_yaml_model.features[0].scenarios[0]
    parametrized_scenarios = list(ParametrizedScenariosBuilder()._build_from_scenario(scenario))

    assert len(parametrized_scenarios) == 2

    assert parametrized_scenarios[0].flow_defined_parameter_names == {'parameter'}
    assert parametrized_scenarios[0].table_defined_parameter_names == {'parameter'}
    assert parametrized_scenarios[0].flow_open_parameter_names == set()
    assert parametrized_scenarios[0].table_open_parameter_names == set()
    try:
        parametrized_scenarios[0].validate_there_are_no_open_parameters()
    except ParametrizedScenario.ValidationError as validation_exc:
        raise AssertionError from validation_exc
    # TODO Add more validations


def test_building_from_simple_feature_with_backgrounded_scenario(resource_path):
    feature_file_yaml_path = (
        resource_path / '..' / '..' / 'feature_with_simplest_backgrounded_scenario.feature.yaml'
    )
    gherkin_yaml_model = load_gherkin_model_by_feature_path(feature_file_yaml_path)

    parametrized_scenarios = list(ParametrizedScenariosBuilder().build(gherkin_yaml_model.features[0]))

    assert len(parametrized_scenarios) == 1
    # TODO Add more validations


def test_building_from_feature_with_backgrounded_scenario_with_examples_on_every_level(resource_path):
    feature_file_yaml_path = (resource_path / '..' / '..' /
                              'feature_with_backgrounded_scenario_with_example_tables_on_every_level.feature.yaml')
    gherkin_yaml_model = load_gherkin_model_by_feature_path(feature_file_yaml_path)

    parametrized_scenarios = list(ParametrizedScenariosBuilder().build(gherkin_yaml_model.features[0]))

    assert len(parametrized_scenarios) == 1
    columns = list(parametrized_scenarios[0].combined_parameters_table.columns)
    assert len(columns) == 6
    assert len(columns[0].data) == 8
    # TODO Add more validations


def test_building_from_feature_with_backgrounded_scenario_with_examples_on_every_level_including_rules(resource_path):
    feature_file_yaml_path = (
        resource_path / '..' / '..' /
        'feature_with_backgrounded_scenario_with_example_tables_on_every_level_including_rules.feature.yaml'
    )
    gherkin_yaml_model = load_gherkin_model_by_feature_path(feature_file_yaml_path)

    parametrized_scenarios = list(ParametrizedScenariosBuilder().build(gherkin_yaml_model.features[0]))

    assert len(parametrized_scenarios) == 1
    parametrized_scenario = parametrized_scenarios[0]
    columns = list(parametrized_scenario.combined_parameters_table.columns)
    assert len(columns) == 14
    assert len(columns[0].data) == 128

    parameter_table_tags = parametrized_scenario.combined_parameters_table.tags
    assert len(parameter_table_tags) == 14

    scenario_flow_tags = parametrized_scenario.scenario_flow.tags
    assert len(scenario_flow_tags) == 7

    try:
        parametrized_scenarios[0].validate_there_are_no_open_parameters()
    except ParametrizedScenario.ValidationError as validation_exc:
        raise AssertionError from validation_exc

    # TODO Add more validations
