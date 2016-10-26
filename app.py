from flask import Flask
from flask import render_template, session, request
from model import code_model
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

@app.route("/use_code", methods=['POST'])
def use_code():
    tag, code_str = request.form['tag'], request.form['code']
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
    session['tag'], session['code'] = tag, code_str
    return "0"

if __name__ == "__main__":
    app.run("localhost", port=8080, debug=True)