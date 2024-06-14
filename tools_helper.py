from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
import re,dotenv,os
import json
import operator
from datetime import datetime
from langchain_experimental.tools import PythonREPLTool
from langchain_community.chat_models import ChatOllama
dotenv.load_dotenv()
model=ChatOllama(
    base_url=os.getenv("OLLAMA_BASE_URL","http://127.0.0.1:11434"),
    model=os.getenv("OLLAMA_MODEL","qwen2:1.5b") #模型用的qwen2
)



# 天气预报
# https://wttr.in/Shanghai?format=j1
@tool
def weather(city )->dict:
    """  the  input type is String  city english name, return weather info, if city is not provided, set the default city name  to  'Shanghai' use english name. """
    #if the city is not provided, set the default city name to 'Shanghai'
   
    url = f"https://wttr.in/{city}?format=j1"
    loader = WebBaseLoader(url)
    doc= loader.load()
    weatherjson= json.loads(doc[0].page_content)
    if weatherjson.get("output") is None:
        return weatherjson.get("current_condition")[0]
    else :
        return  weatherjson.get("output").get("current_condition")[0]




# 获取当前日期
@tool
def get_now(format: str = "%Y-%m-%d %H:%M:%S"):
    """
    Get the current time
    """
   
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


# 代码运行工具，输入需求，自动生成python代码，返回运行后的结果
@tool
def data_process(data: str) -> str:
    """
    输入需求描述，运行python代码后返回运行结果
    """
    
    prompt=PromptTemplate.from_template("""
     你是个数据分析师，请根据以下要求，直接生成python代码，供运行。   
     要求如下：
     {data}
    """)
    codechain={"data":RunnablePassthrough()}|prompt|model|StrOutputParser()
    code = codechain.invoke(data)
    return PythonREPLTool().run(code)


# 网站搜索工具
@tool
def search(question:str)->str:
    """  the  input type is String  question, return search result in web, 当你认为需要搜索时，可以使用这个工具，输入问题，返回搜索结果 """
    url = f"http://47.240.44.238:3000/search?query={question}"
    # print(url)
    try:
        loader = WebBaseLoader(url)
        doc= loader.load()
        return doc[0].page_content
    except Exception as e:
        return ''



# 显示图结构
def  display(runnable):
    from IPython.display import Image, display
    try:
        display(Image(runnable.get_graph(xray=True).draw_mermaid_png()))
    except Exception:
        # This requires some extra dependencies and is optional
        pass


def react_prompt():
    return PromptTemplate.from_template( """
        Answer the following questions as best you can. You have access to the following tools:

            {tools}

            Use the following format:

            Question: the input question you must answer

            Thought: you should always think about what to do

            Action: the action to take, should be one of [{tool_names}]

            Action Input: the input to the action

            Observation: the result of the action

            ... (this Thought/Action/Action Input/Observation can repeat N times)

            Thought: I now know the final answer

            Final Answer: the final answer to the original input question

            Begin!

            Question: {input}

            Thought:{agent_scratchpad}
            """)

def  react_chat_prompt():
    return PromptTemplate.from_template( """
        Assistant is a large language model trained by OpenAI.

            Assistant is designed to be able to assist with a wide range of tasks, from answering simple questions to providing in-depth explanations and discussions on a wide range of topics. As a language model, Assistant is able to generate human-like text based on the input it receives, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.

            Assistant is constantly learning and improving, and its capabilities are constantly evolving. It is able to process and understand large amounts of text, and can use this knowledge to provide accurate and informative responses to a wide range of questions. Additionally, Assistant is able to generate its own text based on the input it receives, allowing it to engage in discussions and provide explanations and descriptions on a wide range of topics.

            Overall, Assistant is a powerful tool that can help with a wide range of tasks and provide valuable insights and information on a wide range of topics. Whether you need help with a specific question or just want to have a conversation about a particular topic, Assistant is here to assist.

            TOOLS:

            ------

            Assistant has access to the following tools:

            {tools}

            To use a tool, please use the following format:

            ```

            Thought: Do I need to use a tool? Yes

            Action: the action to take, should be one of [{tool_names}]

            Action Input: the input to the action

            Observation: the result of the action

            ```

            When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

            ```

            Thought: Do I need to use a tool? No

            Final Answer: [your response here]

            ```

            Begin!

            Previous conversation history:

            {chat_history}

            New input: {input}

            {agent_scratchpad}
            """
    )


def  main():
    # python_repl_tool测试
    python_repl_tool = PythonREPLTool()
    pythoncode = """
    print("Hello, World!")
    """


    print(python_repl_tool.run(pythoncode))

if __name__ == '__main__':
    main()