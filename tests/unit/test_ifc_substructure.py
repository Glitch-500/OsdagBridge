import pytest
from tests.verify_ifc_substructure import verify_ifc_export


def test_ifc_substructure_export():
    assert verify_ifc_export("test_pytest_substructure.ifc") is True
