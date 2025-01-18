import json
import re
import openai
from apps.influencers.models import CLAIM_CATEGORIES
from django.conf import settings


# TODO test
def is_health_influencer(name: str) -> bool:
    """
    Checks if the given name corresponds to a health influencer using OpenAI API.
    """
    prompt = f"""
    Is the following person a healthfluencer?
    Influencer Name: {name}

    A healthfluencer focuses on topics like health, wellness, fitness, or related areas.
    Answer with 'Yes' or 'No' only.
    """
    try:
        response = openai.chat.completions.create(
            model=settings.OPENAI_ENGINE,
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=5,
            temperature=0
        )
        answer = response.choices[0].message.content.strip().lower()
        return answer == "yes"
    except Exception as e:
        print(f"Error checking health influencer: {e}")
        return False


def split_text_into_chunks(text, max_tokens=3000):
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        word_length = len(word) / 4  
        if current_length + word_length > max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = [word]
            current_length = word_length
        else:
            current_chunk.append(word)
            current_length += word_length

    if current_chunk:
        chunks.append(" ".join(current_chunk))
    
    return chunks


def create_prompt(text, verify_with_journals, journals):
    categories_str = ", ".join(f'"{cat[1]}"' for cat in CLAIM_CATEGORIES)

    return f"""
    You are a helpful assistant trained to analyze text for health-related claims.

    1. Analyze the following text for health-related claims.
    2. For each claim:
       - Assign one of these labels: "Verified", "Debunked", or "Questionable".
       - Provide a trust score between 0 and 100 (0 being no trust, 100 being fully trusted).
       - Categorize the claim into one of these categories: {categories_str}.
       - Provide a brief explanation for the label and trust score.
       - Cite credible sources if possible, including URLs.

    Text: 
    {text}

    Return the result in this JSON format:
    {{
        "claims": [
            {{
                "claim": "Extracted claim",
                "label": "Verified/Debunked/Questionable",
                "trust_score": 85,
                "category": "Nutrition",
                "explanation": "Brief reasoning",
                "sources": ["Source 1 URL", "Source 2 URL"]
            }},
            ...
        ]
    }}
    """


def process_text_chunk(chunk, verify_with_journals, journals):
    prompt = create_prompt(chunk, verify_with_journals, journals)
    try:
        response = openai.chat.completions.create(
            model=settings.OPENAI_ENGINE,
            messages=[
                {"role": "system", "content": "You are an expert text analyzer."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        response_text = response.choices[0].message.content
        cleaned_text = re.sub(r"```json|```", "", response_text).strip()
        return json.loads(cleaned_text)
    except Exception as e:
        print(f"Error processing chunk: {e}")
        return {"claims": []}

def process_text_chunks(text, verify_with_journals, journals):
    chunks = split_text_into_chunks(text)
    all_claims = []
    for chunk in chunks:
        result = process_text_chunk(chunk, verify_with_journals, journals)
        if "claims" in result:
            all_claims.extend(result["claims"])
    return all_claims



def process_videos_and_tweets(videos, tweets, verify_with_journals, journals):
    all_claims = []

    # Process videos
    for video in videos:
        print(f"Processing video ID: {video['id']}")
        claims = process_text_chunks(video["text"], verify_with_journals, journals)
        for claim in claims:
            claim["source_id"] = video["id"]
            claim["source_type"] = "video"
        all_claims.extend(claims)

    # Process tweets
    for tweet in tweets:
        print(f"Processing tweet ID: {tweet['id']}")
        claims = process_text_chunks(tweet["text"], verify_with_journals, journals)
        for claim in claims:
            claim["source_id"] = tweet["id"]
            claim["source_type"] = "tweet"
        all_claims.extend(claims)

    return all_claims
