import numpy
import cv2
import pyvirtualcam
import subprocess
from tp1_firsterode import *
from Python import strel

def myerode(im,el):
    return cv2.erode(im, el)

def mydilate(im,el):
    return cv2.dilate(im, el)

def mygradient(im,el):
    return mydilate(im,el)- myerode(im,el)

def first_gradient(im):
    return first_dilate(im) - first_erode(im)

# v4l2loopback 0.12.7 bloque /dev/video10 après chaque utilisation : on recharge le module
def open_virtualcam(width, height):
    try:
        return pyvirtualcam.Camera(width=width, height=height, fps=30, device="/dev/video10")
    except RuntimeError:
        subprocess.run(["pkexec", "sh", "-c",
                        "modprobe -r v4l2loopback; modprobe v4l2loopback devices=1 video_nr=10 "
                        "card_label='Virtual Cam' exclusive_caps=1"], check=True)
        return pyvirtualcam.Camera(width=width, height=height, fps=30, device="/dev/video10")

"""
dog = cv2.imread("Images/dog.png", cv2.IMREAD_GRAYSCALE)
cv2.imshow("Gradient chien", numpy.uint8(first_gradient(dog)))
cv2.waitKey(0)
"""
cap = cv2.VideoCapture(0)
#cap = cv2.VideoCapture("Images/SG1.m4v")

el = strel.build('carre', 1)

_, frame = cap.read()

with open_virtualcam(frame.shape[1], frame.shape[0]) as cam:
    while True:
        _, frame = cap.read()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        frame = frame[:, ::-1]

        im_grad = mygradient(frame, el)
        cv2.imshow("Gradient", numpy.uint8(im_grad))

        cam.send(cv2.cvtColor(im_grad, cv2.COLOR_GRAY2RGB))
        cam.sleep_until_next_frame()

        if cv2.waitKey(1) == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()
