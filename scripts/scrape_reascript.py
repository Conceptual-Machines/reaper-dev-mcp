#!/usr/bin/env python3
"""
Scrape ReaScript API documentation from extremraym.com and export to JSON for MCP server.
Extracts ALL functions organized by language (C, EEL2, Lua, Python).
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
    print("Error: beautifulsoup4 not installed. Run: python3.13 -m pip install beautifulsoup4", file=sys.stderr)
    sys.exit(1)

def fetch_extremraym_docs() -> str:
    """Fetch ReaScript API documentation from extremraym.com."""
    url = "https://www.extremraym.com/cloud/reascript-doc/"
    print(f"Fetching ReaScript API docs from {url}...", file=sys.stderr)
    with urlopen(url) as response:
        return response.read().decode("utf-8")

def parse_function_signature(sig_text: str, language: str = "c") -> dict:
    """Parse a function signature to extract return type, name, and parameters."""
    # Remove HTML tags and clean up
    sig_text = re.sub(r'<[^>]+>', '', sig_text).strip()
    
    # Handle Lua format: reaper.FunctionName(...)
    if language == "lua" and "reaper." in sig_text:
        # Extract: return_type reaper.function_name(params)
        pattern = r'(\w+(?:\s*\*)?)?\s*reaper\.(\w+)\s*\((.*?)\)'
        match = re.match(pattern, sig_text)
        if match:
            return_type = match.group(1).strip() if match.group(1) else None
            name = match.group(2).strip()
            params_str = match.group(3).strip()
            return {
                "return_type": return_type,
                "name": name,
                "parameters": parse_parameters(params_str),
            }
    
    # Handle Python format: RPR_FunctionName(...)
    if language == "python" and "RPR_" in sig_text:
        pattern = r'(\w+(?:\s*\*)?)?\s*RPR_(\w+)\s*\((.*?)\)'
        match = re.match(pattern, sig_text)
        if match:
            return_type = match.group(1).strip() if match.group(1) else None
            name = match.group(2).strip()
            params_str = match.group(3).strip()
            return {
                "return_type": return_type,
                "name": name,
                "parameters": parse_parameters(params_str),
            }
    
    # Standard pattern: return_type function_name(param1, param2, ...)
    pattern = r'(\w+(?:\s*\*)?)\s+(\w+)\s*\((.*?)\)'
    match = re.match(pattern, sig_text)
    
    if not match:
        # Try without return type
        pattern = r'(\w+)\s*\((.*?)\)'
        match = re.match(pattern, sig_text)
        if match:
            return {
                "return_type": None,
                "name": match.group(1),
                "parameters": parse_parameters(match.group(2)),
            }
        return None
    
    return_type = match.group(1).strip()
    name = match.group(2).strip()
    params_str = match.group(3).strip()
    
    return {
        "return_type": return_type if return_type else None,
        "name": name,
        "parameters": parse_parameters(params_str),
    }

def parse_parameters(params_str: str) -> list[dict]:
    """Parse function parameters from a string."""
    if not params_str or params_str.strip() == "":
        return []
    
    params = []
    # Split by comma, but be careful with nested types like "MediaTrack*"
    parts = re.split(r',\s*(?![^<>]*>)', params_str)
    
    for part in parts:
        part = part.strip()
        if not part:
            continue
        
        # Pattern: type name or type* name
        param_match = re.match(r'(\w+(?:\s*\*)?)\s+(\w+)', part)
        if param_match:
            param_type = param_match.group(1).strip()
            param_name = param_match.group(2).strip()
            params.append({
                "type": param_type,
                "name": param_name,
            })
        else:
            # Just type, no name
            params.append({
                "type": part,
                "name": None,
            })
    
    return params

def scrape_all_functions(html: str) -> dict:
    """Scrape all functions from the HTML, organized by language."""
    soup = BeautifulSoup(html, "html.parser")
    
    # Store all functions with all their language signatures
    all_functions = {}
    
    # Also organize by language for easy lookup
    functions_by_language = {
        "c": [],
        "eel2": [],
        "lua": [],
        "python": [],
    }
    
    # Find all function definitions
    functions_section = soup.find("section", class_="functions_all")
    if not functions_section:
        print("Warning: Could not find functions_all section", file=sys.stderr)
        return {"all_functions": all_functions, "by_language": functions_by_language}
    
    for func_div in functions_section.find_all("div", class_="function_definition"):
        func_id = func_div.get("id", "")
        
        # Extract function name from ID
        function_name = func_id
        
        # Get description
        desc_p = func_div.find("p")
        description = desc_p.get_text(strip=True) if desc_p else ""
        
        # Initialize function data
        if function_name not in all_functions:
            all_functions[function_name] = {
                "name": function_name,
                "description": description,
                "signatures": {},
                "available_in": [],
            }
        
        func_data = all_functions[function_name]
        
        # Extract signatures for each language
        c_func = func_div.find("div", class_="c_func")
        e_func = func_div.find("div", class_="e_func")
        l_func = func_div.find("div", class_="l_func")
        p_func = func_div.find("div", class_="p_func")
        
        # Parse C/C++ signature
        if c_func:
            c_code = c_func.find("code")
            if c_code:
                sig = parse_function_signature(c_code.get_text(), "c")
                if sig:
                    func_data["signatures"]["c"] = sig
                    if "c" not in func_data["available_in"]:
                        func_data["available_in"].append("c")
                        functions_by_language["c"].append(function_name)
        
        # Parse EEL2 signature
        if e_func:
            e_code = e_func.find("code")
            if e_code:
                sig = parse_function_signature(e_code.get_text(), "eel2")
                if sig:
                    func_data["signatures"]["eel2"] = sig
                    if "eel2" not in func_data["available_in"]:
                        func_data["available_in"].append("eel2")
                        functions_by_language["eel2"].append(function_name)
        
        # Parse Lua signature
        if l_func:
            l_code = l_func.find("code")
            if l_code:
                sig = parse_function_signature(l_code.get_text(), "lua")
                if sig:
                    func_data["signatures"]["lua"] = sig
                    if "lua" not in func_data["available_in"]:
                        func_data["available_in"].append("lua")
                        functions_by_language["lua"].append(function_name)
        
        # Parse Python signature
        if p_func:
            p_code = p_func.find("code")
            if p_code:
                sig = parse_function_signature(p_code.get_text(), "python")
                if sig:
                    func_data["signatures"]["python"] = sig
                    if "python" not in func_data["available_in"]:
                        func_data["available_in"].append("python")
                        functions_by_language["python"].append(function_name)
    
    return {
        "all_functions": all_functions,
        "by_language": functions_by_language,
    }

def main():
    """Scrape ReaScript API and export to JSON."""
    print("Scraping ReaScript API documentation from extremraym.com...", file=sys.stderr)
    
    html = fetch_extremraym_docs()
    scraped_data = scrape_all_functions(html)
    
    all_functions = scraped_data["all_functions"]
    functions_by_language = scraped_data["by_language"]
    
    # Convert to list for easier JSON handling
    functions_list = list(all_functions.values())
    
    data = {
        "functions": functions_list,
        "functions_by_language": functions_by_language,
        "scraped_at": datetime.now().isoformat(),
        "total_unique_functions": len(all_functions),
        "counts_by_language": {
            lang: len(funcs) for lang, funcs in functions_by_language.items()
        },
    }
    
    output_path = Path(__file__).parent.parent / "data" / "reascript-api.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    
    print(f"Saved ReaScript API data to {output_path}", file=sys.stderr)
    print(f"Total unique functions: {data['total_unique_functions']}", file=sys.stderr)
    print("\nFunctions by language:", file=sys.stderr)
    for lang, count in data["counts_by_language"].items():
        print(f"  {lang.upper()}: {count}", file=sys.stderr)

if __name__ == "__main__":
    main()
