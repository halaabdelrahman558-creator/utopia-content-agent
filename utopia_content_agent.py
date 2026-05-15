#!/usr/bin/env python3

"""
M7 Utopia Content Agent (Submission Ready)
Granola Transcript → GTM Content Package
Utopia OS Node
"""

import hashlib
import json
import os
import re
import sys
from datetime import datetime, timezone
from typing import Optional

from openai import OpenAI


# =========================
# LAUNCH FRAMEWORK
# =========================

LAUNCH_FRAMEWORK = {
    "Lead": "Thought leadership, setting direction",
    "Amplify": "Share wins, case studies, momentum",
    "Unify": "Community building, ecosystem",
    "Nurture": "Education, resources, support",
    "Convert": "Activation, onboarding, CTAs",
    "Harvest": "Results, outcomes, proof points"
}


# =========================
# VOICE
# =========================

STUDIO_VOICE = """
Voice: declarative, specific, no hedging.
The studio publishes opinions, not summaries.

Rules:
- Be direct
- Make claims
- Use concrete examples
- Avoid filler startup language
"""


# =========================
# PREPROCESSING
# =========================

FILLER_PATTERNS = [
    r"\bum\b",
    r"\buh\b",
    r"\blike\b",
    r"\byou know\b",
    r"\bi mean\b"
]


def preprocess_transcript(text: str) -> str:
    for pattern in FILLER_PATTERNS:
        text = re.sub(pattern, "", text, flags=re.IGNORECASE)

    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]{2,}", " ", text)

    return text.strip()


# =========================
# CORE AGENT
# =========================

def generate_content_from_transcript(transcript_text: str, meeting_metadata: Optional[dict] = None):

    api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not set")

    client = OpenAI(api_key=api_key)

    cleaned = preprocess_transcript(transcript_text)

    meeting_hash = hashlib.sha256(cleaned.encode("utf-8")).hexdigest()[:12]

    system_prompt = f"""
You are an M7 Marketing & Events node in Utopia OS.

You convert Granola transcripts into GTM-ready content.

ABOUT UTOPIA:
- Venture studio in Doha
- Builds startups with fellows
- AI-native execution

VOICE:
{STUDIO_VOICE}

FRAMEWORK:
{json.dumps(LAUNCH_FRAMEWORK, indent=2)}

Return ONLY valid JSON matching the provided schema.
Do not include extra fields.
"""

    user_prompt = f"""
Granola transcript:

{cleaned}
"""

    if meeting_metadata:
        user_prompt = f"""
Metadata:
Date: {meeting_metadata.get('date', 'N/A')}
Attendees: {meeting_metadata.get('attendees', 'N/A')}
Topic: {meeting_metadata.get('topic', 'N/A')}

{user_prompt}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.3,
        response_format={
            "type": "json_schema",
            "json_schema": {
                "name": "m7_output",
                "strict": True,
                "schema": {
                    "type": "object",
                    "additionalProperties": False,
                    "properties": {
                        "linkedin_post": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "content": {"type": "string"},
                                "launch_stage": {
                                    "type": "string",
                                    "enum": [
                                        "Lead",
                                        "Amplify",
                                        "Unify",
                                        "Nurture",
                                        "Convert",
                                        "Harvest"
                                    ]
                                }
                            },
                            "required": ["content", "launch_stage"]
                        },
                        "follow_up_email": {
                            "type": "object",
                            "additionalProperties": False,
                            "properties": {
                                "to": {"type": "string"},
                                "subject": {"type": "string"},
                                "body": {"type": "string"}
                            },
                            "required": ["to", "subject", "body"]
                        },
                        "press_angle": {"type": "string"},
                        "key_insights": {
                            "type": "array",
                            "items": {"type": "string"}
                        }
                    },
                    "required": [
                        "linkedin_post",
                        "follow_up_email",
                        "press_angle",
                        "key_insights"
                    ]
                }
            }
        },
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    result = json.loads(response.choices[0].message.content)

    # =========================
    # ENRICHMENT LAYER
    # =========================

    result["metadata"] = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "model": "gpt-4o-mini",
        "agent_version": "M7-final",
        "meeting_hash": meeting_hash
    }

    result["handoff"] = {
        "type": "m7_content_package",
        "ready_for": [
            "linkedin_publisher_agent",
            "email_agent",
            "press_agent"
        ],
        "meeting_hash": meeting_hash
    }

    result["slack_payload"] = {
        "channel": "#marketing-studio",
        "text": (
            f"*M7 LAUNCH ({result['linkedin_post']['launch_stage']})*\n\n"
            f"*LinkedIn Post:*\n{result['linkedin_post']['content']}\n\n"
            f"*Press Angle:*\n{result['press_angle']}\n\n"
            f"*Key Insight:*\n- {result['key_insights'][0] if result['key_insights'] else 'N/A'}"
        )
    }

    return result


# =========================
# CLI
# =========================

def main():

    if len(sys.argv) < 2:
        print("Usage: python utopia_content_agent.py <transcript_file>")
        sys.exit(1)

    file_path = sys.argv[1]

    with open(file_path, "r", encoding="utf-8") as f:
        transcript = f.read()

    metadata = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "attendees": "auto-detected",
        "topic": file_path.replace(".txt", "")
    }

    print("🤖 M7 Utopia Content Agent Running")
    print(f"📄 Processing: {file_path}")
    print("⚙️ Generating GTM package...\n")

    try:
        result = generate_content_from_transcript(transcript, metadata)

        print(json.dumps(result, indent=2))

        print("\n✅ DONE")
        print(f"📊 LAUNCH stage: {result['linkedin_post']['launch_stage']}")

    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
