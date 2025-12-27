# poe_wiki_mcp.py
import httpx
from mcp.server.fastmcp import FastMCP
from urllib.parse import urlencode
import json

mcp = FastMCP("poe-wiki")

WIKI_API = "https://www.poewiki.net/w/api.php"

async def cargo_query(tables: str, fields: str, where: str = "", join_on: str = "", limit: int = 50) -> dict:
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
    
    async with httpx.AsyncClient() as client:
        resp = await client.get(WIKI_API, params=params)
        return resp.json()

@mcp.tool()
async def get_gem_info(gem_name: str) -> str:
    """
    Get skill gem info from PoE Wiki.
    Returns: gem tags, cast time, crit chance, damage effectiveness, description, and stat text.
    """
    # Query skill_gems + skill tables joined
    result = await cargo_query(
        tables="skill_gems,skill,skill_levels",
        fields="skill_gems._pageName=name,skill_gems.gem_tags,skill.cast_time,skill.description,skill.stat_text,skill.radius,"
               "skill_levels.damage_effectiveness,skill_levels.critical_strike_chance,"
               "skill_levels.level_requirement,skill_levels.strength_requirement,skill_levels.dexterity_requirement,skill_levels.intelligence_requirement",
        where=f'skill_gems._pageName="{gem_name}"',
        join_on="skill_gems._pageID=skill._pageID,skill_gems._pageID=skill_levels._pageID"
    )
    
    if not result.get("cargoquery"):
        return f"No gem found with name '{gem_name}'"
    
    gems = [row["title"] for row in result["cargoquery"]]
    return json.dumps(gems, indent=2)

@mcp.tool()
async def get_gem_levels(gem_name: str, levels: str = "1,20") -> str:
    """
    Get skill gem level progression data.
    
    Args:
        gem_name: Name of the gem (e.g., "Absolution")
        levels: Comma-separated levels to fetch (e.g., "1,20" or "1,10,20")
    """
    level_list = [l.strip() for l in levels.split(",")]
    level_condition = " OR ".join([f"skill_levels.level={l}" for l in level_list])
    
    result = await cargo_query(
        tables="skill_gems,skill_levels",
        fields="skill_gems._pageName=name,skill_levels.level,skill_levels.cost_types,"
               "skill_levels.damage_effectiveness,skill_levels.cost_amounts,"
               "skill_levels.stat_text,skill_levels.experience",
        where=f'skill_gems._pageName="{gem_name}" AND ({level_condition})',
        join_on="skill_gems._pageID=skill_levels._pageID",
        limit=100
    )
    
    if not result.get("cargoquery"):
        return f"No level data found for '{gem_name}'"
    
    levels_data = [row["title"] for row in result["cargoquery"]]
    return json.dumps(levels_data, indent=2)

@mcp.tool()
async def search_gems(query: str, tag_filter: str = "") -> str:
    """
    Search for skill gems by name pattern or tag.
    """
    
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

if __name__ == "__main__":
    mcp.run(transport='stdio')
    