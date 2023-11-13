import cv2
import numpy as np
import datetime

def is_car_coming(video):
    # Initialize the video capture object
    video = cv2.VideoCapture(video)  # Use 0 for webcam, or replace with video file path

    # Create the background subtractor object
    fgbg = cv2.createBackgroundSubtractorMOG2(varThreshold=120)

    while True:
        # Read the current frame from the video capture object
        ret, frame = video.read()
        if not ret:
            break

        blurred_frame = cv2.GaussianBlur(frame, (49, 49), 0)


        # Apply the background subtractor to get the foreground mask
        fgmask = fgbg.apply(blurred_frame)

        # Apply a threshold to binarize the mask
        _, thresh = cv2.threshold(fgmask, 240, 255, cv2.THRESH_BINARY)
        # print(f"Original Frame: {frame.shape}")
        # print(f"Mask: {thresh.shape}")

        height, width = frame.shape[:2]
        isolated_frame = np.multiply(thresh.reshape(height, width, 1), frame)
        # print(f"Isolated Frame: {isolated_frame.shape}")


        # Find contours in the thresholded image
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        # Draw bounding boxes around the contours

        for contour in contours:
            # Get the current time
            current_time = datetime.datetime.now()

            # Format the time as a string
            formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
            if cv2.contourArea(contour) < 400:
                # too small, ignore
                continue
            elif cv2.contourArea(contour) < 20000:    
                print(f'A car drove by at {formatted_time}!')
            # Get bounding box coordinates from the contour
            (x, y, w, h) = cv2.boundingRect(contour)
            # Draw the bounding box
            cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)

        # Display the original frame with bounding boxes
        cv2.imshow('Frame', frame)
        # Display the binary image
        cv2.imshow('Foreground', isolated_frame)

        # Break the loop if 'q' is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object and close all windows
    video.release()
    cv2.destroyAllWindows()

is_car_coming('./videos/cars.mov')