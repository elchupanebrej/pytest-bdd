from operator import attrgetter
from pathlib import Path
from unittest.mock import patch

from yaml import FullLoader, load_all

from pytest_bdd.model.feature.builder import GherkinYamlModelBuilder, KeywordData


def test_empty_features_loading(resource_path: Path):
    feature_file_yaml_path = (resource_path / ".." / ".." / "two_empty_features.feature.yaml").resolve()
    feature_file_yaml = feature_file_yaml_path.read_text()
    feature_file_data = list(load_all(feature_file_yaml, Loader=FullLoader))
    with patch("pytest_bdd.model.feature.builder.FeatureBuilder.build") as feature_model_builder:
        gherkin_yaml_model = GherkinYamlModelBuilder(
            context={"DocumentPath": str(feature_file_yaml_path.resolve())}
        ).build(KeywordData("Document", feature_file_data))
        assert feature_model_builder.call_count == 2
        assert len(gherkin_yaml_model.features) == 2


def test_empty_values_features_loading(resource_path: Path):
    feature_file_yaml_path = (resource_path / ".." / ".." / "feature_with_empty_values.feature.yaml").resolve()
    feature_file_yaml = feature_file_yaml_path.read_text()
    feature_file_data = list(load_all(feature_file_yaml, Loader=FullLoader))
    gherkin_yaml_model = GherkinYamlModelBuilder(context={"DocumentPath": str(feature_file_yaml_path.resolve())}).build(
        KeywordData("Document", feature_file_data)
    )

    assert len(gherkin_yaml_model.features) == 1

    feature = gherkin_yaml_model.features[0]

    assert feature.name == "Empty Feature"
    assert feature.description is None
    assert feature.tags == []
    assert feature.backgrounds == []
    assert feature.scenarios == []


def test_without_values_features_loading(resource_path: Path):
    feature_file_yaml_path = (resource_path / ".." / ".." / "feature_without_values.feature.yaml").resolve()
    feature_file_yaml = feature_file_yaml_path.read_text()
    feature_file_data = list(load_all(feature_file_yaml, Loader=FullLoader))

    gherkin_yaml_model = GherkinYamlModelBuilder(context={"DocumentPath": str(feature_file_yaml_path.resolve())}).build(
        KeywordData("Document", feature_file_data)
    )

    assert len(gherkin_yaml_model.features) == 1

    feature = gherkin_yaml_model.features[0]

    assert feature.name == "Empty Feature"
    assert feature.description is None
    assert feature.tags == []
    assert feature.backgrounds == []
    assert feature.scenarios == []


def test_tagged_features_loading(resource_path: Path):
    feature_file_yaml_path = (resource_path / ".." / ".." / "feature_with_tags.feature.yaml").resolve()
    feature_file_yaml = feature_file_yaml_path.read_text()
    feature_file_data = list(load_all(feature_file_yaml, Loader=FullLoader))

    gherkin_yaml_model = GherkinYamlModelBuilder(context={"DocumentPath": str(feature_file_yaml_path.resolve())}).build(
        KeywordData("Document", feature_file_data)
    )

    assert len(gherkin_yaml_model.features) == 1

    feature = gherkin_yaml_model.features[0]
    feature_tag_names = [*map(attrgetter("name"), feature.tags)]
    assert "Cool tag" in feature_tag_names
    assert "Another cool tag" in feature_tag_names
