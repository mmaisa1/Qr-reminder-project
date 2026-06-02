from flask import Blueprint, render_template, send_file, current_app
import qrcode
import io
import os

qr_bp = Blueprint('qr', __name__)

@qr_bp.route('/')
def qr_code_page():
    current_app.logger.info('Rendering QR code page')
    return render_template('qrcode.html')

@qr_bp.route('/qr-code')
def generate_qr():
    url = os.getenv('URL')
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill='black', back_color='white').convert('RGB')
    img = img.resize((300, 300))
    img_with_corners = img.copy()
    corner_radius = 30

    for x in range(img.size[0]):
        for y in range(img.size[1]):
            if (
                x < corner_radius and y < corner_radius
            ) or (
                x < corner_radius and y >= img.size[1] - corner_radius
            ) or (
                x >= img.size[0] - corner_radius and y < corner_radius
            ) or (
                x >= img.size[0] - corner_radius and y >= img.size[1] - corner_radius
            ):
                img_with_corners.putpixel((x, y), (255, 255, 255))

    img_io = io.BytesIO()
    img_with_corners.save(img_io, 'PNG')
    img_io.seek(0)

    current_app.logger.info('Generated QR code')
    return send_file(img_io, mimetype='image/png')