from app.services.filename_rules import build_filename, load_rules
from app.models.schemas import OrderIn

def test_filename_rules_smoke():
    rules = load_rules()
    order = OrderIn(
        customer_name="Test",
        customer_email="t@example.com",
        category="ER",
        design="Solitaire",
        stone="Round",
        metal="14k White Gold",
        size=6.5,
        price=1000.0,
    )
    fn = build_filename(order, rules)
    assert fn.endswith(".3dm")
    assert "er" in fn and "sol" in fn and "rou" in fn and "14kw" in fn
