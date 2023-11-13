import cv2
import numpy as np
import time
# Start capturing video from the webcam
cap = cv2.VideoCapture(0)



# Function to draw a rectangle with rounded corners
def draw_rounded_rect(frame, pt1, pt2, color, thickness, corner_radius):
    x1, y1 = pt1
    x2, y2 = pt2

    # Draw the four rectangles
    cv2.rectangle(frame, (x1 + corner_radius, y1), (x2 - corner_radius, y2), color, -1)
    cv2.rectangle(frame, (x1, y1 + corner_radius), (x2, y2 - corner_radius), color, -1)

    # Draw the four circles
    cv2.circle(frame, (x1 + corner_radius, y1 + corner_radius), corner_radius, color, -1)
    cv2.circle(frame, (x2 - corner_radius, y1 + corner_radius), corner_radius, color, -1)
    cv2.circle(frame, (x1 + corner_radius, y2 - corner_radius), corner_radius, color, -1)
    cv2.circle(frame, (x2 - corner_radius, y2 - corner_radius), corner_radius, color, -1)


# Define the range of the color you want to track
# For example, for a bright green object:
# Define the range of orange color in HSV
colorLower = np.array([10, 100, 100])  # Lower boundary of orange color
colorUpper = np.array([25, 255, 255])  # Upper boundary of orange color

selected_answer = None
start_time = None
clear_time = None  # Timer to clear the selection text
display_final_score = False

selection_threshold = 1  # 2 seconds
clear_threshold = 3  # 3 seconds to clear the selection text

selection_text = ""  # Variable to store the selection text

buffer_start_time = None
buffer_duration = 2  # 2 seconds buffer
user_score_compliment = ''


quiz_questions = [
    {
        "question": "Is it pronounced num-pie or num-pee?",
        "answers": ["num-pie", "num-pee"],
        "correct_answer": 0
    },
    {
        "question": "What is Pete's favorite berry?",
        "answers": ["strawberries", "blueberries", "raspberries"],
        "correct_answer": 1
    },
    {
        "question": "Which planet is known as the Red Planet?",
        "answers": ["Mars", "Venus", "Jupiter",],
        "correct_answer": 2
    }
]

current_question_index = 0
answer_submitted = False

user_score = 0

expansion = 20  # Pixels to expand the detection area
answer_boxes = [
    (200 - expansion, 200 - expansion, 300 + expansion, 250 + expansion),
    (200 - expansion, 400 - expansion, 300 + expansion, 450 + expansion)
]
text_color = (255, 255, 255)  # Default text color (white)

while True:
    # Read a frame and convert it to the HSV color space
    ret, frame = cap.read()
    if not ret:
        break
  # Create a dark, transparent overlay
    overlay = np.zeros(frame.shape, dtype=np.uint8)  # Create a black overlay
    overlay_color = (50, 50, 50)  # Dark gray color
    alpha = 0.55  # Transparency factor (between 0 and 1)

    # Fill the overlay with the dark color
    overlay[:] = overlay_color

    # Blend the overlay with the frame
    cv2.addWeighted(overlay, alpha, frame, 1 - alpha, 0, frame)

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    # Create a mask for the color
    mask = cv2.inRange(hsv, colorLower, colorUpper)

    # Find contours in the mask
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    
    object_present = False  # Flag to check if the object is over any answer box

 # Inside your main loop

    for contour in contours:
        largest_contour = max(contours, key=cv2.contourArea)
        M = cv2.moments(largest_contour)
        if M["m00"] != 0:
            centerX = int(M["m10"] / M["m00"])
            centerY = int(M["m01"] / M["m00"])
            cv2.circle(frame, (centerX, centerY), 20, (0, 0, 255), -1)

            for index, (x1, y1, x2, y2) in enumerate(answer_boxes):
                if x1 < centerX < x2 and y1 < centerY < y2:
                    print(f"Object over answer {index}")  # Debug print
                    if selected_answer != index:
                        selected_answer = index
                        start_time = time.time()
                    break
                else:
                    if selected_answer == index:
                        selected_answer = None
                        start_time = None

            if start_time and (time.time() - start_time > selection_threshold):
                print(f"selected answer: {selected_answer}")
                if selected_answer is not None:
                    # Check if the selected answer is correct
                    if selected_answer == quiz_questions[current_question_index]["correct_answer"]:
                        selection_text = "Correct!"
                        text_color = (0, 255, 0)  # Green for correct
                        user_score += 1  # Increment score

                    else:
                        selection_text = "Wrong!"
                        text_color = (0, 0, 255)  # Red for wrong

                    # Move to the next question after a brief pause
                    clear_time = time.time()  # Start the timer to clear the text
                    current_question_index += 1
                    selected_answer = None
                    start_time = None
                    if current_question_index >= len(quiz_questions):
                        current_question_index = 0  # Reset to first question or end quiz
                        final_score_display_time = time.time()  # Time when the final score is first displayed
                        display_final_score = True

                break


        break
    if clear_time and (time.time() - clear_time > clear_threshold):
        selection_text = ""  # Clear the selection text
        clear_time = None


    # Display the question and answers
    # Get the current question and answers
    current_question = quiz_questions[current_question_index]
    question_text = current_question["question"]
    answers = current_question["answers"]    
    question_size = cv2.getTextSize(question_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
    question_x = 40
    question_y = 80
    question_padding = 10
    question_corner_radius = 10
    question_bg_top_left = (question_x - question_padding, question_y - question_size[1] - question_padding)
    question_bg_bottom_right = (question_x + question_size[0] + question_padding, question_y + question_padding)

    draw_rounded_rect(frame, question_bg_top_left, question_bg_bottom_right, (0, 0, 0), -1, question_corner_radius)
    cv2.putText(frame, question_text, (question_x, question_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
    # Update answer boxes based on the number of answers
    answer_boxes = [(200 - expansion, 200 * (i + 1) - expansion, 300 + expansion, 200 * (i + 1) + 50 + expansion) for i in range(len(answers))]

    answer_padding = 10
    answer_corner_radius = 10
    for index, answer in enumerate(answers):
        answer_text = answer
        answer_size = cv2.getTextSize(answer_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        answer_x = 200
        answer_y = 200 * (index + 1)
        answer_bg_top_left = (answer_x - answer_padding, answer_y - answer_size[1] - answer_padding)
        answer_bg_bottom_right = (answer_x + answer_size[0] + answer_padding, answer_y + answer_padding)

        draw_rounded_rect(frame, answer_bg_top_left, answer_bg_bottom_right, (0, 0, 0), -1, answer_corner_radius)
        cv2.putText(frame, answer_text, (answer_x, answer_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
    
    # Display the selection text if it's not empty
    if selection_text:
        # Calculate the size of the text box
        text_size = cv2.getTextSize(selection_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
        text_x = 300
        text_y = 500
        padding = 10
        corner_radius = 10

        # Calculate the position for the rounded rectangle
        bg_top_left = (text_x - padding, text_y - text_size[1] - padding)
        bg_bottom_right = (text_x + text_size[0] + padding, text_y + padding)

        # Draw the rounded rectangle
        draw_rounded_rect(frame, bg_top_left, bg_bottom_right, (0, 0, 0), -1, corner_radius)
        cv2.putText(frame, selection_text, (300, 500), cv2.FONT_HERSHEY_SIMPLEX, 1, text_color, 2)

        if display_final_score:
            if time.time() - final_score_display_time < 5:  # Display score for 5 seconds
                frame[:] = (0, 0, 0)  # Clear the screen
                if(user_score == 0):
                    score_text = f"Your Score: {user_score} / 3. no sweat, you're just keeping it suspenseful for the comeback!"
                elif(user_score == 1):
                    score_text = f"Your Score: {user_score} / 3. you're just warming up, next round's yours!"
                elif(user_score == 2):
                    score_text = f"Your Score: {user_score} / 3. you're lowkey a brainiac, keep crushing it!"
                else:
                    score_text = f"Your Score: {user_score} / 3. you're the g.o.a.t, full send on that genius energy!"
                # Code to center and display `score_text` on the screen
                text_size = cv2.getTextSize(score_text, cv2.FONT_HERSHEY_SIMPLEX, 1, 2)[0]
                text_x = (frame.shape[1] - text_size[0]) // 2
                text_y = (frame.shape[0] + text_size[1]) // 2
                cv2.putText(frame, score_text, (text_x, text_y), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)

            else:
                display_final_score = False  # Stop displaying the score



    # Display the frame
    cv2.imshow('Video Feed', frame)

    # Break the loop if 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# Release the video capture object and close all windows
cap.release()
cv2.destroyAllWindows()
