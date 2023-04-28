import os

import cv2
import numpy

import serial
import time

import countDown

Name_of_Person = 'David' # must match file name of data folder containing POI

arduino = serial.Serial('/dev/ttyACM0', 9600)
time.sleep(2) # this is a delay we set so that the connection can become
# more stable

def read_images(path, image_size):
    names = []
    training_images, training_labels = [], []
    label = 0
    for dirname, subdirnames, filenames in os.walk(path):
        for subdirname in subdirnames:
            names.append(subdirname)
            subject_path = os.path.join(dirname, subdirname)
            for filename in os.listdir(subject_path):
                img = cv2.imread(os.path.join(subject_path, filename),
                                 cv2.IMREAD_GRAYSCALE)
                if img is None:
                    # The file cannot be loaded as an image.
                    # Skip it.
                    continue
                img = cv2.resize(img, image_size)
                training_images.append(img)
                training_labels.append(label)
            label += 1
    training_images = numpy.asarray(training_images, numpy.uint8)
    training_labels = numpy.asarray(training_labels, numpy.int32)
    return names, training_images, training_labels

path_test = "/home/pi/Desktop/OpenDoorWithFace"

# fixed path issue: turns out you need the path to lead to the parent dir of the img dir
path_to_training_images = path_test




training_image_size = (200, 200) # the size is bc the data img size is 200x200 so we
# need to match that size. otherwise the math doesnt work
names, training_images, training_labels = read_images(path_to_training_images, training_image_size)

# print(training_images)


# error was fixed in the following line by installing "opencv-contrib-python"
# not all files needed were here so that line adds them
model = cv2.face.EigenFaceRecognizer_create()
# HOW DOES EigenFaceRecognizer work?...

# look into facerecognizersave so you can save the model into an XML here is the link: https://docs.opencv.org/2.4/modules/contrib/doc/facerec/facerec_api.html#createeigenfacerecognizer
# png is better than jpg so try to make it that next time

model.train(training_images, training_labels)

face_cascade = cv2.CascadeClassifier(
    'haarcascade_frontalface_default.xml')

counter = 0 # test code for a counting label system
totalcount = 0
sum = 0 # this is used to calculate the avg confidence score

camera = cv2.VideoCapture(0)
while (cv2.waitKey(1) == -1):
    success, frame = camera.read()
    if success:
        faces = face_cascade.detectMultiScale(frame, 1.3, 5)
        for (x, y, w, h) in faces:
            cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            roi_gray = gray[x:x+w, y:y+h]
            if roi_gray.size == 0:
                # The ROI is empty. Maybe the face is at the image edge.
                # Skip it.
                continue
            roi_gray = cv2.resize(roi_gray, training_image_size)
            label, confidence = model.predict(roi_gray)

            totalcount = totalcount + 1
            sum = sum + confidence

            average_confidence = sum / totalcount
            #print(average_confidence)
            print(counter)
            # confidence is how sure it is for the predicted label.
            if confidence > 8200: # at night make 5200
                continue

            if names[label] == Name_of_Person:
                counter = counter + 1
                if counter == 10:
                    
                    # UNLOCK SEQUENCE
                    arduino.write(b'1')
                    print("Unlocking")
                    countDown.countdown(10)                     
                    counter = 0 # resets counter so that the door can be opened again

                    #print("you have 30 seconds to get in before autolock")
                    #countDown.countdown(5) # 5 for now since i just want to dev
                    
                    # LOCK SEQUENCE
                    #arduino.write(b'0')
                    #print("Locking")
                    #countDown.countdown(10)                    
                    
                    

            text = '%s, confidence=%.2f' % (names[label], confidence)
            cv2.putText(frame, text, (x, y - 20),
            cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
        #cv2.imshow('Face Recognition', frame) # this needs to be off during automated use
                    # of the product (during dev you can turn on)