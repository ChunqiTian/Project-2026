

import streamlit as st

from app.router_8 import handle_message
from app.ui_helpers_5 import (response_to_dict, get_risk_badge_text, get_action_badge_text, 
                              format_confidence, normalize_citations)
from app.schemas_1 import ConversationState
st.set_page_config(page_title="Medical Chatbot Demo", page_icon= "🩺", layout="wide")
st.title("Medical Chatbot Demo")
st.caption("This chatbot provides general health information from approved evidence. "
           "It does not provide a medical diagnosis, treatment plan, or emergency care. ")

# Safety boundary banner
st.warning(
    """
    **Important note: **
    This app is for general educational information only. 
    It is **not a medical diagnosis** and does not replace a doctor, pharmacist, nurse, or emergency service. 
    """
)

# Session state
if "messages" not in st.session_state: st.session_state.messages = []
if "debug_enabled" not in st.session_state: st.session_state.debug_enabled = False
if "conversation_state" not in st.session_state: 
    st.session_state.conversation_state = ConversationState()

# Sidebar
with st.sidebar:
    st.header("Transparency Controls")
    st.session_state.debug_enabled = st.checkbox(
        "show debug / evidence panel",
        value = st.session_state.debug_enabled,
    )
    st.markdown("---")
    st.subheader("What this bot can do")
    st.write(
        """
        - Explain general health topics
        - Use aproved knowledge base evidence
        - Show citations when avvailable
        - Refuse unsafe medical requests
        - Escalate urgent or high-risk messages
        """
    )

    st.subheader("What this bot cannot do")
    st.write(
        """
        - Diagnose you
        - Prescribe medicine
        - Change medication doses
        - Replace a licensed clinician
        - Handle emergencies
        """
    )

# Existing chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

        if message["role"] == "assistant" and "metadata" in message:
            metadata = message["metadata"]
            risk_level = metadata.get("risk_level")
            action = metadata.get("action")
            confidence = metadata.get("confidence")
            citations = normalize_citations(metadata.get("citations"))

            col1, col2, col3 = st.columns(3)
            with col1: st.info(get_risk_badge_text(risk_level))
            with col2: st.info(get_action_badge_text(action))
            with col3: st.info(format_confidence(confidence))

            if citations:
                with st.expander("Citations"):
                    for citation in citations: 
                        st.write(citation)
            if metadata.get("needs_human"):
                st.error("This question may need help from a qualified medical professional.")
            if st.session_state.debug_enabled:
                with st.expander("Debug / evidence details"):
                    st.json(metadata)

# Chat input
user_text = st.chat_input("Ask a general health question...")
if user_text:
    # Save and display user message
    st.session_state.messages.append(
        {
            "role": "user", 
            "content": user_text, 
        }
    )
    with st.chat_message("user"):
        st.markdown(user_text)

    # Run chatbot
    response, st.session_state.conversation_state = handle_message(
        user_text,
        state=st.session_state.conversation_state,
        return_state=True,
    )
    response_data = response_to_dict(response)
    answer = response_data.get("answer", "I could not generate an answer.")
    # Save assistant message
    st.session_state.messages.append(
        {
            "role": "assistant", 
            "content": answer, 
            "metadata": response_data,
        }
    )

    # Display assistant message
    with st.chat_message("assistant"):
        st.markdown(answer)
        risk_level = response_data.get("risk_level")
        action = response_data.get("action")
        confidence = response_data.get("confidence")
        citations = normalize_citations(response_data.get("citations"))

        col1, col2, col3 = st.columns(3)
        with col1: st.info(get_risk_badge_text(risk_level))
        with col2: st.info(get_action_badge_text(action))
        with col3: st.info(format_confidence(confidence))

        # Escalation / safety message
        if response_data.get("needs_human"):
            st.error("This question may need help from a qualified medical professional.")
        if action in ["escalate", "emergency"]:
            st.error(
                """
                **Escalation recommended:**
                If this may be urgent, contact local emergency services or a qualified medical professional immediately.
                """
                )
        if action == "refuse":
            reason = response_data.get("reason")
            st.warning(
                f"This request was refused for safety reason. Reason: {reason}"
                if reason
                else "This request was refused for safety reasons."
            )

        # Citations
        if citations:
            with st.expander("Citations"):
                for citation in citations: 
                    st.write(citation)

        # Debug panel
        if st.session_state.debug_enabled:
            with st.expander("Debug / evidence details"):
                st.json(response_data)






