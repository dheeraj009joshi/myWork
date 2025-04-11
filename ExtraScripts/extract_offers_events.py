import openai
import easyocr
import pytesseract
import cv2
import requests
import numpy as np
import json

openai.api_key = "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"

reader = easyocr.Reader(['en'], gpu=False)

def extract_text_with_tesseract(image_url):
    """Extract text from an image using Tesseract OCR with preprocessing."""
    try:
        response = requests.get(image_url)
        response.raise_for_status()
        print(response)
        image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
        image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

        # Preprocessing for better OCR
        gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        denoised_image = cv2.medianBlur(gray_image, 3)
        _, binary_image = cv2.threshold(denoised_image, 128, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Extract text using Tesseract
        extracted_text = pytesseract.image_to_string(binary_image, config='--psm 6', lang='eng')
        return extracted_text.strip()
    except Exception as e:
        print(f"Error processing image with Tesseract: {e}")
        return ""

def extract_text_from_images(image_urls):
    """Extract text from all images using both Tesseract and EasyOCR, combining results."""
    combined_text = ""
    for i, image_url in enumerate(image_urls):
        try:
            print(f"Processing image {i + 1} of {len(image_urls)}: {image_url}")

            # # Attempt extraction with Tesseract
            # tesseract_text = extract_text_with_tesseract(image_url)
            # print(f"Tesseract OCR Result:\n{tesseract_text}")

            # Fall back to EasyOCR if Tesseract results are incomplete
            # if not tesseract_text.strip():
            response = requests.get(image_url)
            response.raise_for_status()
            image_array = np.asarray(bytearray(response.content), dtype=np.uint8)
            image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
            gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            easyocr_text = "\n".join(reader.readtext(gray_image, detail=0))
            print(f"EasyOCR Result:\n{easyocr_text}")
            tesseract_text = easyocr_text

            combined_text += "\n" + tesseract_text
            print(combined_text)
        except Exception as e:
            print(f"Error processing image {image_url}: {e}")
    return combined_text

def analyze_combined_text(combined_text):
    """Analyze the combined text using OpenAI GPT for extracting structured data of places and offers."""
    messages = [
        {
            "role": "system",
            "content": "You are an advanced assistant trained to extract and organize details about places and offers from text."
        },
        {
            "role": "user",
            "content": f"""
Your task is to process the following text and extract details about places and offers, presenting them in a clean and structured JSON format.

### Output Format
Provide the output as a **JSON array**, where each place is a separate object, and the offers for that place are grouped into a **list**. The structure should follow this format:

[
    {{
        "placeName": "Name of the place (if mentioned, or keep as an empty string)",
        "daysAvailable": "Days the offers are valid (if mentioned, or keep as an empty string)",
        "offers": [
            {{
                "description": "Detailed description of the offer.",
                "price": "Price of the offer, if available (or keep as an empty string).",
                "otherDetails": "Other important information, such as timings, terms, or conditions (or keep as an empty string)."
            }},
            ...
        ]
    }},
    ...
]

### Instructions for Extraction
1. **Place Details:**
   - **Name of the Place**: Extract the name of the place if mentioned. If not available, leave `placeName` as an empty string.
   - **Days Available**: Include the validity days for offers (e.g., "Weekends," "Weekdays," or specific dates). Leave empty if not mentioned.

2. **Offers:**
   - Group all offers related to a place into a single list under the `offers` key.
   - For each offer:
     - **Description**: Provide a clear and detailed description.
     - **Price**: Extract and include the price, if available. Otherwise, leave it as an empty string.
     - **Other Details**: Include other significant information (e.g., applicable times, specific conditions, or terms). Leave this as an empty string if no additional information is provided.

3. **Handling Multiple Places:**
   - If the text mentions multiple places, create separate objects for each place with their respective offers.

4. **Missing Information:**
   - For any missing details (e.g., place name, days), keep the corresponding fields as empty strings.
   - If terms or conditions are unclear, extract what is available.

5. **Example Output:**
```json
[
    {{
        "placeName": "Café Mocha",
        "daysAvailable": "Weekdays",
        "offers": [
            {{
                "description": "Buy 1 Get 1 Free on all beverages.",
                "price": "",
                "otherDetails": "Valid from 10 AM to 5 PM."
            }},
            {{
                "description": "20% off on orders above ₹500.",
                "price": "",
                "otherDetails": "Valid for dine-in only."
            }}
        ]
    }},
    {{
        "placeName": "The Coffee House",
        "daysAvailable": "Weekends",
        "offers": [
            {{
                "description": "Flat ₹200 off on orders above ₹1000.",
                "price": "",
                "otherDetails": "Applicable for online orders only."
            }}
        ]
    }}
]


Here is the text extracted from the images:
{combined_text}
"""
        }
    ]

    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=messages,
        max_tokens=2000,
        temperature=0
    )

    output_json = response['choices'][0]['message']['content'].strip()
    print(output_json)
    try:
        
        structured_data = json.loads(output_json.replace("```json", "").replace("```", ""))
        return structured_data
    except json.JSONDecodeError:
        return {"error": "Failed to parse JSON from OpenAI response"}

def extract_places_and_offers_from_images(image_urls):
    """Main function to extract and organize offers from a list of images."""
    combined_text = extract_text_from_images(image_urls)
    extracted_data = analyze_combined_text(combined_text)
    return extracted_data


# Sample image URLs
image_urls = [
    "https://i.ibb.co/PQLd9nr/Whats-App-Image-2025-01-09-at-08-28-05-6cee744d.jpg"
    ]

places_and_offers = extract_places_and_offers_from_images(image_urls)

print(json.dumps(places_and_offers, indent=4))
