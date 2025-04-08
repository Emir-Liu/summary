"""
这里是使用langgraph构建workflow
"""

# 加载系统环境变量
from dotenv import load_dotenv
load_dotenv()

# 加载模型
from langchain_openai import ChatOpenAI
llm = ChatOpenAI()

# 构建图状态
from typing import Annotated

from typing_extensions import TypedDict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages


class State(TypedDict):
    # Messages have the type "list". The `add_messages` function
    # in the annotation defines how this state key should be updated
    # (in this case, it appends messages to the list, rather than overwriting them)
    messages: Annotated[list, add_messages]
    origin_content: str
    auto_outline: str
    human_outline: str
    new_content: str


graph_builder = StateGraph(State)

# 构建节点，初步生成大纲
from langchain_core.prompts import ChatPromptTemplate


def GenerateOutline(state:State):
    """
    生成初步的大纲,
    """
    org_content = state['origin_content']
    request = state['messages'][-1].content

    
    if state['messages']:
        content = f'根据下面的要求，将下面的文档分解为大纲结构：\n要求：{request}\n文档:{org_content}'
    else:
        content = f'将下面的文档分解为大纲结构:\n文档：{org_content}'
        
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            (
                'system',
                '将下面的内容从不同的角度划分初步的结构'
            ),
            (
                'user',
                '{text}'
            )
        ]
    )

    summary_chain = chat_prompt | llm
    outline = summary_chain.invoke(content)
    outline_content = outline.content
    return {'messages':[outline], 'auto_outline':outline_content}


# 构建节点，基于大纲内容，填充大纲
from langgraph.types import Command, interrupt

def fillOutline(state:State):
    """
    根据大纲，补充内容

    增加人工修复大纲的步骤
    """
    auto_outline = state['auto_outline']
    org_content = state['origin_content']

    
    
    human_outline_response = interrupt({'org_content':org_content,'auto_outline':auto_outline})
    print(f'human_outline_response:{human_outline_response}')
    human_outline_content = human_outline_response.get('outline',"")
    if human_outline_content:
        state['human_outline'] = human_outline_content
    else:
        state['human_outline'] = auto_outline
    human_outline = state['human_outline']
    
    
    content = f'原始文档内容：\n{org_content}\n大纲结构:\n{human_outline}\n'
    chat_prompt = ChatPromptTemplate.from_messages(
        [
            (
                'system',
                '从原始文档中获取相关内容，根据大纲的结构，将原始的段落分别填补到对应的结构下，使得每个部分都有足够的细节信息，重新生成一份新的文档，注意在生成的过程中，不要捏造信息，不要有主观判断'
            ),
            (
                'user',
                '{text}'
            )
        ]
    )

    chain = chat_prompt | llm

    new_content = chain.invoke({'text':content})

    new_content_content = new_content.content

    return {'messages':[new_content], 'new_content':new_content_content}


# 构建图结构
graph_builder.add_node('GenerateOutline',GenerateOutline)
graph_builder.add_node('fillOutline',fillOutline)

graph_builder.add_edge(START, 'GenerateOutline')
graph_builder.add_edge('GenerateOutline', 'fillOutline')
# graph_builder.add_conditional_edge('GenerateOutline', 'fillOutline')
graph_builder.add_edge('fillOutline', END)

memory = MemorySaver()
graph = graph_builder.compile(checkpointer=memory)