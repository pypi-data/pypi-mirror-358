import openai
import os
import base64
import json


def image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        image_data = image_file.read()
        base64_encoded = base64.b64encode(image_data).decode("utf-8")

        return base64_encoded

def llm_ocr_extraction(base_64_image):
    ocr_tool = [
        {
            "type": "function",
            "function": {
                "name": "extract_text_from_image",
                "description": "Extract all text strictly as seen in the image. Do not add or modify any words.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "text": {
                            "type": "string",
                            "description": "The exact text seen in the image",
                        },
                    },
                    "required": ["text"],
                },
            },
        }
    ]

    try:
        response = openai.ChatCompletion.create(
            # api_key=key,
            model="gpt-4.1-mini",  # Use a vision-capable model
            temperature=0.2,
            max_tokens=2000,
            tools=ocr_tool,
            tool_choice="auto",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": (
                                    "Extract all text exactly as it appears in the image. "
                                    "Text that is in English should be extracted in English, "
                                    "and text that is in Arabic should be extracted in Arabic. "
                                    "Do not translate, modify, add, or remove any words. "
                                    "Return the extracted text exactly as it appears."
                ),
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base_64_image}",
                            },
                        },
                    ],
                }
            ],
        )

        # Extract structured function response
        tool_response = response.choices[0].message.tool_calls[0].function.arguments
        text = json.loads(tool_response).get("text", "")
        return text
    except Exception as e:
        return f"Error during OCR extraction: {str(e)}"
#
# openai.api_key = "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"
# root = '/Users/husunshujaat/Downloads/Uqudo Mike Testing/Iraqi Passports'
# images = [file for file in os.listdir(root) if file.endswith(('.jpg', '.png'))]
# for image in images:
#     img = image_to_base64(os.path.join(root,image))
#     r = llm_ocr_extraction(img,'')
#     print(r)