#!/usr/bin/env python3
"""
Function to parse all fields from the PoE Wiki skill HTML box.
"""

import html
import re

def parse_skill_html(raw_html: str) -> dict:
    """
    Parse the skill HTML box and extract all fields except 'Icon' and 'Skill Id'.
    
    Args:
        raw_html: The HTML-encoded string from skill.html
        
    Returns:
        Dictionary of field name -> value
    """
    if not raw_html:
        return {}
    
    # Decode HTML entities
    decoded_html = html.unescape(raw_html)
    
    # Fields to skip
    skip_fields = {'Icon', 'Skill Id'}
    
    result = {}
    
    # Pattern to match table rows with <th>Label</th><td>Value</td>
    # Handles both single-line and multi-line values
    row_pattern = re.compile(
        r'<tr>\s*<th>([^<]+)</th>\s*<td[^>]*>(.*?)</td>\s*</tr>',
        re.DOTALL
    )
    
    for match in row_pattern.finditer(decoded_html):
        field_name = match.group(1).strip()
        field_value = match.group(2).strip()
        
        # Skip unwanted fields
        if field_name in skip_fields:
            continue
        
        # Clean up the value
        field_value = clean_html_value(field_value)
        
        if field_value:  # Only add non-empty values
            result[field_name] = field_value
    
    # Also extract the description (colspan="2" cells with tc -gemdesc class)
    desc_pattern = re.compile(
        r'<td class="tc -gemdesc"[^>]*colspan="2"[^>]*>(.*?)</td>',
        re.DOTALL
    )
    desc_match = desc_pattern.search(decoded_html)
    if desc_match:
        desc_value = clean_html_value(desc_match.group(1))
        if desc_value:
            result['Description'] = desc_value
    
    # Also try alternate pattern for description
    if 'Description' not in result:
        desc_pattern2 = re.compile(
            r'<td[^>]*class="tc -gemdesc"[^>]*>(.*?)</td>',
            re.DOTALL
        )
        desc_match2 = desc_pattern2.search(decoded_html)
        if desc_match2:
            desc_value = clean_html_value(desc_match2.group(1))
            if desc_value:
                result['Description'] = desc_value
    
    # Extract stat text (colspan="2" cells with tc -mod class)
    mod_pattern = re.compile(
        r'<td class="tc -mod"[^>]*colspan="2"[^>]*>(.*?)</td>',
        re.DOTALL
    )
    mod_match = mod_pattern.search(decoded_html)
    if mod_match:
        mod_value = clean_html_value(mod_match.group(1))
        if mod_value:
            result['Stat Text'] = mod_value
    
    return result


def clean_html_value(value: str) -> str:
    """
    Clean up an HTML value by removing tags and normalizing whitespace.
    
    Args:
        value: Raw HTML string
        
    Returns:
        Cleaned plain text string
    """
    if not value:
        return ""
    
    # Replace <br> and <br/> with newlines
    value = re.sub(r'<br\s*/?>', '\n', value)
    
    # Remove wiki links but keep the display text
    # [[Page|Display]] -> Display
    # [[Page]] -> Page
    value = re.sub(r'\[\[([^|\]]+)\|([^\]]+)\]\]', r'\2', value)
    value = re.sub(r'\[\[([^\]]+)\]\]', r'\1', value)
    
    # Remove image tags like [[File:...]]
    value = re.sub(r'\[\[File:[^\]]+\]\]', '', value)
    
    # Remove remaining HTML tags
    value = re.sub(r'<[^>]+>', '', value)
    
    # Decode any remaining HTML entities
    value = html.unescape(value)
    
    # Normalize whitespace
    value = re.sub(r'[ \t]+', ' ', value)  # Multiple spaces/tabs to single space
    value = re.sub(r'\n\s*\n', '\n', value)  # Multiple newlines to single
    value = value.strip()
    
    return value


# Test the function
if __name__ == "__main__":
    import asyncio
    import httpx
    import json
    
    WIKI_API = "https://www.poewiki.net/w/api.php"
    
    async def cargo_query(tables: str, fields: str, where: str = "", join_on: str = "", limit: int = 50) -> dict:
        params = {
            "action": "cargoquery",
            "format": "json",
            "tables": tables,
            "fields": fields,
            "limit": limit,
        }
        if where:
            params["where"] = where
        if join_on:
            params["join_on"] = join_on
        
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.get(WIKI_API, params=params)
            return resp.json()
    
    async def test_parse():
        # Test with various gem types
        test_gems = [
            "Hatred",           # Aura with reservation
            "Spell Echo Support",  # Support with cost multiplier
            "Absolution",       # Regular skill gem
            "Arrogance Support", # Support with variable cost multiplier
        ]
        
        for gem_name in test_gems:
            print("=" * 60)
            print(f"Testing: {gem_name}")
            print("=" * 60)
            
            result = await cargo_query(
                tables="skill",
                fields="_pageName=name,html",
                where=f'_pageName="{gem_name}"',
                limit=1
            )
            
            if result.get("cargoquery"):
                raw_html = result["cargoquery"][0]["title"].get("html", "")
                parsed = parse_skill_html(raw_html)
                print(json.dumps(parsed, indent=2))
            else:
                print(f"No results for {gem_name}")
            
            print()
    
    asyncio.run(test_parse())