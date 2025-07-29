import json

from otlp_test_data import sample_proto, sample_json


def test_same_json():
    assert json.loads(sample_json()) == json.loads(sample_json())


def test_same_json_verbatim():
    assert sample_json() == sample_json()


def test_same_proto_verbatim():
    assert sample_proto() == sample_proto()
