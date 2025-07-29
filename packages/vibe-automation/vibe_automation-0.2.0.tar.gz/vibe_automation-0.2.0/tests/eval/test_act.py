import pytest
from pathlib import Path
from .eval import setup_eval_page


@pytest.mark.skip(reason="Stagehand act doesn't work on some tests")
@setup_eval_page(
    html=Path(__file__).parent / "test_pages" / "select" / "native.html",
)
async def test_native_select(eval_page):
    """Test select_dropdown works with different dropdown types and instructions"""
    # Test 1: Simple dropdown selection
    result = await eval_page.act("Select Option 2 from the Simple Dropdown")
    assert result.success is True

    result_element = eval_page.locator("#selection-result")
    assert "Simple Dropdown: option2" in (await result_element.text_content() or "")

    # Test 2: Grouped dropdown selection
    result = await eval_page.act("Select B1 from Group B in the Grouped Dropdown")
    assert result.success is True

    # Verify selection
    result_element = eval_page.locator("#selection-result")
    assert "Grouped Dropdown: b1" in (await result_element.text_content() or "")

    # Test 3: Multiple selection dropdown
    result = await eval_page.act(
        "Select Item 1 and Item 3 from the Multiple Selection dropdown"
    )
    assert result.success is True

    # Verify multiple selection
    result_element = eval_page.locator("#selection-result")
    content = await result_element.text_content() or ""
    assert "Multiple Selection:" in content
    assert "item1" in content
    assert "item3" in content


@pytest.mark.skip(reason="Stagehand act doesn't work on some tests")
@setup_eval_page(
    html=Path(__file__).parent / "test_pages" / "select" / "custom.html",
)
async def test_custom_select(eval_page):
    """Test select_dropdown works with different dropdown types and instructions"""
    # Test 1: Simple dropdown selection
    result = await eval_page.act("Select Option 2 from the Simple Dropdown")
    assert result.success is True

    result_element = eval_page.locator("#selection-result")
    assert "Custom Dropdown: Option 2" in (await result_element.text_content() or "")

    # Test 2: Grouped dropdown selection
    result = await eval_page.act("Select B1 from Group B in the Grouped Dropdown")
    assert result.success is True

    # Verify selection
    result_element = eval_page.locator("#selection-result")
    assert "Custom Grouped Dropdown: B1" in (await result_element.text_content() or "")

    # Test 3: Multiple selection dropdown
    result = await eval_page.act(
        "Select Item 1 and Item 3 from the Multiple Selection dropdown"
    )
    assert result.success is True

    # Verify multiple selection
    result_element = eval_page.locator("#selection-result")
    content = await result_element.text_content() or ""
    assert "Custom Multi-Select:" in content
    assert "item1" in content
    assert "item3" in content
