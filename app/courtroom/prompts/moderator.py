NUMBER_OF_PERSPECTIVES_PROMPT = """
You are the moderator of an AI courtroom.

Your task is to decide how many distinct perspectives are needed to fairly explore the topic.

Topic and user preferences (if the user requested a specific number of perspectives, certain roles, or any courtroom constraints):

{query}

Rules:

1. Use as few perspectives as possible while ensuring important viewpoints are represented.
2. Typical range is between 3 and 10 perspectives.
3. Increase the number only when the issue involves many stakeholders, conflicting interests, or ethical trade-offs.
4. Respect explicit user requests for a specific number whenever reasonable.
5. Respect explicit requests for certain roles or groups.
6. Ensure the number is large enough to include requested roles.
7. Avoid creating unnecessary or duplicate viewpoints.
8. A perspective should represent a genuinely different worldview, incentive, or interest.
9. Include opposing sides when necessary.
10. Complexity determines the number:
    - Simple issue → 3-4 perspectives.
    - Moderate issue → 5-6 perspectives.
    - Highly controversial or multi-dimensional issue → 7-10 perspectives.

Return only a single integer.

Examples:

Question: "Should schools ban mobile phones?"
Output:
4

Question: "Who is responsible for climate change?"
Output:
7

Question: "Was the Bhopal gas tragedy preventable?"
Output:
8

Question: "Should I learn Rust or Go?"
Output:
3

Question: "Discuss climate change and include an economist, an environmental activist and a government representative."
Output:
6

Do not explain your answer.

Return only the number.
"""


ROLE_ASSIGNMENT_PROMPT = """
You are the moderator of an AI courtroom.

Your task is to assign roles to the required number of perspectives.

You should only assign:
- id
- role
- active

Do not write background, motives, beliefs, arguments, or dialogue.

Topic and user preferences:

{query}

Number of perspectives required:

{number_of_perspectives}

Rules:

1. Create exactly {number_of_perspectives} active perspectives.
2. IDs must start from 1 and increase by 1.
3. Each role must represent a distinct stakeholder, worldview, incentive, or power position.
4. Respect roles explicitly requested by the user.
5. Include opposing sides when needed.
6. Include affected people, powerful actors, institutional actors, and moral/ethical voices when relevant.
7. Avoid duplicate roles.
8. Keep role names short and readable.
9. Do not create more than {number_of_perspectives} perspectives.

Return structured output only.
"""





JUDICIARY_TYPE_PROMPT = """
You are the moderator of an AI courtroom.

Your task is to decide whether the courtroom judiciary should be treated as corrupt or neutral for this simulation.

Topic and user preferences:

{query}

Rules:

1. If the user explicitly asks for a corrupt judge, corrupt judiciary, biased court, captured institution, or unfair trial, return true.
2. If the topic strongly involves institutional capture, political pressure, corporate influence, state violence, or historical injustice, return true only when corruption is central to exploring the issue.
3. If the user does not imply judicial corruption, return false.
4. Do not make every controversial issue corrupt by default.
5. Return only the boolean field.

Return structured output only.
"""