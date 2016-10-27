# -*- coding:utf-8 -*- 
from flask import Flask
from flask import render_template, session, request, jsonify
from model import code_model, global_model, architecture_model, content_model
import server_utils.secret.config as config

app = Flask(__name__)
app.secret_key = config.SECRET_KEY

@app.route("/")
def home():
    return render_template('index.html')

@app.route("/code")
def code():
    codes = code_model.get_full_code_history()
    return render_template('code.html', history=codes)

@app.route('/structure')
def structure():
    if not session.has_key('code'):
        return render_template('error.html', page=1, exp=u"请在开始页面内使用Code！")
    model = global_model.load_model(session['code'], session['data'])
    if not model:
        return render_template('error.html', page=1, exp=u"文件路径有误，无法读取网络模型！")
    path = content_model.get_architecture(session['code'])
    if not path:
        path = content_model.get_path_by_code(session['code'], "structure") + "arch.png"
        architecture_model.output_architecture(model, out_path=path)
    return render_template('structure.html', png=path)

@app.route("/use_code", methods=['POST'])
def use_code():
    tag, code_str = request.form['tag'], request.form['code']
    try:
        data = code_model.decrypt_code(code_str, config.AES_KEY, config.AES_IV)
    except Exception:
        return jsonify({"error": 1, "msg": "Incorrect code"})
    history = code_model.get_full_code_history()
    for i, k in enumerate(history):
        if k[1] == code_str:
            if k[0] == tag:
                break
            new_history = [(tag, code_str)] + history[:i] + history[i + 1:]
            code_model.save_code_history(new_history)
            break
    else:
        new_history = [(tag, code_str)] + history
        code_model.save_code_history(new_history)
    session['tag'], session['code'], session['data'], session['type'] = tag, code_str, data['path'], data['type']
    return jsonify({"error": 0, "msg": "ok"})

@app.route("/stop_code", methods=['POST'])
def stop_code():
    if not session.has_key('code'):
        return jsonify({"error": 1, "msg": "No Code"})
    code = session.pop('code')
    try:
        session.pop('tag'), session.pop('type'), session.pop('data')
    except Exception:
        pass
    if global_model.dispose_model(code):
        return jsonify({"error": 0, "msg": "ok"})
    else:
        return jsonify({"error": 2, "msg": "Dispose Error"})

if __name__ == "__main__":
    app.run("localhost", port=8080, debug=True)
