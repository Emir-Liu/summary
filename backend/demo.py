"""
检测大模型的连接情况
"""

# 加载系统环境变量
from dotenv import load_dotenv
load_dotenv()

# 加载模型
from langchain_openai import ChatOpenAI
llm = ChatOpenAI()

# 测试模型链接
from langchain_core.messages import HumanMessage
response = llm.invoke([HumanMessage(content='你好')])
print(f'res:{response.content}')