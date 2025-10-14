import asyncio
from playwright.async_api import async_playwright

CDP_URL = "http://127.0.0.1:9222"
TARGET = "INR"

async def change_currency_field(page, element):
    """Change one currency field using the fastest approach"""
    try:
        # Click the element
        await element.click()
        
        # Minimal wait for dropdown to open
        await page.wait_for_timeout(100)
        
        # Clear and type INR fast
        await page.keyboard.press("Control+a")
        await page.keyboard.type(TARGET, delay=15)
        
        # Critical wait for filtering to show INR
        await page.wait_for_timeout(180)
        
        # Select INR
        await page.keyboard.press("ArrowDown")
        await page.keyboard.press("Enter")
        
        return True
        
    except Exception as e:
        print(f"Failed: {e}")
        return False

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        page = browser.contexts[0].pages[-1]
        
        print("Discovering currency dropdowns...")
        
        # Find all elements that have "USD" in their text and are clickable
        # Look for elements with IDs starting with "spl-form-element_" that contain USD
        all_elements = await page.query_selector_all('[id^="spl-form-element_"]')
        
        currency_fields = []
        for element in all_elements:
            try:
                # Check if this element or its children contain "USD"
                text_content = await element.text_content()
                if text_content and "USD" in text_content:
                    element_id = await element.get_attribute("id")
                    print(f"Found currency field: {element_id}")
                    currency_fields.append(element)
            except:
                continue
        
        if not currency_fields:
            print("No currency fields found! Trying alternative approach...")
            
            # Alternative: Look for any clickable element containing "USD"
            usd_elements = await page.query_selector_all('*:has-text("USD")')
            for element in usd_elements:
                try:
                    # Check if it's clickable (has click handler or is a form element)
                    tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                    if tag_name in ['div', 'button', 'select', 'input']:
                        # Test if it's actually clickable by checking if it responds to hover
                        bbox = await element.bounding_box()
                        if bbox and bbox['width'] > 20 and bbox['height'] > 20:  # Reasonable size
                            currency_fields.append(element)
                            print(f"Found clickable USD element: {tag_name}")
                except:
                    continue
        
        print(f"Found {len(currency_fields)} currency fields to change")
        
        # SIMPLE SOLUTION: Just take the first 17 fields (likely the main salary fields)
        currency_fields = currency_fields[:17]
        print(f"Limited to first {len(currency_fields)} fields")
        
        if not currency_fields:
            print("No currency fields found at all!")
            return
        
        # Remove duplicates by position
        unique_fields = []
        for field in currency_fields:
            try:
                bbox = await field.bounding_box()
                if bbox:
                    is_duplicate = False
                    for existing in unique_fields:
                        existing_bbox = await existing.bounding_box()
                        if existing_bbox:
                            # Same position = duplicate
                            if abs(bbox['x'] - existing_bbox['x']) < 10 and abs(bbox['y'] - existing_bbox['y']) < 10:
                                is_duplicate = True
                                break
                    if not is_duplicate:
                        unique_fields.append(field)
                else:
                    unique_fields.append(field)  # Include if we can't get bbox
            except:
                unique_fields.append(field)
        
        print(f"{len(unique_fields)} unique currency fields to change")
        
        # Change each field using your fast working method
        successful = 0
        for i, field in enumerate(unique_fields, 1):
            print(f"Changing field {i}/{len(unique_fields)}...", end=" ")
            
            if await change_currency_field(page, field):
                successful += 1
                print("Done")
            else:
                print("Failed")
            
            # Minimal delay between fields for speed
            await page.wait_for_timeout(100)
        
        print(f"\nSuccessfully changed {successful}/{len(unique_fields)} fields to {TARGET}")

if __name__ == "__main__":
    asyncio.run(main())