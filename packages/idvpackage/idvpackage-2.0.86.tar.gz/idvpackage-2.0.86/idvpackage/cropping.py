import base64
from io import BytesIO
from PIL import Image
from rembg import remove
import os
def remove_background_from_base64(base64_img_str: str) -> str:
    """
    Takes a base64-encoded image, removes the background using AI,
    and returns a base64-encoded image with only the ID document visible.
    """
    # Remove data URL prefix if present
    if base64_img_str.startswith('data:image'):
        base64_img_str = base64_img_str.split(',', 1)[1]

    # Decode base64 string to bytes
    img_data = base64.b64decode(base64_img_str)

    # Load image from bytes
    input_image = Image.open(BytesIO(img_data))

    # Remove background
    output_image = remove(input_image)

    # Save output image to bytes buffer in PNG format (supports transparency)
    buffered = BytesIO()
    output_image.save(buffered, format="PNG")
    img_bytes = buffered.getvalue()

    # Encode output image bytes to base64 string
    base64_output = base64.b64encode(img_bytes).decode('utf-8')

    # Return with data URL prefix for PNG
    return base64_output

# Example usage:

if __name__=='__main__':
    def image_to_base64(image_path):
        with open(image_path, "rb") as image_file:
            image_data = image_file.read()
            base64_encoded = base64.b64encode(image_data).decode("utf-8")

            return base64_encoded


    import base64


    def base64_to_jpg(base64_string, output_path):
        """
        Convert a base64 string to a JPEG image file.

        Args:
            base64_string (str): The base64-encoded image data.
            output_path (str): The file path where the JPEG image will be saved.
        """
        # Decode the base64 string to bytes
        image_data = base64.b64decode(base64_string)

        # Write the bytes to a file
        with open(output_path, "wb") as f:
            f.write(image_data)

    root = '/Users/husunshujaat/Downloads/iraq_agent/'
    images = [file for file in os.listdir(root) if file.endswith(('.jpg','.png'))]
    for img in images:
        image = image_to_base64(os.path.join(root,img))
        cropped_base64 = remove_background_from_base64(image)

        base64_to_jpg(cropped_base64, f'/Users/husunshujaat/Downloads/iraq_agent/warped/{img}_warped.png')

