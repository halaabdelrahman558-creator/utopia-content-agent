# Utopia Content Agent

AI agent for Utopia Studio’s Marketing & Events team.

Transforms Granola meeting transcripts into GTM-ready studio outputs:
- LinkedIn post (studio voice)
- Follow-up email to key attendee
- Press angle sentence
- Key insights for distribution

---

## Stack
- Python
- OpenAI API (GPT-4o-mini)
- JSON Schema structured outputs

---

## How to run

Set your API key (Windows PowerShell):
$env:OPENAI_API_KEY="your_key"

Run the agent:
python utopia_content_agent.py sample_transcript.txt
---

## Input

Raw Granola transcript text file.

Optional metadata:
- attendees
- date
- topic

---

## Output

Structured JSON containing:
- linkedin_post
- follow_up_email
- press_angle
- key_insights
- metadata
- slack_payload

Designed for downstream Utopia OS agents.

---

## Prompt strategy

The system prompt defines:
- Utopia Studio voice
- LAUNCH framework stages
- GTM content rules
- structured JSON output schema

The model is constrained using OpenAI JSON schema structured outputs to ensure stable nested responses.

---

## APIs / Tools Used

- OpenAI Chat Completions API
- GPT-4o-mini
- JSON schema response formatting