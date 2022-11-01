from flask import Flask, render_template, request
from PIL import Image
import requests
from io import BytesIO

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/color_recognizer', methods=['POST', 'GET'])
def get_image():
    image_source = request.form["image"]
    delta = int(request.form["delta"])
    if image_source[:4] == 'http':
        response = requests.get(image_source)
        img = Image.open(BytesIO(response.content))
    else:
        img = Image.open(f'static/{image_source}')

    width, height = img.size
    total_pixels = width * height
    original_color_count = {}

    # Loop through every pixel in the image
    for w in range(width):
        for h in range(height):
            current_color = img.getpixel((w, h))
            delta_colors = []
            for rgb in current_color:
                delta_color = round(rgb / delta) * delta
                if delta_color > 255:
                    delta_color = 255
                delta_colors.append(delta_color)

            delta_colors = tuple(delta_colors)

            if delta_colors in original_color_count:
                original_color_count[delta_colors] += 1
            else:
                original_color_count[delta_colors] = 1

    all_colors = sorted(original_color_count.items(), key=lambda tup: tup[1], reverse=True)

    hex_perc_colors = {}
    for i in range(10):
        hex_color = '#%02x%02x%02x' % all_colors[i][0]
        perc_color = round(all_colors[i][1] * 100 / total_pixels, 6)
        hex_perc_colors[hex_color] = perc_color

    hex_perc_colors = list(hex_perc_colors.items())

    return render_template("color_recognizer.html", all_colors=all_colors, hex_perc_colors=hex_perc_colors,
                           image_source=image_source)


if __name__ == "__main__":
    app.run(debug=True)
