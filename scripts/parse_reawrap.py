#!/usr/bin/env python3
"""
Parse ReaWrap API from Lua source files.
Extracts methods, classes, and documentation from LDoc comments.
"""

import json
import re
import sys
from datetime import datetime
from pathlib import Path

def parse_ldoc_comment(comment: str) -> dict:
    """Parse an LDoc comment block."""
    lines = [line.strip() for line in comment.split("\n") if line.strip()]
    
    result = {
        "description": "",
        "parameters": [],
        "returns": [],
        "category": None,
    }
    
    current_desc = []
    for line in lines:
        if line.startswith("---"):
            line = line[3:].strip()
        
        if line.startswith("@param"):
            # @param name type description
            match = re.match(r"@param\s+(\w+)\s+(.+?)(?:\s+(.+))?$", line)
            if match:
                name, type_part, desc = match.groups()
                result["parameters"].append({
                    "name": name,
                    "type": type_part.split()[0] if type_part else "any",
                    "description": desc or "",
                    "optional": "optional" in type_part.lower(),
                })
        elif line.startswith("@return"):
            # @return type description
            match = re.match(r"@return\s+(.+?)(?:\s+(.+))?$", line)
            if match:
                type_part, desc = match.groups()
                result["returns"].append({
                    "type": type_part.split()[0] if type_part else "any",
                    "description": desc or "",
                })
        elif line.startswith("@within"):
            # @within category
            result["category"] = line.replace("@within", "").strip()
        elif line.startswith("@module"):
            # @module name
            result["module"] = line.replace("@module", "").strip()
        elif not line.startswith("@"):
            current_desc.append(line)
    
    result["description"] = " ".join(current_desc).strip()
    return result

def parse_lua_file(file_path: Path) -> dict:
    """Parse a Lua file and extract class/method information."""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Extract module name
    module_match = re.search(r"^---\s*@module\s+(\w+)", content, re.MULTILINE)
    module_name = module_match.group(1) if module_match else file_path.stem
    
    class_data = {
        "name": module_name,
        "description": "",
        "methods": [],
    }
    
    # Find all function definitions with their preceding comments
    # Pattern: --- comments --- function Class:method(...) or function Class.method(...)
    pattern = r"(---.*?)(?=function\s+(\w+)[:.](\w+)\s*\()"
    
    for match in re.finditer(pattern, content, re.DOTALL):
        comment_block = match.group(1)
        class_name = match.group(2)
        method_name = match.group(3)
        
        # Parse the comment
        doc = parse_ldoc_comment(comment_block)
        
        # Find the function signature
        func_start = match.end()
        func_match = re.search(r"function\s+\w+[:.]\w+\s*\(([^)]*)\)", content[func_start:func_start+200])
        signature = f"{class_name}:{method_name}({func_match.group(1) if func_match else ''})"
        
        method = {
            "name": method_name,
            "class": class_name,
            "description": doc["description"],
            "signature": signature,
            "parameters": doc["parameters"],
            "returns": doc["returns"],
            "category": doc.get("category"),
        }
        
        class_data["methods"].append(method)
    
    # Also check for module-level description
    module_desc_match = re.search(r"^---\s*([^@\n]+)", content, re.MULTILINE)
    if module_desc_match:
        class_data["description"] = module_desc_match.group(1).strip()
    
    return class_data

def main():
    """Parse all ReaWrap Lua files."""
    reawrap_lua_dir = Path(__file__).parent.parent.parent / "ReaWrap" / "lua"
    
    if not reawrap_lua_dir.exists():
        print(f"Error: ReaWrap lua directory not found: {reawrap_lua_dir}", file=sys.stderr)
        sys.exit(1)
    
    print(f"Parsing ReaWrap Lua files from {reawrap_lua_dir}...", file=sys.stderr)
    
    classes = []
    
    # Find all .lua files
    for lua_file in reawrap_lua_dir.rglob("*.lua"):
        if lua_file.name == "constants.lua":  # Skip large constants file
            continue
        
        try:
            class_data = parse_lua_file(lua_file)
            if class_data["methods"] or class_data["description"]:
                classes.append(class_data)
                print(f"  Parsed {class_data['name']}: {len(class_data['methods'])} methods", file=sys.stderr)
        except Exception as e:
            print(f"  Warning: Error parsing {lua_file}: {e}", file=sys.stderr)
    
    data = {
        "classes": classes,
        "scraped_at": datetime.now().isoformat(),
        "total_classes": len(classes),
        "total_methods": sum(len(c["methods"]) for c in classes),
    }
    
    output_path = Path(__file__).parent.parent / "data" / "reawrap-api.json"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_path, "w") as f:
        json.dump(data, f, indent=2)
    
    print(f"\nSaved ReaWrap API data to {output_path}", file=sys.stderr)
    print(f"Total: {len(classes)} classes, {data['total_methods']} methods", file=sys.stderr)

if __name__ == "__main__":
    main()

