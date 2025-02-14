import pytest

from utils import check_valid_url


@pytest.mark.parametrize(
    "url,expected_valid",
    [
        ("https://testing.com", True),
        ("https://testing.com/product", True),
        ("https://testing.com/product?id=123", True),
        ("https://testing.com/product#section", True),
        ("https://testing.com/shop/product/testproduct", True),
        ("https://testing.com/shop/product/testproduct.html", True),
        ("http://testing.com", True),
        ("https://shop.testing.com", True),
        ("https://shop.testing.co", True),
        ("https://testing.com.au", True),
        ("https://testingcom", False),
        ("not-a-url", False),
        ("http:/store.com", False),
        ("ftp://store.com", False),
    ],
)
def test_check_valid_url_patterns(url, expected_valid):
    assert check_valid_url(url) == expected_valid
