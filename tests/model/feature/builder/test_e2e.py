from unittest.mock import patch, Mock

from yaml import FullLoader, load_all

from pytest_bdd.model.feature.builder import GherkinYamlModelBuilder, KeywordData


def test_e2e_parsing_feature_with_examples_1(resource_path):
    feature_file_yaml_path = (resource_path / '..' / '..' / '..' / 'feature_with_examples.feature.yaml')
    feature_file_yaml_data = feature_file_yaml_path.read_text()
    feature_file_data = list(load_all(feature_file_yaml_data, Loader=FullLoader))

    feature_example_csv_path = (resource_path / '..' / '..' / '..' / 'simple_feature_example.csv')
    feature_example_csv_data = feature_example_csv_path.read_text()

    get_mock = Mock()
    get_mock.text = feature_example_csv_data.strip()
    with patch('pytest_bdd.model.builder.get', return_value=get_mock):
        gherkin_yaml_model = GherkinYamlModelBuilder(
            context={'DocumentPath': str(feature_file_yaml_path.resolve())}
        ).build(KeywordData('Document', feature_file_data))

        assert len(gherkin_yaml_model.features) == 11


def test_e2e_parsing_feature_with_rules(resource_path):
    feature_file_yaml_path = (resource_path / '..' / '..' / 'feature_with_rules.feature.yaml')
    feature_file_yaml_data = feature_file_yaml_path.resolve().read_text()
    feature_file_data = list(load_all(feature_file_yaml_data, Loader=FullLoader))

    gherkin_yaml_model = GherkinYamlModelBuilder(
        context={'DocumentPath': str(feature_file_yaml_path.resolve())}
    ).build(KeywordData('Document', feature_file_data))

    assert len(gherkin_yaml_model.features) == 1
