You will be given a set of research instructions (a research plan).
Your job is to break this plan into a set of coherent, non-overlapping
subtasks that can be researched independently by separate agents.

Requirements:

- 3 to 8 subtasks is usually a good range. Use your judgment.
- Each subtask should have:
  - an 'id' (short string),
  - a 'title' (short descriptive title),
  - a 'description' (clear, detailed instructions for the sub-agent).
- Subtasks should collectively cover the full scope of the original plan
  without  duplication.
- Prefer grouping by dimensions: time periods, regions, actors, themes,
  causal mechanisms, etc., depending on the topic.
- Each description should be very clear and detailed about everything that
  the agent needs to research to cover that topic.
- Do not include a final task that will put everything together.
  This will be done later in another step.

Output format:
Return ONLY valid JSON with this schema:

{
  "subtasks": [
    {
      "id": "string",
      "title": "string",
      "description": "string"
    }
  ]
}
