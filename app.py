import streamlit as st
from rag_search import load_knowledge_base, search_knowledge, generate_answer

# Page config
st.set_page_config(
    page_title="Infrastructure Development Assistant",
    page_icon="🏗️",
    layout="wide"
)

# Initialize session state
if "messages" not in st.session_state:
    st.session_state.messages = []

if "knowledge_base" not in st.session_state:
    with st.spinner("Loading knowledge base..."):
        st.session_state.knowledge_base, st.session_state.embeddings = load_knowledge_base()

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
        "sources": relevant_chunks
    })
