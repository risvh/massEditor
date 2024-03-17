from massEditor import init

init(options=[
    # "regenerate_all",
    # "regenerate_categories",
    # "regenerate_objects",
    # "regenerate_transitions",
    # "regenerate_depths",
    "regenerate_smart",
    ], verbose=True)

from draw import drawObject

img = drawObject(12273)



from flask import Flask, render_template
import base64
import io


app = Flask(__name__)

@app.route('/')
def hello_world():

    data = io.BytesIO()
    # img.save(data, "jpg")
    img.convert('RGBA').save(data, format='PNG')
    encoded_img_data = base64.b64encode(data.getvalue())

    return render_template("index.html", img_data=encoded_img_data.decode('utf-8'))


if __name__ == '__main__':
    app.run(host='0.0.0.0')




