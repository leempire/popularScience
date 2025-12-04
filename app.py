from flask import Flask, render_template, request, redirect, url_for, jsonify
import os
import threading
import json
import uuid
from datetime import datetime, date
from utils.agent import run

app = Flask(__name__)

# 确保data目录存在
os.makedirs('data', exist_ok=True)

# 存储文章生成状态的字典
generation_status = {}

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
        # 如果不是普通授权码，检查是否为包月会员code
        return validate_and_use_monthly_code(code)
    
    # 从列表中移除已使用的授权码
    codes.remove(code)
    
    # 写回文件
    with open('data/code.txt', 'w', encoding='utf-8') as f:
        for c in codes:
            f.write(c + '\n')
    
    return True

def validate_and_use_monthly_code(code):
    """验证并使用包月会员code"""
    # 检查包月会员文件是否存在
    if not os.path.exists('data/monthly_codes.json'):
        return False
    
    # 读取包月会员信息
    with open('data/monthly_codes.json', 'r', encoding='utf-8') as f:
        monthly_codes = json.load(f)
    
    # 检查code是否存在
    if code not in monthly_codes:
        return False
    
    # 获取会员信息
    member_info = monthly_codes[code]
    
    # 检查是否过期
    expiry_date = datetime.fromisoformat(member_info["expiry_date"])
    if datetime.now() > expiry_date:
        # 删除过期的会员code
        del monthly_codes[code]
        with open('data/monthly_codes.json', 'w', encoding='utf-8') as f:
            json.dump(monthly_codes, f, ensure_ascii=False, indent=2)
        return False
    
    # 检查日期是否需要重置使用次数
    last_used_date = date.fromisoformat(member_info["last_used_date"])
    today = date.today()
    if last_used_date != today:
        # 重置今日使用次数
        member_info["usage_today"] = 0
        member_info["last_used_date"] = today.isoformat()
    
    # 检查是否超过每日限制
    if member_info["usage_today"] >= member_info["daily_limit"]:
        return False
    
    # 增加使用次数
    member_info["usage_today"] += 1
    
    # 更新会员信息
    monthly_codes[code] = member_info
    with open('data/monthly_codes.json', 'w', encoding='utf-8') as f:
        json.dump(monthly_codes, f, ensure_ascii=False, indent=2)
    
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
    
    # 生成唯一的任务ID
    task_id = str(uuid.uuid4())
    
    # 初始化任务状态
    generation_status[task_id] = {
        'status': 'processing',
        'topic': topic,
        'message': '文章生成中...'
    }
    
    # 在后台线程中运行生成任务
    def generate_task():
        try:
            run(topic)
            # 更新任务状态为完成
            generation_status[task_id] = {
                'status': 'completed',
                'topic': topic,
                'message': f'文章《{topic}》已生成完成！'
            }
        except Exception as e:
            print(f"生成文章时出错: {e}")
            # 更新任务状态为失败
            generation_status[task_id] = {
                'status': 'failed',
                'topic': topic,
                'message': f'文章生成失败: {str(e)}'
            }
    
    thread = threading.Thread(target=generate_task)
    thread.start()
    
    return jsonify({'success': True, 'message': '文章生成任务已启动，授权码已使用', 'task_id': task_id})

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

@app.route('/status/<task_id>')
def get_generation_status(task_id):
    """获取文章生成状态"""
    if task_id in generation_status:
        return jsonify(generation_status[task_id])
    else:
        return jsonify({'status': 'not_found', 'message': '任务不存在'}), 404

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=8012)