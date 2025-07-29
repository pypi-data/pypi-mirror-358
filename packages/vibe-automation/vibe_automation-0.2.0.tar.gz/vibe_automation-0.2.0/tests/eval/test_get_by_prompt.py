import pytest
from .eval import setup_eval_page


class TestWebEnvSample:
    """Sample tests demonstrating setup_web_env usage."""

    @setup_eval_page(
        html="<input name='search query' placeholder='Enter search'/> <button>Search</button>",
    )
    async def test_get_by_prompt_with_synthetic_html(self, eval_page):
        """Test using setup_web_env with inline HTML content."""
        # Test that we can find elements using get_by_prompt
        search_button = eval_page.get_by_prompt("The search button")
        assert await search_button.text_content() == "Search"

        search_input = eval_page.get_by_prompt("search input field")
        assert await search_input.get_attribute("placeholder") == "Enter search"

    @pytest.mark.skip(reason="Stagehand act doesn't work on some tests")
    @setup_eval_page(
        html="""
        <html>
        <head><title>Test Form</title></head>
        <body>
            <form>
                <label for="name">Customer Name:</label>
                <input type="text" id="name" name="customer_name"/>
                
                <label for="email">Email Address:</label>
                <input type="email" id="email" name="email"/>
                
                <button type="submit">Submit Order</button>
            </form>
        </body>
        </html>
        """,
    )
    async def test_form_interaction(self, eval_page):
        """Test form interaction with more complex HTML."""
        # Fill out the form using get_by_prompt
        name_field = eval_page.get_by_prompt("Customer name")
        await name_field.fill("John Doe")

        email_field = eval_page.get_by_prompt("Email address")
        await email_field.fill("john@example.com")

        # Verify the values were set
        assert await name_field.input_value() == "John Doe"
        assert await email_field.input_value() == "john@example.com"

        # Test the submit button
        submit_btn = eval_page.get_by_prompt("Submit button")
        assert await submit_btn.text_content() == "Submit Order"

    @setup_eval_page(
        html="""
        <div class="product-list">
            <div class="product">
                <h3>Pizza</h3>
                <label><input type="radio" name="size" value="small"> Small</label>
                <label><input type="radio" name="size" value="medium"> Medium</label>
                <label><input type="radio" name="size" value="large"> Large</label>
            </div>
            <button class="add-to-cart">Add to Cart</button>
        </div>
        """,
    )
    async def test_radio_button_selection(self, eval_page):
        """Test radio button interaction."""
        # Select medium size pizza using get_by_prompt
        medium_option = eval_page.get_by_prompt("medium size pizza")
        await medium_option.check()

        # Verify it's selected
        assert await medium_option.is_checked()

        # Test add to cart button
        add_button = eval_page.get_by_prompt("Add to cart")
        assert await add_button.is_visible()

    @pytest.mark.skip(reason="Stagehand act doesn't work on some tests")
    @setup_eval_page(
        html="""
          <button id="main-btn">Main button</button>
          <iframe src="http://localhost/iframe.html" width="400" height="300"></iframe>
        """,
        resources=[
            {
                "url": "http://localhost/iframe.html",
                "content": """
                    <h2>Content inside iframe</h2>
                    <button id="iframe-btn">Click Me</button>
                """,
            }
        ],
    )
    async def test_button_in_iframe(self, eval_page):
        """Test locating a button element inside an iframe."""
        iframe_button = eval_page.get_by_prompt("Click Me button")
        assert await iframe_button.is_visible()
        assert await iframe_button.text_content() == "Click Me"
