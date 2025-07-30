from copy import deepcopy
from datetime import date

from pydantic import ValidationError
from pytest import raises

from usdol_wage_determination_model import WageDetermination


test_fields = {
    'decision_number': 'CA00000001',
    'modification_number': 0,
    'publication_date': '2025-01-01',
    'effective': {
        'start_date': '2025-01-01',
        'end_date': '2025-01-31',
    },
    'active': True,
    'location': {
        'city': 'San Diego',
        'county': 'San Diego',
        'state': 'CA',
    },
    'construction_types': ['building'],
    'rate_identifier': 'SUCA2025-100',
    'job': {
        'title': 'Journeyman',
        'category': 'Plumber',
        'classification': 'Plumber',
    },
    'wage': {
        'currency': 'USD',
        'rate': '123.45',
        'fringe': '12.34'
    },
}

bad_decision_numbers = (
    '0CA000001',
    '0CA0000001',
    '0CA00000001',
    'CA0000001',
    'CA000000001',
    'C00000001',
    'C000000001',
    'C0000000001',
    'CAA000001',
    'CAA0000001',
    'CAA00000001',
    0,
    10000000,
    None,
)

bad_modification_numbers = (-1, 1.1, None)


def check_error(error, expected_message):
    validation_errors = error.value.errors()
    assert len(validation_errors) == 1
    assert validation_errors[0]['msg'] == expected_message


def test_basic():
    wage_determination = WageDetermination(**test_fields)
    assert wage_determination.decision_number == test_fields['decision_number']
    assert wage_determination.modification_number == test_fields['modification_number']
    assert wage_determination.publication_date == date(year=2025, month=1, day=1)
    assert wage_determination.effective.start_date == date(year=2025, month=1, day=1)
    assert wage_determination.effective.end_date == date(year=2025, month=1, day=31)
    assert wage_determination.active


def test_bad_decision_numbers():
    for bad_decision_number in bad_decision_numbers:
        fields = deepcopy(test_fields)
        fields['decision_number'] = bad_decision_number
        with raises(ValidationError) as error:
            WageDetermination(**fields)
        if isinstance(bad_decision_number, str):
            check_error(error, 'String should match pattern \'^[A-Z]{2}[0-9]{8}$\'')
        else:
            check_error(error, 'Input should be a valid string')


def test_bad_modification_numbers():
    for bad_modification_number in bad_modification_numbers:
        fields = deepcopy(test_fields)
        fields['modification_number'] = bad_modification_number
        with raises(ValidationError) as error:
            WageDetermination(**fields)
        if isinstance(bad_modification_number, int):
            check_error(error, 'Input should be greater than or equal to 0')
        elif isinstance(bad_modification_number, float):
            check_error(error, 'Input should be a valid integer, got a number with a fractional part')
        else:
            check_error(error, 'Input should be a valid integer')
