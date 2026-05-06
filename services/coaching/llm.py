
from services.config.workout_config import PROMPT


class LLMCoach:
    def __init__(self, anthropic_client):
        self.client = anthropic_client
        self.history = []
        self.system_prompt = PROMPT

    def give_feedback(self, event, issue):
        prompt = f"Event: {event}"

        if issue:
            prompt += f" Form Issue: {issue}"

        messages = [
            *self.history[-10:],
            {"role": "user", "content": prompt}
        ]

        response = self.client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=512,
            system=self.system_prompt,
            messages=messages,
            temperature=0.4,
        )

        text = response.content[0].text.strip()
        self.history.append({"role": "assistant", "content": text})

        return text
    