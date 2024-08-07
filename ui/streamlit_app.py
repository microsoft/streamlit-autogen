import streamlit as st
import asyncio
from autogen import AssistantAgent, UserProxyAgent

st.write("""# AutoGen Chat Agents""")

class TrackableAssistantAgent(AssistantAgent):
    def _process_received_message(self, message, sender, silent):
        with st.chat_message(sender.name):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)


class TrackableUserProxyAgent(UserProxyAgent):
    def _process_received_message(self, message, sender, silent):
        with st.chat_message(sender.name):
            st.markdown(message)
        return super()._process_received_message(message, sender, silent)


deploy_model = None
api_key = None
api_version = None
azure_endpoint = None
with st.sidebar:
    st.header("Azure OpenAI Configuration")
    azure_endpoint = st.text_input("Azure Endpoint")
    api_version = "2024-02-15-preview"
    #api_version = st.selectbox("Model", ['gpt-3.5-turbo', 'gpt-4'], index=1)
    api_key = st.text_input("API Key", type="password")
    deploy_model = st.text_input("Deployment Model")

with st.container():
    # for message in st.session_state["messages"]:
    #    st.markdown(message)

    user_input = st.chat_input("Give some goal for the agent ...")
    if user_input:
        if not api_key or not deploy_model or not azure_endpoint:
            st.warning(
                'You must provide valid Azure OpenAI API key and choose the deployment', icon="⚠️")
            st.stop()

        llm_config = {
            #"request_timeout": 600,
            "config_list": [
                {
                    "api_type": "azure",
                    "base_url": azure_endpoint,
                    "api_version": api_version,
                    "model": deploy_model,
                    "api_key": api_key
                },
            ],
               "cache_seed": None,
        }

        # create an AssistantAgent instance named "assistant"
        assistant = TrackableAssistantAgent(
            name="assistant", llm_config=llm_config)

        # create a UserProxyAgent instance named "user"
        user_proxy = TrackableUserProxyAgent(
            name="user", human_input_mode="NEVER", llm_config=llm_config)

        # Create an event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        # Define an asynchronous function
        async def initiate_chat():
            await user_proxy.a_initiate_chat(
                assistant,
                message=user_input,
            )

        # Run the asynchronous function within the event loop
        loop.run_until_complete(initiate_chat())