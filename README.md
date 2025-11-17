# 科普文章生成器

这是一个基于大模型的科普文章自动生成系统，可以根据给定的主题自动生成科普文章并渲染成HTML格式。

## 功能特点

- 基于大语言模型自动生成科普文章内容
- 将Markdown格式的文章渲染为美观的HTML页面
- 提供命令行和Web界面两种使用方式

## 目录结构

```
├── app.py              # Flask Web应用
├── main.py             # 命令行入口
├── requirements.txt    # 依赖包列表
├── utils/              # 工具模块
│   ├── agent.py        # 核心处理逻辑
│   └── doubao_api.py   # API接口封装
├── prompt/             # 提示词模板
│   ├── text_generator.md  # 文本生成提示词
│   └── html_generator.md  # HTML渲染提示词
├── data/               # 生成的文章数据
├── templates/          # Flask模板文件
└── README.md           # 项目说明文档
```

## 环境配置

1. 安装依赖：
   ```
   pip install -r requirements.txt
   ```

2. 配置环境变量：
   在项目根目录下创建 `.env` 文件，并添加以下配置：
   ```
   API_BASE=你的API基础地址
   API_KEY=你的API密钥
   MODEL=使用的模型名称
   ```

## 使用方法

### 命令行方式

```bash
python main.py "科普主题"
```

例如：
```bash
python main.py "量子计算"
```

生成的文章将保存在 `data/` 目录下，包含Markdown和HTML两种格式。

### Web界面方式

1. 启动Flask应用：
   ```bash
   python app.py
   ```

2. 在浏览器中访问 `http://127.0.0.1:5000`

3. 在首页可以：
   - 查看已生成的文章列表
   - 输入新的科普主题和授权码生成文章
   - 点击文章标题查看具体内容

### 授权码管理

为了限制文章生成次数，系统引入了授权码机制：
- 每个授权码只能使用一次
- 使用后会从授权码列表中删除
- 管理员可以通过以下方式管理授权码：

```bash
# 添加5个新的授权码
python add_code.py

# 添加指定数量的授权码
python add_code.py 10

# 添加指定的授权码
python add_code.py --add CODE123

# 列出所有可用的授权码
python add_code.py --list
```

## 实现原理

1. 使用大语言模型根据主题生成科普文章内容（Markdown格式）
2. 再次使用大语言模型将Markdown内容渲染为精美的HTML页面
3. 将生成的文件保存到本地供后续查阅

## 注意事项

- 请确保网络连接正常，因为需要调用在线API
- 生成过程可能需要一些时间，请耐心等待
- 请妥善保管API密钥，不要泄露给他人