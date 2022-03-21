# from tensorflow.keras.applications.mobilenet_v2 import preprocess_input
# from tensorflow.keras.preprocessing.image import img_to_array
# from tensorflow.keras.models import load_model
# from imutils.video import VideoStream
# import imutils
import cv2,os 
from django.conf import settings
import face_recognition
import numpy as np
from .models import *
# face_detection_videocam = cv2.CascadeClassifier(os.path.join(
# 			settings.BASE_DIR,'opencv_haarcascade_data/haarcascade_frontalface_default.xml'))
# face_detection_webcam = cv2.CascadeClassifier(os.path.join(
# 			settings.BASE_DIR,'opencv_haarcascade_data/haarcascade_frontalface_default.xml'))

# # Load a sample picture and learn how to recognize it.
# obama_image = face_recognition.load_image_file(os.path.join(settings.BASE_DIR,'checkins/known_face/obama.jpg'))
# obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

# # Load a second sample picture and learn how to recognize it.
# biden_image = face_recognition.load_image_file(os.path.join(settings.BASE_DIR,'checkins/known_face/biden.jpg'))
# biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

# # # Load a second sample picture and learn how to recognize it.
# # modi_image = face_recognition.load_image_file(os.path.join(settings.BASE_DIR,'checkins/known_face/modi.jpg'))
# # modi_face_encoding = face_recognition.face_encodings(modi_image)[0]

# # # # Load a second sample picture and learn how to recognize it.
# # divyam_image = face_recognition.load_image_file(os.path.join(settings.BASE_DIR,'checkins/known_face/divyam.jpeg'))
# # divyam_face_encoding = face_recognition.face_encodings(divyam_image)[0]

# # # Create arrays of known face encodings and their names
# known_face_encodings = [
#     # obama_face_encoding,
#     biden_face_encoding,
#     # modi_face_encoding,
#     # divyam_face_encoding,
# ]
# known_face_names = [
#     # "Barack Obama",
#     "Joe Biden",
#     # "Narendra Modi",
#     # "Divyam",
# ]

known_face_encodings = []
known_face_names = []
known_face_id = []

cevent = ''
current = []
checkin = []
for e in Event.objects.all():
	if e.current:
		cevent = e.title
		break
for i in Invites.objects.all():
	if i.event == cevent:
		current.append(i)
		obj = Checkins.objects.get(pk = i.id)
		checkin.append(obj)
for i in current:
	temp = face_recognition.load_image_file(i.img)
	known_face_encodings.append(
		face_recognition.face_encodings(temp)[0]
	)
	known_face_names.append(
		i.name
	)
	known_face_id.append(
		i.id
	)



class VideoCamera(object):
	def __init__(self):
		self.video = cv2.VideoCapture(0)
		self.process_this_frame = True
		

	def __del__(self):
		self.video.release()

	def get_frame(self):
		#success, image = self.video.read()
		
		# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
		# faces_detected = face_detection_videocam.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)
		# for (x, y, w, h) in faces_detected:
		# 	cv2.rectangle(image, pt1=(x, y), pt2=(x + w, y + h), color=(255, 0, 0), thickness=2)
		# frame_flip = cv2.flip(image,1)
		# ret, jpeg = cv2.imencode('.jpg', frame_flip)
		# return jpeg.tobytes()
		
		#DLIB
		face_locations = []
		face_encodings = []
		face_names = []
		# Grab a single frame of video
		ret, frame = self.video.read()
		# Resize frame of video to 1/4 size for faster face recognition processing
		small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
		# Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
		rgb_small_frame = small_frame[:, :, ::-1]
		# Only process every other frame of video to save time
		if self.process_this_frame:
			# Find all the faces and face encodings in the current frame of video
			face_locations = face_recognition.face_locations(rgb_small_frame)
			face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

			face_names = []
			face_ids = []
			for face_encoding in face_encodings:
				# See if the face is a match for the known face(s)
				matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
				name = "Unknown"
				id = None

				# # If a match was found in known_face_encodings, just use the first one.
				# if True in matches:
				#     first_match_index = matches.index(True)
				#     name = known_face_names[first_match_index]

				# Or instead, use the known face with the smallest distance to the new face
				face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
				best_match_index = np.argmin(face_distances)
				if matches[best_match_index]:
					name = known_face_names[best_match_index]
					id = known_face_id[best_match_index]

				face_names.append(name)
				face_ids.append(id)

		self.process_this_frame = not self.process_this_frame
		# Display the results
		for (top, right, bottom, left), name in zip(face_locations, face_names):
			# Scale back up face locations since the frame we detected in was scaled to 1/4 size
			top *= 4
			right *= 4
			bottom *= 4
			left *= 4
			
			if name == "Unknown": 
				color = (0, 0, 255)
			else:
				index = face_names.index(name)
				id = face_ids[index]
				# object = checkin[index]
				object = Checkins.objects.get(pk=id)
				object.status = True
				if object.checkinType == "both":
					object.checkinType = "both"
				elif object.checkinType == "QR":
					object.checkinType = "both"
				else:
					object.checkinType = "FR"
				
				object.save()
				color = (0, 255, 0)

			# Draw a box around the face
			cv2.rectangle(frame, (left, top), (right, bottom), color, 2)
			# Draw a label with a name below the face
			cv2.rectangle(frame, (left, bottom - 35), (right, bottom), color, cv2.FILLED)
			font = cv2.FONT_HERSHEY_DUPLEX
			cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
		success, jpeg = cv2.imencode('.jpg', frame)

		return jpeg.tobytes()