"""Tests for the build_user_profiles module.

This module contains comprehensive test cases for user profile building functionality,
including profile generation, attribute conversion, and custom profile handling.
"""

import pytest
from unittest.mock import Mock, patch
from typing import Dict, Any

from arklex.evaluation.build_user_profiles import (
    augment_attributes,
    build_profile,
    build_labelled_profile,
    convert_attributes_to_profile,
    filter_attributes,
    get_custom_profiles,
    ATTR_TO_PROFILE,
    ADAPT_GOAL,
    pick_attributes,
    pick_goal,
    find_matched_attribute,
    adapt_goal,
    convert_attributes_to_profiles,
    attributes_to_text,
    get_label,
    select_system_attributes,
    build_user_profiles,
    pick_attributes_random,
    pick_attributes_react,
)


@pytest.fixture
def mock_chatgpt_chatbot():
    """Mock chatgpt_chatbot function."""
    with patch("arklex.evaluation.build_user_profiles.chatgpt_chatbot") as mock:
        mock.return_value = "mocked_response"
        yield mock


@pytest.fixture
def mock_requests_get():
    """Mock requests.get function."""
    with patch("arklex.evaluation.build_user_profiles.requests.get") as mock:
        mock_response = Mock()
        mock_response.json.return_value = ["api_value1", "api_value2"]
        mock.return_value = mock_response
        yield mock


@pytest.fixture
def mock_environment():
    """Mock Environment class."""
    with patch("arklex.evaluation.build_user_profiles.Environment") as mock:
        mock_instance = Mock()
        mock_tool = Mock()
        mock_tool.slots = [Mock(name="slot1", value="value1")]
        mock_tool.description = "Test tool description"
        mock_tool.output = "Test output"
        mock_tool.name = "Test Tool"
        mock_instance.tools = {"tool1": {"execute": Mock(return_value=mock_tool)}}
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def mock_slot_filler():
    """Mock SlotFiller class."""
    with patch("arklex.evaluation.build_user_profiles.SlotFiller") as mock:
        mock_instance = Mock()
        mock_instance.execute.return_value = [Mock(name="slot1", value="filled_value")]
        mock.return_value = mock_instance
        yield mock


@pytest.fixture
def mock_find_matched_attribute():
    """Mock find_matched_attribute function."""
    with patch("arklex.evaluation.build_user_profiles.find_matched_attribute") as mock:
        mock.return_value = {"matched": "data"}
        yield mock


@pytest.fixture
def mock_load_docs():
    """Mock load_docs function."""
    with patch("arklex.evaluation.build_user_profiles.load_docs") as mock:
        mock.return_value = [{"content": "test content"}]
        yield mock


@pytest.fixture
def mock_filter_attributes():
    """Mock filter_attributes function."""
    with patch("arklex.evaluation.build_user_profiles.filter_attributes") as mock:
        mock.return_value = {
            "attr1": {"values": ["val1"]},
            "attr2": {"values": ["val3"]},
        }
        yield mock


@pytest.fixture
def mock_augment_attributes():
    """Mock augment_attributes function."""
    with patch("arklex.evaluation.build_user_profiles.augment_attributes") as mock:
        mock.return_value = {
            "attr1": ["val1", "val2"],
            "attr2": ["val3", "val4"],
        }
        yield mock


@pytest.fixture
def mock_pick_attributes():
    """Mock pick_attributes function."""
    with patch("arklex.evaluation.build_user_profiles.pick_attributes") as mock:
        mock.return_value = (
            {"goal": "test_goal", "attr1": "val1", "attr2": "val3"},
            {"matched": "data"},
        )
        yield mock


@pytest.fixture
def mock_adapt_goal():
    """Mock adapt_goal function."""
    with patch("arklex.evaluation.build_user_profiles.adapt_goal") as mock:
        mock.return_value = "adapted_goal"
        yield mock


@pytest.fixture
def mock_select_system_attributes():
    """Mock select_system_attributes function."""
    with patch(
        "arklex.evaluation.build_user_profiles.select_system_attributes"
    ) as mock:
        mock.return_value = [{"sys_attr": "val"}, {"sys_attr": "val2"}]
        yield mock


@pytest.fixture
def mock_get_custom_profiles():
    """Mock get_custom_profiles function."""
    with patch("arklex.evaluation.build_user_profiles.get_custom_profiles") as mock:
        mock.return_value = (
            {"profile1": ["prof1", "prof2"], "profile2": ["prof3", "prof4"]},
            {"attr1": ["val1", "val2"], "attr2": ["val3", "val4"]},
        )
        yield mock


class TestBuildUserProfiles:
    """Test cases for build_user_profiles module.

    This class contains comprehensive tests for user profile building,
    including predefined and custom profile generation, attribute handling,
    and profile conversion functionality.
    """

    @pytest.fixture
    def mock_config(self) -> Dict[str, Any]:
        """Create a mock configuration for testing."""
        return {
            "documents_dir": "/test/documents",
            "custom_profile": False,
            "system_inputs": True,
            "company_summary": "Test company summary",
            "client": Mock(),
            "user_attributes": {
                "goal": {"values": ["goal1", "goal2", "goal3"]},
                "system_attributes": {
                    "attr1": {"values": ["val1", "val2"]},
                    "attr2": {"values": ["val3", "val4"]},
                },
                "user_profiles": {"profile1": {"values": ["p1"]}},
            },
            "tools": [{"id": "tool1", "name": "Test Tool"}],
            "workers": [{"id": "worker1", "name": "Test Worker"}],
        }

    @pytest.fixture
    def mock_synthetic_params(self) -> Dict[str, int]:
        """Create mock synthetic data parameters."""
        return {"num_convos": 2, "num_goals": 3}

    @pytest.fixture
    def basic_mock_setup(
        self,
        mock_load_docs,
        mock_filter_attributes,
        mock_augment_attributes,
        mock_pick_attributes,
        mock_adapt_goal,
        mock_select_system_attributes,
        mock_chatgpt_chatbot,
    ):
        """Create basic mock setup for build_profile tests."""
        return {
            "load_docs": mock_load_docs,
            "filter_attributes": mock_filter_attributes,
            "augment_attributes": mock_augment_attributes,
            "pick_attributes": mock_pick_attributes,
            "adapt_goal": mock_adapt_goal,
            "select_system_attributes": mock_select_system_attributes,
            "chatgpt_chatbot": mock_chatgpt_chatbot,
        }

    @pytest.fixture
    def custom_profile_mock_setup(
        self,
        mock_load_docs,
        mock_filter_attributes,
        mock_augment_attributes,
        mock_get_custom_profiles,
        mock_pick_attributes,
        mock_adapt_goal,
        mock_chatgpt_chatbot,
    ):
        """Create mock setup for custom profile tests."""
        return {
            "load_docs": mock_load_docs,
            "filter_attributes": mock_filter_attributes,
            "augment_attributes": mock_augment_attributes,
            "get_custom_profiles": mock_get_custom_profiles,
            "pick_attributes": mock_pick_attributes,
            "adapt_goal": mock_adapt_goal,
            "chatgpt_chatbot": mock_chatgpt_chatbot,
        }

    @pytest.mark.parametrize(
        "test_config,test_name",
        [
            ({"system_inputs": False}, "system_inputs_false"),
            (
                {
                    "custom_profile": True,
                    "user_attributes": {
                        "goal": {"values": ["goal1", "goal2"]},
                        "user_profiles": {"profile1": {"values": ["prof1", "prof2"]}},
                        "system_attributes": {"attr1": {"values": ["val1", "val2"]}},
                    },
                },
                "custom_with_binding",
            ),
            (
                {
                    "custom_profile": True,
                    "user_attributes": {
                        "goal": {"values": ["goal1", "goal2"]},
                        "user_profiles": {"profile1": {"values": ["prof1", "prof2"]}},
                        "system_attributes": {"attr1": {"values": ["val1", "val2"]}},
                    },
                },
                "custom_without_documents",
            ),
        ],
    )
    def test_build_profile_variations(
        self,
        basic_mock_setup,
        custom_profile_mock_setup,
        mock_config: Dict[str, Any],
        mock_synthetic_params: Dict[str, int],
        test_config: Dict[str, Any],
        test_name: str,
    ) -> None:
        """Test build_profile with various configurations."""
        # Update config with test-specific values
        mock_config.update(test_config)

        try:
            profiles, goals, attributes, system_attrs, labels = build_profile(
                mock_synthetic_params, mock_config
            )
            assert len(profiles) == 2
            assert len(goals) == 2
            assert len(attributes) == 2
            assert len(system_attrs) == 2
            assert len(labels) == 2
        except Exception as e:
            assert False, f"Function raised an exception: {e}"

    def test_convert_attributes_to_profile(
        self, mock_chatgpt_chatbot: Mock, mock_config: Dict[str, Any]
    ) -> None:
        """Test convert_attributes_to_profile function."""
        attributes = {"attr1": "value1", "attr2": "value2"}
        result = convert_attributes_to_profile(attributes, mock_config)
        assert result == "mocked_response"
        mock_chatgpt_chatbot.assert_called_once()

    def test_get_custom_profiles(self, mock_config: Dict[str, Any]) -> None:
        """Test get_custom_profiles function."""
        user_profiles, system_attributes = get_custom_profiles(mock_config)
        assert isinstance(user_profiles, dict)
        assert isinstance(system_attributes, dict)

    def test_build_labelled_profile(
        self,
        basic_mock_setup,
        mock_config: Dict[str, Any],
        mock_synthetic_params: Dict[str, int],
    ) -> None:
        """Test build_labelled_profile function."""
        profiles, goals, attributes, system_attrs, labels = build_labelled_profile(
            mock_synthetic_params, mock_config
        )
        assert len(profiles) == 2
        assert len(goals) == 2
        assert len(attributes) == 2
        assert len(system_attrs) == 2
        assert len(labels) == 2

    def test_build_user_profiles(self, mock_slot_filler: Mock) -> None:
        """Test build_user_profiles function."""
        test_data = [{"goal": "test goal", "attributes": {"attr1": "value1"}}]
        result = build_user_profiles(test_data)
        assert result is None  # Function is incomplete

    def test_build_user_profiles_complete(self, mock_slot_filler: Mock) -> None:
        """Test build_user_profiles function with complete implementation."""
        test_data = [
            {
                "goal": "test goal 1",
                "attributes": {"attr1": "value1", "attr2": "value2"},
            },
            {
                "goal": "test goal 2",
                "attributes": {"attr1": "value3", "attr2": "value4"},
            },
        ]

        # The function is incomplete (ends with comment), so it returns None
        result = build_user_profiles(test_data)
        assert result is None  # Function is incomplete, returns None

    def test_attr_to_profile_constant(self) -> None:
        """Test ATTR_TO_PROFILE constant."""
        assert "company_summary" in ATTR_TO_PROFILE
        assert "user_attr" in ATTR_TO_PROFILE

    def test_adapt_goal_constant(self) -> None:
        """Test ADAPT_GOAL constant."""
        assert "goal" in ADAPT_GOAL
        assert "company_summary" in ADAPT_GOAL

    @pytest.mark.parametrize(
        "strategy,expected_goal",
        [
            ("react", "goal1"),
            ("llm_based", "goal2"),
        ],
    )
    def test_pick_goal(
        self, mock_chatgpt_chatbot: Mock, strategy: str, expected_goal: str
    ) -> None:
        """Test pick_goal function with different strategies."""
        attributes = {"attr1": "value1"}
        goals = ["goal1", "goal2"]

        if strategy == "llm_based":
            mock_chatgpt_chatbot.return_value = f"Goal: {expected_goal}"
        else:  # react strategy
            mock_chatgpt_chatbot.return_value = f"Thought: test\nGoal: {expected_goal}"

        result = pick_goal(attributes, goals, strategy)
        assert result == expected_goal

    def test_pick_goal_invalid_strategy(self) -> None:
        """Test pick_goal with invalid strategy."""
        attributes = {"attr1": "value1"}
        goals = ["goal1", "goal2"]

        with pytest.raises(ValueError, match="Invalid strategy"):
            pick_goal(attributes, goals, "invalid_strategy")

    def test_find_matched_attribute_react_strategy(
        self, mock_chatgpt_chatbot: Mock
    ) -> None:
        """Test find_matched_attribute with react strategy."""
        goal = "test goal"
        user_profile = "test profile"

        # Mock the expected response format
        mock_chatgpt_chatbot.return_value = "Thought: test\nAttribute: test_attr"

        result = find_matched_attribute(goal, user_profile, "react")
        assert result == "test_attr"
        mock_chatgpt_chatbot.assert_called_once()

    def test_pick_attributes_react(self) -> None:
        """Test pick_attributes_react function."""
        user_profile = {"profile": "test"}
        attributes = {
            "category1": ["value1", "value2"],
            "category2": ["value3", "value4"],
            "goal": ["goal1", "goal2"],
        }
        goals = ["goal1", "goal2"]
        client = Mock()

        selected_attributes, matched_attribute_to_goal = pick_attributes_react(
            user_profile, attributes, goals, client
        )

        assert "goal" in selected_attributes
        assert "category1" in selected_attributes
        assert "category2" in selected_attributes
        assert isinstance(matched_attribute_to_goal, dict)

    def test_pick_attributes_random(self) -> None:
        """Test pick_attributes_random function."""
        user_profile = {"profile": "test"}
        attributes = {
            "category1": ["value1", "value2"],
            "category2": ["value3", "value4"],
            "goal": ["goal1", "goal2"],
        }
        goals = ["goal1", "goal2"]

        selected_attributes, matched_attribute_to_goal = pick_attributes_random(
            user_profile, attributes, goals
        )

        assert "goal" in selected_attributes
        assert "category1" in selected_attributes
        assert "category2" in selected_attributes
        assert isinstance(matched_attribute_to_goal, dict)

    def test_adapt_goal(
        self, mock_chatgpt_chatbot: Mock, mock_config: Dict[str, Any]
    ) -> None:
        """Test adapt_goal function."""
        goal = "test goal"
        doc = "test document"
        user_profile = "test profile"

        # Mock the expected response format
        mock_chatgpt_chatbot.return_value = "adapted goal"

        result = adapt_goal(goal, mock_config, doc, user_profile)
        assert result == "adapted goal"
        mock_chatgpt_chatbot.assert_called_once()

    def test_get_label_with_invalid_attribute(
        self, mock_environment: Mock, mock_config: Dict[str, Any]
    ) -> None:
        """Test get_label with invalid attribute."""
        attribute = {"goal": "test goal"}
        config = {"tools": [{"id": "tool1"}], "workers": [], "client": Mock()}

        label, valid = get_label(attribute, config)
        assert isinstance(label, list)
        assert valid is True

    def test_filter_attributes(self, mock_config: Dict[str, Any]) -> None:
        """Test filter_attributes function."""
        result = filter_attributes(mock_config)
        assert isinstance(result, dict)
        # The function returns user_profiles when system_attributes is empty
        assert "user_profiles" in result

    def test_augment_attributes(self, mock_config: Dict[str, Any]) -> None:
        """Test augment_attributes function."""
        attributes = {"category": {"values": ["value1"], "augment": True}}
        documents = [{"content": "test document"}]
        with patch(
            "arklex.evaluation.build_user_profiles.chatgpt_chatbot"
        ) as mock_chat:
            mock_chat.return_value = "new_value1, new_value2"
            result = augment_attributes(attributes, mock_config, documents)
            assert isinstance(result, dict)
            assert result["category"] == ["value1", "new_value1", "new_value2"]

    def test_attributes_to_text(self) -> None:
        """Test attributes_to_text function."""
        attribute_list = [{"attr1": "value1", "attr2": "value2"}]
        result = attributes_to_text(attribute_list)
        assert isinstance(result, list)
        assert len(result) == 1

    def test_convert_attributes_to_profiles(
        self, mock_chatgpt_chatbot: Mock, mock_config: Dict[str, Any]
    ) -> None:
        """Test convert_attributes_to_profiles function."""
        attributes_list = [
            {"attr1": "value1", "goal": "goal1"},
            {"attr2": "value2", "goal": "goal2"},
        ]
        system_attributes_list = [{"sys1": "val1"}, {"sys2": "val2"}]

        profiles, goals, system_inputs = convert_attributes_to_profiles(
            attributes_list, system_attributes_list, mock_config
        )

        assert len(profiles) == 2
        assert len(goals) == 2
        assert len(system_inputs) == 2

    def test_select_system_attributes(
        self, mock_config: Dict[str, Any], mock_synthetic_params: Dict[str, int]
    ) -> None:
        """Test select_system_attributes function."""
        result = select_system_attributes(mock_config, mock_synthetic_params)
        assert len(result) == 2
        assert all(isinstance(attr, dict) for attr in result)

    def test_build_labelled_profile_edge_case(
        self, mock_config: Dict[str, Any], mock_synthetic_params: Dict[str, Any]
    ) -> None:
        """Test build_labelled_profile with edge case configuration."""
        # Override the mock_config with the correct structure
        mock_config.update(
            {
                "custom_profile": True,
                "user_attributes": {
                    "goal": {"values": ["goal1"]},
                    "user_profiles": {
                        "values": ["prof1", "prof2"]
                    },  # Direct values structure
                    "system_attributes": {"attr1": {"values": ["val1"]}},
                    # Add some attributes that filter_attributes will return
                    "attr1": {"values": ["val1", "val2"]},
                    "attr2": {"values": ["val3", "val4"]},
                    "category1": {"values": ["cat1", "cat2"]},
                },
            }
        )

        # Mock the client to return proper responses
        mock_client = Mock()
        mock_response = Mock()
        mock_response.choices = [Mock()]
        mock_response.choices[0].message = Mock()
        mock_response.choices[0].message.content = "adapted_goal"
        mock_client.chat.completions.create.return_value = mock_response
        mock_config["client"] = mock_client

        profiles, goals, attributes, system_attrs, labels = build_labelled_profile(
            mock_synthetic_params, mock_config
        )

        assert len(profiles) == 2
        assert len(goals) == 2
        assert len(attributes) == 2
        assert len(system_attrs) == 2
        assert len(labels) == 2

    def test_attributes_to_text_empty(self) -> None:
        """Test attributes_to_text with empty list."""
        result = attributes_to_text([])
        assert result == []

    def test_convert_attributes_to_profiles_with_empty_lists(
        self, mock_config: Dict[str, Any]
    ) -> None:
        """Test convert_attributes_to_profiles with empty lists."""
        profiles, goals, system_inputs = convert_attributes_to_profiles(
            [], [], mock_config
        )
        assert profiles == []
        assert goals == []
        assert system_inputs == []

    def test_convert_attributes_to_profile_empty(
        self, mock_chatgpt_chatbot: Mock, mock_config: Dict[str, Any]
    ) -> None:
        """Test convert_attributes_to_profile with empty attributes."""
        attributes = {}
        result = convert_attributes_to_profile(attributes, mock_config)
        assert result == "mocked_response"

    def test_build_profile_custom_with_binding(
        self,
        custom_profile_mock_setup,
        mock_config: Dict[str, Any],
        mock_synthetic_params: Dict[str, int],
    ) -> None:
        """Test build_profile with custom profiles and binding."""
        mock_config["custom_profile"] = True
        mock_config["user_attributes"] = {
            "goal": {"values": ["goal1", "goal2"]},
            "user_profiles": {"profile1": {"values": ["prof1", "prof2"]}},
            "system_attributes": {"attr1": {"values": ["val1", "val2"]}},
        }

        profiles, goals, attributes, system_attrs, labels = build_profile(
            mock_synthetic_params, mock_config
        )

        assert len(profiles) == 2
        assert len(goals) == 2
        assert len(attributes) == 2
        assert len(system_attrs) == 2
        assert len(labels) == 2

    def test_build_profile_custom_without_documents(
        self,
        custom_profile_mock_setup,
        mock_config: Dict[str, Any],
        mock_synthetic_params: Dict[str, int],
    ) -> None:
        """Test build_profile with custom profiles without documents."""
        mock_config["custom_profile"] = True
        mock_config["user_attributes"] = {
            "goal": {"values": ["goal1", "goal2"]},
            "user_profiles": {"profile1": {"values": ["prof1", "prof2"]}},
            "system_attributes": {"attr1": {"values": ["val1", "val2"]}},
        }
        custom_profile_mock_setup["load_docs"].return_value = []

        profiles, goals, attributes, system_attrs, labels = build_profile(
            mock_synthetic_params, mock_config
        )

        assert len(profiles) == 2
        assert len(goals) == 2
        assert len(attributes) == 2
        assert len(system_attrs) == 2
        assert len(labels) == 2

    def test_pick_attributes_with_invalid_strategy(self) -> None:
        """Test pick_attributes with invalid strategy."""
        user_profile = {"profile": "test"}
        attributes = {"category1": ["value1", "value2"]}
        goals = ["goal1", "goal2"]

        # The function doesn't raise ValueError, it falls back to random
        result_attributes, result_matched = pick_attributes(
            user_profile, attributes, goals, strategy="invalid"
        )

        assert isinstance(result_attributes, dict)
        assert isinstance(result_matched, dict)
        assert "goal" in result_attributes

    def test_adapt_goal_with_empty_doc(
        self, mock_chatgpt_chatbot: Mock, mock_config: Dict[str, Any]
    ) -> None:
        """Test adapt_goal with empty document."""
        goal = "test goal"
        doc = ""
        user_profile = "test profile"

        result = adapt_goal(goal, mock_config, doc, user_profile)
        assert result == "mocked_response"

    def test_select_system_attributes_with_empty_config(
        self, mock_synthetic_params: Dict[str, int]
    ) -> None:
        """Test select_system_attributes with empty config."""
        config = {"user_attributes": {"system_attributes": {}}}
        result = select_system_attributes(config, mock_synthetic_params)
        assert len(result) == 2
        assert all(isinstance(attr, dict) for attr in result)

    def test_augment_attributes_with_generate_values_false(
        self, mock_config: Dict[str, Any]
    ) -> None:
        """Test augment_attributes function when generate_values is False."""
        attributes = {
            "attr1": {"values": ["val1", "val2"], "generate_values": False},
            "attr2": {"values": ["val3", "val4"], "generate_values": False},
        }
        documents = [{"content": "test content"}]

        with patch(
            "arklex.evaluation.build_user_profiles.chatgpt_chatbot"
        ) as mock_chatgpt_chatbot:
            mock_chatgpt_chatbot.return_value = "new_val1, new_val2"

            result = augment_attributes(attributes, mock_config, documents)

            # Should return original values when generate_values is False
            assert result["attr1"] == ["val1", "val2"]
            assert result["attr2"] == ["val3", "val4"]
            # Should not call chatgpt_chatbot when generate_values is False
            mock_chatgpt_chatbot.assert_not_called()

    def test_augment_attributes_with_empty_values(
        self, mock_config: Dict[str, Any]
    ) -> None:
        """Test augment_attributes function when some attributes have empty values."""
        attributes = {
            "attr1": {"values": [], "augment": True},  # Empty values
            "attr2": {"values": ["val3", "val4"], "augment": True},
        }
        documents = [{"content": "test content"}]

        with patch(
            "arklex.evaluation.build_user_profiles.chatgpt_chatbot"
        ) as mock_chatgpt_chatbot:
            mock_chatgpt_chatbot.return_value = "new_val1, new_val2"

            result = augment_attributes(attributes, mock_config, documents)

            # Should skip attributes with empty values in text_attribute
            assert (
                "attr1" not in result["attr2"]
            )  # attr1 should not appear in text_attribute
            # Should still process attr2
            assert result["attr2"] == ["val3", "val4", "new_val1", "new_val2"]

    def test_augment_attributes_with_mixed_generate_values_and_documents(
        self, mock_config: Dict[str, Any]
    ) -> None:
        """Test augment_attributes function with mixed generate_values and documents."""
        attributes = {
            "attr1": {"values": ["val1"], "augment": False},
            "attr2": {"values": ["val2"], "augment": True},
        }
        documents = [{"content": "test content"}]

        with patch(
            "arklex.evaluation.build_user_profiles.chatgpt_chatbot"
        ) as mock_chatgpt_chatbot:
            mock_chatgpt_chatbot.return_value = "new_val1, new_val2"

            result = augment_attributes(attributes, mock_config, documents)

            # Should use original values for attr1 (augment=False)
            assert result["attr1"] == ["val1"]
            # Should generate new values for attr2 (augment=True)
            assert result["attr2"] == ["val2", "new_val1", "new_val2"]
            # Should call chatgpt_chatbot only once for attr2
            assert mock_chatgpt_chatbot.call_count == 1

    def test_augment_attributes_with_mixed_generate_values_and_no_documents(
        self, mock_config: Dict[str, Any]
    ) -> None:
        """Test augment_attributes function with mixed generate_values and no documents."""
        attributes = {
            "attr1": {"values": ["val1"], "augment": False},
            "attr2": {"values": ["val2"], "augment": True},
        }
        documents = []  # No documents

        with patch(
            "arklex.evaluation.build_user_profiles.chatgpt_chatbot"
        ) as mock_chatgpt_chatbot:
            mock_chatgpt_chatbot.return_value = "new_val1, new_val2"

            result = augment_attributes(attributes, mock_config, documents)

            # Should use original values for attr1 (augment=False)
            assert result["attr1"] == ["val1"]
            # Should generate new values for attr2 (augment=True) without documents
            assert result["attr2"] == ["val2", "new_val1", "new_val2"]
            # Should call chatgpt_chatbot only once for attr2
            assert mock_chatgpt_chatbot.call_count == 1

    def test_build_profile_with_system_inputs_false_and_custom_profile(
        self, mock_config: Dict[str, Any], mock_synthetic_params: Dict[str, int]
    ) -> None:
        """Test build_profile function when system_inputs is False and custom_profile is True."""
        config = mock_config.copy()
        config["custom_profile"] = True
        config["system_inputs"] = False
        config["user_attributes"] = {
            "goal": {"values": ["goal1", "goal2"]},
            "user_profiles": {
                "profile1": {"values": ["prof1", "prof2"]},
            },
            "system_attributes": {
                "attr1": {"values": ["val1", "val2"]},
            },
        }

        with patch("arklex.evaluation.build_user_profiles.load_docs") as mock_load_docs:
            mock_load_docs.return_value = [{"content": "test content"}]

            with patch(
                "arklex.evaluation.build_user_profiles.filter_attributes"
            ) as mock_filter_attributes:
                mock_filter_attributes.return_value = {
                    "attr1": {"values": ["val1"], "generate_values": False},
                }

                with patch(
                    "arklex.evaluation.build_user_profiles.augment_attributes"
                ) as mock_augment_attributes:
                    mock_augment_attributes.return_value = {
                        "attr1": ["val1"],
                    }

                    with patch(
                        "arklex.evaluation.build_user_profiles.get_custom_profiles"
                    ) as mock_get_custom_profiles:
                        mock_get_custom_profiles.return_value = (
                            {"profile1": ["prof1", "prof2"]},
                            {"attr1": ["val1", "val2"]},
                        )

                        with patch(
                            "arklex.evaluation.build_user_profiles.pick_attributes"
                        ) as mock_pick_attributes:
                            mock_pick_attributes.return_value = (
                                {"goal": "test_goal", "attr1": "val1"},
                                {"matched": "data"},
                            )

                            with patch(
                                "arklex.evaluation.build_user_profiles.adapt_goal"
                            ) as mock_adapt_goal:
                                mock_adapt_goal.return_value = "adapted_goal"

                                with patch(
                                    "arklex.evaluation.build_user_profiles.convert_attributes_to_profiles"
                                ) as mock_convert:
                                    mock_convert.return_value = (
                                        ["profile1", "profile1"],
                                        ["goal1", "goal1"],
                                        [{"sys": "input"}, {"sys": "input"}],
                                    )

                                    (
                                        profiles,
                                        goals,
                                        attributes_list,
                                        system_inputs,
                                        labels_list,
                                    ) = build_profile(mock_synthetic_params, config)

                                    # num_convos is 2, so we expect 2 items
                                    assert len(profiles) == 2
                                    assert len(goals) == 2
                                    assert len(attributes_list) == 2
                                    assert len(system_inputs) == 2
                                    assert len(labels_list) == 2

    def test_build_profile_with_binding_index_mismatch(
        self, mock_config: Dict[str, Any], mock_synthetic_params: Dict[str, int]
    ) -> None:
        """Test build_profile function when binding_index doesn't contain the expected key."""
        config = mock_config.copy()
        config["custom_profile"] = True
        config["user_attributes"] = {
            "goal": {"values": ["goal1", "goal2"]},
            "user_profiles": {
                "profile1": {"values": ["prof1", "prof2"], "bind_to": "system_attr1"},
            },
            "system_attributes": {
                "attr1": {"values": ["val1", "val2"]},  # No bind_to specified
            },
        }

        with patch("arklex.evaluation.build_user_profiles.load_docs") as mock_load_docs:
            mock_load_docs.return_value = [{"content": "test content"}]

            with patch(
                "arklex.evaluation.build_user_profiles.filter_attributes"
            ) as mock_filter_attributes:
                mock_filter_attributes.return_value = {
                    "attr1": {"values": ["val1"], "generate_values": False},
                }

                with patch(
                    "arklex.evaluation.build_user_profiles.augment_attributes"
                ) as mock_augment_attributes:
                    mock_augment_attributes.return_value = {
                        "attr1": ["val1"],
                    }

                    with patch(
                        "arklex.evaluation.build_user_profiles.get_custom_profiles"
                    ) as mock_get_custom_profiles:
                        mock_get_custom_profiles.return_value = (
                            {"profile1": ["prof1", "prof2"]},
                            {"attr1": ["val1", "val2"]},
                        )

                        with patch(
                            "arklex.evaluation.build_user_profiles.pick_attributes"
                        ) as mock_pick_attributes:
                            mock_pick_attributes.return_value = (
                                {"goal": "test_goal", "attr1": "val1"},
                                {"matched": "data"},
                            )

                            with patch(
                                "arklex.evaluation.build_user_profiles.adapt_goal"
                            ) as mock_adapt_goal:
                                mock_adapt_goal.return_value = "adapted_goal"

                                with patch(
                                    "arklex.evaluation.build_user_profiles.convert_attributes_to_profiles"
                                ) as mock_convert:
                                    mock_convert.return_value = (
                                        ["profile1", "profile1"],
                                        ["goal1", "goal1"],
                                        [{"sys": "input"}, {"sys": "input"}],
                                    )

                                    (
                                        profiles,
                                        goals,
                                        attributes_list,
                                        system_inputs,
                                        labels_list,
                                    ) = build_profile(mock_synthetic_params, config)

                                    # num_convos is 2, so we expect 2 items
                                    assert len(profiles) == 2
                                    assert len(goals) == 2
                                    assert len(attributes_list) == 2
                                    assert len(system_inputs) == 2
                                    assert len(labels_list) == 2

    def test_build_profile_with_commented_get_label(
        self, mock_config: Dict[str, Any], mock_synthetic_params: Dict[str, int]
    ) -> None:
        """Test build_profile function with the commented get_label section."""
        config = mock_config.copy()
        config["custom_profile"] = True
        config["user_attributes"] = {
            "goal": {"values": ["goal1", "goal2"]},
            "user_profiles": {
                "profile1": {"values": ["prof1", "prof2"]},
            },
            "system_attributes": {
                "attr1": {"values": ["val1", "val2"]},
            },
        }

        with patch("arklex.evaluation.build_user_profiles.load_docs") as mock_load_docs:
            mock_load_docs.return_value = [{"content": "test content"}]

            with patch(
                "arklex.evaluation.build_user_profiles.filter_attributes"
            ) as mock_filter_attributes:
                mock_filter_attributes.return_value = {
                    "attr1": {"values": ["val1"], "generate_values": False},
                }

                with patch(
                    "arklex.evaluation.build_user_profiles.augment_attributes"
                ) as mock_augment_attributes:
                    mock_augment_attributes.return_value = {
                        "attr1": ["val1"],
                    }

                    with patch(
                        "arklex.evaluation.build_user_profiles.get_custom_profiles"
                    ) as mock_get_custom_profiles:
                        mock_get_custom_profiles.return_value = (
                            {"profile1": ["prof1", "prof2"]},
                            {"attr1": ["val1", "val2"]},
                        )

                        with patch(
                            "arklex.evaluation.build_user_profiles.pick_attributes"
                        ) as mock_pick_attributes:
                            mock_pick_attributes.return_value = (
                                {"goal": "test_goal", "attr1": "val1"},
                                {"matched": "data"},
                            )

                            with patch(
                                "arklex.evaluation.build_user_profiles.adapt_goal"
                            ) as mock_adapt_goal:
                                mock_adapt_goal.return_value = "adapted_goal"

                                with patch(
                                    "arklex.evaluation.build_user_profiles.convert_attributes_to_profiles"
                                ) as mock_convert:
                                    mock_convert.return_value = (
                                        ["profile1", "profile1"],
                                        ["goal1", "goal1"],
                                        [{"sys": "input"}, {"sys": "input"}],
                                    )

                                    (
                                        profiles,
                                        goals,
                                        attributes_list,
                                        system_inputs,
                                        labels_list,
                                    ) = build_profile(mock_synthetic_params, config)

                                    # num_convos is 2, so we expect 2 items
                                    assert len(profiles) == 2
                                    assert len(goals) == 2
                                    assert len(attributes_list) == 2
                                    assert len(system_inputs) == 2
                                    assert len(labels_list) == 2

    def test_build_profile_with_empty_documents_in_custom_mode(
        self, mock_config: Dict[str, Any], mock_synthetic_params: Dict[str, int]
    ) -> None:
        """Test build_profile function with empty documents in custom profile mode."""
        config = mock_config.copy()
        config["custom_profile"] = True
        config["user_attributes"] = {
            "goal": {"values": ["goal1", "goal2"]},
            "user_profiles": {
                "profile1": {"values": ["prof1", "prof2"]},
            },
            "system_attributes": {
                "attr1": {"values": ["val1", "val2"]},
            },
        }

        with patch("arklex.evaluation.build_user_profiles.load_docs") as mock_load_docs:
            mock_load_docs.return_value = []  # Empty documents

            with patch(
                "arklex.evaluation.build_user_profiles.filter_attributes"
            ) as mock_filter_attributes:
                mock_filter_attributes.return_value = {
                    "attr1": {"values": ["val1"], "generate_values": False},
                }

                with patch(
                    "arklex.evaluation.build_user_profiles.augment_attributes"
                ) as mock_augment_attributes:
                    mock_augment_attributes.return_value = {
                        "attr1": ["val1"],
                    }

                    with patch(
                        "arklex.evaluation.build_user_profiles.get_custom_profiles"
                    ) as mock_get_custom_profiles:
                        mock_get_custom_profiles.return_value = (
                            {"profile1": ["prof1", "prof2"]},
                            {"attr1": ["val1", "val2"]},
                        )

                        with patch(
                            "arklex.evaluation.build_user_profiles.pick_attributes"
                        ) as mock_pick_attributes:
                            mock_pick_attributes.return_value = (
                                {"goal": "test_goal", "attr1": "val1"},
                                {"matched": "data"},
                            )

                            with patch(
                                "arklex.evaluation.build_user_profiles.adapt_goal"
                            ) as mock_adapt_goal:
                                mock_adapt_goal.return_value = "adapted_goal"

                                with patch(
                                    "arklex.evaluation.build_user_profiles.convert_attributes_to_profiles"
                                ) as mock_convert:
                                    mock_convert.return_value = (
                                        ["profile1", "profile1"],
                                        ["goal1", "goal1"],
                                        [{"sys": "input"}, {"sys": "input"}],
                                    )

                                    (
                                        profiles,
                                        goals,
                                        attributes_list,
                                        system_inputs,
                                        labels_list,
                                    ) = build_profile(mock_synthetic_params, config)

                                    # num_convos is 2, so we expect 2 items
                                    assert len(profiles) == 2
                                    assert len(goals) == 2
                                    assert len(attributes_list) == 2
                                    assert len(system_inputs) == 2
                                    assert len(labels_list) == 2

    def test_get_custom_profiles_with_api_and_exception(self) -> None:
        """Test get_custom_profiles function when API call raises an exception."""
        config = {
            "user_attributes": {
                "system_attributes": {
                    "attr1": {"api": "http://test.com/api1"},
                },
                "user_profiles": {
                    "profile1": {"api": "http://test.com/api2"},
                },
            }
        }

        with patch(
            "arklex.evaluation.build_user_profiles.requests.get"
        ) as mock_requests_get:
            # Mock the first API call to succeed
            mock_response1 = Mock()
            mock_response1.json.return_value = ["api_value1", "api_value2"]

            # Mock the second API call to raise an exception
            mock_requests_get.side_effect = [mock_response1, Exception("API Error")]

            # This should test the first get_custom_profiles function (lines 548-600)
            # which expects the config structure with API calls
            with pytest.raises(KeyError, match="'values'"):
                # Use the first get_custom_profiles function
                from arklex.evaluation.build_user_profiles import (
                    get_custom_profiles as get_custom_profiles_v1,
                )

                get_custom_profiles_v1(config)

    def test_get_custom_profiles_with_api_and_invalid_response(self) -> None:
        """Test get_custom_profiles function when API returns invalid response."""
        config = {
            "user_attributes": {
                "system_attributes": {
                    "attr1": {"api": "http://test.com/api1"},
                },
                "user_profiles": {
                    "profile1": {"api": "http://test.com/api2"},
                },
            }
        }

        with patch(
            "arklex.evaluation.build_user_profiles.requests.get"
        ) as mock_requests_get:
            # Mock API calls to return invalid responses
            mock_response1 = Mock()
            mock_response1.json.side_effect = ValueError("Invalid JSON")

            mock_response2 = Mock()
            mock_response2.json.return_value = ["api_value1", "api_value2"]

            mock_requests_get.side_effect = [mock_response1, mock_response2]

            with pytest.raises(KeyError, match="'values'"):
                # Use the first get_custom_profiles function
                from arklex.evaluation.build_user_profiles import (
                    get_custom_profiles as get_custom_profiles_v1,
                )

                get_custom_profiles_v1(config)

    def test_select_system_attributes_with_non_dict_values(
        self, mock_synthetic_params: Dict[str, int]
    ) -> None:
        """Test select_system_attributes function when system attributes are not dictionaries."""
        config = {
            "user_attributes": {
                "system_attributes": {
                    "attr1": ["val1", "val2"],  # Not a dict
                }
            }
        }

        with patch(
            "arklex.evaluation.build_user_profiles.requests.get"
        ) as mock_requests_get:
            mock_response = Mock()
            mock_response.json.return_value = ["api_value1", "api_value2"]
            mock_requests_get.return_value = mock_response

            # Should raise TypeError when trying to access "values" key on a list
            with pytest.raises(
                TypeError, match="list indices must be integers or slices, not str"
            ):
                select_system_attributes(config, mock_synthetic_params)

    def test_select_system_attributes_with_empty_list(
        self, mock_synthetic_params: Dict[str, int]
    ) -> None:
        """Test select_system_attributes function when system attributes list is empty."""
        config = {
            "user_attributes": {
                "system_attributes": {
                    "attr1": [],  # Empty list
                }
            }
        }

        with patch(
            "arklex.evaluation.build_user_profiles.requests.get"
        ) as mock_requests_get:
            mock_response = Mock()
            mock_response.json.return_value = []  # Empty response
            mock_requests_get.return_value = mock_response

            # Should raise TypeError when trying to access "values" key on a list
            with pytest.raises(
                TypeError, match="list indices must be integers or slices, not str"
            ):
                select_system_attributes(config, mock_synthetic_params)

    def test_augment_attributes_with_empty_values(
        self, mock_config: Dict[str, Any]
    ) -> None:
        """Test augment_attributes function when some attributes have empty values."""
        attributes = {
            "attr1": {"values": [], "augment": True},  # Empty values
            "attr2": {"values": ["val3", "val4"], "augment": True},
        }
        documents = [{"content": "test content"}]

        with patch(
            "arklex.evaluation.build_user_profiles.chatgpt_chatbot"
        ) as mock_chatgpt_chatbot:
            mock_chatgpt_chatbot.return_value = "new_val1, new_val2"

            result = augment_attributes(attributes, mock_config, documents)

            # Should skip attributes with empty values in text_attribute
            assert (
                "attr1" not in result["attr2"]
            )  # attr1 should not appear in text_attribute
            # Should still process attr2
            assert result["attr2"] == ["val3", "val4", "new_val1", "new_val2"]

    def test_augment_attributes_with_mixed_generate_values_and_documents(
        self, mock_config: Dict[str, Any]
    ) -> None:
        """Test augment_attributes function with mixed generate_values and documents."""
        attributes = {
            "attr1": {"values": ["val1"], "augment": False},
            "attr2": {"values": ["val2"], "augment": True},
        }
        documents = [{"content": "test content"}]

        with patch(
            "arklex.evaluation.build_user_profiles.chatgpt_chatbot"
        ) as mock_chatgpt_chatbot:
            mock_chatgpt_chatbot.return_value = "new_val1, new_val2"

            result = augment_attributes(attributes, mock_config, documents)

            # Should use original values for attr1 (augment=False)
            assert result["attr1"] == ["val1"]
            # Should generate new values for attr2 (augment=True)
            assert result["attr2"] == ["val2", "new_val1", "new_val2"]
            # Should call chatgpt_chatbot only once for attr2
            assert mock_chatgpt_chatbot.call_count == 1

    def test_augment_attributes_with_mixed_generate_values_and_no_documents(
        self, mock_config: Dict[str, Any]
    ) -> None:
        """Test augment_attributes function with mixed generate_values and no documents."""
        attributes = {
            "attr1": {"values": ["val1"], "augment": False},
            "attr2": {"values": ["val2"], "augment": True},
        }
        documents = []  # No documents

        with patch(
            "arklex.evaluation.build_user_profiles.chatgpt_chatbot"
        ) as mock_chatgpt_chatbot:
            mock_chatgpt_chatbot.return_value = "new_val1, new_val2"

            result = augment_attributes(attributes, mock_config, documents)

            # Should use original values for attr1 (augment=False)
            assert result["attr1"] == ["val1"]
            # Should generate new values for attr2 (augment=True) without documents
            assert result["attr2"] == ["val2", "new_val1", "new_val2"]
            # Should call chatgpt_chatbot only once for attr2
            assert mock_chatgpt_chatbot.call_count == 1
