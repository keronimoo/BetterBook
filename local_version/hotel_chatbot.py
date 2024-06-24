import streamlit as st
import sqlite3
import requests
import re

def extract_sql_query(text):
    # Use regular expression to extract the SQL query inside triple quotes
    match = re.search(r"```(.*?;?)```", text, re.DOTALL)
    
    if match:
        print("match found")
        return match.group(1).strip()
    else:
        print(text)
        return "cant extract"

def is_valid_query(database , query):

    query = extract_sql_query(query)
    try:
        # Connect to the SQLite database
        connection = sqlite3.connect(database)

        # Create a cursor object to execute SQL queries
        cursor = connection.cursor()

        # Execute the query
        cursor.execute(query)
        print("executed succesfully")
        # Fetch the result if needed
        result = cursor.fetchall()

        # Print or process the result

        print(result)

        return True

    except sqlite3.Error as e:

        print(f"Error executing the query: {e}")
        print(query)

        # Return False to indicate failure
        return False        
    finally:
        # Close the cursor and connection
        cursor.close()
        connection.close()


st.title("Assistant")

# Initialize the chat messages history
if "messages" not in st.session_state.keys():
    st.session_state.messages = [
        {"role": "assistant", "content": "How can I help?"}
    ]

# Prompt for user input and save
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})

# Display the prior chat messages
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


if st.session_state.messages[-1]["role"] != "assistant":
 
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            #API call
            api_url = "https://localhost:7197/chat"  
            prompt = st.session_state.messages[-1]["content"]
            response = requests.post(api_url, data=prompt , verify=False).json()
            response = response.replace("|" , "")
            response = response.replace("Bob:", "").replace("User:", "")

            if(is_valid_query(database='C:/Users/kerem/Desktop/llmhotel/Db/Hotel.db', query=response)==False):
                validate_string ="""Something is wrong Check the followings and return a correct query:
                Keywords and Clauses: Ensure that SQL keywords and clauses are spelled correctly and used in the right context. For example, make sure you're using correct keywords like SELECT, FROM, WHERE, etc.
                Quotes and Strings: Check if you have properly closed all string literals (single or double quotes). If you're using single quotes to define strings, ensure that you close them properly.
                Column and Table Names: Verify that column and table names are correct and exist in the database.
                """
                response = requests.post(api_url , data=validate_string , verify=False).json()
                response = response.replace("|" , "")
                response = response.replace("Bob:", "").replace("User:", "")
                st.write(response)
            else:
                st.write(response)  

    # Add the response to the chat history
    message = {"role": "assistant", "content": response}
    st.session_state.messages.append(message)
