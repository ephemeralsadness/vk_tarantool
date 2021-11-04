from flask import abort, Flask, redirect, render_template, request, url_for
import os.path
import qrcode
from tarantool_manager import TarantoolManager
from useful_data import TARANTOOL_USERNAME, TARANTOOL_PASSWORD

app = Flask(__name__)
IP = 'http://127.0.0.1:5000'
tarantool_manager = TarantoolManager(TARANTOOL_USERNAME, TARANTOOL_PASSWORD)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/info/<string:link_id>')
def info(link_id):
    image_filename = 'static/{}.png'.format(link_id)
    short_link = '{}/go/{}'.format(IP, link_id)
    link, amount, last_datetime = tarantool_manager.get_full_link(link_id, request.remote_addr)
    if not os.path.isfile(image_filename):
        qrcode.make(short_link).save(image_filename)

    return render_template('link_info.html',
                           image_filename=('/'+image_filename),
                           link=link,
                           amount=amount,
                           last_datetime=last_datetime,
                           recommendations=tarantool_manager.get_recommendations(request.remote_addr))


@app.route('/submit/', methods=['POST'])
def submit():
    link = request.form['link']
    if link is None:
        abort(404, description='Error: can\'t find link argument')
    link_id = tarantool_manager.save_link(link)

    return redirect(url_for('info', link_id=link_id))


@app.route('/set', methods=['POST'])
def set_link():
    link = request.form['link']
    if link is None:
        abort(404, description='Error: can\'t find link argument')
    link_id = tarantool_manager.save_link(link)

    return '{}/go/{}'.format(IP, link_id)


@app.route('/go/<string:link_id>')
def go(link_id):
    link = tarantool_manager.get_link(link_id, request.remote_addr)
    if link is None:
        abort(404, description='Link ID is bad')
    return redirect(link, code=301)


if __name__ == '__main__':
    app.run()
