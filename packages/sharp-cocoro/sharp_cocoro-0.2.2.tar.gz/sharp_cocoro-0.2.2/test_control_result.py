#!/usr/bin/env python3

from sharp_cocoro.properties import ControlResultStatus
from sharp_cocoro.response_types import ControlResultResponse, ControlResultItem


def test_control_result_status():
    print("Available control result statuses:")
    for status in ControlResultStatus:
        print(f'  {status.name} = "{status.value}"')


def test_control_result_response():
    # Test creating a control result response
    test_data = {
        "resultList": [
            {
                "id": "1220840543",
                "status": "success",
                "message": None,
                "cancelled_by": None,
                "errorCode": None,
                "epc": "A0",
                "edt": "Si41",
            },
            {
                "id": "1220840542",
                "status": "unmatch",
                "message": None,
                "cancelled_by": None,
                "errorCode": None,
                "epc": "FA",
                "edt": "Bic30000000000c000000000000000000000000000000000000000000000000000000000000000000000000000000000000201000000000000000000000000000000000000000000000000000000000000",
            },
        ]
    }

    response = ControlResultResponse(**test_data)
    print(f"\nCreated response with {len(response.resultList)} items:")
    for item in response.resultList:
        print(f"  ID: {item.id}, Status: {item.status.value}, EPC: {item.epc}")


if __name__ == "__main__":
    test_control_result_status()
    test_control_result_response()
    print("\nAll tests passed!")
