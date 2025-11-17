#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
添加新的授权码到data/code.txt文件
"""

import os
import sys
import uuid
path = 'data/code.txt'

def add_codes(count=5):
    """添加指定数量的授权码到data/code.txt文件"""
    # 生成授权码
    codes = []
    for i in range(count):
        # 生成类似 CODE-XXXXX 格式的授权码
        code = f"CODE-{str(uuid.uuid4())[:8].upper()}"
        codes.append(code)
    
    # 读取现有授权码
    existing_codes = []
    if os.path.exists('data/code.txt'):
        with open('data/code.txt', 'r', encoding='utf-8') as f:
            existing_codes = [line.strip() for line in f.readlines() if line.strip()]
    
    # 合并新旧授权码并去重
    all_codes = list(set(existing_codes + codes))
    
    # 写入文件
    with open('data/code.txt', 'w', encoding='utf-8') as f:
        for code in all_codes:
            f.write(code + '\n')
    
    print(f"已成功添加 {count} 个授权码到 data/code.txt 文件:")
    for code in codes:
        print(f"  {code}")

def add_specific_code(code):
    """添加指定的授权码到data/code.txt文件"""
    # 如果文件不存在，创建文件
    if not os.path.exists(path):
        # 确保data目录存在
        data_dir = os.path.dirname(path)
        if data_dir and not os.path.exists(data_dir):
            os.makedirs(data_dir)
        open(path, 'w').close()
    
    # 读取现有授权码
    with open(path, 'r', encoding='utf-8') as f:
        existing_codes = [line.strip() for line in f.readlines() if line.strip()]
    
    # 检查授权码是否已存在
    if code in existing_codes:
        print(f"授权码 {code} 已存在")
        return
    
    # 添加新授权码
    with open(path, 'a', encoding='utf-8') as f:
        f.write(code + '\n')
    print(f"已成功添加授权码: {code}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        if sys.argv[1] == "--add":
            if len(sys.argv) > 2:
                add_specific_code(sys.argv[2])
            else:
                print("请提供要添加的授权码，例如: python add_code.py --add CODE123")
        elif sys.argv[1] == "--list":
            # 列出所有授权码
            if os.path.exists('data/code.txt'):
                with open('data/code.txt', 'r', encoding='utf-8') as f:
                    codes = [line.strip() for line in f.readlines() if line.strip()]
                print("当前可用的授权码:")
                for code in codes:
                    print(f"  {code}")
            else:
                print("data/code.txt 文件不存在")
        else:
            try:
                count = int(sys.argv[1])
                add_codes(count)
            except ValueError:
                print("参数错误。使用方法:")
                print("  python add_code.py          # 添加5个授权码")
                print("  python add_code.py 10       # 添加10个授权码")
                print("  python add_code.py --add CODE123  # 添加指定授权码")
                print("  python add_code.py --list   # 列出所有授权码")
    else:
        add_codes(5)
