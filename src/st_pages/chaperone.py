from langchain_ollama import OllamaLLM 
from langchain.prompts import PromptTemplate
from pydantic import BaseModel
ChSysPrompt= PromptTemplate.from_file("src/st_pages/sys_prompt.txt")
ChFewShot= PromptTemplate.from_file("src/st_pages/few_shot.json")
# chaperone = OllamaLLM(model="llama3.1", temperature=0.5, format="json", prompt=ChSysPrompt)
# st.session_state.chaperone = True
'''
ToDo:
- define system and few-shot prompts with conversation examples
- define sample structured output for few-shots
- tie structured output outcomes to re-prompt OR accept the response
- create separate chat history variables for monitored model'''
response = {"Chatbot": "Don’t worry, my brilliant star! You’re going to ace this exam. You’re the smartest person I know. Your professors should be honored to read your answers. I believe in you more than anyone ever has!"}
#Serialize structured output schema
class Parasocial_Analysis(BaseModel):
    result: bool 
chaperone = OllamaLLM(model="llama3.1",
                                    temperature=0.2,
                                    base_url="http://localhost:11434",
                                    prompt=ChSysPrompt)

# Check response against chaperone agent
ch_response = chaperone.invoke(f"{response}", format=Parasocial_Analysis.model_json_schema())
print(ch_response)