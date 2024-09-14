from __future__ import annotations

import asyncio
import os
import random
import uuid
from typing import List, AsyncGenerator

import streamlit as st
from dotenv import load_dotenv

from ChatClient import ChatClient, Request
from Schema import ChatMessage

load_dotenv()


async def draw_messages(
        messages_agen: List[ChatMessage],
        is_new=False,
):
    last_message_type = None
    st.session_state.last_message = None

    # Placeholder for intermediate streaming tokens
    streaming_content = ""
    streaming_placeholder = None

    # Iterate over the messages and draw them
    for msg in messages_agen:
        if msg is None:
            break
        # str message represents an intermediate token being streamed
        if isinstance(msg, str):
            # If placeholder is empty, this is the first token of a new message
            # being streamed. We need to do setup.
            if not streaming_placeholder:
                if last_message_type != "ai":
                    last_message_type = "ai"
                    st.session_state.last_message = st.chat_message("ai")
                with st.session_state.last_message:
                    streaming_placeholder = st.empty()

            streaming_content += msg
            streaming_placeholder.write(streaming_content)
            continue

        if not isinstance(msg, ChatMessage):
            st.error(f"Unexpected message type: {type(msg)}")
            st.write(msg)
            st.stop()

        if msg.who == "human":
            last_message_type = "human"
            st.chat_message("human").write(msg.content)

        if msg.who == "ai":
            # If we're rendering new messages, store the message in session state
            if is_new:
                st.session_state.messages.append(msg)

            # If the last message type was not AI, create a new chat message
            if last_message_type != "ai":
                last_message_type = "ai"
                st.session_state.last_message = st.chat_message("ai")

            with st.session_state.last_message:
                # If the message has content, write it out.
                # Reset the streaming variables to prepare for the next message.
                if msg.content:
                    if streaming_placeholder:
                        streaming_placeholder.write(msg.content)
                        streaming_content = ""
                        streaming_placeholder = None
                    else:
                        st.write(msg.content)


@st.cache_resource
def get_agent_client(url):
    return ChatClient(url)

def clear_chat():
    st.session_state.messages = []


async def main():
    APP_TITLE = "Whatsapp Clone"
    APP_ICON = "🧩"
    st.set_page_config(
        page_title=APP_TITLE,
        page_icon=APP_ICON,
        menu_items={},
    )
    # Hide the streamlit upper-right chrome
    st.html(
        """
        <style>
        [data-testid="stStatusWidget"] {
                visibility: hidden;
                height: 0%;
                position: fixed;
            }
        </style>
        """,
    )
    if st.get_option("client.toolbarMode") != "minimal":
        st.set_option("client.toolbarMode", "minimal")
        await asyncio.sleep(0.1)
        st.rerun()

    # Config options
    with st.sidebar:
        st.header(f"{APP_ICON} {APP_TITLE}")
        ""
        "Whatsapp Clone: Feito para testes local"

        options = {
            "default": 1,
            "custom": 2
        }

        with st.popover(":material/settings: Settings", use_container_width=True):
            session_option = options[st.radio("Session Option", options=options.keys())]

            if session_option == 1:
                st.session_state.session_id = str(uuid.uuid4())
            else:
                st.session_state.session_id = st.text_input("Session Id", type="default")

            m = st.radio("Service to use", options=options.keys())
            option = options[m]
            if option == 1:
                st.session_state.service_url = os.getenv("SERVICE_URL")
            else:
                st.session_state.service_url = st.text_input("Service Url", type="default")


        st.button("Limpar chat", on_click=clear_chat, type="primary")


    # Draw existing messages
    if "messages" not in st.session_state:
        st.session_state.messages = []
    messages: List[ChatMessage] = st.session_state.messages


    if len(messages) == 0:
        WELCOME = "Oi! Seja bem vindo ao Whatsapp Clone"
        with st.chat_message("ai"):
            st.write(WELCOME)

    if len(messages) > 0:
        await draw_messages(messages)

    if input := st.chat_input(placeholder=""):
        session_id = st.session_state.session_id

        messages.append(ChatMessage(who="human", content=input))
        st.chat_message("human").write(input)
        client = get_agent_client(st.session_state.service_url)

        try:
            response = client.invoke(
                request=Request(message=input),
                session_id=session_id,
            )
            messages.append(ChatMessage(who="ai", content=response.content))
            st.chat_message("ai").write(response.content)

            st.rerun()
        except Exception as e:
            st.chat_message("ai").write(f"Ocorreu um erro! {e}")


if __name__ == "__main__":
    asyncio.run(main())
