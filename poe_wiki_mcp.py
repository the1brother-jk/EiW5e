# poe_wiki_mcp.py
import html
import httpx
import json
from mcp.server.fastmcp import FastMCP
from parse_skill_html import parse_skill_html
import re
from urllib.parse import urlencode

mcp = FastMCP("poe-wiki")

WIKI_API = "https://www.poewiki.net/w/api.php"

async def cargo_query(tables: str, fields: str, where: str = "", group_by: str = "", join_on: str = "", order_by: str = "", limit: int = 50) -> dict:
    """Execute a Cargo query against the PoE wiki."""
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
    if order_by:
        params["order_by"] = order_by
    if group_by:
        params["group_by"] = group_by
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(WIKI_API, params=params)
        return resp.json()

@mcp.tool()
async def get_gem_info(gem_name: str) -> str:
    """
    Get skill gem info from PoE Wiki.
    Returns: gem tags, cast time, radius, crit chance, damage effectiveness, description, cost, and stat text at level 1.
    """
    # Query skill_gems + skill tables joined
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

@mcp.tool()
async def get_gem_levels(gem_name: str, levels: str = "1,20") -> str:
    """
    Get skill gem level progression data.
    
    Args:
        gem_name: Name of the gem (e.g., "Absolution")
        levels: Comma-separated levels to fetch (e.g., "1,20" or "1,10,20")
    Returns: gem tags, cast time, radius, crit chance, damage effectiveness, description, cost, and stat text.
    """
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
    
    if not result.get("cargoquery"):
        return f"No level data found for '{gem_name}'"
    
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
    
    return json.dumps(levels_data, indent=2)

@mcp.tool()
async def search_gems(query: str, tag_filter: str = "") -> str:
    """
    Search for skill gems by name pattern or tag.
    """
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

@mcp.tool()
async def get_related_gems(base_gem_name: str) -> str:
    """
    Find all variants of a gem (Vaal, Transfigured, etc.)
    
    Args:
        base_gem_name: Base gem name (e.g., "Absolution")
    """
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

@mcp.tool()
async def get_skill_html(gem_name: str) -> str:
    """
    Get skill gem info from PoE Wiki.
    Returns: gem tags, and any info from the embedded html. This usually includes name, requirements, cost or reservation, base attack or cast numbers, crit chance, description, and stat text.
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

@mcp.tool()
async def get_skill_list() -> str:
    """
    Get skill gem list from PoE Wiki, with first act appearence.
    """
    result = await cargo_query(
        tables="skill_gems,items,vendor_rewards,quest_rewards",
        fields="skill_gems._pageName=name,MIN(vendor_rewards.act)=vendor_act,MIN(quest_rewards.act)=quest_act",
        group_by="name",
        order_by="vendor_act,quest_act,name",
        join_on="skill_gems._pageID=quest_rewards._pageID,skill_gems._pageID=vendor_rewards._pageID,skill_gems._pageID=items._pageID",
        where='items.base_item_id IS NULL '
              'AND (skill_gems.is_vaal_skill_gem = "0" OR skill_gems.is_vaal_skill_gem IS NULL) '
              'AND (skill_gems.is_awakened_support_gem = "0" OR skill_gems.is_awakened_support_gem IS NULL)',
        limit=10,
    )
    
    if not result.get("cargoquery"):
        return f"No gems found matching query='{query}' tag='{tag_filter}'"
    
    gems = []
    for row in result["cargoquery"]:
        data = row["title"]
        
        # Get the minimum act, defaulting to 6 if both are None
        vendor_act = data.get("vendor_act")
        quest_act = data.get("quest_act")
        
        # Convert to int if present, filter out None values, find min
        acts = []
        if vendor_act:
            acts.append(int(vendor_act))
        if quest_act:
            acts.append(int(quest_act))
        
        act = min(acts) if acts else 6
        
        data["act"] = act
        
        # Clean up the intermediate fields
        if "vendor_act" in data:
            del data["vendor_act"]
        if "quest_act" in data:
            del data["quest_act"]
        
        gems.append(data)
    
    return json.dumps(gems, indent=2)

if __name__ == "__main__":
    mcp.run(transport='stdio')
    