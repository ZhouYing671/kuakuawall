#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
夸夸墙 - HR模块网站
功能：登录、权限管理、展示墙、报表导出
"""

from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for, make_response
import json, os
from datetime import datetime
import pandas as pd
import io
import base64

app = Flask(__name__)
app.secret_key = 'kuakuawall-secret-key-2026'

# 数据文件路径
DATA_DIR = '/tmp/kuakuawall'
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, 'users.json')
PRAISES_FILE = os.path.join(DATA_DIR, 'praises.json')

# 初始化默认数据
def init_data():
    if not os.path.exists(USERS_FILE):
        default_users = {
            "101": {"role": "高级用户", "name": "管理员"},
            "102": {"role": "普通用户", "name": "员工A"},
            "103": {"role": "高级用户", "name": "经理B"}
        }
        json.dump(default_users, open(USERS_FILE, 'w'), ensure_ascii=False, indent=2)
    
    if not os.path.exists(PRAISES_FILE):
        json.dump([], open(PRAISES_FILE, 'w'), ensure_ascii=False)

init_data()

# 多语言支持
LANGUAGES = {
    'zh': {
        'title': '夸夸墙',
        'login': '登录',
        'login_id': '登录ID',
        'confirm': '确认',
        'logout': '退出登录',
        'management': '管理页面',
        'display': '展示页面',
        'auxiliary': '辅助页面',
        'import_excel': '导入Excel',
        'export_report': '导出报表',
        'report1': '报表1: 用户权限',
        'report2': '报表2: 录入记录',
        'report3': '报表3: 统计图表',
        'add_praise': '添加夸夸',
        'content': '内容',
        'praise_target': '受表扬人ID',
        'submit': '提交',
        'delete': '删除',
        'batch_delete': '批量删除',
        'view_display': '查看展示页',
        'high_user': '高级用户',
        'normal_user': '普通用户',
        'no_permission': '您没有权限访问此页面',
        'please_login': '请先登录',
        'language': '语言',
        'chinese': '中文',
        'english': 'English',
        'time': '时间',
        'user_id': '用户ID',
        'upload_image': '上传图片',
        'prev_page': '上一页',
        'next_page': '下一页'
    },
    'en': {
        'title': 'Praise Wall',
        'login': 'Login',
        'login_id': 'Login ID',
        'confirm': 'Confirm',
        'logout': 'Logout',
        'management': 'Management',
        'display': 'Display',
        'auxiliary': 'Auxiliary',
        'import_excel': 'Import Excel',
        'export_report': 'Export Report',
        'report1': 'Report 1: User Permissions',
        'report2': 'Report 2: Records',
        'report3': 'Report 3: Statistics',
        'add_praise': 'Add Praise',
        'content': 'Content',
        'praise_target': 'Praise Target ID',
        'submit': 'Submit',
        'delete': 'Delete',
        'batch_delete': 'Batch Delete',
        'view_display': 'View Display',
        'high_user': 'High User',
        'normal_user': 'Normal User',
        'no_permission': 'You do not have permission',
        'please_login': 'Please login first',
        'language': 'Language',
        'chinese': '中文',
        'english': 'English',
        'time': 'Time',
        'user_id': 'User ID',
        'upload_image': 'Upload Image',
        'prev_page': 'Previous',
        'next_page': 'Next'
    }
}

def get_lang():
    return session.get('lang', 'zh')

def t(key):
    return LANGUAGES.get(get_lang(), LANGUAGES['zh']).get(key, key)

def get_users():
    return json.load(open(USERS_FILE))

def save_users(users):
    json.dump(users, open(USERS_FILE, 'w'), ensure_ascii=False, indent=2)

def get_praises():
    return json.load(open(PRAISES_FILE))

def save_praises(praises):
    json.dump(praises, open(PRAISES_FILE, 'w'), ensure_ascii=False, indent=2)

def is_high_user(user_id):
    users = get_users()
    return users.get(str(user_id), {}).get('role') == '高级用户'

def is_logged_in():
    return 'user_id' in session

# 页面模板
LOGIN_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ t('title') }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #9B7EBD 0%, #7B68A6 50%, #5D4E7A 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            position: relative;
            overflow: hidden;
        }
        .bg-pattern {
            position: absolute;
            top: 0; left: 0; right: 0; bottom: 0;
            background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='100' height='100' viewBox='0 0 100 100'%3E%3Cpath d='M50 25c-8.3 0-15 6.7-15 15s6.7 15 15 15 15-6.7 15-15-6.7-15-15-15zm-25 40c0-13.8 11.2-25 25-25s25 11.2 25 25' fill='none' stroke='rgba(255,255,255,0.1)' stroke-width='2'/%3E%3C/svg%3E");
            opacity: 0.3;
        }
        .login-box {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 20px;
            padding: 50px 40px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            width: 100%;
            max-width: 420px;
            position: relative;
            z-index: 1;
        }
        .logo {
            text-align: center;
            margin-bottom: 30px;
        }
        .logo h1 {
            color: #7B68A6;
            font-size: 32px;
            font-weight: 600;
        }
        .logo p {
            color: #9B7EBD;
            font-size: 14px;
            margin-top: 5px;
        }
        .form-group {
            margin-bottom: 20px;
        }
        label {
            display: block;
            color: #5D4E7A;
            font-size: 14px;
            margin-bottom: 8px;
            font-weight: 500;
        }
        input[type="text"] {
            width: 100%;
            padding: 14px 18px;
            border: 2px solid #E8E0F0;
            border-radius: 12px;
            font-size: 16px;
            transition: all 0.3s;
            background: #FAF8FC;
        }
        input[type="text"]:focus {
            outline: none;
            border-color: #9B7EBD;
            background: #fff;
        }
        select {
            width: 100%;
            padding: 14px 18px;
            border: 2px solid #E8E0F0;
            border-radius: 12px;
            font-size: 14px;
            background: #FAF8FC;
            cursor: pointer;
        }
        .btn {
            width: 100%;
            padding: 16px;
            background: linear-gradient(135deg, #9B7EBD, #7B68A6);
            color: white;
            border: none;
            border-radius: 12px;
            font-size: 16px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s;
            margin-top: 10px;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 30px rgba(123, 104, 166, 0.4);
        }
        .error {
            color: #e74c3c;
            text-align: center;
            margin-top: 15px;
            font-size: 14px;
        }
    </style>
</head>
<body>
    <div class="bg-pattern"></div>
    <div class="login-box">
        <div class="logo">
            <h1>🤝 {{ t('title') }}</h1>
            <p>Praise Wall System</p>
        </div>
        <form method="POST" action="/login">
            <div class="form-group">
                <label>{{ t('login_id') }}</label>
                <input type="text" name="user_id" placeholder="请输入登录ID" required>
            </div>
            <div class="form-group">
                <label>{{ t('language') }}</label>
                <select name="lang" onchange="this.form.submit()">
                    <option value="zh" {% if lang == 'zh' %}selected{% endif %}>{{ t('chinese') }}</option>
                    <option value="en" {% if lang == 'en' %}selected{% endif %}>{{ t('english') }}</option>
                </select>
            </div>
            <button type="submit" class="btn">{{ t('confirm') }}</button>
        </form>
        {% if error %}
        <p class="error">{{ error }}</p>
        {% endif %}
    </div>
</body>
</html>
"""

MANAGEMENT_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ t('management') }} - {{ t('title') }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #9B7EBD 0%, #7B68A6 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1400px;
            margin: 0 auto;
        }
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px 30px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            color: #5D4E7A;
            font-size: 24px;
        }
        .header-right {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        .nav {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 15px 30px;
            margin-bottom: 20px;
            display: flex;
            gap: 20px;
        }
        .nav a {
            color: #7B68A6;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 10px;
            transition: all 0.3s;
        }
        .nav a:hover, .nav a.active {
            background: #9B7EBD;
            color: white;
        }
        .content {
            display: grid;
            grid-template-columns: 1fr 400px;
            gap: 20px;
        }
        .panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
        }
        .panel h2 {
            color: #5D4E7A;
            font-size: 18px;
            margin-bottom: 20px;
            padding-bottom: 10px;
            border-bottom: 2px solid #E8E0F0;
        }
        .btn {
            padding: 12px 24px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            font-weight: 500;
            transition: all 0.3s;
            margin: 5px;
        }
        .btn-primary {
            background: linear-gradient(135deg, #9B7EBD, #7B68A6);
            color: white;
        }
        .btn-danger {
            background: #e74c3c;
            color: white;
        }
        .btn-success {
            background: #27ae60;
            color: white;
        }
        .btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 5px 15px rgba(0,0,0,0.2);
        }
        .import-section, .export-section {
            margin-bottom: 25px;
            padding: 20px;
            background: #FAF8FC;
            border-radius: 10px;
        }
        .import-section h3, .export-section h3 {
            color: #7B68A6;
            font-size: 16px;
            margin-bottom: 15px;
        }
        input[type="file"] {
            display: none;
        }
        .file-label {
            display: inline-block;
            padding: 12px 24px;
            background: linear-gradient(135deg, #9B7EBD, #7B68A6);
            color: white;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
        }
        .preview-box {
            background: #fff;
            border: 2px solid #E8E0F0;
            border-radius: 10px;
            padding: 15px;
            margin-top: 15px;
            max-height: 300px;
            overflow-y: auto;
        }
        .preview-box h4 {
            color: #5D4E7A;
            margin-bottom: 10px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 10px;
        }
        th, td {
            padding: 10px;
            text-align: left;
            border-bottom: 1px solid #E8E0F0;
        }
        th {
            background: #FAF8FC;
            color: #5D4E7A;
        }
        .display-preview {
            height: 500px;
            overflow-y: auto;
            border: 2px solid #E8E0F0;
            border-radius: 10px;
            padding: 15px;
            background: #fff;
        }
        .praise-card {
            background: linear-gradient(135deg, #FAF8FC, #F5F0FA);
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 12px;
            border-left: 4px solid #9B7EBD;
            position: relative;
        }
        .praise-card .author {
            color: #7B68A6;
            font-weight: 600;
            font-size: 14px;
        }
        .praise-card .target {
            color: #9B7EBD;
            font-size: 12px;
            margin: 5px 0;
        }
        .praise-card .content {
            color: #5D4E7A;
            font-size: 14px;
            line-height: 1.6;
            margin: 10px 0;
        }
        .praise-card .time {
            color: #aaa;
            font-size: 11px;
        }
        .praise-card .delete-btn {
            position: absolute;
            top: 10px;
            right: 10px;
            background: #e74c3c;
            color: white;
            border: none;
            border-radius: 5px;
            padding: 5px 10px;
            cursor: pointer;
            font-size: 12px;
        }
        .checkbox-select {
            position: absolute;
            top: 10px;
            left: 10px;
            width: 18px;
            height: 18px;
        }
        .batch-actions {
            margin-top: 15px;
            padding-top: 15px;
            border-top: 2px solid #E8E0F0;
        }
        .user-info {
            color: #5D4E7A;
            font-size: 14px;
        }
        .user-info span {
            background: #E8E0F0;
            padding: 5px 12px;
            border-radius: 20px;
            margin-left: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤝 {{ t('title') }} - {{ t('management') }}</h1>
            <div class="header-right">
                <div class="user-info">
                    {{ t('user_id') }}: {{ user_id }} <span>{{ role }}</span>
                </div>
                <a href="/logout" class="btn btn-danger">{{ t('logout') }}</a>
            </div>
        </div>
        
        <div class="nav">
            <a href="/management" class="active">{{ t('management') }}</a>
            <a href="/display">{{ t('display') }}</a>
            <a href="/auxiliary">{{ t('auxiliary') }}</a>
        </div>
        
        <div class="content">
            <div class="panel">
                <h2>📋 {{ t('import_excel') }} & {{ t('export_report') }}</h2>
                
                <div class="import-section">
                    <h3>📁 {{ t('import_excel') }}</h3>
                    <p style="color: #7B68A6; font-size: 13px; margin-bottom: 15px;">
                        Excel格式：第一列用户ID，第二列权限名称（普通用户/高级用户）
                    </p>
                    <label class="file-label">
                        选择Excel文件
                        <input type="file" id="excelFile" accept=".xlsx,.xls" onchange="handleFileUpload(this)">
                    </label>
                    <button class="btn btn-primary" onclick="confirmImport()" id="importBtn" style="display:none;">
                        确认导入
                    </button>
                    <div id="preview" class="preview-box" style="display:none;">
                        <h4>预览导入数据：</h4>
                        <div id="previewContent"></div>
                    </div>
                </div>
                
                <div class="export-section">
                    <h3>📊 {{ t('export_report') }}</h3>
                    <button class="btn btn-success" onclick="exportReport1()">{{ t('report1') }}</button>
                    <button class="btn btn-success" onclick="exportReport2()">{{ t('report2') }}</button>
                    <button class="btn btn-success" onclick="exportReport3()">{{ t('report3') }}</button>
                </div>
            </div>
            
            <div class="panel">
                <h2>👁️ {{ t('view_display') }}</h2>
                <div class="display-preview" id="displayPreview"></div>
                <div class="batch-actions">
                    <button class="btn btn-danger" onclick="batchDelete()">{{ t('batch_delete') }}</button>
                </div>
            </div>
        </div>
    </div>
    
    <script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script>
    <script>
        let importData = [];
        
        function handleFileUpload(input) {
            const file = input.files[0];
            if (!file) return;
            
            const reader = new FileReader();
            reader.onload = function(e) {
                const data = new Uint8Array(e.target.result);
                const workbook = XLSX.read(data, {type: 'array'});
                const sheet = workbook.Sheets[workbook.SheetNames[0]];
                const json = XLSX.utils.sheet_to_json(sheet, {header: 1});
                
                importData = [];
                let html = '<table><tr><th>用户ID</th><th>权限名称</th></tr>';
                
                json.forEach((row, index) => {
                    if (index === 0 && isNaN(row[0])) return; // 跳过标题行
                    if (row[0] && row[1]) {
                        importData.push({id: String(row[0]), role: row[1]});
                        html += '<tr><td>' + row[0] + '</td><td>' + row[1] + '</td></tr>';
                    }
                });
                
                html += '</table>';
                document.getElementById('previewContent').innerHTML = html;
                document.getElementById('preview').style.display = 'block';
                document.getElementById('importBtn').style.display = 'inline-block';
            };
            reader.readAsArrayBuffer(file);
        }
        
        async function confirmImport() {
            if (importData.length === 0) {
                alert('没有数据可导入');
                return;
            }
            
            const res = await fetch('/api/import-users', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(importData)
            });
            const result = await res.json();
            
            if (result.ok) {
                alert('导入成功！共导入 ' + importData.length + ' 条数据');
                location.reload();
            } else {
                alert('导入失败：' + result.error);
            }
        }
        
        async function loadDisplay() {
            const res = await fetch('/api/praises');
            const praises = await res.json();
            
            let html = '';
            praises.slice(0, 20).forEach(p => {
                html += '<div class="praise-card">' +
                    '<input type="checkbox" class="checkbox-select" data-id="' + p.id + '">' +
                    '<div class="author">👤 ' + p.user_id + '</div>' +
                    '<div class="target">🎯 受表扬: ' + p.target_id + '</div>' +
                    '<div class="content">' + p.content + '</div>' +
                    '<div class="time">📅 ' + p.time + '</div>' +
                    '<button class="delete-btn" onclick="deletePraise(' + p.id + ')">删除</button>' +
                    '</div>';
            });
            
            document.getElementById('displayPreview').innerHTML = html || '<p style="color:#999;text-align:center;padding:20px;">暂无数据</p>';
        }
        
        async function deletePraise(id) {
            if (!confirm('确定删除这条记录吗？')) return;
            
            const res = await fetch('/api/praises/' + id, {method: 'DELETE'});
            const result = await res.json();
            
            if (result.ok) {
                loadDisplay();
            }
        }
        
        async function batchDelete() {
            const checkboxes = document.querySelectorAll('.checkbox-select:checked');
            if (checkboxes.length === 0) {
                alert('请先选择要删除的记录');
                return;
            }
            
            if (!confirm('确定删除选中的 ' + checkboxes.length + ' 条记录吗？')) return;
            
            const ids = Array.from(checkboxes).map(cb => parseInt(cb.dataset.id));
            const res = await fetch('/api/praises/batch-delete', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({ids: ids})
            });
            const result = await res.json();
            
            if (result.ok) {
                loadDisplay();
            }
        }
        
        function exportReport1() {
            window.location.href = '/api/export/report1';
        }
        
        function exportReport2() {
            window.location.href = '/api/export/report2';
        }
        
        function exportReport3() {
            window.location.href = '/api/export/report3';
        }
        
        loadDisplay();
    </script>
</body>
</html>
"""

DISPLAY_PAGE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ t('display') }} - {{ t('title') }}</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #9B7EBD 0%, #7B68A6 100%);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
        }
        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px 30px;
            margin-bottom: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        .header h1 {
            color: #5D4E7A;
            font-size: 24px;
        }
        .header-right {
            display: flex;
            gap: 15px;
            align-items: center;
        }
        .user-info {
            color: #5D4E7A;
            font-size: 14px;
        }
        .user-info span {
            background: #E8E0F0;
            padding: 5px 12px;
            border-radius: 20px;
            margin-left: 10px;
        }
        .nav {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 15px 30px;
            margin-bottom: 20px;
            display: flex;
            gap: 20px;
        }
        .nav a {
            color: #7B68A6;
            text-decoration: none;
            padding: 10px 20px;
            border-radius: 10px;
            transition: all 0.3s;
        }
        .nav a:hover, .nav a.active {
            background: #9B7EBD;
            color: white;
        }
        .add-btn {
            position: fixed;
            bottom: 30px;
            right: 30px;
            width: 60px;
            height: 60px;
            background: linear-gradient(135deg, #9B7EBD, #7B68A6);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 28px;
            color: white;
            cursor: pointer;
            box-shadow: 0 5px 20px rgba(123, 104, 166, 0.5);
            z-index: 100;
            transition: all 0.3s;
        }
        .add-btn:hover {
            transform: scale(1.1);
        }
        .wall {
            display: grid;
            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
            gap: 20px;
            padding: 10px;
        }
        .praise-card {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
            transition: all 0.3s;
            position: relative;
        }
        .praise-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        }
        .praise-card .avatar {
            width: 45px;
            height: 45px;
            background: linear-gradient(135deg, #9B7EBD, #7B68A6);
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            color: white;
            font-weight: bold;
            font-size: 18px;
            position: absolute;
            top: 15px;
            right: 15px;
        }
        .praise-card .author {
            color: #7B68A6;
            font-weight: 600;
            font-size: 15px;
            margin-bottom: 5px;
        }
        .praise-card .target {
            color: #9B7EBD;
            font-size: 13px;
            margin-bottom: 12px;
        }
        .praise-card .content {
            color: #5D4E7A;
            font-size: 14px;
            line-height: 1.7;
            margin-bottom: 15px;
        }
        .praise-card .image {
            width: 100%;
            border-radius: 10px;
            margin-bottom: 15px;
        }
        .praise-card .time {
            color: #aaa;
            font-size: 12px;
            border-top: 1px solid #E8E0F0;
            padding-top: 12px;
        }
        .pagination {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin-top: 30px;
        }
        .pagination button {
            padding: 10px 20px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s;
        }
        .pagination button:disabled {
            background: #ddd;
            cursor: not-allowed;
        }
        .pagination button:not(:disabled) {
            background: rgba(255, 255, 255, 0.9);
            color: #7B68A6;
        }
        .pagination button:not(:disabled):hover {
            background: #9B7EBD;
            color: white;
        }
        .pagination .page-info {
            background: rgba(255, 255, 255, 0.9);
            padding: 10px 20px;
            border-radius: 10px;
            color: #5D4E7A;
        }
        /* 弹窗样式 */
        .modal {
            display: none;
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: rgba(0, 0, 0, 0.5);
            align-items: center;
            justify-content: center;
            z-index: 1000;
        }
        .modal.show {
            display: flex;
        }
        .modal-content {
            background: white;
            border-radius: 20px;
            padding: 30px;
            width: 90%;
            max-width: 500px;
            max-height: 80vh;
            overflow-y: auto;
        }
        .modal-content h2 {
            color: #5D4E7A;
            margin-bottom: 20px;
        }
        .modal-content textarea {
            width: 100%;
            height: 120px;
            border: 2px solid #E8E0F0;
            border-radius: 10px;
            padding: 15px;
            font-size: 14px;
            resize: none;
            margin-bottom: 15px;
        }
        .modal-content input[type="text"], .modal-content select {
            width: 100%;
            padding: 12px;
            border: 2px solid #E8E0F0;
            border-radius: 10px;
            font-size: 14px;
            margin-bottom: 15px;
        }
        .modal-content .btn {
            padding: 12px 30px;
            border: none;
            border-radius: 10px;
            cursor: pointer;
            font-size: 14px;
            margin: 5px;
        }
        .modal-content .btn-primary {
            background: linear-gradient(135deg, #9B7EBD, #7B68A6);
            color: white;
        }
        .modal-content .btn-secondary {
            background: #ddd;
            color: #666;
        }
        .file-upload {
            border: 2px dashed #E8E0F0;
            border-radius: 10px;
            padding: 20px;
            text-align: center;
            margin-bottom: 15px;
            cursor: pointer;
            transition: all 0.3s;
        }
        .file-upload:hover {
            border-color: #9B7EBD;
        }
        .file-upload input {
            display: none;
        }
        .preview-img {
            max-width: 100%;
            border-radius: 10px;
            margin-top: 10px;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🤝 {{ t('title') }} - {{ t('display') }}</h1>
            <div class="header-right">
                <div class="user-info">
                    {{ t('user_id') }}: {{ user_id }} <span>{{ role }}</span>
                </div>
                <a href="/logout" class="btn" style="background:#e74c3c;color:white;padding:10px 20px;border-radius:10px;text-decoration:none;">{{ t('logout') }}</a>
            </div>
        </div>
        
        {% if is_high %}
        <div class="nav">
            <a href="/management">{{ t('management') }}</a>
            <a href="/display" class="active">{{ t('display') }}</a>
            <a href="/auxiliary">{{ t('auxiliary') }}</a>
        </div>
        {% endif %}
        
        <div class="wall" id="wall"></div>
        
        <div class="pagination">
            <button onclick="prevPage()" id="prevBtn">{{ t('prev_page') }}</button>
            <span class="page-info" id="pageInfo">1 / 1</span>
            <button onclick="nextPage()" id="nextBtn">{{ t('next_page') }}</button>
        </div>
    </div>
    
    <div class="add-btn" onclick="showModal()">+</div>
    
    <div class="modal" id="modal">
        <div class="modal-content">
            <h2>{{ t('add_praise') }}</h2>
            <textarea id="content" placeholder="请输入夸夸内容..."></textarea>
            
            <label>{{ t('praise_target') }}</label>
            <select id="targetId"></select>
            
            <div class="file-upload" onclick="document.getElementById('imageInput').click()">
                <p>📷 {{ t('upload_image') }}（可选）</p>
                <input type="file" id="imageInput" accept="image/*" onchange="previewImage(this)">
                <img id="imagePreview" class="preview-img" style="display:none;">
            </div>
            
            <div style="text-align: center; margin-top: 20px;">
                <button class="btn btn-secondary" onclick="hideModal()">取消</button>
                <button class="btn btn-primary" onclick="submitPraise()">{{ t('submit') }}</button>
            </div>
        </div>
    </div>
    
    <script>
        let currentPage = 1;
        let totalPages = 1;
        const pageSize = 10;
        let imageBase64 = '';
        
        async function loadUsers() {
            const res = await fetch('/api/users');
            const users = await res.json();
            
            const select = document.getElementById('targetId');
            select.innerHTML = '';
            
            for (const [id, info] of Object.entries(users)) {
                const option = document.createElement('option');
                option.value = id;
                option.textContent = id + ' - ' + info.name;
                select.appendChild(option);
            }
        }
        
        async function loadPraises() {
            const res = await fetch('/api/praises');
            const praises = await res.json();
            
            totalPages = Math.ceil(praises.length / pageSize) || 1;
            
            const start = (currentPage - 1) * pageSize;
            const pageData = praises.slice(start, start + pageSize);
            
            let html = '';
            pageData.forEach(p => {
                const avatar = p.user_id.toString().slice(-1);
                html += '<div class="praise-card">' +
                    '<div class="avatar">' + avatar + '</div>' +
                    '<div class="author">👤 用户 ' + p.user_id + '</div>' +
                    '<div class="target">🎯 受表扬: ' + p.target_id + '</div>' +
                    '<div class="content">' + p.content + '</div>';
                
                if (p.image) {
                    html += '<img src="' + p.image + '" class="image">';
                }
                
                html += '<div class="time">📅 ' + p.time + '</div></div>';
            });
            
            document.getElementById('wall').innerHTML = html || '<p style="color:#999;text-align:center;padding:40px;background:rgba(255,255,255,0.9);border-radius:15px;">暂无夸夸记录，快来发表第一条吧！</p>';
            
            document.getElementById('pageInfo').textContent = currentPage + ' / ' + totalPages;
            document.getElementById('prevBtn').disabled = currentPage <= 1;
            document.getElementById('nextBtn').disabled = currentPage >= totalPages;
        }
        
        function prevPage() {
            if (currentPage > 1) {
                currentPage--;
                loadPraises();
            }
        }
        
        function nextPage() {
            if (currentPage < totalPages) {
                currentPage++;
                loadPraises();
            }
        }
        
        function showModal() {
            document.getElementById('modal').classList.add('show');
            loadUsers();
        }
        
        function hideModal() {
            document.getElementById('modal').classList.remove('show');
            document.getElementById('content').value = '';
            document.getElementById('imagePreview').style.display = 'none';
            imageBase64 = '';
        }
        
        function previewImage(input) {
            if (input.files && input.files[0]) {
                const reader = new FileReader();
                reader.onload = function(e) {
                    imageBase64 = e.target.result;
                    const preview = document.getElementById('imagePreview');
                    preview.src = imageBase64;
                    preview.style.display = 'block';
                };
                reader.readAsDataURL(input.files[0]);
            }
        }
        
        async function submitPraise() {
            const content = document.getElementById('content').value.trim();
            const targetId = document.getElementById('targetId').value;
            
            if (!content) {
                alert('请输入内容');
                return;
            }
            
            const res = await fetch('/api/praises', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    content: content,
                    target_id: targetId,
                    image: imageBase64
                })
            });
            
            const result = await res.json();
            
            if (result.ok) {
                hideModal();
                loadPraises();
            } else {
                alert('提交失败');
            }
        }
        
        loadPraises();
    </script>
</body>
</html>
"""

# 路由
@app.route('/')
def index():
    if is_logged_in():
        return redirect(url_for('display'))
    return redirect(url_for('login'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        user_id = request.form.get('user_id', '').strip()
        lang = request.form.get('lang', 'zh')
        
        session['lang'] = lang
        
        # 检查语言切换
        if not user_id:
            return render_template_string(LOGIN_PAGE, t=t, lang=lang, error=None)
        
        users = get_users()
        if user_id in users:
            session['user_id'] = user_id
            return redirect(url_for('display'))
        else:
            return render_template_string(LOGIN_PAGE, t=t, lang=lang, error='用户ID不存在')
    
    return render_template_string(LOGIN_PAGE, t=t, lang=get_lang(), error=None)

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

@app.route('/management')
def management():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    users = get_users()
    role = users.get(user_id, {}).get('role', '普通用户')
    
    if role != '高级用户':
        return '<h2 style="color:#e74c3c;text-align:center;margin-top:100px;">' + t('no_permission') + '</h2>'
    
    return render_template_string(MANAGEMENT_PAGE, t=t, user_id=user_id, role=role)

@app.route('/display')
def display():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    users = get_users()
    role = users.get(user_id, {}).get('role', '普通用户')
    
    return render_template_string(DISPLAY_PAGE, t=t, user_id=user_id, role=role, is_high=(role=='高级用户'))

@app.route('/auxiliary')
def auxiliary():
    if not is_logged_in():
        return redirect(url_for('login'))
    
    user_id = session['user_id']
    users = get_users()
    role = users.get(user_id, {}).get('role', '普通用户')
    
    if role != '高级用户':
        return '<h2 style="color:#e74c3c;text-align:center;margin-top:100px;">' + t('no_permission') + '</h2>'
    
    return '''
    <html>
    <head><meta charset="utf-8"><title>辅助页面</title></head>
    <body style="background:#9B7EBD;min-height:100vh;display:flex;align-items:center;justify-content:center;">
        <div style="background:white;padding:50px;border-radius:20px;text-align:center;">
            <h2 style="color:#5D4E7A;">辅助页面</h2>
            <p style="color:#9B7EBD;margin-top:10px;">此页面暂无内容</p>
            <a href="/management" style="display:inline-block;margin-top:20px;padding:12px 30px;background:#9B7EBD;color:white;text-decoration:none;border-radius:10px;">返回管理页</a>
        </div>
    </body>
    </html>
    '''

# API 路由
@app.route('/api/users')
def api_users():
    return jsonify(get_users())

@app.route('/api/import-users', methods=['POST'])
def api_import_users():
    if not is_logged_in() or not is_high_user(session['user_id']):
        return jsonify({'error': '无权限'}), 403
    
    data = request.json
    users = {}
    
    for item in data:
        users[str(item['id'])] = {'role': item['role'], 'name': f"用户{item['id']}"}
    
    save_users(users)
    return jsonify({'ok': True})

@app.route('/api/praises')
def api_praises():
    praises = get_praises()
    # 按时间倒序
    praises.sort(key=lambda x: x['time'], reverse=True)
    return jsonify(praises)

@app.route('/api/praises', methods=['POST'])
def api_add_praise():
    if not is_logged_in():
        return jsonify({'error': '未登录'}), 401
    
    data = request.json
    praises = get_praises()
    
    new_praise = {
        'id': len(praises) + 1 + int(datetime.now().timestamp()),
        'user_id': session['user_id'],
        'target_id': data.get('target_id', ''),
        'content': data.get('content', ''),
        'image': data.get('image', ''),
        'time': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    }
    
    praises.append(new_praise)
    save_praises(praises)
    
    return jsonify({'ok': True})

@app.route('/api/praises/<int:praise_id>', methods=['DELETE'])
def api_delete_praise(praise_id):
    if not is_logged_in() or not is_high_user(session['user_id']):
        return jsonify({'error': '无权限'}), 403
    
    praises = get_praises()
    praises = [p for p in praises if p['id'] != praise_id]
    save_praises(praises)
    
    return jsonify({'ok': True})

@app.route('/api/praises/batch-delete', methods=['POST'])
def api_batch_delete():
    if not is_logged_in() or not is_high_user(session['user_id']):
        return jsonify({'error': '无权限'}), 403
    
    data = request.json
    ids = data.get('ids', [])
    
    praises = get_praises()
    praises = [p for p in praises if p['id'] not in ids]
    save_praises(praises)
    
    return jsonify({'ok': True})

# 报表导出
@app.route('/api/export/report1')
def export_report1():
    if not is_logged_in() or not is_high_user(session['user_id']):
        return '无权限', 403
    
    users = get_users()
    data = []
    for uid, info in users.items():
        data.append({'用户ID': uid, '权限名称': info.get('role', ''), '姓名': info.get('name', '')})
    
    df = pd.DataFrame(data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='用户权限')
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = 'attachment; filename=report1_users.xlsx'
    
    return response

@app.route('/api/export/report2')
def export_report2():
    if not is_logged_in() or not is_high_user(session['user_id']):
        return '无权限', 403
    
    praises = get_praises()
    
    # 过滤当月
    now = datetime.now()
    current_month = now.strftime('%Y-%m')
    
    data = []
    for p in praises:
        if p['time'].startswith(current_month):
            data.append({
                '用户ID': p['user_id'],
                '受表扬人ID': p['target_id'],
                '内容': p['content'],
                '时间': p['time']
            })
    
    df = pd.DataFrame(data) if data else pd.DataFrame(columns=['用户ID', '受表扬人ID', '内容', '时间'])
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='录入记录')
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = 'attachment; filename=report2_records.xlsx'
    
    return response

@app.route('/api/export/report3')
def export_report3():
    if not is_logged_in() or not is_high_user(session['user_id']):
        return '无权限', 403
    
    praises = get_praises()
    
    # 过滤当月
    now = datetime.now()
    current_month = now.strftime('%Y-%m')
    
    # 统计频次
    user_counts = {}
    target_counts = {}
    
    for p in praises:
        if p['time'].startswith(current_month):
            uid = p['user_id']
            tid = p['target_id']
            
            user_counts[uid] = user_counts.get(uid, 0) + 1
            target_counts[tid] = target_counts.get(tid, 0) + 1
    
    # 创建数据
    user_data = [{'ID': k, '类型': '发布者', '频次': v} for k, v in user_counts.items()]
    target_data = [{'ID': k, '类型': '受表扬人', '频次': v} for k, v in target_counts.items()]
    
    df = pd.DataFrame(user_data + target_data)
    
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='统计')
    
    output.seek(0)
    
    response = make_response(output.getvalue())
    response.headers['Content-Type'] = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    response.headers['Content-Disposition'] = 'attachment; filename=report3_stats.xlsx'
    
    return response

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
