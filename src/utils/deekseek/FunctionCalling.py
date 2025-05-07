from openai import OpenAI

def get_weather(location):
    
        print("this is get_weather")
        return f"location 的温度是143摄氏度"


def send_messages(messages):
    print(f"send_messages>>>>>>>>>>>>>>>>{messages} \n")
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        tools=tools
    )
    return response.choices[0].message

client = OpenAI(
    api_key="sk-811ba66952094c55b56b51ff87a3013b",
    base_url="https://api.deepseek.com",
)

def function_call_playground(prompt):

    messages = [{"role": "user", "content": f"{prompt}"}]
    message = send_messages(messages)
    print(f"User>>>\t {messages[0]['content']}")

    tool = message.tool_calls[0]
    print(f"==tools>>>{tool}")
    messages.append(message)

    print(f"==tools id>>>{tool.id}")
    funcl_name = message.tool_calls[0].function.name
    print(f"==tools name>>>{funcl_name}")
    funcl_args = message.tool_calls[0].function.arguments
    print(f"==tools args>>>{funcl_args}")

    #step2 调用本地方法
    funcl_out = eval(f'{funcl_name}(**{funcl_args})')
    print(f"==funcl_out>>>{funcl_out}")

    #step3 在把本地方法结果 传给deekseep, 输出人话
    messages.append({"role": "tool", "tool_call_id": tool.id, "content": f"{funcl_out}"})
    message = send_messages(messages)
    print(f"Model>\t {message.content}")


    return message.content

tools = [
    {
        "type": "function",
        "function": {
            "name": "get_weather",
            "description": "Get weather of an location, the user shoud supply a location first",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                    }
                },
                "required": ["location"]
            },
        }
    },
    {
        "type": "function",
        "function": {
            "name": "send_email",
            "description": "Send an email",
            "parameters": {
                "type": "object",
                "properties": {
                    "to": {"type": "string"},
                    "subject": {"type": "string"},
                    "body": {"type": "string"}
                },
                "required": ["to", "subject", "body"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "run_script",
            "description": "Run a script",
            "parameters": {
                "type": "object",
                "properties": {
                    "script_path": {"type": "string"}
                },
                "required": ["script_path"]
            }
        }
    }
]


    

# 使用示例
if __name__ == "__main__":

    function_call_playground(" How's the weather in NewYork?")