import os
from PIL import Image
import supervision as sv
import cv2
import numpy as np

def open_image(image_path: str) -> Image:
    """
    Open and return an image.

    Args:
        image_path (str): The path to the image file.

    Returns:
        Image object: The opened image.
    """
    try:
        # Open the image file
        img = Image.open(image_path)
        return img
    except Exception as e:
        print(f"Error opening image: {e}")
        return None
    
def save_image(image: Image, output_path: str, name: str) -> str:
    """
    Save an image to the local disk.

    Args:
        image (Image object): The image to be saved.
        output_path (str): The path to save the image.
        name (str): The name of the saved image file.

    Returns:
        str: The file path where the image is saved, or an error message if saving fails.
    """
    try:
        # Save the image to the specified path
        file_path = os.path.join(output_path, name)
        image.save(file_path)
        return file_path
    except Exception as e:
        print(f"Error saving image: {e}")
        return str(e)
    
def convert_image_format(input_path: str, output_path: str, output_filename: str, output_format: str = "JPEG") -> str:
    """
    Convert an image to another image format (e.g., from PNG to JPEG).

    Args:
        input_path (str): The path to the input image file.
        output_path (str): The path to save the converted image.
        output_filename (str): The name of the converted image file.
        output_format (str): The format to which the image should be converted. Default is "JPEG".

    Returns:
        str: The file path where the converted image is saved, or an error message if conversion fails.
    """
    try:
        file_path = os.path.join(output_path, output_filename + "." + output_format)
        # Open the input image
        with Image.open(input_path) as img:
            # Convert and save the image to the desired format
            img.convert("RGB").save(file_path, format=output_format)
            print(f"Image converted successfully: {file_path}")
    except Exception as e:
        print(f"Error converting image: {e}")
        return str(e)

    return file_path
    
def resize_image(image: Image, new_width: int, new_height: int) -> Image:
    """
    Resize an image to the specified width and height.

    Args:
        image (PIL.Image.Image): The PIL image object to be resized.
        new_width (int): The desired width of the resized image.
        new_height (int): The desired height of the resized image.

    Returns:
        PIL.Image.Image: The resized image.
    """
    try:
        # Resize the image
        resized_img = image.resize((new_width, new_height))
        return resized_img
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None
    
def crop_image(image: Image, x: int, y: int, width: int, height: int) -> Image:
    """
    Crop an image based on the specified coordinates and dimensions.

    Args:
        image (PIL.Image.Image): The PIL image object to be cropped.
        x (int): The x-coordinate of the top-left corner of the cropping region.
        y (int): The y-coordinate of the top-left corner of the cropping region.
        width (int): The width of the cropping region.
        height (int): The height of the cropping region.

    Returns:
        PIL.Image.Image: The cropped image.
    """
    try:
        # Crop the image
        cropped_img = image.crop((x, y, x + width, y + height))
        return cropped_img
    except Exception as e:
        print(f"Error cropping image: {e}")
        return None
    
def flip_image(image: Image, direction: str = 'horizontal') -> Image:
    """
    Flip an image horizontally or vertically.

    Args:
        image (PIL.Image.Image): The PIL image object to be flipped.
        direction (str): The direction of the flip ('horizontal' or 'vertical'). Default is 'horizontal'.

    Returns:
        PIL.Image.Image: The flipped image.
    """
    try:
        # Flip the image
        if direction == 'horizontal':
            flipped_img = image.transpose(Image.FLIP_LEFT_RIGHT)
        elif direction == 'vertical':
            flipped_img = image.transpose(Image.FLIP_TOP_BOTTOM)
        else:
            print("Invalid flip direction. Please use 'horizontal' or 'vertical'.")
            return None

        return flipped_img
    except Exception as e:
        print(f"Error flipping image: {e}")
        return None

def rotate_image(image: Image, angle: float) -> Image:
    """
    Rotate an image by the given angle (in degrees).

    Args:
        image (PIL.Image.Image): The PIL image object to be rotated.
        angle (float): The angle by which to rotate the image (in degrees).

    Returns:
        PIL.Image.Image: The rotated image.
    """
    try:
        # Rotate the image
        rotated_img = image.rotate(angle)
        return rotated_img
    except Exception as e:
        print(f"Error rotating image: {e}")
        return None

def convert_to_grayscale(image: Image) -> Image:
    """
    Convert a color image to grayscale.

    Args:
        image (PIL.Image.Image): The PIL image object to be converted.

    Returns:
        PIL.Image.Image: The grayscale image.
    """
    try:
        # Convert the image to grayscale
        grayscale_img = image.convert("L")
        return grayscale_img
    except Exception as e:
        print(f"Error converting image to grayscale: {e}")
        return None

def PIL_get_image_size(image: Image) -> tuple:
    """
    Get PILLOW image size.

    Args:
        image (PIL.Image.Image): The PIL image object.

    Returns:
        tuple: A tuple containing the width and height of the image.
    """
    width, height = image.size
    return width, height

def cv_get_image_size(image) -> tuple:
    """
    Get cv2 image size.

    Args:
        image: The cv2 image array.

    Returns:
        tuple: A tuple containing the width and height of the image.
    """
    height, width, _ = image.shape
    return width, height

def convert_PIL_to_cv(image: Image) -> np.ndarray:
    """
    Convert an image from Pillow to CV2.

    Args:
        image (PIL.Image.Image): The PIL image object.

    Returns:
        numpy.ndarray: The converted cv2 image array.
    """
    numpy_array = np.array(image)
    cv2_image = cv2.cvtColor(numpy_array, cv2.COLOR_RGB2BGR)
    return cv2_image

def convert_cv2_to_pil(cv2_image: np.ndarray) -> Image:
    """
    Convert an image from OpenCV format (BGR) to Pillow format (RGB).

    Args:
        cv2_image (np.ndarray): The input image in OpenCV format (BGR).

    Returns:
        Image.Image: The converted image in Pillow format (RGB).
    """
    # Convert the OpenCV image from BGR to RGB format
    rgb_image = cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB)
    
    # Create a Pillow Image from the RGB image
    pil_image = Image.fromarray(rgb_image)
    
    return pil_image

def compress_image(image: Image, output_path: str, name: str, quality: int) -> str:
    """
    Compress an image with a specified quality level.

    Args:
        image (Image.Image): The image object to be compressed.
        output_path (str): The directory path where the compressed image will be saved.
        name (str): The name of the compressed image file.
        quality (int): The quality level for compression (0 to 100, higher is better).

    Returns:
        str: The file path of the compressed image, or an empty string if an error occurred.
    """
    try:
        # Create the file path by joining the output path and file name
        file_path = os.path.join(output_path, name)
        
        # Save the image with the specified quality
        image.save(file_path, quality=quality)
        
        return file_path
    except Exception as e:
        print(f"Error compressing image: {e}")
        return ""
    

def cv2_read_image(path: str) -> np.ndarray:
    """
    Read an image file using OpenCV.

    Args:
        path (str): The file path to the image.

    Returns:
        np.ndarray: The image read by OpenCV as a NumPy array.
    """
    # Read the image from the given path
    image = cv2.imread(path)
    return image

def cv2_write_image(image: np.ndarray, path: str, name: str) -> str:
    """
    Write an image to a file using OpenCV.

    Args:
        image (np.ndarray): The image to be saved.
        path (str): The directory path where the image will be saved.
        name (str): The name of the image file.

    Returns:
        str: The file path of the saved image.
    """
    # Create the file path by joining the directory path and file name
    file_path = os.path.join(path, name)
    
    # Write the image to the specified file path
    cv2.imwrite(file_path, image)
    
    return file_path

def cv2_crop_image(image: np.ndarray, xmin: int, ymin: int, xmax: int, ymax: int) -> np.ndarray:
    """
    Crop an image by specified coordinates.

    Args:
        image (np.ndarray): The input image to be cropped.
        xmin (int): The minimum x-coordinate (left).
        ymin (int): The minimum y-coordinate (top).
        xmax (int): The maximum x-coordinate (right).
        ymax (int): The maximum y-coordinate (bottom).

    Returns:
        np.ndarray: The cropped image.
    """
    # Crop the image using the provided coordinates
    cropped_img = image[ymin:ymax, xmin:xmax]
    return cropped_img

def cv2_flip(image: np.ndarray, direction: str = 'horizontal') -> np.ndarray:
    """
    Flip an image either horizontally or vertically using OpenCV.

    Args:
        image (np.ndarray): The input image to be flipped.
        direction (str): The direction to flip the image, either 'horizontal' or 'vertical'. 
                         Default is 'horizontal'.

    Returns:
        np.ndarray: The flipped image.

    Raises:
        ValueError: If the direction is neither 'horizontal' nor 'vertical'.
    """
    if direction == 'horizontal':
        flipped_image = cv2.flip(image, 1)
    elif direction == 'vertical':
        flipped_image = cv2.flip(image, 0)
    else:
        raise ValueError("Direction should be 'horizontal' or 'vertical'")
    
    return flipped_image

def cv2_rotate_image(image: np.ndarray, angle: float) -> np.ndarray:
    """
    Rotate an image by a specified angle using OpenCV.

    Args:
        image (np.ndarray): The input image to be rotated.
        angle (float): The angle by which to rotate the image (in degrees).

    Returns:
        np.ndarray: The rotated image.
    """
    # Get the height and width of the image
    height, width = image.shape[:2]

    # Calculate the rotation matrix
    rotation_matrix = cv2.getRotationMatrix2D((width / 2, height / 2), angle, 1)

    # Apply the rotation to the image
    rotated_image = cv2.warpAffine(image, rotation_matrix, (width, height))

    return rotated_image

def cv2_convert_to_grayscale(image: np.ndarray) -> np.ndarray:
    """
    Convert an image to grayscale using OpenCV.

    Args:
        image (np.ndarray): The input image to be converted.

    Returns:
        np.ndarray: The grayscale image.
    """
    # Convert the image to grayscale
    grayscale_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    return grayscale_image
    
def draw_circle(image: np.ndarray, x: int, y: int, size: int = 5, color: tuple = (255, 0, 0)) -> np.ndarray:
    """
    Draw a circle on an OpenCV image.

    Args:
        image (np.ndarray): The input image on which to draw the circle.
        x (int): The x-coordinate of the center of the circle.
        y (int): The y-coordinate of the center of the circle.
        size (int, optional): The radius of the circle. Default is 5.
        color (tuple, optional): The color of the circle in RGB format. Default is red (255, 0, 0).

    Returns:
        np.ndarray: The image with the circle drawn on it.
    """
    # Convert the image from BGR to RGB color space
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    
    # Draw the circle on the RGB image
    image_with_circle = cv2.circle(image_rgb, (x, y), size, color, -1)
    
    return image_with_circle


def apply_mask(image: np.ndarray, mask: np.ndarray, color_mask: list = [255, 255, 255], reverse: bool = True, transparency: float = 1.0) -> np.ndarray:
    """
    Apply a transparent color mask on an image.

    Args:
        image (numpy.ndarray): The input image to which the mask will be applied.
        mask (numpy.ndarray): The binary mask indicating where to apply the color mask.
        color_mask (list, optional): The RGB color to use for the mask. Default is white [255, 255, 255].
        reverse (bool, optional): If True, apply the color mask where the mask is False; otherwise, apply where True. Default is True.
        transparency (float, optional): The transparency level of the color mask (0.0 to 1.0). Default is 1.0 (opaque).

    Returns:
        numpy.ndarray: The image with the color mask applied.
    """
    # Validate transparency value
    transparency = max(0.0, min(1.0, transparency))

    # Create a copy of the image
    masked_image = np.copy(image)

    # Calculate alpha value based on transparency
    alpha = int(255 * (1 - transparency))

    # Set the alpha channel of the color_mask
    color_mask_with_alpha = color_mask + [alpha]

    # Ensure the mask is a binary mask with the same dimensions as the image
    if mask.ndim == 2:
        mask = mask[:, :, np.newaxis]

    if reverse:
        # Apply the color mask where the mask is False
        masked_image[mask == 0] = color_mask_with_alpha
    else:
        # Apply the color mask where the mask is True
        masked_image[mask != 0] = color_mask_with_alpha

    return masked_image

def transform_coordinates_CV_to_YOLO(left: float, top: float, width: float, height: float) -> tuple:
    """
    Transform MS Custom Vision annotation format to YOLO format.

    Args:
        left (float): The x-coordinate of the top-left corner of the bounding box.
        top (float): The y-coordinate of the top-left corner of the bounding box.
        width (float): The width of the bounding box.
        height (float): The height of the bounding box.

    Returns:
        tuple: A tuple containing the transformed coordinates in YOLO format (center_x, center_y, width, height).
    """
    # Calculate the center coordinates
    center_x = left + (width / 2)
    center_y = top + (height / 2)
    
    return (center_x, center_y, width, height)


def transform_coordinates_PascalVOC_to_YOLO(xmin: float, ymin: float, xmax: float, ymax: float, width: float, height: float) -> tuple:
    """
    Transform PascalVOC coordinates to YOLO format.

    Args:
        xmin (float): The minimum x-coordinate (left boundary) of the bounding box.
        ymin (float): The minimum y-coordinate (top boundary) of the bounding box.
        xmax (float): The maximum x-coordinate (right boundary) of the bounding box.
        ymax (float): The maximum y-coordinate (bottom boundary) of the bounding box.
        width (float): The width of the image.
        height (float): The height of the image.

    Returns:
        tuple: A tuple containing the transformed coordinates in YOLO format (x_center, y_center, box_width, box_height).
    """
    # Calculate the center x-coordinate of the bounding box in YOLO format
    x_center = ((xmax + xmin) / 2) / width
    
    # Calculate the center y-coordinate of the bounding box in YOLO format
    y_center = ((ymax + ymin) / 2) / height
    
    # Calculate the width of the bounding box in YOLO format
    box_width = (xmax - xmin) / width
    
    # Calculate the height of the bounding box in YOLO format
    box_height = (ymax - ymin) / height
    
    return (x_center, y_center, box_width, box_height)


def transform_coordinates_YOLO_to_PascalVOC(center_x: float, center_y: float, width: float, height: float, image_width: int, image_height: int) -> tuple:
    """
    Convert YOLO coordinates to Pascal VOC format.

    Args:
        center_x (float): The x-coordinate of the center of the bounding box (YOLO format).
        center_y (float): The y-coordinate of the center of the bounding box (YOLO format).
        width (float): The width of the bounding box (YOLO format).
        height (float): The height of the bounding box (YOLO format).
        image_width (int): The width of the image.
        image_height (int): The height of the image.

    Returns:
        tuple: Pascal VOC coordinates (xmin, ymin, xmax, ymax).
    """
    # Convert YOLO coordinates to absolute coordinates
    abs_x = int(center_x * image_width)
    abs_y = int(center_y * image_height)
    abs_width = int(width * image_width)
    abs_height = int(height * image_height)

    # Calculate Pascal VOC coordinates
    xmin = max(0, int(abs_x - abs_width / 2))
    ymin = max(0, int(abs_y - abs_height / 2))
    xmax = min(image_width, int(abs_x + abs_width / 2))
    ymax = min(image_height, int(abs_y + abs_height / 2))

    return xmin, ymin, xmax, ymax


def sv_detections_ultralytics(results) -> sv.Detections:
    """
    Load detections from Ultralytics results.

    Args:
        results: The results object from Ultralytics containing detection data.

    Returns:
        sv.Detections: An object containing the loaded detections.
    """
    detections = sv.Detections.from_ultralytics(results)
    return detections

def sv_convert_mask_to_box(masks) -> sv.Detections:
    """
    Convert mask coordinates to bounding boxes.

    Args:
        masks: The mask data from which to derive bounding boxes.

    Returns:
        sv.Detections: An object containing the bounding boxes and original masks.
    """
    detections = sv.Detections(
        xyxy=sv.mask_to_xyxy(masks=masks),
        mask=masks
    )
    return detections

def sv_annotate_image_bbox(image: np.ndarray, detections: sv.Detections) -> np.ndarray:
    """
    Draw bounding boxes on an image.

    Args:
        image (np.ndarray): The input image on which to draw the bounding boxes.
        detections (sv.Detections): The detections containing bounding box information.

    Returns:
        np.ndarray: The annotated image with bounding boxes drawn.
    """
    bounding_box_annotator = sv.BoundingBoxAnnotator()
    annotated_image = bounding_box_annotator.annotate(scene=image, detections=detections)
    return annotated_image

def sv_annotate_image_mask(image: np.ndarray, detections: sv.Detections) -> np.ndarray:
    """
    Draw mask areas on an image.

    Args:
        image (np.ndarray): The input image on which to draw the mask areas.
        detections (sv.Detections): The detections containing mask information.

    Returns:
        np.ndarray: The annotated image with mask areas drawn.
    """
    mask_annotator = sv.MaskAnnotator()
    annotated_image = mask_annotator.annotate(scene=image, detections=detections)
    return annotated_image

def sv_annotate_image_label(
    image: np.ndarray, 
    detections: sv.Detections, 
    model, 
    color: sv.Color = sv.Color.ROBOFLOW, 
    text_color: sv.Color = sv.Color.WHITE, 
    text_position: sv.Position = sv.Position.TOP_CENTER
) -> np.ndarray:
    """
    Draw label rectangles on detections.

    Args:
        image (np.ndarray): The input image on which to draw the labels.
        detections (sv.Detections): The detections containing information about the detected objects.
        model: The model object containing the class names.
        color (sv.Color, optional): The color for the label rectangles. Defaults to sv.Color.ROBOFLOW.
        text_color (sv.Color, optional): The color for the text. Defaults to sv.Color.WHITE.
        text_position (sv.Position, optional): The position of the text relative to the detection. Defaults to sv.Position.TOP_CENTER.

    Returns:
        np.ndarray: The annotated image with label rectangles drawn.
    """
    # Instantiate the LabelAnnotator with the specified colors and text position
    label_annotator = sv.LabelAnnotator(color=color, text_color=text_color, text_position=text_position)

    # Extract the class names for each detected object
    labels = [
        model.model.names[class_id]
        for class_id in detections.class_id
    ]

    # Annotate the image with the labels
    annotated_image = label_annotator.annotate(scene=image, detections=detections, labels=labels)

    return annotated_image