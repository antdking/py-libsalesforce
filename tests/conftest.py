import pytest
from faker import Factory


@pytest.fixture(scope="session")
def faker():
    return Factory.create("en_GB")
