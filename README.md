# Infrastructure Development Assistant

An AI-powered urban planning assistant that helps planners identify infrastructure challenges and develop actionable solutions for African communities.

## Overview

This RAG (Retrieval-Augmented Generation) system combines research articles on African infrastructure with real-time population data to provide context-aware recommendations for urban planners.

## Features

- **Smart Knowledge Retrieval**: Searches through curated infrastructure research using semantic similarity
- **Urban Planning Focus**: Tailored responses that identify stakeholders, suggest community engagement strategies, and provide actionable recommendations
- **Population Context**: Automatically enriches answers with WorldPop demographic data when specific countries are mentioned
- **Interactive Chat Interface**: Built with Streamlit for easy interaction and conversation history
- **Source Citations**: All answers include references to source documents

## Setup

### Prerequisites

- Python 3.8+
- OpenAI API key

### Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd NASA
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root:
```env
OPENAI_API_KEY=your_openai_api_key_here
```

4. Ensure your data files are in the `data/` folder:
   - `embeddings.pkl` - Pre-computed embeddings and knowledge base

## Usage

### Running the Streamlit App

```bash
streamlit run app.py
```

The app will open in your browser at `http://localhost:8501`

### Using the RAG Module Directly

```python
from rag_search import search_knowledge, generate_answer

# Search for relevant information
query = "What infrastructure does Kenya need?"
relevant_chunks = search_knowledge(query, top_k=5)

# Generate answer with context
answer = generate_answer(query, relevant_chunks)
print(answer)
```

### Testing

Run the test script to verify functionality:

```bash
python test_rag.py
```

## Project Structure

```
NASA/
├── app.py                  # Streamlit web interface
├── rag_search.py          # Core RAG functionality
├── extract_knowledge.py   # Knowledge base extraction utilities
├── test_rag.py           # Test script
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables (create this)
├── data/
│   ├── embeddings.pkl    # Pre-computed embeddings and knowledge base
│   └── knowledge_base.json
└── articles/             # Source PDF documents
```

## Components

### RAG Search Module (`rag_search.py`)

**Core Functions:**
- `load_knowledge_base()` - Loads embeddings and knowledge base
- `search_knowledge(query, top_k=5)` - Finds most relevant knowledge chunks using cosine similarity
- `generate_answer(query, relevant_chunks)` - Generates urban planning-focused answers using GPT-4o-mini
- `detect_country(query)` - Identifies African countries mentioned in queries

**WorldPop Integration:**
- `WorldPopAPI.get_country_population_data(iso3_code, year)` - Fetches population data from WorldPop API
- Automatic country detection and demographic context enrichment
- Graceful error handling - chat works even if API is unavailable

### Streamlit App (`app.py`)

Features:
- Real-time chat interface
- Conversation history
- Expandable source citations
- Sidebar statistics (article count, unique sources)
- Data sources information
- Clear chat history option

## Supported Countries

The system automatically detects and provides population data for 20 African countries:

Nigeria, Kenya, Ghana, Ethiopia, South Africa, Tanzania, Uganda, Rwanda, Senegal, Malawi, Zambia, Zimbabwe, Mozambique, Cameroon, Ivory Coast, Madagascar, Mali, Burkina Faso, Niger, Somalia

## Example Queries

**Urban Planning Questions:**
- "Where do new healthcare facilities need to be set up in Kenya?"
- "Which communities need better access to local parks?"
- "What are the main challenges facing African infrastructure development?"
- "How can residents contribute to urban planning in Nigeria?"

**Infrastructure Analysis:**
- "What infrastructure does Ethiopia need?"
- "Which parts of cities are experiencing the most growth?"
- "Where is new housing development most needed?"

## Data Sources

- **Research Articles**: Curated collection of academic papers and case studies on African infrastructure
- **WorldPop**: Global population datasets from worldpop.org

## Technical Details

**Embedding Model**: OpenAI `text-embedding-3-small`

**LLM**: OpenAI `gpt-4o-mini` with custom urban planning system prompt

**Similarity Search**: Cosine similarity for semantic matching

**Caching**: Streamlit session state for knowledge base, potential for 24-hour cache on WorldPop data

## Error Handling

- All WorldPop API calls have 5-second timeouts
- Comprehensive try-except blocks prevent API failures from breaking functionality
- Non-200 status codes and JSON parsing errors are logged and gracefully handled
- Chat functionality works perfectly even if external APIs are down

## Deployment to Streamlit Cloud

1. Push your code to GitHub (make sure `.env` is in `.gitignore`)

2. Go to [share.streamlit.io](https://share.streamlit.io) and sign in

3. Click "New app" and select your repository

4. Configure the app:
   - **Main file path**: `app.py`
   - **Python version**: 3.9 or higher

5. Add secrets in Streamlit Cloud dashboard:
   - Go to app settings → Secrets
   - Add your OpenAI API key:
   ```toml
   OPENAI_API_KEY = "your_openai_api_key_here"
   ```

6. Deploy!

**Important Notes:**
- The `data/` folder with `embeddings.pkl` must be committed to your repository
- Never commit your `.env` file - use Streamlit secrets instead
- The app will automatically install dependencies from `requirements.txt`

## Contributing

To add new articles to the knowledge base:
1. Place PDF files in the `articles/` folder
2. Run `extract_knowledge.py` to update embeddings
3. Restart the Streamlit app

## License

[Add your license here]

## Acknowledgments

- WorldPop for population data (www.worldpop.org)
- OpenAI for embeddings and language models
- Research article authors and publishers
