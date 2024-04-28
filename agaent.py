import streamlit as ui
from langchain_community.llms.ollama import Ollama
from langchain.prompts import PromptTemplate
from langchain.memory import ConversationBufferMemory
from langchain.chains.llm import LLMChain

    
llm = Ollama(model="llama3")

template = """You are a nice chatbot having a conversation with a human.

Previous conversation:
{chat_history}

New human question: {question}
Response:"""

prompt = PromptTemplate.from_template(template)
memory = ConversationBufferMemory(memory_key="chat_history")
conversation = LLMChain(llm=llm,verbose = True,memory=memory,prompt=prompt)



input = ui.text_input("Input")
button = ui.button("sub")
hist = ""
if button:
    
    ans = conversation.invoke({"question": input},{"chat_history":hist})
    hist = ans['text']
    memory.chat_memory.add_user_message("hi!")
    memory.chat_memory.add_ai_message("what's up?")
    ui.write(ans['text'])
