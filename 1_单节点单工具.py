
from typing import Annotated, TypedDict, Union
from langgraph.graph import END, StateGraph
from langchain_core.messages import BaseMessage
from langchain_core.agents import AgentAction, AgentFinish
from langgraph.prebuilt.tool_node import ToolNode
from langgraph.prebuilt import ToolExecutor, ToolInvocation
import operator
from langchain import hub
from langchain.agents import create_react_agent  
# from langgraph.prebuilt import create_react_agent # 不支持bind_tools
from tools_helper import *
import os


# 绑定工具
tools=[weather,get_now,data_process]
tool_executor = ToolExecutor(tools)
prompt = hub.pull("hwchase17/react")
agent_runnable  = create_react_agent(model, tools, prompt)


class AgentState(TypedDict):
    input: str
    chat_history: list[BaseMessage]
    agent_outcome: Union[AgentAction, AgentFinish, None]
    intermediate_steps: Annotated[list[tuple[AgentAction, str]], operator.add]

def execute_tools(state):
    messages = [state["agent_outcome"]]
    last_message = messages[-1]
    tool_name = last_message.tool
    action = ToolInvocation(
        tool=tool_name,
        tool_input=last_message.tool_input,
    )
    response = tool_executor.invoke(action)
    return {"intermediate_steps": [(state["agent_outcome"], response)]}


def run_agent(state):
    agent_outcome = agent_runnable.invoke(state)
    return {"agent_outcome": agent_outcome}


def should_continue(state):
    messages = [state["agent_outcome"]]
    last_message = messages[-1]
    if "Action" not in last_message.log:
        return "end"
    else:
        return "continue"


workflow = StateGraph(AgentState)
workflow.add_node("agent", run_agent)
workflow.add_node("action", execute_tools)

workflow.set_entry_point("agent")
workflow.add_conditional_edges(
    "agent", should_continue, {"continue": "action", "end": END}
)


workflow.add_edge("action", "agent")
app = workflow.compile()


input_text = input("请输入问题：")
inputs = {"input": input_text, "chat_history": []}
output= app.invoke(inputs)
answer= output['agent_outcome'].log.split('Final Answer')[1]
print(answer)

  

