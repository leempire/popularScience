from volcenginesdkarkruntime import Ark
import os
import dotenv
dotenv.load_dotenv()


def run(target):
    content = generate_text(target)
    with open(f'data/{target}.md', 'w', encoding='utf-8') as f:
        f.write(content)
    html = render_html(content)
    with open(f'data/{target}.html', 'w', encoding='utf-8') as f:
        f.write(html)


def generate_text(target) -> str:
    print('正在生成科普文章...')
    # 初始化模型
    client = Ark(
        base_url=os.getenv('API_BASE'),
        api_key=os.getenv('API_KEY'),
    )
    # 使用联网搜索工具
    tools = [{
        "type": "web_search",
        "max_keyword": 2,  
    }]
    # 读取prompt文件
    with open('prompt/text_generator.md', encoding='utf-8') as f:
        prompt = f.read()
    # 替换占位符
    prompt = prompt.replace("{{input}}", target)
    # 创建上下文
    messages = [
        {"role": "system", "content": prompt}
    ]
    response = client.responses.create(
        model=os.getenv('MODEL'),
        input=messages,
        tools=tools,
    )
    print(f'文章生成完成，消耗的token数量: {response.usage.total_tokens}')
    data = response.model_dump()['output'][-1]['content'][-1]['text']
    return data

def render_html(content) -> str:
    print('正在渲染HTML...')
    # 加载prompt
    with open('prompt/html_generator.md', encoding='utf-8') as f:
        prompt = f.read()
    client = Ark(
        base_url=os.getenv('API_BASE'),
        api_key=os.getenv('API_KEY'),
    )
    completion = client.chat.completions.create(
        model=os.getenv('MODEL'),
        messages=[
            {"role": "system", "content": prompt},
            {"role": "user", "content": content}
        ],
        max_completion_tokens =32768,
    )
    print(f'HTML渲染完成，消耗的token数量: {completion.usage.total_tokens}')
    html = completion.choices[0].message.content
    return html
