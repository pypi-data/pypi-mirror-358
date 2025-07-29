"""Test models."""

from datetime import date

from onsite_edp_sdk import Customer, Design, DesignLocation, EDPDocument, Order

SAMPLE_DOCUMENT = EDPDocument(
    order=Order(
        external_order_id="TEST",
        date_external=date(2022, 8, 5),
        order_type_id=1,
        date_order_placed=date(2022, 8, 5),
        on_hold=True,
        status_allow_commission=True,
    ),
    customer=Customer(
        customer_id=1,
    ),
    designs=[
        (
            Design(
                design_name="Design1",
            ),
            [
                DesignLocation(
                    location="Test Location",
                ),
            ],
        ),
    ],
)

SAMPLE_OUTPUT = """\
---- Start Order ----
ExtOrderID: TEST
date_External: 08/05/2022
id_OrderType: 1.0
sts_CommishAllow: 1
HoldOrderText: Yes
date_OrderPlaced: 08/05/2022
---- End Order ----
---- Start Customer ----
id_Customer: 1
---- End Customer ----
---- Start Design ----
DesignName: Design1
---- Start Location ----
Location: Test Location
---- End Location ----
---- End Design ----
"""


def test_can_create_order() -> None:
    """Sanity check."""
    assert SAMPLE_DOCUMENT.to_edp() == SAMPLE_OUTPUT
