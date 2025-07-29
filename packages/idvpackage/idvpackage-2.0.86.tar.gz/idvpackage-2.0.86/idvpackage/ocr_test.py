import pandas as pd
from google.oauth2.service_account import Credentials
from google.cloud import vision_v1
import json
import pycountry
from googletrans import Translator
from PIL import Image, ImageEnhance, ImageOps, ImageFilter
import base64
import io
import numpy as np
import cv2
from datetime import datetime, timedelta
import tempfile
from rapidfuzz import fuzz
import face_recognition
import re
import os

from idvpackage.constants import BRIGHTNESS_THRESHOLD, BLUR_THRESHOLD
from io import BytesIO
import time
import logging
# import anthropic
import openai
from idvpackage.blur_detection import is_image_blur

# from idvpackage.common import (
#     # load_and_process_image_deepface,
#     load_and_process_image_deepface_all_orientations
# )


logging.basicConfig(level=logging.INFO)

google_client_dict = {}


class IdentityVerification:

    def __init__(self, credentials_string, api_key=None, genai_key=None):
        """
        This is the initialization function of a class that imports a spoof model and loads an OCR
        reader.
        """
        st = time.time()
        credentials_dict = json.loads(credentials_string)
        credentials = Credentials.from_service_account_info(credentials_dict)

        self.client = google_client_dict.get(credentials)
        if not self.client:
            self.client = vision_v1.ImageAnnotatorClient(credentials=credentials)
            google_client_dict[credentials] = self.client

        self.api_key = api_key

        # self.genai_client = anthropic.Anthropic(
        #         api_key=genai_key,
        #     )

        openai.api_key = genai_key

        self.translator = Translator()
        self.iso_nationalities = [country.alpha_3 for country in pycountry.countries]
        print(f"\nInitialization time inside IDV Package: {time.time() - st}")

    def preprocess_image(self, image, sharpness=1.0, contrast=2.0, radius=2, percent=150, threshold=3):
        """Preprocess the image by sharpening and enhancing contrast."""

        # Apply sharpening
        enhancer = ImageEnhance.Sharpness(image)
        image = enhancer.enhance(sharpness)  # Sharpen the image (increase sharpness)

        # Enhance the contrast
        enhancer = ImageEnhance.Contrast(image)
        image = enhancer.enhance(contrast)  # Increase contrast

        image = image.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold))

        return image

    def image_conversion(self, image):
        """
        This function decodes a base64 string data and returns an image object.
        If the image is in RGBA mode, it is converted to RGB mode.
        :return: an Image object that has been created from a base64 encoded string.
        """
        # Decode base64 String Data
        # img = Image.open(io.BytesIO(base64.decodebytes(bytes(image, "utf-8"))))

        img_data = io.BytesIO(base64.decodebytes(bytes(image, "utf-8")))
        with Image.open(img_data) as img:
            if img.mode == 'RGBA':
                # Create a blank background image
                background = Image.new('RGB', img.size, (255, 255, 255))
                # Paste the image on the background.
                background.paste(img, mask=img.split()[3])  # 3 is the alpha channel
                img = background
            else:
                img = img.copy()
            return img

    def rgb2yuv(self, img):
        """
        Convert an RGB image to YUV format.
        """
        try:
            img = np.array(img)
            return cv2.cvtColor(img, cv2.COLOR_RGB2YUV)
        except Exception as e:
            raise Exception(f"Error: {e}")

    def find_bright_areas(self, image, brightness_threshold):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        thresh_image = cv2.threshold(gray_image, brightness_threshold, 255, cv2.THRESH_BINARY)[1]
        contours, hierarchy = cv2.findContours(thresh_image, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        bright_areas = []

        for contour in contours:
            bounding_box = cv2.boundingRect(contour)

            area = bounding_box[2] * bounding_box[3]

            if area > 800:
                bright_areas.append(bounding_box)

        return len(bright_areas)

    def is_blurry(self, image):
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        laplacian_variance = cv2.Laplacian(gray_image, cv2.CV_64F).var()

        return laplacian_variance

    def identify_input_type(self, data):
        if isinstance(data, bytes):
            return "video_bytes"
        else:
            pass

        try:
            decoded_data = base64.b64decode(data)

            if decoded_data:
                return "base_64"
        except Exception:
            pass

        return "unknown"

    def sharpen_image(self, image):
        kernel = np.array([[-1, -1, -1],
                           [-1, 9, -1],
                           [-1, -1, -1]])
        return cv2.filter2D(image, -1, kernel)

    def adjust_contrast(self, image, factor):
        pil_image = Image.fromarray(image)
        enhancer = ImageEnhance.Contrast(pil_image)
        enhanced_image = enhancer.enhance(factor)
        return np.array(enhanced_image)

    def adjust_brightness(self, image, factor):
        pil_image = Image.fromarray(image)
        enhancer = ImageEnhance.Brightness(pil_image)
        enhanced_image = enhancer.enhance(factor)
        return np.array(enhanced_image)

    def enhance_quality(self, image):
        sharpened_image = self.sharpen_image(image)
        enhanced_image = self.adjust_brightness(sharpened_image, 1.2)
        enhanced_contrast = self.adjust_contrast(enhanced_image, 1.2)
        # grayscale_image = cv2.cvtColor(enhanced_contrast, cv2.COLOR_BGR2GRAY)

        return enhanced_contrast

    def check_document_quality(self, data):
        video_quality = {"error": ""}
        temp_video_file = tempfile.NamedTemporaryFile(delete=False)
        temp_video_file_path = temp_video_file.name

        try:
            # Write video bytes to the temporary file and flush
            temp_video_file.write(data)
            temp_video_file.flush()
            temp_video_file.close()  # Close the file to ensure it can be accessed by other processes

            video_capture = cv2.VideoCapture(temp_video_file.name)

            if video_capture.isOpened():
                frame_count = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))

                for _ in range(frame_count):
                    ret, frame = video_capture.read()
                    #                         if ret:
                    # frame_count_vid+=1
                    # if frame_count_vid % 10 == 0:
                    _, buffer = cv2.imencode(".jpg", frame)
                    image_data = buffer.tobytes()

                    image = vision_v1.Image(content=image_data)

                    response = self.client.face_detection(image=image)
                    if len(response.face_annotations) >= 1:
                        break

            video_capture.set(cv2.CAP_PROP_POS_FRAMES, 0)

            selfie_result = self.extract_selfie_from_video(video_capture)
            if isinstance(selfie_result, dict):
                video_quality["error"] = selfie_result["error"]
            else:
                (
                    selfie_blurry_result,
                    selfie_bright_result,
                ) = self.get_blurred_and_glared_for_doc(selfie_result)
                if (
                        selfie_blurry_result == "consider"
                        or selfie_bright_result == "consider"
                ):
                    video_quality["error"] = "face_not_clear_in_video"
                else:
                    video_quality["selfie"] = selfie_result
                    video_quality["shape"] = selfie_result.shape

            video_capture.release()  # Release the video capture

        # except Exception as e:
        #     video_quality["error"] = "bad_video"

        finally:
            # Ensure the temporary file is deleted
            if os.path.exists(temp_video_file_path):
                os.remove(temp_video_file_path)
                # print(f"Temporary file {temp_video_file_path} has been deleted.")

        return video_quality

    def extract_selfie_from_video(self, video_capture):
        """Extract the best quality selfie from video with speed optimizations for frontal faces."""
        video_dict = {'error': ''}

        try:
            total_frames = int(video_capture.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames <= 0:
                video_dict['error'] = 'invalid_video_frame_count'
                return video_dict

            # Check only 6 frames - 2 at start, 2 in the middle, 2 at the end
            frame_positions = [
                int(total_frames * 0.05),
                int(total_frames * 0.15),
                int(total_frames * 0.45),
                int(total_frames * 0.55),
                int(total_frames * 0.85),
                int(total_frames * 0.95)
            ]

            best_face = None
            best_score = -1
            best_frame = None
            best_frame_position = None
            frame_results = []

            print(f"Analyzing video with {total_frames} frames")
            print(f"Checking {len(frame_positions)} strategic frames")

            for target_frame in frame_positions:
                if target_frame >= total_frames:
                    target_frame = total_frames - 1
                if target_frame < 0:
                    target_frame = 0

                video_capture.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
                ret, frame = video_capture.read()
                if not ret or frame is None or frame.size == 0:
                    continue

                try:
                    scale = 0.7
                    small_frame = cv2.resize(frame, (0, 0), fx=scale, fy=scale)

                    encode_params = [cv2.IMWRITE_JPEG_QUALITY, 90]
                    _, buffer = cv2.imencode(".jpg", small_frame, encode_params)

                    image = vision_v1.Image(content=buffer.tobytes())
                    response = self.client.face_detection(image=image, max_results=2)
                    faces = response.face_annotations

                    if not faces:
                        continue

                    frame_best_face = None
                    frame_best_score = -1

                    for face in faces:
                        vertices = [(int(vertex.x / scale), int(vertex.y / scale))
                                    for vertex in face.bounding_poly.vertices]

                        left = min(v[0] for v in vertices)
                        upper = min(v[1] for v in vertices)
                        right = max(v[0] for v in vertices)
                        lower = max(v[1] for v in vertices)

                        # Validate face coordinates
                        if not (0 <= left < right <= frame.shape[1] and 0 <= upper < lower <= frame.shape[0]):
                            continue

                        # Calculate face metrics
                        face_width = right - left
                        face_height = lower - upper
                        face_area = (face_width * face_height) / (frame.shape[0] * frame.shape[1])

                        # Reject small faces
                        if face_area < 0.05:
                            continue

                        # Calculate how centered the face is
                        face_center_x = (left + right) / 2
                        face_center_y = (upper + lower) / 2
                        frame_center_x = frame.shape[1] / 2
                        frame_center_y = frame.shape[0] / 2

                        center_dist_x = abs(face_center_x - frame_center_x) / (frame.shape[1] / 2)
                        center_dist_y = abs(face_center_y - frame_center_y) / (frame.shape[0] / 2)
                        center_score = 1.0 - (center_dist_x + center_dist_y) / 2

                        # For frontal faces, left and right eye/ear should be roughly symmetric
                        if len(face.landmarks) > 0:
                            # Head rotation detection
                            roll, pan, tilt = 0, 0, 0
                            if hasattr(face, 'roll_angle'):
                                roll = abs(face.roll_angle)
                            if hasattr(face, 'pan_angle'):
                                pan = abs(face.pan_angle)
                            if hasattr(face, 'tilt_angle'):
                                tilt = abs(face.tilt_angle)

                            head_angle_penalty = (roll + pan + tilt) / 180.0

                            # Symmetry detection from face bounding box
                            left_half = face_center_x - left
                            right_half = right - face_center_x
                            width_ratio = min(left_half, right_half) / max(left_half, right_half)

                            # Frontal-face score: higher for more frontal faces
                            # Perfect frontal face would be 1.0
                            frontal_score = width_ratio * (1.0 - head_angle_penalty)
                        else:
                            # No landmarks, estimate from bounding box
                            left_half = face_center_x - left
                            right_half = right - face_center_x
                            frontal_score = min(left_half, right_half) / max(left_half, right_half)

                        # Combined score weights different factors
                        # More weight for frontal-ness and face confidence
                        score = (
                                face.detection_confidence * 0.3 +
                                face_area * 0.2 +
                                center_score * 0.2 +
                                frontal_score * 0.3
                        )

                        # Heavy bonus for very frontal faces (nearly symmetric)
                        if frontal_score > 0.8:
                            score *= 1.5

                        # Extra bonus for centered faces
                        if center_score > 0.8:
                            score *= 1.2

                        if score > frame_best_score:
                            # Add margins for the face
                            margin_x = int(face_width * 0.2)
                            margin_y_top = int(face_height * 0.3)
                            margin_y_bottom = int(face_height * 0.1)

                            left_with_margin = max(0, left - margin_x)
                            upper_with_margin = max(0, upper - margin_y_top)
                            right_with_margin = min(frame.shape[1], right + margin_x)
                            lower_with_margin = min(frame.shape[0], lower + margin_y_bottom)

                            # Store the best face info
                            frame_best_score = score
                            frame_best_face = {
                                'face': face,
                                'left': left_with_margin,
                                'upper': upper_with_margin,
                                'right': right_with_margin,
                                'lower': lower_with_margin,
                                'frontal_score': frontal_score,
                                'center_score': center_score,
                                'confidence': face.detection_confidence,
                                'frame': target_frame
                            }

                    if frame_best_face is not None:
                        frame_results.append({
                            'frame': target_frame,
                            'face': frame_best_face,
                            'score': frame_best_score,
                            'frame_data': frame.copy()
                        })

                        if frame_best_score > best_score:
                            best_score = frame_best_score
                            best_face = frame_best_face
                            best_frame = frame.copy()
                            best_frame_position = target_frame

                except Exception as e:
                    continue

            # Process results
            if len(frame_results) > 0:
                # Sort faces by score
                frame_results.sort(key=lambda x: x['score'], reverse=True)

                for i, result in enumerate(frame_results[:min(3, len(frame_results))]):
                    face_info = result['face']
                    print(f"Rank {i + 1}: Frame {face_info['frame']}, "
                          f"Score: {result['score']:.2f}, "
                          f"Frontal: {face_info['frontal_score']:.2f}, "
                          f"Center: {face_info['center_score']:.2f}")

                # Use the best frame
                best_result = frame_results[0]
                best_face = best_result['face']
                best_frame = best_result['frame_data']

                print(f"Selected frame {best_face['frame']} as best selfie")

            if best_face and best_frame is not None:
                try:
                    left = best_face['left']
                    upper = best_face['upper']
                    right = best_face['right']
                    lower = best_face['lower']

                    # Convert to RGB and crop
                    rgb_frame = cv2.cvtColor(best_frame, cv2.COLOR_BGR2RGB)
                    cropped_face = rgb_frame[upper:lower, left:right]

                    # Validate cropped face
                    if cropped_face is None or cropped_face.size == 0:
                        video_dict['error'] = 'invalid_cropped_face'
                        return video_dict

                    print(f"Face shape: {cropped_face.shape}")
                    return cropped_face

                except Exception as e:
                    video_dict['error'] = 'error_processing_detected_face'
                    return video_dict
            else:
                video_dict['error'] = 'no_suitable_face_detected_in_video'
                return video_dict

        except Exception as e:
            video_dict['error'] = 'video_processing_error'
            return video_dict

    def is_colored(self, base64_image):
        img = self.image_conversion(base64_image)
        img = np.array(img)

        return len(img.shape) == 3 and img.shape[2] >= 3

    def get_blurred_and_glared_for_doc(self, image, brightness_threshold=BRIGHTNESS_THRESHOLD,
                                       blur_threshold=BLUR_THRESHOLD):
        blurred = 'clear'
        glare = 'clear'

        blurry1 = self.is_blurry(image)
        if blurry1 < blur_threshold:
            blurred = 'consider'

        brightness1 = np.average(image[..., 0])
        if brightness1 > brightness_threshold:
            glare = 'consider'

        return blurred, glare

    def standardize_date(self, input_date):
        input_formats = [
            "%Y/%m/%d", "%m/%d/%Y", "%m-%d-%Y",
            "%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y",
            "%Y%m%d", "%m%d%Y", "%d%m%Y",
            "%Y.%m.%d", "%d.%m.%Y", "%m.%d.%Y",
            "%Y %m %d", "%d %m %Y", "%m %d %Y",
        ]

        for format in input_formats:
            try:
                parsed_date = datetime.strptime(input_date, format)
                standardized_date = parsed_date.strftime("%d/%m/%Y")
                return standardized_date
            except ValueError:
                pass

        return None

    def compare_dates(self, date_str1, date_str2):
        date_format = "%d/%m/%Y"

        date1 = datetime.strptime(date_str1, date_format)
        date2 = datetime.strptime(date_str2, date_format)

        if date1 == date2:
            return True
        else:
            return False

    def check_nationality_in_iso_list(self, nationality):
        try:
            if len(nationality) > 3:
                try:
                    country = pycountry.countries.lookup(nationality)
                    nationality = country.alpha_3
                except:
                    return 'consider'

            ## Handling case for OMN as it comes as MN, due to O being considered as 0
            if nationality.upper() == 'MN':
                nationality = 'OMN'

            if nationality.upper() in self.iso_nationalities:
                return 'clear'
            else:
                return 'consider'

        except:
            return 'consider'

    def get_face_orientation(self, face_landmarks):
        left_eye = np.array(face_landmarks['left_eye']).mean(axis=0)
        right_eye = np.array(face_landmarks['right_eye']).mean(axis=0)

        eye_slope = (right_eye[1] - left_eye[1]) / (right_eye[0] - left_eye[0])
        angle = np.degrees(np.arctan(eye_slope))

        return angle

    def rotate_image(self, img):
        from skimage.transform import radon

        img_array = np.array(img)

        if len(img_array.shape) == 2:
            gray = img_array
        else:
            gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)

        h, w = gray.shape
        if w > 640:
            gray = cv2.resize(gray, (640, int((h / w) * 640)))
        gray = gray - np.mean(gray)
        sinogram = radon(gray)
        r = np.array([np.sqrt(np.mean(np.abs(line) ** 2)) for line in sinogram.transpose()])
        rotation = np.argmax(r)
        angle = round(abs(90 - rotation) + 0.5)

        if abs(angle) > 5:
            rotated_img = img.rotate(angle, expand=True)
            return rotated_img

        return img

    def load_and_process_image_fr(self, base64_image, arr=False):
        try:
            if not arr:
                img = self.image_conversion(base64_image)
                img = np.array(img)
                image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            else:
                if base64_image.dtype != np.uint8:
                    base64_image = base64_image.astype(np.uint8)

                image = cv2.cvtColor(base64_image, cv2.COLOR_BGR2RGB)

            # base64_image = base64_image.split(',')[-1]
            # image_data = base64.b64decode(base64_image)
            # image_file = io.BytesIO(image_data)

            # image = face_recognition.load_image_file(image_file)

            face_locations = []
            face_locations = face_recognition.face_locations(image)

            if not face_locations:
                return [], []

            face_encodings = []
            face_encodings = face_recognition.face_encodings(image, face_locations)

            return face_locations, face_encodings
        except:
            return [], []

    def calculate_similarity(self, face_encoding1, face_encoding2):
        similarity_score = 1 - face_recognition.face_distance([face_encoding1], face_encoding2)[0]
        return round(similarity_score + 0.25, 2)

    def extract_face_and_compute_similarity(self, selfie, front_face_locations, front_face_encodings):
        from idvpackage.common import load_and_process_image_deepface
        try:
            if selfie is None:
                print("Error: Selfie image is None")
                return 0

            # Ensure the input array is contiguous and in the correct format
            if not selfie.flags['C_CONTIGUOUS']:
                selfie = np.ascontiguousarray(selfie)

            # Convert array to uint8 if needed
            if selfie.dtype != np.uint8:
                if selfie.max() > 255:
                    selfie = (selfie / 256).astype(np.uint8)
                else:
                    selfie = selfie.astype(np.uint8)

            # Try DeepFace first as it's generally more reliable
            # start_time = time.time()
            face_locations1, face_encodings1 = load_and_process_image_deepface(selfie)
            # end_time = time.time()

            if not face_locations1 or not face_encodings1:
                print("No face detected in Selfie Video by DeepFace")
                return 0

            # print(f"Face detection took {end_time - start_time:.3f} seconds")

            face_locations2, face_encodings2 = front_face_locations, front_face_encodings

            if not face_encodings2.any():
                print('No face detected in front ID')
                return 0

            largest_face_index1 = face_locations1.index(
                max(face_locations1, key=lambda loc: (loc[2] - loc[0]) * (loc[3] - loc[1])))
            largest_face_index2 = face_locations2.index(
                max(face_locations2, key=lambda loc: (loc[2] - loc[0]) * (loc[3] - loc[1])))

            face_encoding1 = face_encodings1[largest_face_index1]
            face_encoding2 = face_encodings2[largest_face_index2]

            similarity_score = self.calculate_similarity(face_encoding1, face_encoding2)
            # print(f"Calculated similarity score: {similarity_score}")

            return min(1, similarity_score)

        except Exception as e:
            print(f"Error in extract_face_and_compute_similarity: {e}")
            import traceback
            traceback.print_exc()
            return 0

    def calculate_landmarks_movement(self, current_landmarks, previous_landmarks):
        return sum(
            abs(cur_point.position.x - prev_point.position.x) +
            abs(cur_point.position.y - prev_point.position.y)
            for cur_point, prev_point in zip(current_landmarks, previous_landmarks)
        )

    def calculate_face_movement(self, current_face, previous_face):
        return abs(current_face[0].x - previous_face[0].x) + abs(current_face[0].y - previous_face[0].y)

    def calculate_liveness_result(self, eyebrow_movement, nose_movement, lip_movement, face_movement):
        eyebrow_movement_threshold = 15.0
        nose_movement_threshold = 15.0
        lip_movement_threshold = 15.0
        face_movement_threshold = 10.0

        if (
                eyebrow_movement > eyebrow_movement_threshold or
                nose_movement > nose_movement_threshold or
                lip_movement > lip_movement_threshold or
                face_movement > face_movement_threshold
        ):
            return True
        else:
            return False

    def detect_image_format(self, base64_image):
        import imghdr

        decoded_image = base64.b64decode(base64_image)
        format = imghdr.what(None, decoded_image)

        return format

    def frame_count_and_save(self, cap):
        frames = []
        status, frame = cap.read()
        while status:
            frames.append(frame)
            status, frame = cap.read()

        cap.release()
        return frames

    def classify_id_side_with_gpt(self, image_base64):
        response = openai.ChatCompletion.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text",
                         "text": "This is an image of an Iraqi National ID. Please tell me whether it's the front or the back of the ID. The front contains the person's name, gender, and blood type. The back contains the date of birth, date of issue, expiry date, and MRZ (machine-readable zone)."},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{image_base64}"}}
                    ],
                }
            ],
            max_tokens=10
        )
        content = response.choices[0].message.content.strip().lower()

        if "front" in content:
            return "front"
        elif "back" in content:
            return "back"
        else:
            # fallback in case of ambiguous answer
            return "ambigous"

    def get_ocr_results(self, processed_image, country=None, side=None):
        # with io.BytesIO() as output:
        #     processed_image.save(output, format="PNG")
        #     image_data = output.getvalue()

        # image = vision_v1.types.Image(content=image_data)

        if country == 'QAT' or country == 'LBN' or country == 'IRQ' or country == 'SDN':
            image = vision_v1.types.Image(content=processed_image)

        else:
            compressed_image = BytesIO()
            processed_image.save(compressed_image, format="JPEG", quality=60, optimize=True)
            compressed_image_data = compressed_image.getvalue()
            image = vision_v1.types.Image(content=compressed_image_data)

        response = self.client.text_detection(image=image)
        id_infos = response.text_annotations

        return id_infos

    def extract_document_info(self, image, side, document_type, country, nationality, step_data=None):
        st = time.time()
        document_data = {}
        # side=auto only in testing mode.
        # if document_type != 'passport' and country == 'IRQ':
        #     document_data = self.agent_extraction(image, country, side)
        #     logging.info(
        #         f"--------------Time taken for Front ID Extraction in IDV package: {time.time() - st} seconds\n")
        #     return document_data

        if country == 'IRQ':
            document_data = self.agent_extraction(image, country, nationality, side, step_data)
            logging.info(
                f"--------------Time taken for Front ID Extraction in IDV package: {time.time() - st} seconds\n")
            return document_data

        if document_type == 'national_id' and side == 'front':
            document_data = self.extract_front_id_info(image, country, nationality)
            logging.info(
                f"--------------Time taken for Front ID Extraction in IDV package: {time.time() - st} seconds\n")
            return document_data

        if document_type == 'national_id' and side == 'back':
            document_data = self.extract_back_id_info(image, country, nationality)
            logging.info(
                f"--------------Time taken for Back ID Extraction in IDV package: {time.time() - st} seconds\n")

        if document_type == 'passport' and (side == 'first' or side == 'page1' or side == ''):
            document_data = self.exract_passport_info(image, country, nationality, step_data)
            logging.info(
                f"--------------Time taken for Passport Extraction in IDV package: {time.time() - st} seconds\n")

        if document_type == 'passport' and (side == 'last' or side == 'page2'):
            document_data = self.exract_passport_info_back(image, country, nationality)
            logging.info(
                f"--------------Time taken for Passport Extraction in IDV package: {time.time() - st} seconds\n")

        if document_type == 'driving_license':
            pass

        return document_data

    def agent_extraction(self, front_id, country, nationality, side, step_data=None):
        from idvpackage.ocr_utils import detect_photo_on_screen, detect_screenshot, document_on_printed_paper
        from idvpackage.common import load_and_process_image_deepface
        from idvpackage.iraq_id_extraction_withopenai_test import extraction_chain_test
        result = {'error': '', "error_details": ''}
        try:
            gpt_side = self.classify_id_side_with_gpt(front_id)

            if gpt_side == 'back':

                st = time.time()
                processed_front_id = self.image_conversion(front_id)
                logging.info(f'----------------Time taken for image conversion: {time.time() - st} seconds\n')
                compressed_image = BytesIO()
                processed_front_id.save(compressed_image, format="JPEG", quality=85, optimize=True)
                compressed_image_data = compressed_image.getvalue()

                front_id_text = self.get_ocr_results(compressed_image_data, country=country)

                front_id_text_desc = front_id_text[0].description

                # google vision api replacement:
                # front_id_text_desc, result_extraction, side = ocr_and_extraction(front_id, openai.api_key, side)

                # the extra side here is for testing. So that when we test, we can pass in side='auto', instead of passing front and back seperately.

                ocr_text, side_predicted = extraction_chain_test(ocr_text=front_id_text_desc, openai_key=openai.api_key,
                                                           side=side)

                return ocr_text, side_predicted
            else:
                return "Front ID"
        except Exception as e:
            print(f"some exception: {e}")
