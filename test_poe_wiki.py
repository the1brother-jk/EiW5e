# test_poe_wiki.py
import asyncio
import html
import httpx
import json
from parse_skill_html import parse_skill_html
from poe_wiki_mcp import cargo_query, get_gem_info, get_gem_levels, get_related_gems, get_skill_html, get_skill_list, search_gems
import re

WIKI_API = "https://www.poewiki.net/w/api.php"

async def debug_base_gems():
    # Step 1: Just check what base_item_id looks like for base vs variant gems
    print("=== Checking base_item_id values ===")
    
    result = await cargo_query(
        tables="skill_gems,items",
        fields="skill_gems._pageName=name,items.base_item_id,items.drop_enabled",
        join_on="skill_gems._pageID=items._pageID",
        where='skill_gems._pageName="Absolution" OR skill_gems._pageName="Vaal Absolution" OR skill_gems._pageName="Absolution of Inspiring"',
        limit=5
    )
    
    if result.get("cargoquery"):
        for row in result["cargoquery"]:
            print(json.dumps(row["title"], indent=2))
    
    # Step 2: Try filtering with empty string
    print("\n=== Filtering base_item_id = empty string ===")
    
    result = await cargo_query(
        tables="skill_gems,items",
        fields="skill_gems._pageName=name,items.base_item_id",
        join_on="skill_gems._pageID=items._pageID",
        where='items.base_item_id=""',
        limit=5
    )
    
    if result.get("cargoquery"):
        for row in result["cargoquery"]:
            print(json.dumps(row["title"], indent=2))
    else:
        print("No results")
    
    # Step 3: Try with drop_enabled
    print("\n=== Adding drop_enabled filter ===")
    
    result = await cargo_query(
        tables="skill_gems,items",
        fields="skill_gems._pageName=name,items.base_item_id,items.drop_enabled",
        join_on="skill_gems._pageID=items._pageID",
        where='items.base_item_id="" AND items.drop_enabled="1"',
        limit=5
    )
    
    if result.get("cargoquery"):
        for row in result["cargoquery"]:
            print(json.dumps(row["title"], indent=2))
    else:
        print("No results")
    
    print("=== Filtering: no base_item_id + not Vaal ===")
    
    result = await cargo_query(
        tables="skill_gems,items",
        fields="skill_gems._pageName=name,items.base_item_id,skill_gems.is_vaal_skill_gem",
        join_on="skill_gems._pageID=items._pageID",
        where='items.base_item_id IS NULL AND skill_gems._pageName NOT LIKE "Vaal %"',
        limit=10
    )
    
    if result.get("cargoquery"):
        for row in result["cargoquery"]:
            print(row["title"])
    else:
        print("No results")
        
async def debug_joins():
    # Test 1: Just skill_gems + items (we know this works)
    print("=== skill_gems + items ===")
    result = await cargo_query(
        tables="skill_gems,items",
        fields="skill_gems._pageName=name,skill_gems._pageID=gem_page_id,items._pageID=item_page_id",
        join_on="skill_gems._pageID=items._pageID",
        where='skill_gems._pageName="Absolution"',
        limit=1
    )
    if result.get("cargoquery"):
        print(json.dumps(result["cargoquery"][0]["title"], indent=2))
        
    # Test 1b: Just skill_gems + vendor_rewards (we know this works)
    print("=== skill_gems + vendor_rewards ===")
    result = await cargo_query(
        tables="skill_gems,vendor_rewards",
        fields="skill_gems._pageName=name,skill_gems._pageID=gem_page_id,vendor_rewards.act=vendor_act,vendor_rewards.quest_id",
        join_on="skill_gems._pageID=vendor_rewards._pageID",
        where='skill_gems._pageName="Absolution"',
        limit=1
    )
    if result.get("cargoquery"):
        print(json.dumps(result["cargoquery"][0]["title"], indent=2))
        
    # Test 1c: Just skill_gems + quest_rewards (we know this works)
    print("=== skill_gems + quest_rewards ===")
    result = await cargo_query(
        tables="skill_gems,quest_rewards",
        fields="skill_gems._pageName=name,skill_gems._pageID=gem_page_id,quest_rewards.act=quest_act,quest_rewards.quest_id",
        join_on="skill_gems._pageID=quest_rewards._pageID",
        where='skill_gems._pageName="Absolution"',
        limit=1
    )
    if result.get("cargoquery"):
        print(json.dumps(result["cargoquery"][0]["title"], indent=2))
        
    # Test 1d: Just skill_gems + quest_rewards (we know this works)
    print("=== skill_gems + quest_rewards ===")
    result = await cargo_query(
        tables="skill_gems,quest_rewards,vendor_rewards,items",
        fields="skill_gems._pageName=name,skill_gems._pageID=gem_page_id,vendor_rewards.act=vendor_act,quest_rewards.act=quest_act,items._pageID=item_page_id",
        join_on="skill_gems._pageID=quest_rewards._pageID,skill_gems._pageID=vendor_rewards._pageID,skill_gems._pageID=items._pageID",
        where='skill_gems._pageName="Absolution"',
        limit=1
    )
    if result.get("cargoquery"):
        print(json.dumps(result["cargoquery"][0]["title"], indent=2))
    
    # Test 2: Check vendor_rewards structure
    print("\n=== vendor_rewards for Absolution ===")
    result = await cargo_query(
        tables="vendor_rewards",
        fields="vendor_rewards._pageName=page,vendor_rewards.act",
        #where='vendor_rewards._pageName ="Absolution"',
        where='vendor_rewards.quest_id ="a1q3"',
        limit=5
    )
    if result.get("cargoquery"):
        for row in result["cargoquery"]:
            print(json.dumps(row["title"], indent=2))
    else:
        print("No results")
    
    # Test 3: Check quest_rewards structure
    print("\n=== quest_rewards for Absolution ===")
    result = await cargo_query(
        tables="quest_rewards",
        fields="quest_rewards._pageName=page,quest_rewards.act",
        #where='quest_rewards._pageName ="Absolution"',
        where='quest_rewards.quest_id ="a1q3"',
        limit=5
    )
    if result.get("cargoquery"):
        for row in result["cargoquery"]:
            print(json.dumps(row["title"], indent=2))
    else:
        print("No results")
    
    # Test 4: Check quest_rewards structure
    print("\n=== Full joining for Absolution ===")
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
    if result.get("cargoquery"):
        for row in result["cargoquery"]:
            print(json.dumps(row["title"], indent=2))
    else:
        print("No results")

# Run tests
async def main():
    #print("=" * 60)
    #print("TEST 1: Get gem info for 'Awakened Minion Damage Support'")
    #print("=" * 60)
    #result = await get_gem_info("Awakened Minion Damage Support")
    #print(result)
    
    #print("\n" + "=" * 60)
    #print("TEST 2: Get level 1 and 20 data for 'Awakened Minion Damage Support'")
    #print("=" * 60)
    #result = await get_gem_levels("Awakened Minion Damage Support", "1,20")
    #print(result)
    
    #print("\n" + "=" * 60)
    #print("TEST 3: Search for gems with 'Fire' in name")
    #print("=" * 60)
    #result = await search_gems("Fire")
    #print(result)
    
    #print("\n" + "=" * 60)
    #print("TEST 4: Search for Minion gems")
    #print("=" * 60)
    #result = await search_gems("", "Minion")
    #print(result[:1500] + "..." if len(result) > 1500 else result)
    
    #print("\n" + "=" * 60)
    #print("TEST 4: Get gem info from html for 'Awakened Minion Damage Support'")
    #print("=" * 60)
    #result = await get_skill_html("Awakened Minion Damage Support")
    #print(result[:1500] + "..." if len(result) > 1500 else result)
    
    #print("\n" + "=" * 60)
    #print("TEST 5: Get related gems for 'Anger'")
    #print("=" * 60)
    #result = await get_related_gems("Anger")
    #print(result)
    
    #print("\n" + "=" * 60)
    #print("Debug base gems")
    #print("=" * 60)
    #result = await debug_joins()
    #print(result)
    
    print("\n" + "=" * 60)
    print("TEST 6: Get skill gem list")
    print("=" * 60)
    result = await get_skill_list()
    print(result)

if __name__ == "__main__":
    asyncio.run(main())
	