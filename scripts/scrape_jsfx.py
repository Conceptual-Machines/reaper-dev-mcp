#!/usr/bin/env python3
"""
Scrape JSFX documentation from https://www.reaper.fm/sdk/js/js.php
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from urllib.request import urlopen

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Error: beautifulsoup4 not installed. Run: pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)

def fetch_url(url: str) -> str:
    """Fetch a URL and return its content."""
    print(f"Fetching {url}...", file=sys.stderr)
    with urlopen(url) as response:
        return response.read().decode("utf-8")

def find_jsfx_pages(main_html: str) -> list[str]:
    """Find all JSFX documentation pages linked from the main page."""
    soup = BeautifulSoup(main_html, "html.parser")
    base_url = "https://www.reaper.fm/sdk/js/"
    pages = set()
    
    # Find all links that point to .php files in the js directory
    # These are in the navigation list in the intro section
    for link in soup.find_all("a", href=True):
        href = link.get("href", "")
        
        # Look for links containing .php (could have anchors)
        if ".php" in href and not href.startswith("http"):
            # Extract filename (remove anchor if present)
            filename = href.split("#")[0]
            
            # Skip if it has path components going up (../) or is absolute path
            if "../" not in filename and not filename.startswith("/"):
                # It's a relative link - should be in js directory
                full_url = base_url + filename
                pages.add(full_url)
    
    # Always include the main page
    pages.add("https://www.reaper.fm/sdk/js/js.php")
    
    # Filter to only pages in the js directory and remove duplicates/normalize
    filtered_pages = []
    seen = set()
    for p in pages:
        if "/sdk/js/" in p:
            # Normalize URL (remove anchors, ensure consistent format)
            normalized = p.split("#")[0]
            if normalized not in seen:
                seen.add(normalized)
                filtered_pages.append(normalized)
    
    return sorted(filtered_pages)

def parse_jsfx_html(html: str, url: str = "") -> dict:
    """Parse JSFX HTML documentation from a single page."""
    soup = BeautifulSoup(html, "html.parser")
    
    data = {
        "functions": [],
        "operators": [],
        "special_variables": [],
        "sections": [],
        "source_url": url,
    }
    
    # Extract sections
    for link in soup.find_all("a", href=re.compile(r"^#")):
        text = link.get_text(strip=True)
        if text and text not in ("top", "Home"):
            href = link.get("href", "")
            if href.startswith("#"):
                section_id = href[1:]
                # Try to find the section content
                section_el = soup.find(id=section_id) or soup.find("a", {"name": section_id})
                if section_el:
                    # Get description from following content
                    desc = ""
                    next_el = section_el.next_sibling
                    if next_el:
                        desc = next_el.get_text(strip=True)[:200]
                    data["sections"].append({
                        "name": text,
                        "id": section_id,
                        "description": desc,
                    })
    
    # Extract function references from code blocks and text
    seen_functions = set()
    
    # Look for function definitions in code blocks
    for code in soup.find_all(["code", "pre"]):
        text = code.get_text(strip=True)
        # Look for function patterns like function_name(...)
        func_matches = re.finditer(r"(\w+)\s*\([^)]*\)", text)
        for match in func_matches:
            func_name = match.group(1)
            # Filter out common non-function patterns
            if (func_name not in seen_functions and 
                len(func_name) > 2 and 
                func_name not in ["if", "while", "loop", "return", "abs", "min", "max"]):
                seen_functions.add(func_name)
                # Get context/description
                parent = code.parent
                description = ""
                if parent:
                    # Try to get description from surrounding text
                    desc_text = parent.get_text(strip=True)
                    # Look for function name followed by description
                    desc_match = re.search(rf"{re.escape(func_name)}[^a-zA-Z0-9_]+(.{{0,300}})", desc_text, re.IGNORECASE)
                    if desc_match:
                        description = desc_match.group(1).strip()
                    else:
                        description = desc_text[:500]
                
                data["functions"].append({
                    "name": func_name,
                    "category": "unknown",
                    "description": description,
                    "signature": match.group(0),
                })
    
    # Also look for function definitions in list items (like "sin(angle) -- returns...")
    for li in soup.find_all("li"):
        text = li.get_text(strip=True)
        # Pattern: function_name(params) -- description
        func_match = re.match(r"(\*\*)?(\w+)\s*\([^)]*\)\s*[–-]\s*(.+)", text)
        if func_match:
            func_name = func_match.group(2)
            if func_name not in seen_functions:
                seen_functions.add(func_name)
                description = func_match.group(3).strip()
                # Extract signature
                sig_match = re.search(rf"{re.escape(func_name)}\s*\([^)]*\)", text)
                signature = sig_match.group(0) if sig_match else f"{func_name}()"
                
                data["functions"].append({
                    "name": func_name,
                    "category": "unknown",
                    "description": description,
                    "signature": signature,
                })
    
    # Common JSFX special variables
    data["special_variables"] = [
        {"name": "spl0", "description": "Left channel audio sample", "type": "number", "scope": "@sample"},
        {"name": "spl1", "description": "Right channel audio sample", "type": "number", "scope": "@sample"},
        {"name": "slider1", "description": "First slider parameter", "type": "number"},
        {"name": "param[0]", "description": "First parameter array access", "type": "number"},
        {"name": "srate", "description": "Sample rate", "type": "number"},
        {"name": "tempo", "description": "Current tempo", "type": "number"},
        {"name": "play_state", "description": "Playback state", "type": "number"},
        {"name": "gfx_w", "description": "Graphics width", "type": "number", "scope": "@gfx"},
        {"name": "gfx_h", "description": "Graphics height", "type": "number", "scope": "@gfx"},
        {"name": "mouse_x", "description": "Mouse X position", "type": "number", "scope": "@gfx"},
        {"name": "mouse_y", "description": "Mouse Y position", "type": "number", "scope": "@gfx"},
    ]
    
    # Common operators
    data["operators"] = [
        {"operator": "+", "description": "Addition"},
        {"operator": "-", "description": "Subtraction"},
        {"operator": "*", "description": "Multiplication"},
        {"operator": "/", "description": "Division"},
        {"operator": "%", "description": "Modulo"},
        {"operator": "=", "description": "Assignment"},
        {"operator": "==", "description": "Equality"},
        {"operator": "!=", "description": "Inequality"},
        {"operator": "<", "description": "Less than"},
        {"operator": ">", "description": "Greater than"},
        {"operator": "<=", "description": "Less than or equal"},
        {"operator": ">=", "description": "Greater than or equal"},
        {"operator": "&&", "description": "Logical AND"},
        {"operator": "||", "description": "Logical OR"},
        {"operator": "!", "description": "Logical NOT"},
        {"operator": "?:", "description": "Ternary operator"},
    ]
    
    return data

def main():
    """Main scraper function."""
    try:
        # Start with main page
        main_url = "https://www.reaper.fm/sdk/js/js.php"
        main_html = fetch_url(main_url)
        
        # Find all JSFX documentation pages
        pages = find_jsfx_pages(main_html)
        print(f"Found {len(pages)} JSFX documentation pages", file=sys.stderr)
        
        # Aggregate data from all pages
        all_data = {
            "functions": [],
            "operators": [],
            "special_variables": [],
            "sections": [],
            "scraped_at": datetime.now().isoformat(),
            "pages_scraped": [],
        }
        
        seen_functions = set()
        seen_operators = set()
        seen_sections = set()
        
        # Scrape each page
        for page_url in pages:
            try:
                print(f"  Scraping {page_url}...", file=sys.stderr)
                html = fetch_url(page_url)
                page_data = parse_jsfx_html(html, page_url)
                
                # Merge functions (avoid duplicates)
                for func in page_data["functions"]:
                    if func["name"] not in seen_functions:
                        seen_functions.add(func["name"])
                        all_data["functions"].append(func)
                
                # Merge operators (avoid duplicates)
                for op in page_data["operators"]:
                    op_key = op["operator"]
                    if op_key not in seen_operators:
                        seen_operators.add(op_key)
                        all_data["operators"].append(op)
                
                # Merge sections (avoid duplicates by name)
                for section in page_data["sections"]:
                    if section["name"] not in seen_sections:
                        seen_sections.add(section["name"])
                        all_data["sections"].append(section)
                
                # Special variables are only added once (from first page or hardcoded)
                if not all_data["special_variables"]:
                    all_data["special_variables"] = page_data["special_variables"]
                
                all_data["pages_scraped"].append(page_url)
            except Exception as e:
                print(f"  Warning: Error scraping {page_url}: {e}", file=sys.stderr)
        
        output_path = Path(__file__).parent.parent / "data" / "jsfx-api.json"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, "w") as f:
            json.dump(all_data, f, indent=2)
        
        print(f"\nSaved JSFX API data to {output_path}", file=sys.stderr)
        print(f"Found {len(all_data['functions'])} functions, {len(all_data['operators'])} operators, "
              f"{len(all_data['special_variables'])} special variables, {len(all_data['sections'])} sections",
              file=sys.stderr)
        print(f"Scraped {len(all_data['pages_scraped'])} pages", file=sys.stderr)
    except Exception as e:
        print(f"Error scraping JSFX docs: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()

