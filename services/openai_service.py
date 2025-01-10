### Updated openai_service.py
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI  # Updated import from the new package
from langchain.prompts import ChatPromptTemplate

load_dotenv()
# Initialize LangChain's ChatOpenAI
LLM = ChatOpenAI(model="gpt-4o-mini")

# Define the fitness chatbot's prompt template
prompt = ChatPromptTemplate.from_template(
    """
    You are a fitness chatbot that provides advice on workouts, nutrition, and fitness goals only.Remember whatever user tells you like name,fitness goal,progress remember everything what user told you.
    Be friendly and informative in your answers.Also suggest latest exercise video tutorial that are must available from youtube to every exercise you suggest according to question.Include the YouTube links directly in the response like this:
    "Here is the tutorial: https://www.youtube.com/watch?v=example".Also give nutrition infornation and advices.
    Do not use Markdown or nested links. Keep the response clean and user-friendly..Remember personal details of user remember everything user tell you.Accept only fitness related queries apologize friendly if any question other than fitness arrives. The user has asked the following question:
    {question}
    """
)

# Chain the prompt and LLM
chain = prompt | LLM

def fitness_chatbot(question):
    """
    Processes a fitness-related question and returns a response from the chatbot.
    """
    try:
        response = chain.invoke({"question": question})
        bot_response = response.content

         # Clean up any redundant or nested link formatting
        bot_response = bot_response.replace("[", "").replace("]", "").replace("(", "").replace(")", "")

        return bot_response
    except Exception as e:
        return f"An error occurred: {e}"       
    
    