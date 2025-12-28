## Conversion Design

Every skill gem come in three tiers, Lesser, Standard, and Greater, with Vaal Skill Gems being a special case. The cost and effects of a skill gem scale with the proficiency bonus, PRO, of the character.

Mana Cost:
  * This scales based on the tier of the skill, rounding up:
    * Lesser skill gems: 1/2 * PRO
    * Standard skill gems: PRO
    * Greater skill gems: PRO + 3
  * If the skill is a channeling skill, it scales differently:
    * Lesser skill gems: 1/3 * PRO
    * Standard skill gems: 1/2 * PRO
    * Greater skill gems: 1/2 * PRO + 2
  * If the skill is an aura, it both uses and reserves a set of mana:
    * Lesser skill gems: PRO + 1
    * Standard skill gems: 2 * PRO
    * Greater skill gems: 3 * PRO

Action Cost:
  * For attack skills, using the skill gem takes an attack: "When making a [?] attack..."
  * For spell skills, using the skill gem takes an action: "As an action,..."
  * If the skill is a channeling skill, then it can also be used as a bonus action: "If you channeled [skill] as an action, you may also channel it as a bonus action."
  * For aura skills, the casting time is 1 minute. "After concentrating for 1 minute,...

Saving Throws:
  * AoE skills, or skills that apply a persistent effect should require a saving throw. The DC of the saving throw is dependent on whether it originates from a weapon attack or a spell. If it is from a weapon attack, the DC is equal to 8 + PRO + ability modifier of the ability used to make the attack. If it is from a spell, the DC is equal to the spell DC of the caster. If the caster has no spell DC, it is equal to 8 + PRO + ability modifier of the ability they chose to use with skill gems.

Ailments:
  * Any modifiers to ailment chance should be changed to ailment threshold: "+1 to ignite threshold"
  * Skills can increase or decrease ailment effects.
	
Damage:
  * At every tier, damage scaled based on proficiency bonus: ex. PRO*(1d4)
  * As the gem increases in tier, generally the damage dice increase in size: 1d6 -> 1d8 -> 1d10

Duration:
  * Duration is generally either 4 rounds or 1 minute (10 rounds), but this can be varied dependent on the skill gem.

Range/Area:
  * A skill should only have an area of effect if the PoE skill has substantial AoE.
  * The Range and Area increase with tier if the PoE skill gem has increasing area.

Support Gems:
  * Support Gems come in one tier, but their effect scales with PRO and both the effect and cost modifier scale with the active skill tier. For example, Pierce Support will add +1 mana to the cost of a lesser projectile skill and let it pierce one target, but will add +2 mana to the cost of a standard projectile skill and let it pierce two targets.
  * The requirements, if there are any, for using a support gem are spelled in the first part of the description: "When using a melee attack skill", or "When using a projectile skill," etc.

Here is the format for writing the skill gems:

### {Skill Name}
*{List of gem tags}*

Casting Time: {Action Cost}
Range: {Range}
{Area: If applicable}
Mana Cost: {Mana Cost}

{Physical description of the gem}

**Lesser**: {Action Cost}, you may spend {Mana Cost} to use {Skill Name}. {Skill Description}
**Standard**: ...
**Greater**: ...