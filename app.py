#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
夸夸墙 - HR模块网站 (简化版)
"""

from flask import Flask, render_template_string, request, jsonify, session, redirect, url_for, make_response
import json, os
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'kuakuawall-secret-key-2026'

DATA_DIR = '/tmp/kuakuawall'
os.makedirs(DATA_DIR, exist_ok=True)

USERS_FILE = os.path.join(DATA_DIR, 'users.json')
PRAISES_FILE = os.path.join(DATA_DIR, 'praises.json')

def init_data():
    if not os.path.exists(USERS_FILE):
        default_users = {"101": {"role": "高级用户", "name": "管理员"}, "102": {"role": "普通用户", "name": "员工A"}, "103": {"role": "高级用户", "name": "经理B"}}
        json.dump(default_users, open(USERS_FILE, 'w'), ensure_ascii=False, indent=2)
    if not os.path.exists(PRAISES_FILE):
        json.dump([], open(PRAISES_FILE, 'w'))

init_data()

LANGUAGES = {
    'zh': {'title': '夸夸墙', 'login': '登录', 'login_id': '登录ID', 'confirm': '确认', 'logout': '退出', 'management': '管理', 'display': '展示', 'auxiliary': '辅助', 'import_excel': '导入', 'report1': '报表1', 'report2': '报表2', 'report3': '报表3', 'add': '添加', 'submit': '提交', 'delete': '删除', 'high': '高级用户', 'normal': '普通用户', 'ch': '中文', 'en': 'English'},
    'en': {'title': 'Praise Wall', 'login': 'Login', 'login_id': 'ID', 'confirm': 'OK', 'logout': 'Logout', 'management': 'Manage', 'display': 'Display', 'auxiliary': 'Aux', 'import_excel': 'Import', 'report1': 'Report1', 'report2': 'Report2', 'report3': 'Report3', 'add': 'Add', 'submit': 'Submit', 'delete': 'Delete', 'high': 'High User', 'normal': 'Normal User', 'ch': '中文', 'en': 'English'}
}

def t(k): return LANGUAGES.get(session.get('lang', 'zh'), LANGUAGES['zh']).get(k, k)
def get_users(): return json.load(open(USERS_FILE))
def save_users(u): json.dump(u, open(USERS_FILE, 'w'), ensure_ascii=False, indent=2)
def get_praises(): return json.load(open(PRAISES_FILE))
def save_praises(p): json.dump(p, open(PRAISES_FILE, 'w'), ensure_ascii=False, indent=2)
def is_high(): u = session.get('user_id',''); return get_users().get(u,{}).get('role') == '高级用户'
def is_login(): return 'user_id' in session

LOGIN = '''<!DOCTYPE html><html><head><meta charset="utf-8"><title>夸夸墙</title><style>body{font-family:Arial;background:linear-gradient(135deg,#9B7EBD,#7B68A6);min-height:100vh;display:flex;align-items:center;justify-content:center}.box{background:white;padding:40px;border-radius:20px;box-shadow:0 10px 40px rgba(0,0,0,0.2);width:350px}input,select{width:100%;padding:12px;margin:10px 0;border:2px solid #ddd;border-radius:8px}.btn{width:100%;padding:14px;background:#9B7EBD;color:white;border:none;border-radius:8px;cursor:pointer;font-size:16px}.logo{text-align:center;font-size:28px;color:#7B68A6;margin-bottom:20px}</style></head><body><div class="box"><div class="logo">🤝 夸夸墙</div><form method="POST"><input type="text" name="user_id" placeholder="输入ID" required><select name="lang" onchange="this.form.submit()"><option value="zh" {% if l=='zh'%}selected{%endif%}>中文</option><option value="en" {% if l=='en'%}selected{%endif%}>English</option></select><button class="btn">{{t('confirm')}}</button></form></div></body></html>'''

MANAGE = '''<!DOCTYPE html><html><head><meta charset="utf-8"><title>管理</title><style>body{background:linear-gradient(135deg,#9B7EBD,#7B68A6);padding:20px}.nav{background:white;padding:15px;border-radius:10px;margin-bottom:20px}.nav a{color:#7B68A6;text-decoration:none;margin:0 15px}.h{background:white;padding:20px;border-radius:10px;margin-bottom:20px;display:flex;justify-content:space-between}.p{background:white;padding:20px;border-radius:10px;margin-bottom:20px}.btn{padding:10px 20px;background:#9B7EBD;color:white;border:none;border-radius:8px;cursor:pointer;margin:5px}</style></head><body><div class="h"><h1>🤝 夸夸墙-管理</h1><a href="/logout" class="btn" style="background:#e74c3c">退出</a></div><div class="nav"><a href="/management">管理</a><a href="/display">展示</a></div><div class="p"><h3>📥 导入用户</h3><p style="color:#666;font-size:13px">Excel格式: 用户ID | 权限</p><input type="file" id="f" accept=".xlsx"><button class="btn" onclick="up()">导入</button></div><div class="p"><h3>📊 导出报表</h3><button class="btn" onclick="loc='/api/r1'">{{t('report1')}}</button><button class="btn" onclick="loc='/api/r2'">{{t('report2')}}</button></div><div class="p"><h3>🗑️ 删除内容</h3><div id="l"></div></div><script src="https://cdnjs.cloudflare.com/ajax/libs/xlsx/0.18.5/xlsx.full.min.js"></script><script>async function up(){let f=document.getElementById('f').files[0];if(!f)return;let d=new Uint8Array(await f.arrayBuffer());let wb=XLSX.read(d,{type:'array'});let ws=wb.Sheets[wb.SheetNames[0]];let data=XLSX.utils.sheet_to_json(ws,{header:1});let u={};data.forEach(r=>{if(r[0]&&r[1])u[String(r[0])]={role:r[1],name:'用户'+r[0]}});await fetch('/api/import',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(u)});alert('导入成功');}async function load(){let r=await fetch('/api/p');let p=await r.json();let h='';p.forEach(x=>{h+='<div style="padding:10px;border-bottom:1px solid #eee"><input type="checkbox" value="'+x.id+'"> <b>'+x.u+'</b>: '+x.c.substring(0,30)+' <button onclick="del('+x.id+')" style="background:#e74c3c;color:white;border:none;padding:5px 10px;border-radius:5px;cursor:pointer">删除</button></div>'});document.getElementById('l').innerHTML=h||'暂无';}async function del(id){await fetch('/api/p/'+id,{method:'DELETE'});load();}load();</script></body></html>'''

DISPLAY = '''<!DOCTYPE html><html><head><meta charset="utf-8"><title>展示</title><style>body{background:linear-gradient(135deg,#9B7EBD,#7B68A6);padding:20px}.nav{background:white;padding:15px;border-radius:10px;margin-bottom:20px}.nav a{color:#7B68A6;text-decoration:none;margin:0 15px}.h{background:white;padding:20px;border-radius:10px;margin-bottom:20px;display:flex;justify-content:space-between}.g{display:grid;grid-template-columns:repeat(auto-fill,minmax(280px,1fr));gap:20px}.c{background:white;padding:20px;border-radius:15px;box-shadow:0 5px15px rgba(0,0,0,0.1)}.c .a{color:#7B68A6;font-weight:bold}.c .t{color:#999;font-size:12px}.add{position:fixed;bottom:30px;right:30px;width:60px;height:60px;background:#9B7EBD;border-radius:50%;color:white;font-size:30px;display:flex;align-items:center;justify-content:center;cursor:pointer;box-shadow:0 5px20px rgba(123,104,166,0.5)}.m{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.5);align-items:center;justify-content:center;z-index:100}.ms{background:white;padding:30px;border-radius:20px;width:90%;max-width:400px}textarea{width:100%;height:100px;margin:10px 0;border:2px solid #ddd;border-radius:8px;padding:10px}select{width:100%;padding:10px;margin:10px 0;border:2px solid #ddd;border-radius:8px}</style></head><body><div class="h"><h1>🤝 夸夸墙-展示</h1><a href="/logout" class="btn" style="background:#e74c3c;color:white;padding:10px 20px;text-decoration:none;border-radius:8px">退出</a></div>{% if h %}<div class="nav"><a href="/management">{{t('management')}}</a><a href="/display">{{t('display')}}</a></div>{% endif %}<div class="g" id="g"></div><div class="add" onclick="show()">+</div><div class="m" id="m"><div class="ms"><h3>{{t('add')}}</h3><textarea id="c" placeholder="输入内容..."></textarea><select id="tid"></select><button class="btn" onclick="sub()">{{t('submit')}}</button><button class="btn" onclick="hide()" style="background:#999">取消</button></div></div><script>let p=1;async function load(){let r=await fetch('/api/p');let d=await r.json();let h='';d.slice((p-1)*10,p*10).forEach(x=>{h+='<div class="c"><div class="a">👤 '+x.u+'</div><div style="color:#9B7EBD;font-size:13px">🎯 '+x.ti+'</div><div style="margin:10px0">'+x.c+'</div><div class="t">'+x.te+'</div></div>'});document.getElementById('g').innerHTML=h||'暂无记录';}async function users(){let r=await fetch('/api/u');let u=await r.json();let s=document.getElementById('tid');s.innerHTML='';for(let id in u)s.innerHTML+='<option value="'+id+'">'+id+' - '+u[id].name+'</option>';}function show(){document.getElementById('m').style.display='flex';users();}function hide(){document.getElementById('m').style.display='none';}async function sub(){let c=document.getElementById('c').value;if(!c)return alert('请输入');let ti=document.getElementById('tid').value;await fetch('/api/p',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({c:c,ti:ti})});hide();load();}load();</script></body></html>'''

@app.route('/')
def index(): return redirect('/display' if is_login() else '/login')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method=='POST':
        uid = request.form.get('user_id','').strip()
        lang = request.form.get('lang','zh')
        session['lang'] = lang
        if uid:
            if uid in get_users():
                session['user_id'] = uid
                return redirect('/display')
            else:
                return render_template_string(LOGIN, t=t, l=lang, e='用户不存在')
    return render_template_string(LOGIN, t=t, l=get_lang(), e='')

@app.route('/logout')
def logout(): session.clear(); return redirect('/login')

@app.route('/management')
def management():
    if not is_login(): return redirect('/login')
    if not is_high(): return '<h2 style="text-align:center;margin-top:100px;color:#e74c3c">无权限</h2>'
    return render_template_string(MANAGE, t=t)

@app.route('/display')
def display():
    if not is_login(): return redirect('/login')
    return render_template_string(DISPLAY, t=t, h=is_high())

def get_lang(): return session.get('lang','zh')

@app.route('/api/u')
def api_u(): return jsonify(get_users())

@app.route('/api/import', methods=['POST'])
def api_import():
    if not is_login() or not is_high(): return '无权限',403
    save_users(request.json)
    return jsonify({'ok':True})

@app.route('/api/p')
def api_p():
    ps = get_praises()
    ps.sort(key=lambda x:x['te'],reverse=True)
    return jsonify([{'id':p['id'],'u':p['u'],'ti':p['ti'],'c':p['c'],'te':p['te']} for p in ps])

@app.route('/api/p', methods=['POST'])
def api_add_p():
    if not is_login(): return '未登录',401
    ps = get_praises()
    np = {'id':int(datetime.now().timestamp()*100),'u':session['user_id'],'ti':request.json.get('ti',''),'c':request.json.get('c',''),'te':datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    ps.append(np)
    save_praises(ps)
    return jsonify({'ok':True})

@app.route('/api/p/<int:pid>', methods=['DELETE'])
def api_del_p(pid):
    if not is_login() or not is_high(): return '无权限',403
    ps = [p for p in get_praises() if p['id']!=pid]
    save_praises(ps)
    return jsonify({'ok':True})

# 导出CSV格式(Excel可直接打开)
@app.route('/api/r1')
def export_r1():
    if not is_login() or not is_high(): return '无权限',403
    users = get_users()
    csv = '用户ID,权限,姓名\n'
    for uid,info in users.items(): csv += f'{uid},{info.get("role","")},{info.get("name","")}\n'
    r = make_response(csv)
    r.headers['Content-Type'] = 'text/csv'
    r.headers['Content-Disposition'] = 'attachment; filename=user_permissions.csv'
    return r

@app.route('/api/r2')
def export_r2():
    if not is_login() or not is_high(): return '无权限',403
    ps = get_praises()
    now = datetime.now().strftime('%Y-%m')
    csv = '用户ID,受表扬ID,内容,时间\n'
    for p in ps:
        if p['te'].startswith(now): csv += f'{p["u"]},{p["ti"]},{p["c"].replace(","," ")},{p["te"]}\n'
    r = make_response(csv)
    r.headers['Content-Type'] = 'text/csv'
    r.headers['Content-Disposition'] = 'attachment; filename=monthly_records.csv'
    return r

if __name__=='__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT',5000)))
