import streamlit as st
import json
import os
from pathlib import Path
from rag_search import load_knowledge_base, search_knowledge, generate_answer

# Page config
st.set_page_config(
    page_title="Infrastructure Development Assistant",
    page_icon="🏗️",
    layout="wide"
)

# Helper functions for image search
def load_image_knowledge_base():
    """Load the image knowledge base from JSON file."""
    try:
        image_kb_path = Path("data/image_knowledge_base.json")
        if image_kb_path.exists():
            with open(image_kb_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                return data.get("image_knowledge_base", [])
        return []
    except Exception as e:
        st.error(f"Error loading image knowledge base: {e}")
        return []

def find_relevant_images(query, image_kb, max_images=2):
    """Find relevant images based on query matching."""
    query_lower = query.lower()
    matched_images = []

    try:
        for article in image_kb:
            for image in article.get("images", []):
                score = 0

                # Check relevance keywords
                relevance_keywords = image.get("relevance", [])
                for keyword in relevance_keywords:
                    if keyword.lower() in query_lower:
                        score += 2

                # Check geographic focus
                geo_focus = image.get("geographic_focus")
                if geo_focus and geo_focus.lower() in query_lower:
                    score += 3

                # Check data type
                data_type = image.get("data_type")
                if data_type and data_type.replace("_", " ").lower() in query_lower:
                    score += 2

                # Check article topic
                article_topic = article.get("article_topic", "")
                if article_topic.lower() in query_lower:
                    score += 1

                if score > 0:
                    matched_images.append({
                        "score": score,
                        "filename": image.get("filename"),
                        "description": image.get("description"),
                        "article_source": article.get("article_id"),
                        "type": image.get("type")
                    })

        # Sort by score and return top matches
        matched_images.sort(key=lambda x: x["score"], reverse=True)
        return matched_images[:max_images]

    except Exception as e:
        # Fail silently - don't break chat functionality
        return []

def display_related_images(images):
    """Display related images in an expandable section."""
    if not images:
        return

    try:
        # Filter to only images that actually exist and are not PDFs
        existing_images = []
        for img in images:
            img_path = Path(f"images/{img['filename']}")
            # Skip PDF files
            if img_path.suffix.lower() == '.pdf':
                continue
            if img_path.exists():
                existing_images.append((img, img_path))

        if not existing_images:
            return

        with st.expander("📊 Related Research Figures", expanded=True):
            for img, img_path in existing_images:
                try:
                    # Display regular image files (PNG, JPG, etc.)
                    st.image(
                        str(img_path),
                        caption=f"{img['description']}\n\nSource: {img['article_source']}",
                        use_container_width=True
                    )
                except Exception as e:
                    # Skip images that fail to load but don't break the chat
                    continue

    except Exception as e:
        # Fail silently - don't break chat functionality
        pass

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "knowledge_base" not in st.session_state:
    with st.spinner("Loading knowledge base..."):
        st.session_state.knowledge_base, st.session_state.embeddings = load_knowledge_base()

if "image_knowledge_base" not in st.session_state:
    st.session_state.image_knowledge_base = load_image_knowledge_base()

# Sidebar
with st.sidebar:
    st.header("About")
    st.write("This assistant provides information about African infrastructure development based on curated articles and case studies.")

    st.divider()

    st.metric("Articles Loaded", len(st.session_state.knowledge_base))

    # Calculate stats
    sources = set()
    for item in st.session_state.knowledge_base:
        sources.add(item["source"])

    st.metric("Unique Sources", len(sources))

    st.divider()

    st.subheader("Data Sources")
    st.write("• Research articles on African infrastructure")
    st.write("• WorldPop population data (worldpop.org)")

    st.info("💡 Responses may include figures from research articles when relevant")

    st.divider()

    if st.button("Clear Chat History"):
        st.session_state.messages = []
        st.rerun()

# Main app
st.title("🏗️ Infrastructure Development Assistant")
st.write("Ask questions about African infrastructure development, case studies, and recommendations.")

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        # Show images if available
        if message["role"] == "assistant" and "images" in message:
            display_related_images(message["images"])

        # Show sources if available
        if message["role"] == "assistant" and "sources" in message:
            with st.expander("📚 Sources"):
                for i, source in enumerate(message["sources"], 1):
                    st.markdown(f"**{i}. {source['source']}**")
                    st.text(source["text"][:300] + "..." if len(source["text"]) > 300 else source["text"])
                    st.divider()

# Chat input
if prompt := st.chat_input("Ask about infrastructure development..."):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Display user message
    with st.chat_message("user"):
        st.markdown(prompt)

    # Generate response
    with st.chat_message("assistant"):
        with st.spinner("Searching knowledge base..."):
            # Search for relevant chunks
            relevant_chunks = search_knowledge(prompt, top_k=5)

            # Generate answer
            answer = generate_answer(prompt, relevant_chunks)

            # Display answer
            st.markdown(answer)

            # Find and display relevant images
            relevant_images = find_relevant_images(
                prompt,
                st.session_state.image_knowledge_base,
                max_images=2
            )
            display_related_images(relevant_images)

            # Show sources
            with st.expander("📚 Sources"):
                for i, chunk in enumerate(relevant_chunks, 1):
                    st.markdown(f"**{i}. {chunk['source']}**")
                    st.text(chunk["text"][:300] + "..." if len(chunk["text"]) > 300 else chunk["text"])
                    st.divider()

    # Add assistant message to chat history
    st.session_state.messages.append({
        "role": "assistant",
        "content": answer,
        "sources": relevant_chunks,
        "images": relevant_images
    })
