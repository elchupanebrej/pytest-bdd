class Keyword:
    class Description:
        DESCRIPTION = "Description"
        all = [DESCRIPTION]

    class Backgrounds:
        BACKGROUNDS = "Backgrounds"
        all = [BACKGROUNDS]

    class Scenarios:
        SCENARIOS = "Scenarios"
        all = [SCENARIOS]

    class Feature:
        FEATURE = "Feature"
        all = [FEATURE]

    class Steps:
        STEPS = "Steps"
        all = [STEPS]

    class Step:
        STEP = "Step"
        all = [STEP]

        class Key:
            GIVEN = "Given"
            WHEN = "When"
            THEN = "Then"
            AND = "And"
            BUT = "But"
            STAR = "*"

            all = [GIVEN, WHEN, THEN, AND, BUT, STAR]
            defining_context = [GIVEN, WHEN, THEN]
            continuing_context = [AND, STAR]
            dropping_context = [BUT]

    class ExecutableNode:
        class Rule:
            RULE = "Rule"
            all = [RULE]

        class Scenario:
            SCENARIO = "Scenario"
            SCENARIO_OUTLINE = "Scenario Outline"
            EXAMPLE = "Example"

            all = [SCENARIO_OUTLINE, SCENARIO, EXAMPLE]

    class Examples:
        EXAMPLE_TABLES = "Examples"
        DATA_TABLES = "DataTables"
        all = [EXAMPLE_TABLES, DATA_TABLES]

        class Table:
            TABLE = "Table"
            all = [TABLE]

        class Loader:
            class Embeded:
                CONTENT = "Content"
                all = [CONTENT]

            class File:
                PATH = "Path"
                all = [PATH]

                class Resolver:
                    class Type:
                        TYPE = "Type"

                    DOCUMENT = "FeatureRelative"
                    CWD = "CWD"
                    all = [DOCUMENT, CWD]

            class URI:
                URI = "URI"
                URL = "URL"
                all = [URI, URL]

    class Tags:
        TAG = "Tags"

        all = [TAG]

    class FeatureNode:
        NAME = "Name"

        all = [NAME]
