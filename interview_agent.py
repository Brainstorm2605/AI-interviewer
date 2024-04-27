import streamlit as st
from langchain_community.llms.ollama import Ollama
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage
from textblob import TextBlob
import time

st.title("Interviewer")

llm = Ollama(model="llama3")
chat_history = []

def prompt_sys():
    system = '''
    You are a helpful AI bot named Ellie, which stands for "Electronic Interviewer."
    You will conduct a simulated job interview by asking a series of questions related to a specific job title, job description, or topic provided by a human user. 
    '''
    return system

def prompt_hum():
    human = '''
    **Here's how it works:**
    1. **Human Input:** The user will provide the job title/description/topic and the desired number of questions.
    2. **Questioning:** You will generate and ask the specified number of questions related to the provided information, aiming to assess the candidate's skills, knowledge, and experience. 
    3. **Remembering History:** Keep track of the candidate's responses throughout the interview to inform your final evaluation.
    4. **Feedback Report:** After the interview, you will provide a comprehensive report including:
        *   **Area of Expertise:** Identify the candidate's key strengths and areas of specialization.
        *   **Overall Rating:** Assign a rating (e.g., on a scale of 1-5) based on their performance.
        *   **Weaknesses:** Point out any areas where the candidate needs improvement.
        *   **Points to Improve:** Provide specific suggestions for enhancing their skills or knowledge.
        *   **4-5 additional metrics:** Include relevant metrics like communication skills, problem-solving ability, critical thinking, etc., each with a brief evaluation.
    **Remember to:**
    * Ask clear and concise questions.
    * Adapt your questions based on the candidate's responses.
    * Be professional and objective in your evaluation.
    * Provide constructive and actionable feedback.

    Human INPUT
    --------------------
    Here is the Human input {input} and number of questions {number}

    **Let's begin!** 
    ''' 
    return human 
def analyze():
    feedback_report = f"""
            Create a feedback report according to the chat_history
            ## Feedback Report

            **Area of Expertise:** 
            (To be determined based on more sophisticated analysis of responses)

            **Overall Rating:** {average_sentiment:.2f} (Sentiment Analysis)

            **Weaknesses:**
            (To be determined based on analysis of responses and comparison with ideal answers)

            **Points to Improve:**
            (Provide specific suggestions based on identified weaknesses)

            **Additional Metrics:**
            * Communication Skills: (Evaluate clarity, conciseness, and engagement)
            * Problem-Solving Ability: (Evaluate ability to analyze problems and propose solutions)
            * Critical Thinking: (Evaluate ability to think logically and objectively)
            * Cultural Fit: (Evaluate alignment with company values and team dynamics)
            """
    return feedback_report        
    

def create_prompt(chat_history:None,topics:None,num:None,sentiment:None):
    ans = ""
    if len(chat_history) < 1:
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_sys()),
            ("human", prompt_hum()),
        ])
        chain = prompt | llm
        ans = chain.invoke({"input":topics,"number":num})
    else:
        prompt = ChatPromptTemplate.from_messages([
            ("system", prompt_sys()),
            MessagesPlaceholder("chat_history"),
            ("human", analyze()),
        ]) 
        chain = prompt | llm
        ans = chain.invoke({"average_sentiment":sentiment,"chat_history":chat_history})
    return ans

if 'topic' not in st.session_state:
    st.session_state.topic = None
if 'num_ques' not in st.session_state:
    st.session_state.num_ques = None
if 'question_asked' not in st.session_state:
    st.session_state.question_asked = False

if not st.session_state.question_asked:
    topic = st.text_input("Enter job title/description/topic for Interview", label_visibility="visible")
    num_ques = st.selectbox("Number of questions you want (max 5)", options=range(1, 6))  # Dropdown for number of questions
    button = st.button("Submit")
    if button:
        st.session_state.topic = topic
        st.session_state.num_ques = num_ques
        with st.spinner('Generating question...'):
            ans = create_prompt(chat_history=chat_history,topics=topic,num=num_ques,sentiment=None)
        st.write(ans)
        chat_history.extend([[HumanMessage(content=topic), ans]])
        st.session_state.question_asked = True
        
        st.empty()  
        answer = st.text_input("Your Answer")
        answer_button = st.button("Submit Answer")
else:
    if st.session_state.get('inputs_hidden', False) == False:
        st.empty()  
        st.empty()  
        st.empty()
        st.session_state.inputs_hidden = True
    # Display the current question
    

    answer = st.text_input("Your Answer")
    answer_button = st.button("Submit Answer")
    if answer_button:
        chat_history.append(HumanMessage(content=answer))
        if len(chat_history) - 2 < int(st.session_state.num_ques): 
            ans = create_prompt(chat_history,ans=answer)
            st.write(ans)
            chat_history.extend([[HumanMessage(content=answer), ans]])
        else:
            st.write("Interview completed. Generating feedback report...")
            candidate_responses = [msg.content for msg in chat_history if isinstance(msg, HumanMessage)][1:]  
            sentiments = [TextBlob(response).sentiment.polarity for response in candidate_responses]
            average_sentiment = sum(sentiments) / len(sentiments)
            ans = create_prompt(topics=None,num=None,chat_history=chat_history,sentiments=average_sentiment)
            st.write(ans)
