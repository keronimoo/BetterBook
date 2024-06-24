import streamlit as st
import sqlite3
from openai import OpenAI
import anthropic
import google.generativeai as gemini
import re
import pandas as pd


st.set_page_config(page_title="BetterBook" , menu_items={'About': "# This is a header. This is an *extremely* cool app!"})
st.sidebar.success('Select a page Above')
client = OpenAI(api_key=st.secrets.OPENAI_API_KEY)
antClient = anthropic.Anthropic(api_key=st.secrets.ANTHROPIC_API_KEY)
gemini.configure(api_key=st.secrets.GEMINI_API_KEY)

with st.sidebar:
    st.title("BetterBook")
    st.subheader('Parameters')
    temperature = st.sidebar.slider('temperature', min_value=0.01, max_value=5.0, value=0.1, step=0.01)
    top_p = st.sidebar.slider('top_p', min_value=0.01, max_value=1.0, value=0.9, step=0.01)
    max_length = st.sidebar.slider('max_length', min_value=64, max_value=4096, value=512, step=8)

# Initialize the chat messages history

if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "system", "content": st.secrets["OPENAI_SYSTEM_PROMPT"]["system_prompt"]}]

# Prompt for user input and save
if prompt := st.chat_input():
    claudemessage = antClient.messages.create(
    #model="claude-3-opus-20240229",
    model="claude-3-haiku-20240307",
    max_tokens=1000,
    temperature=0,
    system=st.secrets["CLAUDE_SYSTEM_PROMPT"]["system_prompt_claude"],
    messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"{prompt}"
                    }
                ]
            }
        ]
    )
    clauderesponse=(claudemessage.content[0].text).replace("[", "").replace("]", "")
    if(clauderesponse=="Hotel"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        print(clauderesponse)
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        st.session_state.messages.append({"role": "assistant", "content": "Travel context is under developemnt"})
        print(clauderesponse)

    #st.session_state.messages.append({"role": "user", "content": prompt})

# display the existing chat messages
for message in st.session_state.messages:
    if message["role"] == "system":
        continue
    with st.chat_message(message["role"]):
        st.write(message["content"])
        if "results" in message:
            st.dataframe(message["results"])
            
def clear_chat_history():
    st.session_state.messages = [{"role": "system", "content": st.secrets["OPENAI_SYSTEM_PROMPT"]["system_prompt"]}]
st.sidebar.button('Clear Chat History', on_click=clear_chat_history)

if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = ""
            resp_container = st.empty()
            for delta in client.chat.completions.create(
                model="gpt-3.5-turbo-1106",
                messages=[{"role": m["role"], "content": m["content"]} for m in st.session_state.messages],
                stream=True,
            ):
                response += (delta.choices[0].delta.content or "")
                resp_container.markdown(response)

            message = {"role": "assistant", "content": response}
            # Parse the response for a SQL query and execute if available
            sql_match = re.search(r"```sql\n(.*)\n```", response, re.DOTALL)
            if sql_match:
                sql = sql_match.group(1)
                print("GPT SQL:")
                print(sql)
                conn = st.connection("Hotel_Db" ,"sql")
                res = conn.query(sql)
                #while olcak gelecekte find hotels in Nondon diyince nondonu London olarak düzeltiyor amaç
                if(len(res)==0):
                    model = gemini.GenerativeModel(
                        model_name="gemini-1.5-pro-latest",
                        system_instruction=st.secrets["GEMINI_SYSTEM_PROMPT"]["system_prompt_gemini"]
                                            )
                    response = model.generate_content(f"{sql}")
                    print("GEMINI SQL")
                    print(response.text)
                    sql = response.text #yeni
                #message["results"] = conn.query(sql) res gelcek
                message["results"] = conn.query(sql)
                st.dataframe(message["results"])
                print(pd.DataFrame(message["results"]).to_string())
                with st.container(border=True):
                    for index, row in message["results"].iterrows():
                        with st.container(border=True):
                            st.image('https://i.pinimg.com/736x/6f/c9/a2/6fc9a2e11f72bc594eeec013c4c2e60d.jpg', width=200)
                            hotel_name = row['name']
                            city = row['city']
                            rating = row['rating']
                            st.write(f"Hotel Name: {hotel_name}, City: {city}, Rating: {rating}")
                            st.link_button(label="Show", url="https://streamlit.io/gallery", type="primary")
                    
            st.session_state.messages.append(message)
