from volcenginesdkarkruntime import Ark
from volcenginesdkarkruntime.types.chat import ChatCompletion
import json
import os
import dotenv

dotenv.load_dotenv()


class DoubaoAPI:
    def __init__(self):
        self.tools = dict[str, dict]()
        self.prompt = ""
        self.api_key = os.getenv("API_KEY")
        self.api_base = os.getenv("API_BASE")
        self.model = os.getenv("MODEL")
        self.context = []
        self.tokens_consumed = 0
        
    def set_api_key(self, api_key: str):
        self.api_key = api_key
        
    def set_api_base(self, api_base: str):
        self.api_base = api_base
        
    def set_model(self, model: str):
        self.model = model
        
    def set_prompt(self, prompt: str):
        self.prompt = prompt
        
    def add_tool(self, description: dict, function: callable):
        """
        e.g.
        {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "获取指定地点的天气信息",
            "parameters": {
            "type": "object",
            "properties": {
                "location": {
                "type": "string",
                "description": "地点的位置信息，例如北京、上海"
                },
                "unit": {
                "type": "string",
                "enum": ["摄氏度", "华氏度"],
                "description": "温度单位"
                }
            },
            "required": ["location"]
            }
        }
        }
        
        def get_current_weather(location: str, unit="摄氏度"):
            # 实际调用天气查询 API 的逻辑
            # 此处为示例，返回模拟的天气数据
            return f"{location}今天天气晴朗，温度 25 {unit}。"
        """
        self.tools[description["function"]["name"]] = {
            "function": function,
            "description": description
        }
    
    def get_context(self):
        message = []
        if self.prompt:
            message.append({"role": "system", "content": self.prompt})
        message.extend(self.context)
        return message
    
    def chat_with_tools(self, message):
        if type(message) == str:
            message = {"role": "user", "content": message}
        self.context.append(message)
        
        client = Ark(
            api_key=self.api_key,
            base_url=self.api_base
        )
        tools = [tool["description"] for tool in list(self.tools.values())]
        while True:
            # 步骤2: 发起模型请求，由于模型在收到工具执行结果后仍然可能有工具调用意愿，因此需要多次请求
            completion: ChatCompletion = client.chat.completions.create(
                model=self.model,
                messages=self.get_context(),
                tools=tools,
                thinking={"type": "disabled"},
            )
            resp_msg = completion.choices[0].message
            with open('log.txt', 'a', encoding='utf-8') as f:
                f.write(json.dumps(resp_msg.model_dump(), ensure_ascii=False) + '\n')
            self.context.append(resp_msg.model_dump())
            self.tokens_consumed += completion.usage.total_tokens
            # 展示模型中间过程的回复内容
            # print(resp_msg.content)
            if completion.choices[0].finish_reason != "tool_calls":
                # 模型最终总结，没有调用工具意愿
                break
            tool_calls = completion.choices[0].message.tool_calls
            for tool_call in tool_calls:
                tool_name = tool_call.function.name
                # 步骤 3：调用外部工具
                args = json.loads(tool_call.function.arguments)
                func = self.tools[tool_name]["function"]
                tool_result = str(func(**args))
                # print(f'call {tool_name} with args {args}')
                # 步骤 4：回填工具结果，并获取模型总结回复
                messages.append(
                    {"role": "tool", "content": tool_result, "tool_call_id": tool_call.id}
                )
        resp_msg = resp_msg.content.encode('utf-8').decode('utf-8')
        return resp_msg
    
    def chat(self, message, web_search=False):
        if type(message) == str:
            message = {"role": "user", "content": message}
        self.context.append(message)
        
        client = Ark(
            api_key=self.api_key,
            base_url=self.api_base
        )
        if web_search:
            response = client.responses.create(
                model=self.model,
                input=self.get_context(),
                tools=[{
                        "type": "web_search",
                        "max_keyword": 2,  
                    }],
                thinking={"type": "disabled"},
            )
            resp_msg = response.output[-1].content[0].text
            self.context.append({"role": "assistant", "content": resp_msg})
            self.tokens_consumed += response.usage.total_tokens
        else:
            completion = client.chat.completions.create(
                model=self.model,
                messages=self.get_context(),
                thinking={"type": "disabled"},
            )
            resp_msg = completion.choices[0].message.content
            self.context.append({"role": "assistant", "content": resp_msg})
            self.tokens_consumed += completion.usage.total_tokens
            
        resp_msg = resp_msg.encode('utf-8').decode('utf-8')
        return resp_msg