from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)

def setup_camera(width, height):
    cam = cv2.VideoCapture(0)
    cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
    cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
    return cam

def get_frame(cam):
    _, frame = cam.read()
    return frame

def convert_to_hsv(frame):
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    return hsv_frame

def get_center_coordinates(frame):
    height, width, _ = frame.shape
    cx = int(width / 2)
    cy = int(height / 2)
    return cx, cy

def detect_color(hue, saturation, value):
    if hue == 0 or saturation == 0:
        return "PUTIH"
    elif value < 50:
        return "HITAM"
    elif saturation < 50:
        return "ABU-ABU"
    elif hue < 5:
        return "MERAH"
    elif hue < 20:
        return "ORANGE"
    elif hue < 30:
        return "KUNING"
    elif hue < 70:
        return "HIJAU"
    elif hue < 125:
        return "BIRU"
    elif hue < 145:
        return "UNGU"
    elif hue < 170:
        return "PINK"
    else:
        return "MERAH"

def draw_center_circle(frame, cx, cy):
    cv2.circle(frame, (cx, cy), 5, (25, 25, 25), 3)

def put_text(frame, text, cx, cy, b, g, r):
    cv2.putText(frame, text, (cx - 100, cy - 150), cv2.FONT_HERSHEY_SIMPLEX, 1.5, (b, g, r), 2)

def generate_frames():
    cam = setup_camera(1280, 720)
    while True:
        frame = get_frame(cam)
        hsv_frame = convert_to_hsv(frame)
        cx, cy = get_center_coordinates(frame)
        
        pixel_center = hsv_frame[cy, cx]
        hue, saturation, value = pixel_center
        
        color = detect_color(hue, saturation, value)
        
        pixel_center_bgr = frame[cy, cx]
        b, g, r = [int(x) for x in pixel_center_bgr]
        
        draw_center_circle(frame, cx, cy)
        put_text(frame, color, cx, cy, b, g, r)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

if __name__ == "__main__":
    app.run(debug=True)
