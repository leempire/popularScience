from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import threading
from utils.agent import run

app = Flask(__name__)

# 确保data目录存在
os.makedirs('data', exist_ok=True)

def get_html_files():
    """获取data目录下所有的html文件"""
    html_files = []
    if os.path.exists('data'):
        for filename in os.listdir('data'):
            if filename.endswith('.html'):
                html_files.append(filename)
    return html_files

@app.route('/')
def index():
    """首页：显示所有科普文章链接和生成表单"""
    html_files = get_html_files()
    return render_template('index.html', files=html_files)

def validate_and_consume_code(code):
    """验证授权码并消费它（从文件中删除）"""
    if not os.path.exists('data/code.txt'):
        return False
    
    # 读取所有授权码
    with open('data/code.txt', 'r', encoding='utf-8') as f:
        codes = [line.strip() for line in f.readlines() if line.strip()]
    
    # 检查授权码是否存在
    if code not in codes:
        return False
    
    # 从列表中移除已使用的授权码
    codes.remove(code)
    
    # 写回文件
    with open('data/code.txt', 'w', encoding='utf-8') as f:
        for c in codes:
            f.write(c + '\n')
    
    return True

@app.route('/generate', methods=['POST'])
def generate_article():
    """处理科普文章生成请求"""
    topic = request.form.get('topic')
    code = request.form.get('code')
    
    if not topic:
        return jsonify({'error': '主题不能为空'}), 400
    
    if not code:
        return jsonify({'error': '授权码不能为空'}), 400
    
    # 验证授权码
    if not validate_and_consume_code(code):
        return jsonify({'error': '无效的授权码或授权码已被使用'}), 400
    
    # 在后台线程中运行生成任务
    def generate_task():
        try:
            run(topic)
        except Exception as e:
            print(f"生成文章时出错: {e}")
    
    thread = threading.Thread(target=generate_task)
    thread.start()
    
    return jsonify({'success': True, 'message': '文章生成任务已启动，授权码已使用'})

@app.route('/article/<filename>')
def article(filename):
    """显示指定的科普文章"""
    # 安全检查，确保只访问data目录下的文件
    if '..' in filename or filename.startswith('/'):
        return "无效的文件名", 400
    
    filepath = os.path.join('data', filename)
    if not os.path.exists(filepath):
        return "文件不存在", 404
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
    
    return content

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8012)