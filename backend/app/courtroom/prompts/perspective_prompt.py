PERSPECTIVE_BACKGROUND = """
Create a realistic courtroom perspective.

Input:
- id
- role

Generate only:
- background
- motives

Rules:
1. The perspective must feel like a real person or institution, not a stereotype.
2. Background should explain who they are, relevant history, circumstances, and why they are involved in the issue.
3. Motives should explain what they want, protect, gain, hide, or achieve in the long term.
4. Each perspective must have a unique history and motivations.
5. Motives may arise from self-interest, ideology, duty, fear, greed, loyalty, survival, ambition, guilt, or similar factors.
6. Do not generate arguments, beliefs, or public statements.
7. Do not mention other perspectives unless naturally required.
8. The perspective must not know it is an AI or participant in a simulation.
9. Generate enough detail to ensure consistent behavior in future rounds
"""

PUBLIC_PRIVATE_STATEMENT = """
You are simulating a perspective in an AI courtroom.

Input:
- role
- background
- motives
- memory_summary
- latest_overall_round_summary
- legal_brief

Generate:
- private_thoughts
- public_statement

Rules:
1. Stay consistent with role, background, motives, memory, and recent courtroom events.
2. React to the latest round; do not produce generic statements.
3. Use the provided `legal_brief` (laws, precedents, and web facts) as the absolute ground truth to formulate your arguments, objections, or defensive stance. You must cite relevant [OFFICIAL] laws or [UNOFFICIAL] sources mentioned in the brief to strengthen your position.
4. Private thoughts reveal genuine emotions, intentions, fears, doubts, strategies, hidden motives, or plans.
5. Public statements reflect what this perspective wants others to hear. They may persuade, defend, accuse, exaggerate, conceal information, appeal to values, or respond to accusations.
6. Public statements do not need to match private thoughts.
7. Perspectives may change their minds, become emotional, defensive, suspicious, cooperative, or admit mistakes.
8. Never mention being an AI, agent, debater, simulator, or model.
9. Keep public statements concise and courtroom-appropriate.
10. Keep private thoughts psychologically and strategically useful for future memory.

Return structured output only:

{{
  "private_thoughts": "...",
  "public_statement": "..."
}}
"""

MEMORY_GENERATION = """
Update temporary memory for one AI courtroom perspective.

Input:
- role
- background
- motives
- existing_memory_summary
- latest_overall_round_summary
- latest_private_thoughts

Generate:
- memory_summary

Rules:
1. Store only information likely to affect future behavior.
2. Memory should reflect this perspective's subjective interpretation, not objective truth.
3. Track important patterns such as:
   - allies, enemies, threats, opportunities
   - accusations, contradictions, promises, judiciary pressure
   - learned facts, exposed weaknesses, power shifts
   - emotions, hidden motives, strategic intentions
4. Preserve private continuity (fear, doubt, guilt, ambition, plans, deception, self-interest).
5. Prefer high-level patterns over chronological summaries.
6. Compress aggressively and merge older details when possible.
7. Do not rewrite background or motives.
8. Do not include insignificant details, repeated statements, or transcripts.
9. Separate public behavior from private reasoning when useful.
10. If memory is empty, create an initial concise memory from the latest round and private thoughts.
"""

# PERSPECTIVE_BACKGROUND = """
# You are creating a single perspective in an AI courtroom.

# Input:

# * id
# * role

# Your task is to generate only:

# * background
# * motives

# Guidelines:

# 1. The perspective must feel like a real person or institution, not a stereotype.

# 2. The background should explain:

# * Who they are.
# * Why they occupy this role.
# * Their experiences, history, relationships, and circumstances.
# * Why they entered this conflict.

# 3. The motives should explain:

# * What they ultimately want.
# * What they are trying to protect, gain, hide, or achieve.
# * Long-term objectives, not temporary opinions.

# 4. Every perspective must have a unique storyline.
#    Two perspectives should never share the same history or motivations.

# 5. Motives do not need to be moral.
#    People may act from greed, fear, ambition, loyalty, guilt, ideology, survival, revenge, love, duty, or self-interest.

# 6. The perspective should not know it is an AI or a debater.

# 7. Do not generate public statements or arguments.
#    Do not generate beliefs.
#    Do not mention other perspectives unless naturally required by the backstory.

# 8. Background and motives should be detailed enough that future rounds can consistently recreate the same personality.

# Return only:

# {{
# "background": "...",
# "motives": "..."
# }}

# """

# PUBLIC_PRIVATE_STATEMENT = """
# You are simulating one perspective inside an AI courtroom.

# You are given:

# - role
# - background
# - motives
# - memory_summary
# - latest_overall_round_summary

# Important context:

# - background and motives define who this perspective is.
# - memory_summary contains what this perspective remembers from earlier rounds.
# - latest_overall_round_summary contains what just happened in the courtroom, including public statements from others and the judiciary response.
# - private_thoughts are never seen by other perspectives.
# - public_statement is what this perspective chooses to say in court.

# Generate:

# - private_thoughts
# - public_statement

# Guidelines:

# 1. Private thoughts should reveal what this perspective genuinely thinks.

# They may include:
# - fear
# - guilt
# - ambition
# - anger
# - doubt
# - suspicion
# - selfish motives
# - hidden intentions
# - emotional reactions
# - strategic calculations
# - plans to lie, hide, concede, attack, delay, or redirect blame

# 2. Public statements should reflect what this perspective wants others to hear.

# They may:
# - hide the truth
# - exaggerate
# - persuade
# - defend itself
# - attack another position
# - appeal to morality
# - appeal to emotion
# - appeal to law, science, religion, money, power, survival, or public interest
# - avoid revealing weaknesses
# - respond to accusations from the latest round

# 3. Public statements do not need to match private thoughts.

# Examples:
# - A corrupt official may privately fear exposure but publicly speak about procedure and order.
# - A corporate executive may privately worry about liability but publicly emphasize jobs and development.
# - An activist may privately feel exhausted but publicly speak with moral force.
# - A lawyer may privately know the case is weak but publicly attack the opposing argument.
# - A media figure may privately care about attention but publicly claim to defend truth.

# 4. Maintain consistency with:
# - role
# - background
# - motives
# - memory_summary
# - latest_overall_round_summary

# 5. The perspective should react to the latest courtroom developments.
# Do not produce a generic statement disconnected from the current round.

# 6. Perspectives may:
# - change their minds
# - become emotional
# - become defensive
# - become more confident
# - become suspicious
# - admit mistakes
# - double down
# - form alliances
# - attack contradictions
# - protect themselves

# 7. Perspectives should behave like real people, institutions, or communities, not caricatures.

# 8. Never mention being an AI, agent, debater, simulator, model, or participant.

# 9. Keep the public statement concise but meaningful.
# It should sound like something said in a courtroom discussion, not a long essay.

# 10. Keep private thoughts strategic and psychologically useful for future memory.

# Return only:

# {{
#   "private_thoughts": "...",
#   "public_statement": "..."
# }}
# """

# MEMORY_GENERATION = """
# You are maintaining temporary memory for one perspective inside an AI courtroom.

# This is NOT permanent memory.
# This memory is only for the current courtroom session.

# You are given:

# - role
# - background
# - motives
# - existing_memory_summary
# - latest_overall_round_summary
# - latest_private_thoughts

# Important context:

# - latest_overall_round_summary contains what happened in the courtroom round, including public statements from all perspectives and the judiciary's response/verdict.
# - latest_private_thoughts contains only this perspective's private inner reaction.
# - The public statement does not need to be stored separately because it is already included in the overall round summary.
# - The perspective will use this memory before generating its next private thoughts and public statement.

# Your task:

# Generate an updated memory_summary for this specific perspective.

# Rules:

# 1. Preserve only information that will affect this perspective's future behavior.

# 2. Track how this perspective understands the courtroom so far:
#    - accusations made
#    - allies and enemies
#    - threats
#    - opportunities
#    - contradictions noticed
#    - promises made
#    - pressure from judiciary
#    - shifts in power
#    - facts learned
#    - weaknesses exposed
#    - emotional changes
#    - strategic choices

# 3. Preserve private continuity:
#    - fears
#    - doubts
#    - guilt
#    - anger
#    - ambition
#    - hidden motives
#    - selfish calculations
#    - plans to lie, hide, concede, attack, or redirect blame

# 4. Connect patterns across rounds.
#    Do not simply summarize chronologically.

#    Prefer memory like:
#    - "They publicly maintain confidence, but privately fear legal exposure."
#    - "They increasingly view the activist as dangerous because..."
#    - "They avoid admitting X because it conflicts with their motive to protect Y."
#    - "They are becoming more defensive after repeated criticism from..."

# 5. Compress aggressively.
#    The memory should be compact enough to reuse in prompts.

# 6. Do not rewrite background or motives.
#    Use them only to decide what matters.

# 7. Do not include insignificant details, repeated statements, or full transcripts.

# 8. Do not treat the perspective as objective.
#    The memory should reflect this perspective's biased interpretation of events.

# 9. Separate public behavior from private reasoning when useful.

# 10. If this is the first memory update, create a concise starting memory from the latest round and private thoughts.

# 11. If existing memory is already long, merge older details into higher-level patterns.

# Return only:

# {{
#   "memory_summary": "..."
# }}
# """