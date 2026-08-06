import pytest
from pydantic import ValidationError

from opportunity_agent.models.profile import SearchProfile


def test_search_profile_defaults():
    """Verify that all fields default to empty lists
    when instantiated with no arguments."""
    profile = SearchProfile()

    assert profile.keywords == []
    assert profile.job_titles == []
    assert profile.countries == []
    assert profile.job_types == []


def test_search_profile_full_initialization():
    """Verify successful initialization with all fields provided."""
    profile = SearchProfile(
        keywords=["python", "fastapi", "pydantic"],
        job_titles=["Backend Engineer", "Software Engineer"],
        countries=["United States", "Canada"],
        job_types=["full-time", "remote"],
    )

    assert profile.keywords == ["python", "fastapi", "pydantic"]
    assert profile.job_titles == ["Backend Engineer", "Software Engineer"]
    assert profile.countries == ["United States", "Canada"]
    assert profile.job_types == ["full-time", "remote"]


def test_search_profile_partial_initialization():
    """Verify initialization when only a subset of fields is provided."""
    profile = SearchProfile(
        keywords=["machine learning"],
        job_types=["contract"],
    )

    assert profile.keywords == ["machine learning"]
    assert profile.job_types == ["contract"]
    assert profile.job_titles == []
    assert profile.countries == []


def test_search_profile_list_independence():
    """Ensure default_factory prevents list mutation leakage between instances."""
    profile1 = SearchProfile()
    profile2 = SearchProfile()

    profile1.keywords.append("python")
    profile1.countries.append("Germany")

    assert profile1.keywords == ["python"]
    assert profile1.countries == ["Germany"]
    assert profile2.keywords == []
    assert profile2.countries == []


@pytest.mark.parametrize(
    "invalid_data",
    [
        {"keywords": 123},  # Integer instead of list
        {"job_titles": {"title": "Dev"}},  # Dict instead of list of strings
        {"countries": [123, None]},  # List containing non-string/uncoercible items
    ],
)
def test_search_profile_invalid_types(invalid_data):
    """Verify that invalid field types raise a ValidationError."""
    with pytest.raises(ValidationError):
        SearchProfile(**invalid_data)


def test_search_profile_serialization():
    """Verify model_dump and model_dump_json serialization."""
    profile = SearchProfile(
        keywords=["AI"],
        job_titles=["Data Scientist"],
    )

    dumped_dict = profile.model_dump()
    assert dumped_dict == {
        "keywords": ["AI"],
        "job_titles": ["Data Scientist"],
        "countries": [],
        "job_types": [],
    }

    json_data = profile.model_dump_json()
    assert '"keywords":["AI"]' in json_data


def test_search_profile_deserialization():
    """Verify model_validate and model_validate_json deserialization."""
    raw_dict = {
        "keywords": ["pytest"],
        "job_titles": ["QA Engineer"],
        "countries": ["UK"],
        "job_types": ["part-time"],
    }
    profile_from_dict = SearchProfile.model_validate(raw_dict)
    assert profile_from_dict.keywords == ["pytest"]
    assert profile_from_dict.countries == ["UK"]

    raw_json = '{"keywords": ["devops"], "job_titles": ["SRE"]}'
    profile_from_json = SearchProfile.model_validate_json(raw_json)
    assert profile_from_json.keywords == ["devops"]
    assert profile_from_json.job_titles == ["SRE"]
    assert profile_from_json.countries == []


def test_search_profile_search_queries_field():
    """Verify that the search_queries field is correctly initialized and serialized."""
    profile = SearchProfile(
        search_queries=[
            "Quantum Computing Research Engineer",
            "PyTorch Machine Learning PhD",
        ]
    )

    assert profile.search_queries == [
        "Quantum Computing Research Engineer",
        "PyTorch Machine Learning PhD",
    ]

    dumped_dict = profile.model_dump()
    assert dumped_dict["search_queries"] == [
        "Quantum Computing Research Engineer",
        "PyTorch Machine Learning PhD",
    ]

    json_data = profile.model_dump_json()
    assert (
        '"search_queries":["Quantum Computing Research Engineer",'
        '"PyTorch Machine Learning PhD"]' in json_data
    )
