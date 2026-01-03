## Conversion Design

Every skill gem come in three tiers, Lesser, Standard, and Greater, with Vaal Skill Gems being a special case. The cost and effects of a skill gem scale with the proficiency bonus, PRO, of the character.

Names:
  * If the name of the skill matches a spell that already exists in D&D, change it to something appropriate. These have been changed so far:
    * Fireball -> Firestrike

Attack Skills:
  * The mana cost of attack skills scales with its tier:
    * Lesser skill gems: 1
    * Standard skill gems: 2
    * Greater skill gems: 3
  * Using an attack skill gem takes an attack. Use this phrasing when describing the skill: "When making a [Type/Damage Requirement] attack..."
  * Damage is based on tier, and the default progression is: 1d4 → 1d6 → 1d8
  * Standard tier should enhance damage without overshadowing the base attack

Spell Skills:
  * The mana cost of spell skills scales with the tier and your proficiency bonus:
    * Lesser skill gems: PRO/2, rounded up
    * Standard skill gems: PRO
    * Greater skill gems: PRO + 3
  * Using a spell skill gem takes an action. Use this phrasing when describing the skill: "As an action,..."
  * Damage is based on tier, but scales with proficiency bonus: PRO×(damage dice)
  * Default damage dice progression across tiers: 1d4 → 1d6 → 1d8

Channeling Skills:
  * Channeling Skills are either spell skills or attack skills that come in two varieties: Charging or Sustain
  * Channeling Skills have an upfront cost, and a cost to amplify:
    * Attack Skill: 1/2/3 mana upfront, 1 mana to amplify
    * Spell Skill: [PRO/2]/PRO/[PRO+3], half the upfront cost, rounded down, to amplify
  * You are considered Channeling until the skill ends, and Channeling requires concentration.
  * Charging Channeling:
    * Each use of the skill gives it a charge, up to the maximum charges equal to your proficiency bonus.
    * You may use an action and pay the amplify cost to increase charges, or release the skill to end it.
    * When the skill ends, for any reason, the charges are all consumed for some large effect.
  * Sustain Channeling:
    * Each use of the skill gives it a charge, up to the maximum charges equal to your proficiency bonus.
    * The skill has an ongoing effect dependent on the number of charges
    * You can pay the costs necessary to amplify the skill and increase its charges, or you can maintain the skill for free, up to a specific duration (such as 4 rounds) dependent on the skill
    * When the skill ends, all charges are lost without effect.

Auras:
  * Aura skills both cost and reserve mana dependent on teir and proficiency bonus:
    * Lesser skill gems: PRO + 1
    * Standard skill gems: 2×PRO
    * Greater skill gems: 3×PRO
  * To activate an aura, you must spend 1 minute casting the skill. Use this phrasing when describing the skill: "After concentrating for 1 minute,..

Saving Throws:
  * AoE skills, or skills that apply a persistent effect should require a saving throw.
  * Use the standardized phrasing: "DC equal to your spellcasting DC"
  * This automatically handles different casting abilities across classes and covers both spell attacks and weapon attacks that require saves.

Ailments:
  * Any modifiers to ailment chance should be changed to ailment threshold bonuses.
  * Use the phrasing: "+X to [Ailment] Threshold"
  * Ailment threshold bonuses scale gradually across tiers:
    * Lesser skill gems: +4 to ailment threshold
    * Standard skill gems: +5 to ailment threshold
    * Greater skill gems: +6 to ailment threshold
  * Skills can increase or decrease ailment effects (duration, damage per round, etc.).

Damage:
  * Use the multiplication symbol (×) not asterisk (*) when writing damage formulas
  * Standard tier should enhance damage without overshadowing the base attack

Duration:
  * Duration is generally either 4 rounds or 1 minute (10 rounds), but this can be varied dependent on the skill gem.

Range/Area:
  * A skill should only have an area of effect if the PoE skill has substantial AoE.
  * The Range and Area only increase with tier if the PoE skill gem has increasing area.

Support Gems:
  * Support Gems come in one tier, but their effect scales with PRO and both the effect and cost modifier scale with the active skill tier.
  * Support gem mana cost additions are flat values:
    * When supporting a Lesser skill: +1 mana
    * When supporting a Standard skill: +2 mana
    * When supporting a Greater skill: +3 mana
  * Specific support gems may have different cost additions
  * Support gem effects scale with the tier of the supported skill. For example, Pierce Support will let a lesser projectile skill pierce one target, but will let a standard projectile skill pierce two targets.
  * The requirements, if there are any, for using a support gem are spelled in the first part of the description: "When using a melee attack skill", or "When using a projectile skill," etc.

Design Philosophy:
  * Prefer simple mechanics over complex tracking systems
  * Avoid multi-turn counting mechanics unless they are central to the skill's identity
  * Use flat bonuses or die size increase instead of percentage increases where possible
  * Don't require players to track multiple conditional states simultaneously

Greater Tier Design:
  * Focus on increased damage dice, thresholds, and ranges
  * Avoid stacking multiple bonus effects on Greater tier
  * Only add new mechanical complexity if it's the core identity of the skill
  * Greater bonuses should feel impactful but not require extensive bookkeeping

Cooldown Mechanics:
  * Avoid fractional rounds (no "1.5 rounds" or similar)
  * For powerful triggered effects, use recharge mechanics instead of cooldowns:
    * "Once you have triggered [effect], you cannot do so again until it is recharged. At the start of your turn, roll 1d6. On a 6, the ability is recharged."

General Standards:
  * Avoid fractional or percentile numbers if possible. Ideally, the player want need to perform math any more complicated than simple multiplication, such as 2×.

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