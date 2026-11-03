import cv2
import numpy



def myerode(im, el):
    return cv2.erode(im, el)

def mydilate(im, el):
    return cv2.dilate(im, el)

def mygradient(im, el):
    return cv2.subtract(mydilate(im, el), myerode(im, el))

def myopen(im, el):
    return mydilate(myerode(im, el), el)

def myclose(im, el):
    return myerode(mydilate(im, el), el)

def myconddilat(ref, mask, el):
    return numpy.minimum(ref, mydilate(mask, el))

def myreconinf(ref, mask, el):
    previous = ref
    while not numpy.array_equal(previous, mask):
        previous = mask
        mask = myconddilat(ref, mask, el)

    return mask