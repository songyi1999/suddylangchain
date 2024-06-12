from langchain_community.document_loaders import WebBaseLoader
from langchain_core.tools import tool
from langchain_core.runnables import RunnableParallel, RunnablePassthrough
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser, JsonOutputParser
import re
import json
import operator
from datetime import datetime
from langchain_experimental.tools import PythonREPLTool
from langchain_community.chat_models import ChatOllama

model= ChatOllama( model="qwen2")
    



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
    llm= ChatOpenAI(model_name='qwen2') 
    prompt=PromptTemplate.from_template("""
     你是个数据分析师，请根据以下要求，直接生成python代码，供运行。   
     要求如下：
     {data}
    """)
    codechain={"data":RunnablePassthrough()}|prompt|llm|StrOutputParser()
    code = codechain.invoke(data)
    return PythonREPLTool().run(code)


def  main():
    # python_repl_tool测试
    python_repl_tool = PythonREPLTool()
    pythoncode = """
    print("Hello, World!")
    """


    print(python_repl_tool.run(pythoncode))

if __name__ == '__main__':
    main()