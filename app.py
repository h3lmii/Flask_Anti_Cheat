from flask import Flask, render_template, Response
import cv2 
import os
app = Flask(__name__)

Conf_threshold = 0.4
NMS_threshold = 0.4
COLORS = [(0, 255, 0), (0, 0, 255), (255, 0, 0),
          (255, 255, 0), (255, 0, 255), (0, 255, 255)]
this_path=os.getcwd()
class_name = []
list_labels=[]
with open('classes.txt', 'r') as f:
    class_name = [cname.strip() for cname in f.readlines()]
#print(class_name)

#get the yolo model weights & params
net = cv2.dnn.readNet('yolov7-tiny.weights', 'yolov7-tiny.cfg')
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA_FP16)

model = cv2.dnn_DetectionModel(net)
model.setInputParams(size=(416, 416), scale=1/255, swapRB=True)


#ready='Verify''}
conditions=['-Camera ❌','-One Person detected ❌','-face detected ❌','-No phones ❌','Verify','window.location.reload(true)','window.location.reload(true)','window.location.reload(true)']

camera = cv2.VideoCapture(0)  # use 0 for web camera
#camera2 = cv2.VideoCapture(0)


frame_width = int(camera.get(3))
frame_height = int(camera.get(4))
   
size = (frame_width, frame_height)



def gen_frames():  # generate frame by frame from camera
    conditions[3]='-No phones ✅'
    single=True
    while True:
        # Capture frame-by-frame
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            
            
            detector=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
            faces=detector.detectMultiScale(frame,1.1,7)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
             #Draw the rectangle around each face
            if type(faces)!=tuple:
                if (len(faces)>1):
                    single=False
                else:
                    conditions[2]="-Face detected ✅"
            else:

                conditions[2]="-Face detected ❌"

           # if len(sr.Microphone.list_microphone_names()):
            #    conditions[1]="-Microphone ✅"
            #else:
              #  '-Microphone ❌'
            if single==True and conditions[2]=="-Face detected ✅":
                conditions[1]="-One Person detected ✅"
            else:
                conditions[1]="-One Person detected ❌"






            classes, scores, boxes = model.detect(frame, Conf_threshold, NMS_threshold)
            for (classid, score, box) in zip(classes, scores, boxes):
                #color = COLORS[int(classid) % len(COLORS)]
                color=(0,0,0)
                label = "%s" %(class_name[classid])
                if label=='cell phone':
                    conditions[3]='-No phones ❌'
                

                #print(label)
                #cv2.rectangle(frame, box, color, 1)
                #cv2.putText(frame, label, (box[0], box[1]-10),
                           #cv2.FONT_HERSHEY_COMPLEX, 0.6, color, 1)
                

            if camera.isOpened():
                conditions[0]="-Camera ✅"
            
            if  conditions[1]=="-One Person detected ✅" and conditions[2]=="-Face detected ✅" and conditions[3]=="-No phones ✅" and conditions[0]=="-Camera ✅" :
                conditions[4]='take the test'
                conditions[5]="window.location.href='http://localhost:3000/js_quizz'"
                conditions[6]="window.location.href='http://localhost:3000/html_quiz'"
                conditions[7]="window.location.href='http://localhost:3000/css_quiz'"
            else:
                conditions[4]='Please Verify all the Conditions to take the Test'
                conditions[5]="window.location.reload(true)"
                conditions[6]="window.location.reload(true)"
                conditions[7]="window.location.reload(true)"


               

            for (x, y, w, h) in faces:
                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                roi_gray = gray[y:y+h, x:x+w]
                roi_color = frame[y:y+h, x:x+w]
                

            ret, buffer = cv2.imencode('.jpg', frame)
            ready='Take The Test'
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                  b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            #print(single)
            

@app.route('/video_feed')
def video_feed():
    #Video streaming route. Put this in the src attribute of an img tag
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/js')
def index():
    """Video streaming home page."""
    #return render_template('form.html', j=j)
    return render_template('form.html', conds=conditions,read=conditions[4],url=conditions[5])

@app.route('/html')
def html():
    """Video streaming home page."""
    #return render_template('form.html', j=j)
    return render_template('form.html', conds=conditions,read=conditions[4],url=conditions[6])

@app.route('/css')
def css():
    """Video streaming home page."""
    #return render_template('form.html', j=j)
    return render_template('form.html', conds=conditions,read=conditions[4],url=conditions[7])

app.run(debug=True)