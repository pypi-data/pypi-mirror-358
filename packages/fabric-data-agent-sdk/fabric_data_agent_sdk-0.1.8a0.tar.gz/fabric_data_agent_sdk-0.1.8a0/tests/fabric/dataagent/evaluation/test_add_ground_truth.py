"""
Unit-tests for evaluator_api.update_ground_truth

They avoid heavy dependencies (deltalake, sempy_labs, Spark, HTTP) by
registering minimal stub modules in ``sys.modules`` **before** the code
under test is imported.
"""

from __future__ import annotations

import sys
import types
import pandas as pd
import pytest
import string
import importlib

def _ensure(name: str) -> types.ModuleType:
    """
    Return the real module if importable, otherwise create a dummy one.
    """
    if name in sys.modules:
        return sys.modules[name]
    try:
        return importlib.import_module(name)          # real package present
    except ModuleNotFoundError:
        mod = types.ModuleType(name)
        sys.modules[name] = mod
        return mod

# ── only the packages required by kustodb.py ──────────────────────────────
for path in (
    "azure.kusto",
    "azure.kusto.data",
    "azure.kusto.data.helpers",
    "azure.kusto.data.exceptions",
    "synapse.ml.fabric.token_utils",
    "synapse.ml.fabric.service_discovery",
):
    parts = path.split(".")
    for i in range(1, len(parts) + 1):
        _ensure(".".join(parts[:i]))

# minimal attributes for kustodb
az_data = _ensure("azure.kusto.data")
exc_mod = sys.modules["azure.kusto.data.exceptions"]
exc_mod.KustoServiceError = type("KustoServiceError", (), {})
exc_mod.KustoClientError  = type("KustoClientError",  (), {})
az_data.ClientRequestProperties = type(
    "ClientRequestProperties", (), {"set_option": lambda *_, **__: None}
)
az_data.KustoConnectionStringBuilder = type(
    "KustoConnectionStringBuilder",
    (),
    {"with_token_provider": staticmethod(lambda *_, **__: None)},
)
az_data.KustoClient = type(
    "KustoClient",
    (),
    {"execute": lambda *_, **__: types.SimpleNamespace(primary_results=[pd.DataFrame()])},
)
sys.modules["azure.kusto.data.helpers"].dataframe_from_result_table = (
    lambda *_: pd.DataFrame()
)

_ensure("synapse.ml.fabric.token_utils").TokenUtils = type(
    "TokenUtils",
    (),
    {
        "get_access_token": lambda *_, **__: "token",
        "get_aad_token": lambda *_, **__: "aad-token",
    },
)

_ensure("synapse.ml.fabric.service_discovery").get_fabric_env_config = (
    lambda *_a, **_kw: {}
)       


# 1.  Stub external libraries so evaluator_api imports cleanly
def _register_stub(name: str) -> types.ModuleType:
    mod = types.ModuleType(name)
    sys.modules[name] = mod
    return mod


# create parent & sub-modules (deltalake, deltalake.writer, sempy_labs)
for missing in ("deltalake", "deltalake.writer", "sempy_labs"):
    parts = missing.split(".")
    for i in range(1, len(parts) + 1):
        _register_stub(".".join(parts[:i]))

# give the required attribute so `from deltalake.writer import write_deltalake` works
sys.modules["deltalake.writer"].write_deltalake = lambda *_, **__: None

# 2.  Import module under test
from fabric.dataagent.evaluation import evaluator_api


# 3.  Helpers
def _dummy_sql(df: pd.DataFrame):
    """Mimic labs.ConnectX context manager with a .query() method returning *df*."""

    class _Ctx:
        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            pass

        def query(self, _):
            return df

    return _Ctx()


# Patch the evaluator_api module to use our dummy SQL connection
def _patch(monkeypatch, df: pd.DataFrame):
    # force a lakehouse source and dummy connection
    monkeypatch.setattr(
        evaluator_api,
        "_get_source",
        lambda *_: types.SimpleNamespace(connect=lambda: _dummy_sql(df)),
    )


# 4.  Tests
def test_single_scalar_named_placeholder(monkeypatch):
    """Single column, named placeholder is rendered correctly."""
    _patch(monkeypatch, pd.DataFrame({"total": [42]}))

    out = evaluator_api.add_ground_truth(
        question="Total sales?",
        answer_template="Total sales: {total}",
        datasource_id_or_name="Any",
        query="dummy",
        data_agent=None,
    )
    assert out["expected_answer"].iloc[0] == "Total sales: 42"


def test_single_row_multi_column(monkeypatch):
    """Several columns with matching named placeholders."""
    _patch(monkeypatch, pd.DataFrame({"country": ["US"], "sales": [123]}))

    out = evaluator_api.add_ground_truth(
        "By country",
        "{country} sold {sales}",
        "Any",
        "dummy",
        data_agent=None,
    )
    assert out["expected_answer"].iloc[0] == "US sold 123"


def test_error_positional_placeholder(monkeypatch):
    """Positional '{}' is now forbidden."""
    _patch(monkeypatch, pd.DataFrame({"x": [1]}))

    with pytest.raises(ValueError, match="Positional"):
        evaluator_api.add_ground_truth(
            "Bad",
            "Answer is {}",
            "Any",
            "dummy",
            data_agent=None,
        )


def test_error_multiple_rows(monkeypatch):
    """Multiple query rows should raise."""
    _patch(monkeypatch, pd.DataFrame({"id": [1, 2]}))

    with pytest.raises(ValueError, match="multiple rows"):
        evaluator_api.add_ground_truth(
            "Bad",
            "{id}",
            "Any",
            "dummy",
            data_agent=None,
        )

# 5.  _extract_placeholders() edge-cases coverage
@pytest.mark.parametrize(
    "template, expected",
    [
        ("Value is {amount:.2f}", {"amount"}),          # format-spec
        ("Balance {{USD}} {balance}", {"balance"}),     # escaped braces
        ("Repeated {a}-{a}-{b}", {"a", "b"}),           # duplicates collapse
        ("No placeholders here", set()),                # no placeholders
    ],
)
def test_extract_placeholders_edge_cases(template, expected):
    assert evaluator_api._extract_placeholders(template) == expected

def test_add_ground_truth_batch(monkeypatch):
    """add_ground_truth_batch returns one output row per input row."""
    df_single = pd.DataFrame({"val": [1]})            # 1-row result for every query
    _patch(monkeypatch, df_single)

    batch_in = pd.DataFrame(
        [
            dict(question="q1", answer_template="v={val}", query="dummy"),
            dict(question="q2", answer_template="v={val}", query="dummy"),
        ]
    )

    out = evaluator_api.add_ground_truth_batch(batch_in, "Any", data_agent=None)

    assert len(out) == 2
    assert list(out["question"]) == ["q1", "q2"]
    assert list(out["expected_answer"]) == ["v=1", "v=1"]
