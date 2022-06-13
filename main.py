from flask import Flask, jsonify, request
from werkzeug.utils import secure_filename
import os, subprocess, time, threading

app = Flask(__name__)
@app.route("/")
def home():
    return jsonify(
                {
                    'status':200,
                    'message':'Welcome to API Video'
                }
            )

@app.route('/upload/', methods=['POST'])
def update_record():
    dt = request.form
    res = dt['resolution']

    if int(res) not in [360, 480, 720, 1280, 2048]:
        return jsonify({
            'status': 400,
            'messages':'Error -- Please insert the correct resolution video. etc: 360, 480, 720, 1280, 2048'
        })

    file = request.files['file']
    file_name = secure_filename(file.filename)
    file_dir = '/home/thoriq/Documents/thor/flask/api-video/tmp/'
    file.save(os.path.join(file_dir, file_name))
    file_loc = file_dir + file_name

    uploads_name = str(int(time.time())) + '_converted_' + str(res) + '.mp4'
    uploads_dir = '/home/thoriq/Documents/thor/flask/api-video/uploads/' + uploads_name

    scale = 'scale='+str(res)+':-2'

    file_res = subprocess.run(args=['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-show_entries', 'stream=width', '-of', 'default=nw=1:nk=1', file_loc], stdout=subprocess.PIPE)

    if int(res) > int(file_res.stdout):
        subprocess.run(['rm', file_loc])
        return jsonify({
            'status': 400,
            'messages':'Error -- New resolution is too high from the original video'
        })

    class myThread (threading.Thread):
        def __init__(self):
            threading.Thread.__init__(self)
        def run(self):
            video_process()
            subprocess.run(['rm', file_loc])
            exit()

    def video_process():
        subprocess.run(['ffmpeg', '-y', '-i', file_loc, '-vcodec', 'libx264', '-preset', 'fast', '-filter:v', scale, '-crf', '26', uploads_dir])

    thread_video = myThread()

    thread_video.start()

    return jsonify({
        'status': 200,
        'file':uploads_name
    })
