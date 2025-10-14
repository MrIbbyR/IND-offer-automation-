# -*- coding: utf-8 -*-
# Combined: Set currencies to INR + Fill Excel data into fields

import asyncio
from typing import Dict, Optional, Set
from playwright.async_api import async_playwright
import openpyxl

CDP_URL = "http://127.0.0.1:9222"
TARGET = "INR"
EXCEL_FILE_PATH = r"/path/to/your/excel-file.xlsx"

# Map page label → Excel cell
BINDINGS = [
    {"label_text": "Annual Salary", "excel_cell": "E21", "container_id": None},
    {"label_text": "Pay Based on Frequency", "excel_cell": "D6", "container_id": None},
    {"label_text": "Basic Pay (Annual)", "excel_cell": "E6", "container_id": None},
    {"label_text": "House Rent Allowance (Monthly)", "excel_cell": "D7", "container_id": None},
    {"label_text": "House Rent Allowance (annual)", "excel_cell": "E7", "container_id": None},
    {"label_text": "General Allowance (Monthly)", "excel_cell": "D8", "container_id": None},
    {"label_text": "General Allowance (annual)", "excel_cell": "E8", "container_id": None},
    {"label_text": "Cash Salary (Monthly) Section", "excel_cell": "D10", "container_id": None},
    {"label_text": "Cash Salary (Annual) Section", "excel_cell": "E10", "container_id": None},
    {"label_text": "Employer PF Contribution (Monthly)", "excel_cell": "D13", "container_id": None},
    {"label_text": "Employer PF Contribution (annual)", "excel_cell": "E13", "container_id": None},
    {"label_text": "Total Base Salary (Monthly)", "excel_cell": "D16", "container_id": None},
    {"label_text": "Total Base Salary (Annual)", "excel_cell": "E16", "container_id": None},
    {"label_text": "Monthly Bonus", "excel_cell": "D19", "container_id": None},
    {"label_text": "Annual Bonus", "excel_cell": "E19", "container_id": None},
    {"label_text": "Total Cash Compensation (Monthly)", "excel_cell": "D21", "container_id": None},
    {"label_text": "Total Cash Compensation (Annual)", "excel_cell": "E21", "container_id": None},
]

# ---------- CURRENCY CHANGER ----------
async def change_currency_field(page, element):
    try:
        # Step 1: Click USD to open dropdown
        await element.click()
        await page.wait_for_timeout(80)
        
        # Step 2: Type INR to filter dropdown
        await page.keyboard.press("Control+a")
        await page.keyboard.type(TARGET, delay=5)
        
        # Step 3: CRITICAL - Wait for dropdown to filter properly so INR is highlighted
        await page.wait_for_timeout(220)
        
        # Step 4: Press ArrowDown to select INR from filtered list
        await page.keyboard.press("ArrowDown")
        await page.wait_for_timeout(30)
        
        # Step 5: Press Enter to confirm INR selection
        await page.keyboard.press("Enter")
        await page.wait_for_timeout(30)
        
        return True
    except Exception as e:
        print(f"Failed: {e}")
        return False

async def change_all_currencies(page):
    print("Step 1: Changing currencies from USD to INR...")
    all_elements = await page.query_selector_all('[id^="spl-form-element_"]')
    currency_fields = []
    
    for element in all_elements:
        try:
            text_content = await element.text_content()
            if text_content and "USD" in text_content:
                element_id = await element.get_attribute("id")
                currency_fields.append(element)
        except:
            continue
    
    if not currency_fields:
        print("No currency fields found! Trying alternative approach...")
        usd_elements = await page.query_selector_all('*:has-text("USD")')
        for element in usd_elements:
            try:
                tag_name = await element.evaluate("el => el.tagName.toLowerCase()")
                if tag_name in ['div', 'button', 'select', 'input']:
                    bbox = await element.bounding_box()
                    if bbox and bbox['width'] > 20 and bbox['height'] > 20:
                        currency_fields.append(element)
            except:
                continue
    
    currency_fields = currency_fields[:17]
    
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
                        if abs(bbox['x'] - existing_bbox['x']) < 10 and abs(bbox['y'] - existing_bbox['y']) < 10:
                            is_duplicate = True
                            break
                if not is_duplicate:
                    unique_fields.append(field)
            else:
                unique_fields.append(field)
        except:
            unique_fields.append(field)
    
    # Change currencies
    successful = 0
    for i, field in enumerate(unique_fields, 1):
        print(f"Changing currency {i}/{len(unique_fields)}...", end=" ")
        if await change_currency_field(page, field):
            successful += 1
            print("Done")
        else:
            print("Failed")
        await page.wait_for_timeout(100)
    
    print(f"Currency change: {successful}/{len(unique_fields)} fields changed to {TARGET}")
    return successful > 0

# ---------- EXCEL DATA FILLER ----------
def _fmt_num(v) -> str:
    if v is None:
        return ""
    if isinstance(v, (int, float)):
        return str(int(v))
    s = str(v).strip().replace(",", "")
    try:
        return str(int(float(s)))
    except:
        return s

def read_cells_once(path: str, cells: Set[str]) -> Dict[str, str]:
    wb = openpyxl.load_workbook(path, data_only=True, read_only=True)
    sh = wb[wb.sheetnames[0]]
    out: Dict[str, str] = {}
    for addr in cells:
        try:
            out[addr] = _fmt_num(sh[addr].value)
        except Exception:
            out[addr] = ""
    wb.close()
    return out

_ID_CACHE: Dict[str, str] = {}

async def get_block(page, label_text: str, container_id: Optional[str]):
    cached = _ID_CACHE.get(label_text)
    if cached:
        blk = page.locator(f"#{cached}")
        if await blk.count():
            return blk.first

    if container_id:
        blk = page.locator(f"#{container_id}")
        if await blk.count():
            return blk.first

    blk = page.locator('[id^="spl-form-element_"]').filter(
        has=page.get_by_text(label_text, exact=False)
    ).first

    if await blk.count():
        bid = await blk.get_attribute("id")
        if bid:
            _ID_CACHE[label_text] = bid

    return blk

async def focus_value_box_via_tab(page, block) -> bool:
    try:
        currency = block.locator('[role="combobox"], button[aria-expanded], button').first
        await currency.click()
        await page.keyboard.press("Escape")
        await page.keyboard.press("Tab")
        return True
    except:
        return False

async def type_into_focused(page, value: str) -> bool:
    try:
        await page.keyboard.press("Control+a")
        await page.keyboard.type(value, delay=5)
        return True
    except:
        return False

async def fill_field(page, label_text: str, excel_value: str, container_id: Optional[str] = None) -> bool:
    if not excel_value:
        return False

    try:
        block = await get_block(page, label_text, container_id)
        if not await block.count():
            return False

        # Method 1: Tab navigation
        if await focus_value_box_via_tab(page, block) and await type_into_focused(page, excel_value):
            return True

        # Method 2: Direct click fallback
        bb = await block.bounding_box()
        if bb:
            positions = [
                (bb["x"] + bb["width"] - 14, bb["y"] + bb["height"] / 2),
                (bb["x"] + bb["width"] - 50, bb["y"] + bb["height"] / 2),
                (bb["x"] + bb["width"] - 100, bb["y"] + bb["height"] / 2)
            ]
            
            for x, y in positions:
                try:
                    await page.mouse.click(x, y)
                    if await type_into_focused(page, excel_value):
                        return True
                except:
                    continue

    except:
        pass
        
    return False

async def fill_excel_data(page):
    print("Step 2: Reading Excel and filling data...")
    
    # Read all cells at once
    needed = {b["excel_cell"] for b in BINDINGS}
    excel_values = read_cells_once(EXCEL_FILE_PATH, needed)
    
    filled = 0
    for i, b in enumerate(BINDINGS):
        v = excel_values.get(b["excel_cell"], "")
        if v:
            print(f"[{i+1:2d}] {b['label_text']}: {v}", end=" ")
            
            ok = await fill_field(page, b["label_text"], v, b.get("container_id"))
            if ok:
                filled += 1
                print("✅")
            else:
                print("✗")
            
            await page.wait_for_timeout(25)
        else:
            print(f"[{i+1:2d}] {b['label_text']}: (empty)")
    
    print(f"Data entry: {filled}/{len(BINDINGS)} fields filled")
    return filled

# ---------- MAIN ----------
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        page = browser.contexts[0].pages[-1]
        await page.bring_to_front()

        print("Starting combined currency change + Excel data filling...")
        
        # Step 1: Change all currencies to INR
        currency_success = await change_all_currencies(page)
        
        # Wait for page to settle after currency changes
        await page.wait_for_timeout(1000)
        
        # Step 2: Fill Excel data into fields
        filled_count = await fill_excel_data(page)
        
        # Summary
        print(f"\nCompleted:")
        print(f"- Currency change: {'✅' if currency_success else '❌'}")
        print(f"- Data entry: {filled_count} fields filled")

if __name__ == "__main__":
    asyncio.run(main())