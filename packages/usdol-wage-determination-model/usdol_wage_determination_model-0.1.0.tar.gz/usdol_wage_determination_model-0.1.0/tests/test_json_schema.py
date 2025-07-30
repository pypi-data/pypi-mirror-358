import json

from usdol_wage_determination_model import WageDetermination


expected_json_schema = '''{
    "$defs": {
        "ConstructionType": {
            "enum": [
                "building",
                "highway",
                "heavy",
                "residential"
            ],
            "title": "ConstructionType",
            "type": "string"
        },
        "DateRange": {
            "properties": {
                "start_date": {
                    "format": "date",
                    "title": "Start Date",
                    "type": "string"
                },
                "end_date": {
                    "default": "9999-12-31",
                    "format": "date",
                    "title": "End Date",
                    "type": "string"
                }
            },
            "required": [
                "start_date"
            ],
            "title": "DateRange",
            "type": "object"
        },
        "Job": {
            "properties": {
                "title": {
                    "title": "Title",
                    "type": "string"
                },
                "category": {
                    "title": "Category",
                    "type": "string"
                },
                "classification": {
                    "title": "Classification",
                    "type": "string"
                }
            },
            "required": [
                "title",
                "category",
                "classification"
            ],
            "title": "Job",
            "type": "object"
        },
        "Location": {
            "properties": {
                "state": {
                    "title": "State",
                    "type": "string"
                },
                "county": {
                    "title": "County",
                    "type": "string"
                }
            },
            "required": [
                "state",
                "county"
            ],
            "title": "Location",
            "type": "object"
        },
        "Wage": {
            "properties": {
                "currency": {
                    "default": "USD",
                    "enum": [
                        "AED",
                        "AFN",
                        "ALL",
                        "AMD",
                        "ANG",
                        "AOA",
                        "ARS",
                        "AUD",
                        "AWG",
                        "AZN",
                        "BAM",
                        "BBD",
                        "BDT",
                        "BGN",
                        "BHD",
                        "BIF",
                        "BMD",
                        "BND",
                        "BOB",
                        "BOV",
                        "BRL",
                        "BSD",
                        "BTN",
                        "BWP",
                        "BYN",
                        "BZD",
                        "CAD",
                        "CDF",
                        "CHE",
                        "CHF",
                        "CHW",
                        "CLF",
                        "CLP",
                        "CNY",
                        "COP",
                        "COU",
                        "CRC",
                        "CUC",
                        "CUP",
                        "CVE",
                        "CZK",
                        "DJF",
                        "DKK",
                        "DOP",
                        "DZD",
                        "EGP",
                        "ERN",
                        "ETB",
                        "EUR",
                        "FJD",
                        "FKP",
                        "GBP",
                        "GEL",
                        "GHS",
                        "GIP",
                        "GMD",
                        "GNF",
                        "GTQ",
                        "GYD",
                        "HKD",
                        "HNL",
                        "HRK",
                        "HTG",
                        "HUF",
                        "IDR",
                        "ILS",
                        "INR",
                        "IQD",
                        "IRR",
                        "ISK",
                        "JMD",
                        "JOD",
                        "JPY",
                        "KES",
                        "KGS",
                        "KHR",
                        "KMF",
                        "KPW",
                        "KRW",
                        "KWD",
                        "KYD",
                        "KZT",
                        "LAK",
                        "LBP",
                        "LKR",
                        "LRD",
                        "LSL",
                        "LYD",
                        "MAD",
                        "MDL",
                        "MGA",
                        "MKD",
                        "MMK",
                        "MNT",
                        "MOP",
                        "MRU",
                        "MUR",
                        "MVR",
                        "MWK",
                        "MXN",
                        "MXV",
                        "MYR",
                        "MZN",
                        "NAD",
                        "NGN",
                        "NIO",
                        "NOK",
                        "NPR",
                        "NZD",
                        "OMR",
                        "PAB",
                        "PEN",
                        "PGK",
                        "PHP",
                        "PKR",
                        "PLN",
                        "PYG",
                        "QAR",
                        "RON",
                        "RSD",
                        "RUB",
                        "RWF",
                        "SAR",
                        "SBD",
                        "SCR",
                        "SDG",
                        "SEK",
                        "SGD",
                        "SHP",
                        "SLE",
                        "SLL",
                        "SOS",
                        "SRD",
                        "SSP",
                        "STN",
                        "SVC",
                        "SYP",
                        "SZL",
                        "THB",
                        "TJS",
                        "TMT",
                        "TND",
                        "TOP",
                        "TRY",
                        "TTD",
                        "TWD",
                        "TZS",
                        "UAH",
                        "UGX",
                        "USD",
                        "USN",
                        "UYI",
                        "UYU",
                        "UYW",
                        "UZS",
                        "VED",
                        "VES",
                        "VND",
                        "VUV",
                        "WST",
                        "XAF",
                        "XCD",
                        "XOF",
                        "XPF",
                        "XSU",
                        "XUA",
                        "YER",
                        "ZAR",
                        "ZMW",
                        "ZWL"
                    ],
                    "maxLength": 3,
                    "minLength": 3,
                    "title": "Currency",
                    "type": "string"
                },
                "rate": {
                    "anyOf": [
                        {
                            "type": "number"
                        },
                        {
                            "type": "string"
                        }
                    ],
                    "title": "Rate"
                },
                "fringe": {
                    "anyOf": [
                        {
                            "type": "number"
                        },
                        {
                            "type": "string"
                        }
                    ],
                    "title": "Fringe"
                }
            },
            "required": [
                "rate",
                "fringe"
            ],
            "title": "Wage",
            "type": "object"
        }
    },
    "properties": {
        "decision_number": {
            "pattern": "^[A-Z]{2}[0-9]{8}$",
            "title": "Decision Number",
            "type": "string"
        },
        "modification_number": {
            "minimum": 0,
            "title": "Modification Number",
            "type": "integer"
        },
        "publication_date": {
            "format": "date",
            "title": "Publication Date",
            "type": "string"
        },
        "effective": {
            "$ref": "#/$defs/DateRange"
        },
        "active": {
            "title": "Active",
            "type": "boolean"
        },
        "location": {
            "$ref": "#/$defs/Location"
        },
        "construction_types": {
            "items": {
                "$ref": "#/$defs/ConstructionType"
            },
            "minItems": 1,
            "title": "Construction Types",
            "type": "array",
            "uniqueItems": true
        },
        "rate_identifier": {
            "title": "Rate Identifier",
            "type": "string"
        },
        "job": {
            "$ref": "#/$defs/Job"
        },
        "wage": {
            "$ref": "#/$defs/Wage"
        }
    },
    "required": [
        "decision_number",
        "modification_number",
        "publication_date",
        "effective",
        "active",
        "location",
        "construction_types",
        "rate_identifier",
        "job",
        "wage"
    ],
    "title": "WageDetermination",
    "type": "object"
}'''


def test_json_schema():
    schema = WageDetermination.model_json_schema()
    json_schema = json.dumps(schema, indent=4)
    assert json_schema == expected_json_schema
