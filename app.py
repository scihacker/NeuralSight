# -*- coding:utf-8 -*- 
from flask import Flask
from flask import render_template, session, request, jsonify, redirect
from model import code_model, global_model, architecture_model, content_model, activation_model
import server_utils.secret.config as config
import os
import threading

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
    path = content_model.get_architecture(session['code'])
    if not path:
        model = global_model.load_model(session['code'], session['data'])
        if not model:
            return render_template('error.html', page=1, exp=u"文件路径有误，无法读取网络模型！")
        path = content_model.get_path_by_code(session['code'], "structure") + "arch.png"
        architecture_model.output_architecture(model, out_path=path)
    return render_template('structure.html', png=path)

@app.route('/activation')
def activation():
    if not session.has_key('code'):
        return render_template('error.html', page=2, exp=u"请在开始页面内使用Code！")
    if session.has_key('image'):
        model = global_model.load_model(session['code'], session['data'])
        layers = model.layers
        out_layers = [[k, v.name, False] for k, v in enumerate(layers)]
        path, activation_list = content_model.get_activation(session['code'], session['image'], out_layers)
    else:
        layers, activation_list, path = [], [], ""
    return render_template('activation.html', layers=out_layers, activations=activation_list, path=path)

@app.route('/filter')
def filter():
    if not session.has_key('code'):
        return render_template('error.html', page=2, exp=u"请在开始页面内使用Code！")
    model = global_model.load_model(session['code'], session['data'])
    layers = model.layers
    out_layers = [[k, v.name, False] for k, v in enumerate(layers)]
    out_layers = out_layers[1:]
    path, filter_list = content_model.get_filter(session['code'], out_layers)
    return render_template('filter.html', layers=out_layers, filters=filter_list, path=path)

@app.route("/compute_filter", methods=['POST'])
def compute_filter():
    layer_id = int(request.form['id'])
    if not session.has_key('code'):
        return jsonify({"error": 1, "msg": "invalid use"})
    model = global_model.load_model(session['code'], session['data'])
    out_path = content_model.get_path_by_code(session['code'], "filter") + model.layers[layer_id].name + "/"
    def filter_thread():
        filter_model.compute_filter(model, layer_id, out_path)
    return jsonify({"error": 0, "msg": "ok"})

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
        session.pop('tag'), session.pop('type'), session.pop('data'), session.pop('image')
    except Exception:
        pass
    if global_model.dispose_model(code):
        return jsonify({"error": 0, "msg": "ok"})
    else:
        return jsonify({"error": 2, "msg": "Dispose Error"})

@app.route("/upload_image", methods=['POST'])
def upload_image():
    f_n = request.form.get("file_name")
    if not request.files.has_key('file') and not f_n:
        return jsonify({"error": 1, "msg": "File Not Uploaded"})
    if request.files.has_key('file'):
        f = request.files['file']
        if (f.filename[-4:] not in ['.jpg', '.png', '.JPG', '.PNG']):
            return jsonify({"error": 3, "msg": f.filename[-4:] + "File Not Supported"})
        import time
        now = int(time.time() * 1000)
        file_name = "./static/upload/" + str(now) + f.filename[-4:]
        f.save(file_name)
        session['image'] = str(now) + f.filename[-4:]
    elif f_n:
        if os.path.exists("./static/upload/" + f_n):
            session['image'] = f_n
        else:
            return jsonify({"error": 2, "msg": "File_name Not Found"})
    return jsonify({"error": 0, "msg": "ok"})

@app.route("/compute_activation", methods=['POST'])
def compute_activation():
    layer_id = int(request.form['id'])
    if not session.has_key('code') or not session.has_key('image'):
        return jsonify({"error": 1, "msg": "invalid use"})
    model = global_model.load_model(session['code'], session['data'])
    out_path = content_model.get_path_by_code(session['code'], "activation") + session['image'][:-4] + "/" + model.layers[layer_id].name + "/"
    count = activation_model.compute_activation(model, layer_id, session['image'], out_path)
    return jsonify({"error": 0, "path": out_path, "count": count, "msg": "ok"})

if __name__ == "__main__":
    app.run("localhost", port=8080, debug=True)
