import cv2
from iscarcoming import static_object_detection
from dynamicobjectdetection import dynamic_object_detection
def check_if_static(video):
    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        print("Error: Could not open video.")
        exit()

    # Read the first frame
    ret, prev_frame = cap.read()
    if not ret:
        print("Cannot read video file")
        exit()

    prev_frame_gray = cv2.cvtColor(prev_frame, cv2.COLOR_BGR2GRAY)
    frame_count = 0
    dynamic_score = 0
    dynamic_threshold = 1

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        
        current_frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate absolute difference between current frame and the previous frame
        frame_diff = cv2.absdiff(current_frame_gray, prev_frame_gray)
        
        # Threshold to get the significant differences
        thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)[1]
        
        # Calculate the percentage of difference
        diff_percent = (cv2.countNonZero(thresh) / (frame.size)) * 100
        
        # Accumulate a score or decide on-the-fly
        dynamic_score += diff_percent
        frame_count += 1
        
        # Update the previous frame
        prev_frame_gray = current_frame_gray

        # Break the loop if necessary
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    

    # Determine if the background is dynamic or static
    average_dynamic_score = dynamic_score / frame_count
    if average_dynamic_score > dynamic_threshold:  # dynamic_threshold is a predefined limit
        dynamic_object_detection(video)
    else:
        static_object_detection(video)
