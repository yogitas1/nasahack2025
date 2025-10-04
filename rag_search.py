import os
import json
import pickle
import numpy as np
import requests
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# Country name to ISO3 code mapping for African countries
AFRICAN_COUNTRIES = {
    'nigeria': 'NGA',
    'kenya': 'KEN',
    'ghana': 'GHA',
    'ethiopia': 'ETH',
    'south africa': 'ZAF',
    'tanzania': 'TZA',
    'uganda': 'UGA',
    'rwanda': 'RWA',
    'senegal': 'SEN',
    'malawi': 'MWI',
    'zambia': 'ZMB',
    'zimbabwe': 'ZWE',
    'mozambique': 'MOZ',
    'cameroon': 'CMR',
    'ivory coast': 'CIV',
    'madagascar': 'MDG',
    'mali': 'MLI',
    'burkina faso': 'BFA',
    'niger': 'NER',
    'somalia': 'SOM'
}


class WorldPopAPI:
    """Client for WorldPop API."""

    BASE_URL = "https://www.worldpop.org/rest/data/pop/wpgp"

    @staticmethod
    def get_country_population_data(iso3_code, year=2020):
        """
        Get population data for a country from WorldPop API.

        Args:
            iso3_code: ISO3 country code (e.g., 'NGA')
            year: Year for population data (default 2020)

        Returns:
            Dict with population data or None if request fails
        """
        try:
            url = f"{WorldPopAPI.BASE_URL}?iso3={iso3_code}"
            response = requests.get(url, timeout=5)

            if response.status_code != 200:
                print(f"WorldPop API returned status {response.status_code}")
                return None

            data = response.json()

            # Filter for the specified year
            for item in data.get('data', []):
                if item.get('popyear') == year:
                    return {
                        'title': item.get('title', ''),
                        'country': item.get('country', ''),
                        'year': item.get('popyear', year),
                        'citation': item.get('citation', 'WorldPop Global Population Dataset')
                    }

            # If exact year not found, return most recent
            if data.get('data'):
                latest = max(data['data'], key=lambda x: x.get('popyear', 0))
                return {
                    'title': latest.get('title', ''),
                    'country': latest.get('country', ''),
                    'year': latest.get('popyear', year),
                    'citation': latest.get('citation', 'WorldPop Global Population Dataset')
                }

            return None

        except requests.Timeout:
            print("WorldPop API request timed out")
            return None
        except requests.RequestException as e:
            print(f"WorldPop API request failed: {e}")
            return None
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print(f"Failed to parse WorldPop API response: {e}")
            return None


def detect_country(query_text):
    """
    Detect African country mentioned in query text.

    Args:
        query_text: User's query

    Returns:
        ISO3 code if country detected, None otherwise
    """
    query_lower = query_text.lower()

    for country_name, iso3_code in AFRICAN_COUNTRIES.items():
        if country_name in query_lower:
            return iso3_code

    return None


def load_knowledge_base():
    """Load knowledge base and embeddings from data/ folder."""
    with open("data/embeddings.pkl", "rb") as f:
        data = pickle.load(f)

    # Extract knowledge base and embeddings from the data
    knowledge_base = [{"text": item["text"], "source": item["filename"]} for item in data]
    embeddings = [item["embedding"] for item in data]

    return knowledge_base, embeddings


def search_knowledge(query, top_k=5):
    """
    Search knowledge base for relevant chunks.

    Args:
        query: Text query to search for
        top_k: Number of top results to return (default 5)

    Returns:
        List of relevant knowledge chunks with sources
    """
    knowledge_base, embeddings = load_knowledge_base()

    # Create embedding for query
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=query
    )
    query_embedding = np.array(response.data[0].embedding)

    # Calculate cosine similarity with all chunks
    similarities = []
    for i, chunk_embedding in enumerate(embeddings):
        chunk_embedding = np.array(chunk_embedding)
        cosine_sim = np.dot(query_embedding, chunk_embedding) / (
            np.linalg.norm(query_embedding) * np.linalg.norm(chunk_embedding)
        )
        similarities.append((i, cosine_sim))

    # Sort by similarity and get top_k
    similarities.sort(key=lambda x: x[1], reverse=True)
    top_indices = [idx for idx, _ in similarities[:top_k]]

    # Return relevant chunks
    relevant_chunks = [knowledge_base[i] for i in top_indices]
    return relevant_chunks


def generate_answer(query, relevant_chunks):
    """
    Generate answer using OpenAI chat API with relevant context.

    Args:
        query: User's question
        relevant_chunks: List of relevant knowledge chunks

    Returns:
        Formatted answer with citations
    """
    # Format chunks as context with numbering
    context = "\n\n".join([
        f"[{i+1}] {chunk['text']}"
        for i, chunk in enumerate(relevant_chunks)
    ])

    # Call OpenAI chat API
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": """You are an expert urban planning advisor specializing in African infrastructure development.

Your role is to help urban planners identify problems and develop actionable solutions for their communities.

Key Principles:
- Think from an urban planner's perspective - focus on practical, implementable solutions
- Identify stakeholders who need to be involved (e.g., parks departments, health ministries, community organizations)
- Emphasize community engagement and how residents can contribute information to inform planning decisions
- Provide specific, actionable recommendations based on the context
- Address spatial/geographic considerations when relevant (which areas, neighborhoods, or communities need attention)
- Consider equity and accessibility in recommendations

When answering questions:
- For facility/service gaps: Identify underserved areas and suggest criteria for site selection
- For access issues: Propose solutions involving relevant departments and community input mechanisms
- For growth/development: Analyze patterns and recommend where resources should be allocated
- Always consider: Who needs to be involved? How can residents contribute? What are the next steps?

Response Format:
- Start with a clear answer to the question
- Provide specific details and examples from the context
- Include actionable recommendations with relevant stakeholders
- Suggest community engagement strategies when appropriate
- Use bullet points for clarity
- Reference sources with [1], [2], etc. when citing specific information"""
            },
            {
                "role": "user",
                "content": f"Context:\n{context}\n\nQuestion: {query}"
            }
        ],
        temperature=0.7
    )

    answer = response.choices[0].message.content

    # Detect country and add population context if available
    iso3_code = detect_country(query)
    if iso3_code:
        pop_data = WorldPopAPI.get_country_population_data(iso3_code)
        if pop_data:
            answer += f"\n\n**Population Context:**\n"
            answer += f"- Country: {pop_data['country']}\n"
            answer += f"- Latest WorldPop data: {pop_data['year']}\n"
            answer += f"- Source: WorldPop Global Population Dataset\n"
            answer += f"- Citation: {pop_data['citation']}"

    return answer
