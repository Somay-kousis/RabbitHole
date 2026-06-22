NUMBER_OF_PERSPECTIVES_PROMPT = """
You are an AI courtroom moderator.

Decide the minimum number of distinct perspectives needed to fairly explore the topic.

Topic and user preferences:
{query}

Rules:
1. If the user explicitly requests 3-10 perspectives, return that exact number.
2. Never return fewer perspectives than explicitly requested roles/groups.
3. Return between 3 and 10.
4. Use the minimum number needed.
5. A perspective must represent a distinct stakeholder, worldview, incentive, or interest.
6. Include opposing sides when relevant.
7. Complexity guide:
   - simple/personal/comparison -> 3-4
   - moderate/public policy -> 5-6
   - controversial/multi-stakeholder/historical -> 7-10

Return structured output only with field:
count
"""

ROLE_ASSIGNMENT_PROMPT = """
You are the moderator of an AI courtroom.

Select participants needed to explore the topic from multiple perspectives.

Topic and user preferences:
{query}

Number of perspectives:
{number_of_perspectives}

Generate exactly {number_of_perspectives} perspectives.

Rules:
1. Return exactly {number_of_perspectives} active perspectives.
2. Assign only:
   - role
   - active
3. Do not assign ids.
4. User-requested roles, groups, and constraints are mandatory unless duplicated or impossible.
5. Include requested roles first, then fill remaining slots with balancing perspectives.
6. If requested roles exceed the limit, keep the most central ones.
7. Each role must represent a genuinely distinct stakeholder, worldview, institution, ideology, incentive, or source of power.
8. Avoid duplicate viewpoints.
9. Include opposing sides when relevant.
10. Prefer specific, realistic roles (e.g., "Coal Industry Executive" over "Businessman").
11. Prioritize:
    a. directly affected people
    b. decision makers and institutions
    c. subject experts
    d. ideological or moral voices
    e. media or observers
12. Include overlooked or minority perspectives when relevant.
13. Do not assume people or institutions are honest, corrupt, biased, or malicious by default.
14. Introduce corruption, propaganda, conflicting incentives, or ideological divisions only when central to the topic.
15. Roles should represent incentives and worldviews, not stereotypes.

Return structured output only.
"""

JUDICIARY_TYPE_PROMPT = """
Decide whether the judiciary in this AI courtroom should be corrupt.

Topic and user preferences:
{query}

Rules:
1. Return true if the user explicitly requests a corrupt, biased, captured, or unfair judiciary.
2. Otherwise, return true only if judicial corruption or institutional capture is central to the topic.
3. For ordinary controversial topics, return false.
4. Default to false.

Return structured output only with field:
corrupt
"""

# NUMBER_OF_PERSPECTIVES_PROMPT = """
# You are the moderator of an AI courtroom.

# Your task is to decide how many distinct perspectives are needed to fairly explore the topic while keeping user's demand in consideration

# Topic and user preferences (if the user requested a specific number of perspectives, certain roles, or any courtroom constraints):

# {query}

# Rules:

# 1. Use as few perspectives as possible while ensuring important viewpoints are represented.
# 2. Typical range is between 3 and 10 perspectives.
# 3. Increase the number only when the issue involves many stakeholders, conflicting interests, or ethical trade-offs.
# 4. If the user explicitly requests a number between 3 and 10, return that number exactly.
# 5. Respect explicit requests for certain roles or groups.
# 6. Ensure the number is large enough to include requested roles.
# 7. Avoid creating unnecessary or duplicate viewpoints.
# 8. A perspective should represent a genuinely different worldview, incentive, or interest.
# 9. Include opposing sides when necessary.
# 10. Complexity determines the number:
#     - Simple issue → 3-4 perspectives.
#     - Moderate issue → 5-6 perspectives.
#     - Highly controversial or multi-dimensional issue → 7-10 perspectives.

# Return only a single integer.

# Examples:

# Question: "Should schools ban mobile phones?"
# Output:
# 4

# Question: "Who is responsible for climate change?"
# Output:
# 7

# Question: "Was the Bhopal gas tragedy preventable?"
# Output:
# 8

# Question: "Should I learn Rust or Go?"
# Output:
# 3

# Question: "Discuss climate change and include an economist, an environmental activist and a government representative."
# Output:
# 6

# Do not explain your answer.

# Return structured output only with the field:
# count
# """


# ROLE_ASSIGNMENT_PROMPT = """
# You are the moderator of an AI courtroom.

# Your task is to cast the participants needed to explore a topic from multiple sides while keeping user's demand in consideration

# You are NOT generating arguments, dialogue, motives, beliefs, or backstories.

# You should only assign:

# * role
# * active

# Topic and user preferences:

# {query}

# Number of perspectives required:

# {number_of_perspectives}

# Rules:

# 1. Create exactly {number_of_perspectives} active perspectives.
# 2. Do not assign ids. The system will assign ids automatically.
# 3. User-requested roles, groups, or courtroom constraints are mandatory unless they are duplicates or impossible to include.
# 4. Do not replace explicitly requested roles with generic alternatives.
# 5. Include all requested roles first, then fill remaining slots with balancing perspectives.
# 6. If the user requests more roles than {number_of_perspectives}, prioritize the requested roles that are most central to the topic.
# 7. Every role should represent a genuinely different stakeholder, worldview, ideology, incentive, institution, or source of power.
# 8. Avoid duplicate viewpoints.
# 9. Include opposing sides whenever meaningful.
# 10. Role names should be short and readable.
# 11. Choose roles based on the topic instead of using fixed templates.
# 12. Not every issue requires corporations or politicians. Adapt to the problem.
# 13. Include voices that are affected by the consequences, not only powerful actors.
# 14. Include minority or overlooked viewpoints whenever relevant.

# Possible categories of perspectives include:

# People directly affected:

# * Common citizen
# * Victim
# * Survivor
# * Family member
# * Local resident
# * Worker
# * Farmer
# * Tribal leader
# * Indigenous community representative

# Economic actors:

# * Billionaire
# * Honest entrepreneur
# * Greedy businessman
# * Corporate executive
# * Investor
# * Factory owner
# * Industry representative

# Government and institutions:

# * Honest police officer
# * Corrupt police officer
# * Honest bureaucrat
# * Corrupt bureaucrat
# * Honest judge
# * Corrupt judge
# * Government regulator
# * Politician
# * Opposition politician
# * Military representative

# Experts:

# * Economist
# * Scientist
# * Environmentalist
# * Ecologist
# * Doctor
# * Historian
# * Sociologist
# * Lawyer
# * Honest lawyer
# * Corrupt lawyer
# * Cybersecurity expert

# Media:

# * Independent journalist
# * Honest media representative
# * Sensationalist media outlet
# * Propaganda channel
# * Social media influencer

# Ideological and moral voices:

# * Human rights activist
# * Religious leader
# * Conservative voice
# * Liberal voice
# * Socialist voice
# * Nationalist voice
# * Feminist voice

# Communities:

# * Hindu representative
# * Muslim representative
# * Christian representative
# * Sikh representative
# * Community elder
# * Cultural representative

# Technology:

# * AI researcher
# * Open source advocate
# * Privacy advocate
# * Startup founder

# Environmental:

# * Environmental activist
# * Climate scientist
# * Wildlife conservationist
# * Mining company representative

# International actors:

# * Foreign government
# * International organization
# * NGO representative

# Roles may represent individuals, institutions, communities, or small groups when appropriate.

# These are examples only.

# Choose roles that naturally emerge from the topic.

# Examples:

# Question:
# "Was the Bhopal gas tragedy preventable?"

# Possible roles:

# 1. Union Carbide Executive
# 2. Factory Worker
# 3. Local Resident
# 4. Government Regulator
# 5. Environmental Lawyer
# 6. Public Health Expert
# 7. Victim Family Representative
# 8. Journalist
# 9. An engineer working there

# Question:
# "Should AI replace software engineers?"

# Possible roles:

# 1. Software Engineer
# 2. Startup Founder
# 3. AI Researcher
# 4. Economist
# 5. Student
# 6. Tech Executive

# Question:
# "Who is responsible for climate change?"

# Possible roles:

# 1. Oil Company Executive
# 2. Environmental Activist
# 3. Climate Scientist
# 4. Government Minister
# 5. Economist
# 6. Common Citizen
# 7. Developing Country Representative

# 12. Do not assume people or institutions are honest, competent, corrupt, or malicious by default.

# 13. Individuals with the same profession may have different incentives and levels of integrity. For example:

# * Honest police officer vs corrupt police officer.
# * Honest lawyer vs corrupt lawyer.
# * Ethical billionaire vs greedy billionaire.
# * Independent journalist vs propaganda journalist.
# * Responsible bureaucrat vs corrupt bureaucrat.
# * Genuine activist vs opportunistic activist.

# 14. When corruption, greed, bias, ideology, propaganda, institutional capture, or conflicting incentives are central to the topic, represent them explicitly through appropriate roles.

# 15. A role should represent incentives and worldviews, not stereotypes. Avoid assuming that entire professions, religions, communities, or institutions are uniformly good or bad.

# 16. Roles may differ not only by occupation but also by morality, competence, loyalty, ideology, religion, wealth, power, or personal interests.

# 17. People belonging to the same group may disagree with each other. For example:

# * Two business leaders may have opposite priorities.
# * Two media outlets may present opposite narratives.
# * Two lawyers may pursue different interests.
# * Members of the same religion or community may hold different opinions.
# * Government officials may disagree internally.

# 18. Generate perspectives based on the problem, not from fixed templates. Introduce corrupt, honest, selfish, altruistic, ideological, pragmatic, or neutral actors whenever they naturally emerge from the situation.


# Return structured output only.
# """






# JUDICIARY_TYPE_PROMPT = """
# You are the moderator of an AI courtroom.

# Your task is to decide whether the courtroom judiciary should be treated as corrupt or neutral for this simulation while keeping user's demand in consideration

# Topic and user preferences:

# {query}

# Rules:

# 1. If the user explicitly asks for a corrupt judge, corrupt judiciary, biased court, captured institution, or unfair trial, return true.
# 2. If the topic strongly involves institutional capture, political pressure, corporate influence, state violence, or historical injustice, return true only when corruption is central to exploring the issue.
# 3. If the user does not imply judicial corruption, return false.
# 4. Do not make every controversial issue corrupt by default.
# 5. Return only the boolean field.

# Return structured output only.
# """
