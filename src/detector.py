import cv2
import numpy as np
import logging
import time

# Configure logging to output to a file and console
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s',
    handlers=[
        logging.FileHandler("qr_detection.log"),
        logging.StreamHandler()
    ]
)

def open_camera(camera_index=1, attempts=5, delay=5):
    """Attempt to open the camera repeatedly."""
    cap = None
    for i in range(attempts):
        cap = cv2.VideoCapture(camera_index)
        if cap.isOpened():
            logging.info(f"Camera opened successfully on index {camera_index}.")
            return cap
        else:
            logging.warning(f"Attempt {i+1}/{attempts}: Unable to open camera on index {camera_index}. Retrying in {delay} seconds...")
            time.sleep(delay)
    logging.critical("Failed to open the camera after multiple attempts.")
    return None

def main():
    # Initialize the camera (adjust the index or device name as needed)
    cap = open_camera(camera_index=0)
    if cap is None:
        return  # Exit if the camera cannot be opened

    # Initialize the QR Code Detector
    qr_detector = cv2.QRCodeDetector()

    logging.info("Starting main loop. Press 'q' in the display window to quit.")

    while True:
        try:
            ret, frame = cap.read()
            if not ret or frame is None:
                logging.warning("Frame read failed. Attempting to reinitialize the camera.")
                cap.release()
                time.sleep(2)
                cap = open_camera(camera_index=1)
                if cap is None:
                    logging.critical("Exiting due to camera failure.")
                    break
                continue

            # Try detecting and decoding the QR code
            try:
                data, points, _ = qr_detector.detectAndDecode(frame)
            except cv2.error as e:
                logging.error("QR Code detection error: %s", e)
                points = None

            # Process detected QR code if valid points exist
            if points is not None and points.size > 0:
                # Reshape points to a (4,2) array
                points = points.reshape(-1, 2)
                pts_int = points.astype(int)
                cv2.polylines(frame, [pts_int], isClosed=True, color=(0, 255, 0), thickness=3)

                # Calculate the orientation using the first edge (from point 0 to point 1)
                pt0 = points[0]
                pt1 = points[1]
                dx = pt1[0] - pt0[0]
                dy = pt1[1] - pt0[1]
                angle_rad = np.arctan2(dy, dx)
                angle_deg = np.degrees(angle_rad)
                # angle_deg will be in the range [-180, 180]
                angle_text = f"Angle: {angle_deg:.6f} deg"
                cv2.putText(frame, angle_text, (pts_int[0][0], pts_int[0][1] - 10),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)
                logging.info(angle_text)

            # Display the processed frame
            cv2.imshow("GP AI - Rotation Detection @gp4isi", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                logging.info("Exit key pressed. Exiting...")
                break

        except Exception as e:
            logging.exception("Unexpected error in main loop: %s", e)
            # Delay briefly and continue the loop
            time.sleep(1)
            continue

    # Release resources on exit
    cap.release()
    cv2.destroyAllWindows()
    logging.info("Camera released and windows closed.")

if __name__ == '__main__':
    main()
