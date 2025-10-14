# -*- coding: utf-8 -*-
# Field filler: read Excel and type into specific fields (IMPROVED FOR SPEED)

import asyncio
from typing import Dict, Optional, Set
from playwright.async_api import async_playwright
import openpyxl

CDP_URL = "http://127.0.0.1:9222"
EXCEL_FILE_PATH = r"/path/to/your/excel-file.xlsx"

# Map page label → Excel cell (extend as needed)
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

# ---------- Excel helpers (OPTIMIZED) ----------
def _fmt_num(v) -> str:
    if v is None:
        return ""
    # Fast path for numbers
    if isinstance(v, (int, float)):
        return str(int(v))
    s = str(v).strip().replace(",", "")
    try:
        return str(int(float(s)))
    except:
        return s

def read_cells_once(path: str, cells: Set[str]) -> Dict[str, str]:
    """Read all needed cells in one operation"""
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

# ---------- Targeting helpers (SPEED OPTIMIZED) ----------
_ID_CACHE: Dict[str, str] = {}  # Cache learned IDs for instant reuse

async def get_block(page, label_text: str, container_id: Optional[str]):
    # Try cached ID first (FASTEST)
    cached = _ID_CACHE.get(label_text)
    if cached:
        blk = page.locator(f"#{cached}")
        if await blk.count():
            return blk.first

    # Try explicit ID if provided
    if container_id:
        blk = page.locator(f"#{container_id}")
        if await blk.count():
            return blk.first

    # Fallback: find by text content
    blk = page.locator('[id^="spl-form-element_"]').filter(
        has=page.get_by_text(label_text, exact=False)
    ).first

    # Cache the ID for future use
    if await blk.count():
        bid = await blk.get_attribute("id")
        if bid:
            _ID_CACHE[label_text] = bid

    return blk

async def focus_value_box_via_tab(page, block) -> bool:
    try:
        # Find currency dropdown faster
        currency = block.locator('[role="combobox"], button[aria-expanded], button').first
        await currency.click()
        # Removed waits - let browser handle timing
        await page.keyboard.press("Escape")
        await page.keyboard.press("Tab")
        return True
    except:
        return False

async def type_into_focused(page, value: str) -> bool:
    try:
        await page.keyboard.press("Control+a")
        await page.keyboard.type(value, delay=5)  # Even faster typing - 5ms delay
        return True
    except:
        return False

async def pick_amount_input_near_currency(block):
    try:
        # Ultra-fast candidate search - only check first match
        currency = block.locator('[role="combobox"], button[aria-expanded], button').first
        cbox = await currency.bounding_box()
        if not cbox:
            return None
            
        cur_right = cbox["x"] + cbox["width"]
        cur_mid_y = cbox["y"] + cbox["height"] / 2

        # Only check the most likely input type for speed
        inputs = block.locator('input, [role="textbox"]')
        n = await inputs.count()
        
        # Return first reasonable match instead of finding "best" match
        for i in range(min(n, 2)):  # Only check first 2
            el = inputs.nth(i)
            try:
                b = await el.bounding_box()
                if b and b["width"] >= 50:
                    cx = b["x"] + b["width"] / 2
                    cy = b["y"] + b["height"] / 2
                    dx = cx - cur_right
                    if dx > 0 and abs(cy - cur_mid_y) <= 60:
                        return el  # Return first match, don't optimize further
            except:
                continue
        return None
    except:
        return None

async def fill_field(page, label_text: str, excel_value: str, container_id: Optional[str] = None) -> bool:
    if not excel_value:
        return False

    try:
        block = await get_block(page, label_text, container_id)
        if not await block.count():
            return False

        # Method 1: Tab navigation (FASTEST) - try this first always
        if await focus_value_box_via_tab(page, block) and await type_into_focused(page, excel_value):
            return True

        # Method 2: Skip complex input detection, try direct click fallback immediately
        bb = await block.bounding_box()
        if bb:
            # Try multiple click positions quickly
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

# ---------- Main (MAXIMUM SPEED) ----------
async def main():
    async with async_playwright() as p:
        browser = await p.chromium.connect_over_cdp(CDP_URL)
        page = browser.contexts[0].pages[-1]

        print("Reading Excel data...")
        # Read all cells at once
        needed = {b["excel_cell"] for b in BINDINGS}
        excel_values = read_cells_once(EXCEL_FILE_PATH, needed)

        print("Filling fields at maximum speed...")
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
                
                # Ultra-minimal delay - just enough to prevent conflicts
                await page.wait_for_timeout(25)  # Down to 25ms
            else:
                print(f"[{i+1:2d}] {b['label_text']}: (empty)")

        print(f"Finished: {filled}/{len(BINDINGS)} filled")

if __name__ == "__main__":
    asyncio.run(main())