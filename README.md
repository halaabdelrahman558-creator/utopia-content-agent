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

```bash
export OPENAI_API_KEY=your_key
python utopia_content_agent.py sample_transcript.txt