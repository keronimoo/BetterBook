
from app.prompts import CLAUDE_SYSTEM_PROMPT , GEMINI_SYSTEM_PROMPT , PROMPT_TO_PROMPT , OPENAI_SYSTEM_PROMPT
from app import gemini , antClient ,client 
import re
import pandas as pd
import sqlite3
import requests
from dotenv import load_dotenv
import os
from colorama import Fore

load_dotenv()

databaseuri = os.getenv('DATABASE_URI')
databaseuri = databaseuri.replace("sqlite:///" , "")

# mystring = PROMPT_TO_PROMPT.substitute(user_prompt="find me an hotel in london")
# print(mystring)

# mystring2 = OPENAI_SYSTEM_PROMPT.substitute(user_question="find me an hotel in germany")
# print(mystring2)

def bot_sql_engine(prompt):
    completion = client.chat.completions.create(
        # model="gpt-3.5-turbo-1106",
        model = "gpt-4o",
        messages=[
            {"role": "system", "content": OPENAI_SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    response = completion.choices[0].message.content
    #print(completion.choices[0].message.content)
    sql_match = re.search(r"```sql\n(.*)\n```", response, re.DOTALL)
    #print(sql_match)
    # if(sql_match):
    #     sql = sql_match.group(1)
    #     print("GPT SQL:")
    #     print(sql)
    sql = sql_match.group(1)
    print("DEBUG SQL:" , sql)
    return sql

def execute_sql(sql , prompt , iteration):
    # conn = sqlite3.connect("C:/Users/kerem/Desktop/llmhotel/llm-integrated-hotel-app/demo.db")
    conn = sqlite3.connect(databaseuri)
    cursor = conn.cursor()
    cursor.execute(sql)
    results = cursor.fetchall()
    print("DEBUG: execute_sql" , results)
    conn.close()
    print(Fore.RED + "DEBUG: RESULTS COUNT" , len(results)==0)
    print(Fore.RESET)
    if(iteration !=0):
        if(len(results)==0):
            iteration_prompt = f"For this question: \n{prompt} following sql is generated: \n{sql} and failed to find a proper hotel. Provide correct SQL"
            print("DEBUG: ITERATION PROMPT" ,iteration_prompt)
            corrected_iteration = bot_sql_engine(iteration_prompt)
            iteration = iteration - 1
            print("DEBUG ITERATION NUMBER:" , iteration)
            print("DEBUG: CORRECTED ITERATION SQL" , corrected_iteration)
            execute_sql(corrected_iteration , prompt , iteration)
    return results
def bot_prompt_2_prompt(prompt):
    completion = client.chat.completions.create(
        # model="gpt-3.5-turbo-1106",
        model = "gpt-4o",
        messages=[
            {"role": "system", "content": PROMPT_TO_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )
    response = completion.choices[0].message.content
    print("DEBUG: P2P" , response)
    return response

resp3 = bot_prompt_2_prompt("tell me about hotels in USA")
resp  = bot_sql_engine(resp3)
resp2 = execute_sql(resp ,resp3 ,2)

def claude_context_decider(prompt):
    claudemessage = antClient.messages.create(
    #model="claude-3-opus-20240229",
    model="claude-3-haiku-20240307",
    max_tokens=1000,
    temperature=0,
    system=CLAUDE_SYSTEM_PROMPT,
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
    return clauderesponse

def send_email(subject, from_email, from_name, to_email, body_html, body_text):
    api_key = os.getenv('ELASTIC_EMAIL_API')
    data = {
        'apikey': api_key,
        'subject': subject,
        'from': from_email,
        'fromName': from_name,
        'to': to_email,
        'bodyHtml': body_html,
        'bodyText': body_text,
        'isTransactional': True
    }
    response = requests.post('https://api.elasticemail.com/v2/email/send', data=data)
    return response.json()