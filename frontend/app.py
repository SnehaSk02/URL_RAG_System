# import streamlit as st

# import requests

# st.title(
#     "URL-Based RAG System"
# )

# page = st.sidebar.selectbox(
#     "Choose",
#     [
#         "Ingest URL",
#         "Ask Question"
#     ]
# )

# if page == "Ingest URL":

#     st.header(
#         "Ingest URL"
#     )

#     url = st.text_input(
#         "Enter URL"
#     )

#     if st.button(
#         "Ingest"
#     ):

#         response = requests.post(

#             "http://127.0.0.1:8000/ingest",

#             json={
#                 "url": url
#             }
#         )

#         st.json(
#             response.json()
#         )

# if page == "Ask Question":

#     st.header(
#         "Ask Questions"
#     )

#     query = st.text_input(
#         "Question"
#     )

#     if st.button(
#         "Ask"
#     ):

#         response = requests.post(

#             "http://127.0.0.1:8000/ask",

#             json={
#                 "query": query
#             }
#         )

#         data = response.json()

#         st.subheader(
#             "Answer"
#         )

#         st.write(
#             data["answer"]
#         )

#         st.subheader(
#             "Sources"
#         )

#         st.json(
#             data["sources"]
#         )

import streamlit as st
import requests
import uuid

# --------------------------------------------------
# Configuration
# --------------------------------------------------
API_URL = "http://127.0.0.1:8000"

# Initialize Session State for Chat History
if 'chats' not in st.session_state:
    # Structure: { chat_id: { "url": "...", "messages": [], "title": "..." } }
    st.session_state.chats = {}

if 'current_chat_id' not in st.session_state:
    st.session_state.current_chat_id = None

# --------------------------------------------------
# Helper Functions
# --------------------------------------------------
def create_new_chat_session(url):
    """Creates a new chat session for a given URL."""
    chat_id = str(uuid.uuid4())
    st.session_state.chats[chat_id] = {
        "url": url,
        "messages": [],
        "title": url  # You can fetch page title later if needed
    }
    st.session_state.current_chat_id = chat_id
    return chat_id

# --------------------------------------------------
# Sidebar Layout
# --------------------------------------------------

st.sidebar.title("🌐 URL RAG System")

# 1. Page Navigation
page = st.sidebar.selectbox(
    "Choose Page",
    ["Ingest URL", "Ask Question"],
    index=1 if st.session_state.current_chat_id else 0
)

st.sidebar.divider()

# 2. Saved Chats List (Persisted in Sidebar)
st.sidebar.subheader("💬 Saved Chats")

if not st.session_state.chats:
    st.sidebar.caption("No active chats yet.")
else:
    # Iterate backwards to show newest first
    for chat_id in list(st.session_state.chats.keys())[::-1]:
        chat_data = st.session_state.chats[chat_id]
        
        with st.sidebar.container():
            col1, col2 = st.columns([4, 1])
            
            # Chat Title/URL
            with col1:
                # Truncate URL for display
                display_title = (chat_data['title'][:30] + '...') if len(chat_data['title']) > 30 else chat_data['title']
                
                # Button to load this chat
                if st.button(display_title, key=f"load_{chat_id}", use_container_width=True):
                    st.session_state.current_chat_id = chat_id
                    st.rerun()
            
            # Delete Button
            with col2:
                if st.button("🗑️", key=f"del_{chat_id}", help="Delete Chat"):
                    del st.session_state.chats[chat_id]
                    # If we deleted the active chat, reset active chat
                    if st.session_state.current_chat_id == chat_id:
                        st.session_state.current_chat_id = None
                    st.rerun()

# Optional: Show Database Stats (from previous logic)
try:
    stats_resp = requests.get(f"{API_URL}/stats")
    if stats_resp.status_code == 200:
        stats = stats_resp.json()
        st.sidebar.metric("Total Chunks", stats.get("points_count", 0))
except:
    pass

# --------------------------------------------------
# Page 1: Ingest URL
# --------------------------------------------------
if page == "Ingest URL":
    st.header("🔗 Ingest New URL")
    
    with st.form("ingest_form"):
        url = st.text_input("Enter URL to ingest", placeholder="https://example.com")
        submitted = st.form_submit_button("Ingest & Start Chat")
        
        if submitted and url:
            with st.spinner("Ingesting content..."):
                try:
                    # 1. Ingest to Backend
                    response = requests.post(f"{API_URL}/ingest", json={"url": url})
                    
                    if response.status_code == 200:
                        st.success("Ingestion Successful!")
                        
                        # 2. Create Local Chat Session
                        new_chat_id = create_new_chat_session(url)
                        
                        # 3. Switch to Ask Question page automatically
                        st.session_state.current_chat_id = new_chat_id
                        st.switch_page("app.py") # Forces page reload to switch view
                        # Alternatively, simply set a state and rerun, but switch_page is cleaner for selectbox updates
                        
                    else:
                        st.error(f"Error: {response.text}")
                except Exception as e:
                    st.error(f"Connection Error: {e}")

# --------------------------------------------------
# Page 2: Ask Question (Chat Interface)
# --------------------------------------------------
elif page == "Ask Question":
    
    # Check if a chat is active
    if st.session_state.current_chat_id is None:
        st.info("👈 Please select a chat from the sidebar or go to 'Ingest URL' to start.")
    else:
        # Load current chat data
        chat_data = st.session_state.chats[st.session_state.current_chat_id]
        current_url = chat_data['url']
        messages = chat_data['messages']
        
        # Header with "New Chat" button
        col1, col2, col3 = st.columns([6, 1, 1])
        with col1:
            st.subheader(f"Chatting about: {current_url}")
        with col2:
            if st.button("🔄 New"):
                # Just resets the view, does not delete history
                st.session_state.current_chat_id = None
                st.rerun()
        
        # 1. Display Chat History
        for msg in messages:
            with st.chat_message(msg["role"]):
                st.markdown(msg["content"])
                if "sources" in msg and msg["sources"]:
                    with st.expander("🔍 Sources"):
                        for source in msg["sources"]:
                            st.markdown(f"**[{source.get('title', 'Source')}]({source.get('source_url')})**")
                            st.caption(source.get('text', '')[:200] + "...")
                            st.divider()

        # 2. Chat Input
        if prompt := st.chat_input("Ask a question..."):
            # Display User Message immediately
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Add to history
            messages.append({"role": "user", "content": prompt})

            # Generate Response
            with st.chat_message("assistant"):
                with st.spinner("Thinking..."):
                    try:
                        # Backend call (Passing URL/Hash is optional here, 
                        # but good if you want to restrict search to this specific URL)
                        response = requests.post(
                            f"{API_URL}/ask",
                            json={
                                "query": prompt,
                                "url_hash": None # Set to specific hash if you implemented filtering
                            }
                        )
                        
                        if response.status_code == 200:
                            data = response.json()
                            answer = data.get("answer", "No answer found.")
                            sources = data.get("sources", [])
                            
                            st.markdown(answer)
                            
                            # Save to history
                            messages.append({
                                "role": "assistant", 
                                "content": answer,
                                "sources": sources
                            })
                        else:
                            st.error("Backend Error")
                            
                    except Exception as e:
                        st.error(str(e))

            # Update session state (required because we modified the list)
            st.session_state.chats[st.session_state.current_chat_id]["messages"] = messages
            