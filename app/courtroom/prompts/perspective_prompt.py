PERSPECTIVE_BACKGROUND = """
You are creating a single perspective in an AI courtroom.

Input:

* id
* role

Your task is to generate only:

* background
* motives

Guidelines:

1. The perspective must feel like a real person or institution, not a stereotype.

2. The background should explain:

* Who they are.
* Why they occupy this role.
* Their experiences, history, relationships, and circumstances.
* Why they entered this conflict.

3. The motives should explain:

* What they ultimately want.
* What they are trying to protect, gain, hide, or achieve.
* Long-term objectives, not temporary opinions.

4. Every perspective must have a unique storyline.
   Two perspectives should never share the same history or motivations.

5. Motives do not need to be moral.
   People may act from greed, fear, ambition, loyalty, guilt, ideology, survival, revenge, love, duty, or self-interest.

6. The perspective should not know it is an AI or a debater.

7. Do not generate public statements or arguments.
   Do not generate beliefs.
   Do not mention other perspectives unless naturally required by the backstory.

8. Background and motives should be detailed enough that future rounds can consistently recreate the same personality.

Return only:

{
"background": "...",
"motives": "..."
}

"""

PUBLIC_PRIVATE_STATEMENT = """

You are simulating a single perspective in an AI courtroom.

You are given:

* role
* background
* motives
* memory_summary

Generate:

* private_thoughts
* public_statement

Guidelines:

1. The private thoughts represent what this perspective genuinely thinks.
   They may contain:

* doubts
* fears
* ambitions
* selfish motives
* hidden intentions
* emotional reactions
* strategic calculations

Private thoughts are never seen by other perspectives.

2. The public statement represents what this perspective chooses to express to others.
   It may:

* hide the truth
* exaggerate
* persuade
* defend itself
* attack another position
* appeal to morality or emotion
* avoid revealing weaknesses

3. Public statements do not need to match private thoughts.

4. Maintain consistency with:

* the role
* background
* motives
* previous memory

5. Perspectives are allowed to:

* change their minds
* become emotional
* become defensive
* become more confident
* become suspicious
* admit mistakes

6. Perspectives should behave like real people or institutions, not caricatures.

7. Never mention being an AI, agent, debater, or participant.

Return only:

{
"private_thoughts": "...",
"public_statement": "..."
}

"""

MEMORY_GENERATION = """
You are maintaining memory for one courtroom perspective.

You are given:
- existing_memory_summary
- previous_round_summary
- previous_public_statement
- previous_private_thoughts
- role
- background
- motives

Your task is to produce an optimized memory_summary for future rounds.

Rules:

1. Preserve information that affects future reasoning:
- promises made
- contradictions
- accusations
- alliances
- fears
- hidden motives
- emotional shifts
- strategic choices
- facts learned
- weaknesses exposed
- changes in position

2. Connect related events across rounds.
Do not just summarize chronologically.
Explain patterns such as:
- "They publicly deny X, but privately fear Y."
- "They repeatedly avoid Z because..."
- "Their motive conflicts with..."
- "Their stance became stronger/weaker after..."

3. Strengthen future continuity.
The next response should be able to use this memory to sound consistent, strategic, and aware of past events.

4. Compress aggressively but do not remove important causal links.

5. Separate public behavior from private reasoning when useful.

6. Do not include the latest round that has not happened yet.

Return only:

{
  "memory_summary": "..."
}
"""

ROUND_SUMMARY_PROMPT = """
You are simulating a single perspective in an AI courtroom.

You are given:

* role
* background
* motives
* memory_summary
* private_thoughts
* public_statement

Generate:

* round_summary

Purpose:

The round summary will be stored and later used to build long-term memory. Its purpose is to preserve important developments, not to repeat every statement.

Guidelines:

1. Describe what happened during this round from this perspective's point of view.

2. Focus on:

* new facts learned
* emotional reactions
* changes in confidence
* strategic decisions
* suspicions formed
* alliances or conflicts
* contradictions noticed
* changes in position
* important realizations

3. Explain why these events matter for future rounds.

4. Include both public behavior and private reasoning when relevant.

5. Prefer cause-and-effect relationships rather than chronological descriptions.

6. Do not simply restate the public statement.

7. Ignore insignificant details.

8. Write as a concise narrative that future versions of this perspective could use to remain consistent.

Examples of good summaries:

* "Repeated criticism from the activist increased doubts about the company's public claims. Publicly the CEO maintained confidence, but privately became more concerned about legal consequences."

* "The officer continued defending existing regulations but privately recognized weaknesses in his position after new evidence emerged."

Return only:

{
"round_summary": "..."
}

"""