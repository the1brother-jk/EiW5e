# test_poe_wiki.py
import asyncio
import html
import httpx
import json
from parse_skill_html import parse_skill_html
import re

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
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(WIKI_API, params=params)
        return resp.json()

async def get_gem_info(gem_name: str) -> str:
    result = await cargo_query(
        tables="skill_gems,skill,skill_levels",
        fields="skill_gems._pageName=name,skill_gems.gem_tags,skill.cast_time,skill.description,skill.stat_text,skill.radius,skill.html,"
               "skill_levels.damage_effectiveness,skill_levels.critical_strike_chance,skill_levels.cost_amounts,"
               "skill_levels.level_requirement,skill_levels.strength_requirement,skill_levels.dexterity_requirement,skill_levels.intelligence_requirement",
        where=f'skill_gems._pageName="{gem_name}" AND skill_levels.level=1',
        join_on="skill_gems._pageID=skill._pageID,skill_gems._pageID=skill_levels._pageID"
    )
    
    if not result.get("cargoquery"):
        return f"No gem found with name '{gem_name}'"
    
    gems = []
    for row in result["cargoquery"]:
        data = row["title"]
        raw_html = data.get("html", "")
        
        decoded_html = html.unescape(raw_html)
        
        # Extract reservation
        res_match = re.search(r'<th>Reservation</th><td[^>]*>([^<]+)</td>', decoded_html)
        if res_match:
            data["reservation"] = res_match.group(1)
        
        # Extract cost multiplier
        mult_match = re.search(r'<th>Cost and Reservation Multiplier</th><td[^>]*>([^<]+)</td>', decoded_html)
        if mult_match:
            data["cost_multiplier"] = mult_match.group(1)
        
        # Remove the bulky html field from output
        del data["html"]
        gems.append(data)
    
    return json.dumps(gems, indent=2)

async def get_gem_levels(gem_name: str, levels: str = "1,20") -> str:
    level_list = [l.strip() for l in levels.split(",")]
    level_condition = " OR ".join([f"skill_levels.level={l}" for l in level_list])
    
    result = await cargo_query(
        tables="skill_gems,skill,skill_levels",
        fields="skill_gems._pageName=name,skill_gems.gem_tags,skill.cast_time,skill.description,skill.stat_text,skill.radius,skill.html,"
               "skill_levels.damage_effectiveness,skill_levels.critical_strike_chance,skill_levels.cost_amounts,"
               "skill_levels.level_requirement,skill_levels.strength_requirement,skill_levels.dexterity_requirement,skill_levels.intelligence_requirement",
        where=f'skill_gems._pageName="{gem_name}" AND ({level_condition})',
        join_on="skill_gems._pageID=skill._pageID,skill_gems._pageID=skill_levels._pageID",
        limit=100
    )
    
    levels_data = []
    for row in result["cargoquery"]:
        data = row["title"]
        raw_html = data.get("html", "")
        
        decoded_html = html.unescape(raw_html)
        
        # Extract reservation
        res_match = re.search(r'<th>Reservation</th><td[^>]*>([^<]+)</td>', decoded_html)
        if res_match:
            data["reservation"] = res_match.group(1)
        
        # Extract cost multiplier
        mult_match = re.search(r'<th>Cost and Reservation Multiplier</th><td[^>]*>([^<]+)</td>', decoded_html)
        if mult_match:
            data["cost_multiplier"] = mult_match.group(1)
        
        # Remove the bulky html field from output
        del data["html"]
        levels_data.append(data)
    
    if not result.get("cargoquery"):
        return f"No level data found for '{gem_name}'"
    
    return json.dumps(levels_data, indent=2)

async def search_gems(query: str, tag_filter: str = "") -> str:
    """Search for skill gems by name pattern or tag."""
    where_clauses = []
    
    if query:
        where_clauses.append(f'skill_gems._pageName LIKE "%{query}%"')
    if tag_filter:
        where_clauses.append(f'skill_gems.gem_tags HOLDS "{tag_filter}"')
    
    # Need at least one filter
    if not where_clauses:
        return "Please provide a query or tag_filter"
    
    where_clause = " AND ".join(where_clauses)
    
    result = await cargo_query(
        tables="skill_gems",
        fields="skill_gems._pageName=name,skill_gems.gem_tags",
        where=where_clause,
        limit=20
    )
    
    if not result.get("cargoquery"):
        return f"No gems found matching query='{query}' tag='{tag_filter}'"
    
    gems = [row["title"] for row in result["cargoquery"]]
    return json.dumps(gems, indent=2)

async def get_related_gems(base_gem_name: str) -> str:
    """Find all variants of a gem (Vaal, Transfigured, etc.)"""
    result = await cargo_query(
        tables="skill_gems,skill",
        fields="skill_gems._pageName=name,skill_gems.gem_tags,skill.description",
        where=f'skill_gems._pageName LIKE "%{base_gem_name}%"',
        join_on="skill_gems._pageID=skill._pageID",
        limit=20
    )
    
    if not result.get("cargoquery"):
        return f"No gems found related to '{base_gem_name}'"
    
    gems = [row["title"] for row in result["cargoquery"]]
    return json.dumps(gems, indent=2)

async def get_skill_html(gem_name: str) -> str:
    """
    Get skill gem info from PoE Wiki.
    Returns: gem tags, cast time, crit chance, damage effectiveness, description, and stat text.
    """
    # Query skill_gems + skill tables joined
    result = await cargo_query(
        tables="skill_gems,skill",
        fields="skill_gems._pageName=name,skill_gems.gem_tags,skill.html",
        where=f'skill_gems._pageName="{gem_name}"',
        join_on="skill_gems._pageID=skill._pageID"
    )
    
    if not result.get("cargoquery"):
        return f"No gem found with name '{gem_name}'"
    
    gems = []
    for row in result["cargoquery"]:
        data = row["title"]
        raw_html = data.get("html", "")
        
        parsed_fields = parse_skill_html(data.get("html", ""))
        data.update(parsed_fields)
        
        # Remove the bulky html field from output
        del data["html"]
        gems.append(data)
    
    return json.dumps(gems, indent=2)

# Run tests
async def main():
    print("=" * 60)
    print("TEST 1: Get gem info for 'Awakened Minion Damage Support'")
    print("=" * 60)
    result = await get_gem_info("Awakened Minion Damage Support")
    print(result)
    
    print("\n" + "=" * 60)
    print("TEST 2: Get level 1 and 20 data for 'Awakened Minion Damage Support'")
    print("=" * 60)
    result = await get_gem_levels("Awakened Minion Damage Support", "1,20")
    print(result)
    
    print("\n" + "=" * 60)
    print("TEST 3: Search for gems with 'Fire' in name")
    print("=" * 60)
    result = await search_gems("Fire")
    print(result)
    
    #print("\n" + "=" * 60)
    #print("TEST 4: Search for Minion gems")
    #print("=" * 60)
    #result = await search_gems("", "Minion")
    #print(result[:1500] + "..." if len(result) > 1500 else result)
    
    print("\n" + "=" * 60)
    print("TEST 4: Get gem info from html for 'Awakened Minion Damage Support'")
    print("=" * 60)
    result = await get_skill_html("Awakened Minion Damage Support")
    print(result[:1500] + "..." if len(result) > 1500 else result)
    
    print("\n" + "=" * 60)
    print("TEST 5: Get related gems for 'Anger'")
    print("=" * 60)
    result = await get_related_gems("Anger")
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
	