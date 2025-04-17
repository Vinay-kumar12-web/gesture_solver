import cv2
import numpy as np
import math
import time
import pyttsx3  # Importing pyttsx3 for text-to-speech

# Initialize video capture
cap = cv2.VideoCapture(0)

# Initialize variables
expression = ""
result = ""
last_input_time = 0  # Track last gesture time
error_spoken = False  # Flag to prevent repeating error speech

# Initialize pyttsx3 engine for voice feedback
engine = pyttsx3.init()

# Function to speak text
def speak(text):
    engine.say(text)
    engine.runAndWait()

while True:
    ret, frame = cap.read()
    frame = cv2.flip(frame, 1)
    roi = frame[100:400, 100:400]

    # Draw rectangle around hand detection area
    cv2.rectangle(frame, (100, 100), (400, 400), (0, 255, 0), 2)

    # Convert the region of interest (ROI) to HSV
    hsv = cv2.cvtColor(roi, cv2.COLOR_BGR2HSV)

    # Define skin color range in HSV
    lower_skin = np.array([0, 20, 70], dtype=np.uint8)
    upper_skin = np.array([20, 255, 255], dtype=np.uint8)

    # Mask the skin color
    mask = cv2.inRange(hsv, lower_skin, upper_skin)

    # Apply Gaussian Blur
    mask = cv2.GaussianBlur(mask, (5, 5), 100)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    count_defects = 0
    current_time = time.time()

    try:
        # Find the largest contour (hand)
        cnt = max(contours, key=lambda x: cv2.contourArea(x))
        hull = cv2.convexHull(cnt, returnPoints=False)
        defects = cv2.convexityDefects(cnt, hull)

        if defects is not None:
            for i in range(defects.shape[0]):
                s, e, f, d = defects[i, 0]
                start = tuple(cnt[s][0])
                end = tuple(cnt[e][0])
                far = tuple(cnt[f][0])

                # Calculate distances
                a = math.dist(start, end)
                b = math.dist(start, far)
                c = math.dist(end, far)
                angle = math.acos((b**2 + c**2 - a**2) / (2 * b * c))

                if angle <= math.pi / 2:
                    count_defects += 1
                    cv2.circle(roi, far, 5, [0, 0, 255], -1)

        finger_count = count_defects + 1

        # Only process the input if 1.5 seconds have passed since last input
        if current_time - last_input_time > 1.5:
            # Mapping gestures to math operations and digits
            if finger_count == 1:
                # Solve expression when 1 finger detected
                try:
                    result = str(eval(expression))
                    speak(f"The answer is {result}")  # Speak the result
                    error_spoken = False  # Reset the error flag after successful calculation
                except:
                    result = "Error"
                    if not error_spoken:  # Speak the error only once
                        speak("There was an error in the calculation.")
                        error_spoken = True  # Set the flag to prevent repeating the error message
                expression = ""  # Reset after solving
                last_input_time = current_time
            elif finger_count == 2:
                expression += "2"
                last_input_time = current_time
            elif finger_count == 3:
                expression += "3"
                last_input_time = current_time
            elif finger_count == 4:
                expression += "+"
                last_input_time = current_time
            elif finger_count == 5:
                expression += "-"
                last_input_time = current_time

    except:
        finger_count = 0

    # Display the expression and result on the screen
    cv2.putText(frame, f"Expression: {expression}", (10, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    cv2.putText(frame, f"Result: {result}", (10, 100),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow("Math Solver", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
