
import json

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse

from langgraph.types import Command, interrupt

from pydantic import BaseModel

from workflow import graph

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*']
)

@app.get('/')
async def root():
    return {'message':'hello'}


class BuildOutlineRequest(BaseModel):
    """
    thread_id:用于持久化数据
    origin_content:用于获取原始的会议内容
    user_cmd:用于获取定制化需求
    """
    thread_id: int
    origin_content: str
    user_cmd: str


# @app.post('/build_outline')
# async def build_outline(buildoutline_request:BuildOutlineRequest):
@app.get('/build_outline')
async def build_outline(thread_id:str, origin_content:str, user_cmd:str):
    # thread_id = buildoutline_request.thread_id
    # origin_content = buildoutline_request.origin_content
    # user_cmd = buildoutline_request.user_cmd
    config = {"configurable": {"thread_id": str(thread_id)}}

    async def event_stream():
        total_content = ''
        for msg, metadata in graph.stream(
            {
                'messages':[
                    {
                        'role':'user',
                        'content': user_cmd
                    }
                ],
                'origin_content':origin_content,
            },
            config,
            stream_mode = 'messages'
        ):
            total_content += msg.content
            print(f'total content:{total_content}')
            ret_json = {
                'status':'generating',
                'content': total_content
            }
            yield f'data:{json.dumps(ret_json, ensure_ascii=False)}\n\n'

        ret_json = {
            'status':'finished',
            'content': total_content
        }
        yield f'data:{json.dumps(ret_json, ensure_ascii=False)}\n\n'
            
    return StreamingResponse(event_stream(), media_type="text/event-stream")

@app.get('/build_report')
async def build_report(thread_id:str, human_response:str):
    config = {"configurable": {"thread_id": str(thread_id)}}
    human_command = Command(resume={"outline": human_response})

    # events = graph.stream(human_command, config, stream_mode = 'messages')
    # for msg, metadata in graph.stream(human_command, config, stream_mode = 'messages'):
    #     print(f'msg:{msg}')
    #     if "messages" in event:
    #         event["messages"][-1].pretty_print()

    async def event_stream():
        total_content = ''
        for msg, metadata in graph.stream(
            human_command,
            config,
            stream_mode = 'messages'
        ):
            total_content += msg.content
            print(f'total content:{total_content}')
            ret_json = {
                'status': 'generating',
                'content': total_content
            }
            yield f'data:{json.dumps(ret_json, ensure_ascii=False)}\n\n'
        
        ret_json = {
            'status': 'finished',
            'content': total_content
        }
        yield f'data:{json.dumps(ret_json, ensure_ascii=False)}\n\n'
    
    return StreamingResponse(event_stream(), media_type="text/event-stream")