import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).parent.parent.resolve()))

from app import app



@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client
