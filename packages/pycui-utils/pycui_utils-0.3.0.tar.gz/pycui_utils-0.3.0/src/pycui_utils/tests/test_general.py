import os

import pytest

from pycui_utils import (
    DATABASE_DIR,
    BasicCategories,
    Categories,
    Category,
    Organizations,
    SpecialCategories,
    resource_filename,
)


@pytest.fixture
def categories():
    """Fixture providing the actual Categories instance."""

    database_path = os.path.join(DATABASE_DIR, "cui.json")
    return Categories(database_path)


@pytest.fixture
def basic_categories(categories):
    """Fixture providing the basic Categories instance."""
    return BasicCategories(categories)


@pytest.fixture
def special_categories(categories):
    """Fixture providing the special Categories instance."""
    return SpecialCategories(categories)


@pytest.fixture
def organizations(categories):
    """Fixture providing the organizations instance."""
    return Organizations(categories)


def test_resource_filename():
    """Test the resource_filename function."""

    result = resource_filename("test_package", "test_resource")
    assert "test_package" in result
    assert result.endswith("test_package/test_resource")

    assert DATABASE_DIR.endswith("pycui_utils/databases")
    assert os.path.isdir(os.path.dirname(DATABASE_DIR))


def test_raises_error_when_path_not_found():
    with pytest.raises(RuntimeError):
        Categories("invalid/path/to/database.json")


def test_category_initialization():
    """Test Category class initialization and properties."""

    data = {
        "name": "Test Category",
        "description": "Test description",
        "is_specified": True,
        "index_group": "TEST_ORG",
        "marking_format": "TEST-MF",
    }

    category = Category("TEST-CODE", data)

    assert category.code == "TEST-CODE"
    assert category.name == "Test Category"
    assert category.description == "Test description"
    assert category.is_specified is True
    assert category.organization_code == "TEST_ORG"
    assert category.marking_format == "TEST-MF"


def test_string_representation_format():
    category = Category(
        "TEST",
        {
            "name": "Test Category",
            "index_group": "ORG",
            "description": "",
            "is_specified": False,
            "marking_format": "",
        },
    )
    assert repr(category) == "<Category: TEST - Test Category>"


def test_get_category_by_marking(categories):
    """Test getting a specific category by marking."""

    category = categories.get_by_marking("SP-SSI")
    assert category is not None
    assert category.code == "SP-SSI"
    assert category.name == "Sensitive Security Information"
    assert category.is_specified is True
    assert category.organization_code == "TRANSPORTATION"


def test_get_category_by_marking_lowercase(categories):
    """Test getting a specific category by name with case insensitivity"""

    category = categories.get_by_marking("cvi")
    assert category is not None
    assert category.code == "CVI"
    assert category.name == "Chemical-terrorism Vulnerability Information"
    assert category.is_specified is False
    assert category.organization_code == "CRITICAL_INFRASTRUCTURE"


def test_get_category_by_marking_with_invalid_marking_returns_none(categories):

    category = categories.get_by_marking("XXX")
    assert category is None


def test_get_categories_by_organization(categories):

    organizations = categories.by_organization("DEFENSE")
    assert organizations is not None
    assert len(organizations) == 7


def test_get_all_categories(categories):

    all_categories = categories.all()
    assert all_categories is not None
    assert len(all_categories) == 152


def test_get_all_basic_categories(basic_categories):

    all_basic_categories = basic_categories.all()
    assert all_basic_categories is not None
    assert len(all_basic_categories) == 94


def test_get_all_special_categories(special_categories):

    all_special_categories = special_categories.all()
    assert all_special_categories is not None
    assert len(all_special_categories) == 58


def test_get_all_special_categories_organizations(special_categories):
    special_categories_orgs = special_categories.by_organization("TRANSPORTATION")
    assert special_categories_orgs is not None

    assert len(special_categories_orgs) == 1


def test_get_category_filter_by_marking(basic_categories):
    category = basic_categories.get_by_marking("DCRIT")

    assert category is not None
    assert category.code == "DCRIT"
    assert category.name == "DoD Critical Infrastructure Security Information"
    assert category.is_specified is False
    assert category.organization_code == "DEFENSE"


def test_get_all_organizations(organizations):

    all_organizations = organizations.all()
    assert all_organizations is not None

    assert len(all_organizations) == 20


def test_get_organizations_categories(organizations):
    organizations_categories = organizations.categories("DEFENSE")
    assert organizations_categories is not None

    assert len(organizations_categories) == 7
