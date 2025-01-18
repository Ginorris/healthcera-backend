import openai
from django.conf import settings


# TODO see exception
def is_health_influencer(name: str) -> bool:
    """Returns True if openapi determines the name corresponds to a health influencer"""
    prompt = f"""
    Is the following person a healthfluencer?
    Influencer Name: {name}

    A healthfluencer focuses on topics like health, wellness, fitness, or related areas.
    Answer with 'Yes' or 'No' only.
    """
    try:
        response = openai.completions.create(
            engine=settings.OPENAI_ENGINE,
            prompt=prompt,
            max_tokens=5,
            temperature=0
        )
        answer = response.choices[0].text.strip().lower()
        return answer == "yes"
    except Exception:
        return False