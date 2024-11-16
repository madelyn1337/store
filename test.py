import requests
from bs4 import BeautifulSoup
import re

# Function to extract IMDb ID from the URL or random string
def get_imdb_id(input_string):
    match = re.search(r'tt\d{7,8}', input_string)
    if match:
        return match.group(0)
    return None

# Function to construct the correct IMDb technical URL
def construct_technical_url(imdb_id):
    return f'https://www.imdb.com/title/{imdb_id}/technical/?ref_=tt_ov_at_dt_spec'

# Function to get the aspect ratios and negative format from IMDb
def get_technical_details(imdb_id):
    technical_url = construct_technical_url(imdb_id)
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }

    # Send the request with headers
    response = requests.get(technical_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to fetch page: {response.status_code}")
        return None, None
    
    soup = BeautifulSoup(response.text, 'html.parser')
    
    content_containers = soup.find_all('div', class_='ipc-metadata-list-item__content-container')
    if not content_containers:
        print("No content containers found.")
        return None, None

    aspect_ratios = []
    negative_formats = []

    # Extract aspect ratios
    for container in content_containers:
        ratio_items = container.find_all('span', class_='ipc-metadata-list-item__list-content-item')
        if ratio_items:
            for item in ratio_items:
                text = item.get_text(strip=True)
                match = re.match(r'^\d+(\.\d+)?\s?:\s?\d+(\.\d+)?$', text) or re.match(r'^\d+(\.\d+)?\s?x\s?\d+(\.\d+)?$', text)
                if match:
                    context = item.find_next('span', class_='ipc-metadata-list-item__list-content-item--subText')
                    context_text = context.get_text(strip=True) if context else ""
                    aspect_ratios.append((text, context_text))

        # Extract negative formats (like 35mm, Digital)
        ul_item = container.find('ul', class_='ipc-inline-list')
        if ul_item:
            format_items = ul_item.find_all('span', class_='ipc-metadata-list-item__list-content-item')
            for format_item in format_items:
                format_text = format_item.get_text(strip=True)
                if re.search(r'\d+\s?mm|digital', format_text, re.IGNORECASE):
                    format_text = format_text.replace("mm", "mm").strip().lower()
                    if format_text not in negative_formats:
                        negative_formats.append(format_text)

    negative_format_section = soup.find('li', id='negativeFormat')
    if negative_format_section:
        ul_negative = negative_format_section.find('ul', class_='ipc-inline-list')
        if ul_negative:
            negative_items = ul_negative.find_all('span', class_='ipc-metadata-list-item__list-content-item')
            for item in negative_items:
                negative_format = item.get_text(strip=True)
                if re.search(r'\d+\s?mm|digital', negative_format, re.IGNORECASE):
                    negative_format = negative_format.replace("mm", "mm").strip().lower()
                    if negative_format not in negative_formats:
                        negative_formats.append(negative_format)

    return aspect_ratios, negative_formats

# Function to calculate corrected dimensions based on aspect ratio and input width or height
def calculate_corrected_dimensions(width, height, aspect_ratio):
    try:
        ratio_parts = re.split('[:x]', aspect_ratio)
        if len(ratio_parts) == 2:
            ratio = float(ratio_parts[0].strip()) / float(ratio_parts[1].strip())
        else:
            ratio = float(ratio_parts[0].strip())

        # Version 1: Calculate height based on the width and aspect ratio
        corrected_height_based_on_width = int(width / ratio)

        # Version 2: Calculate width based on the height and aspect ratio
        corrected_width_based_on_height = int(height * ratio)

        return corrected_width_based_on_height, corrected_height_based_on_width

    except Exception as e:
        print(f"Error calculating dimensions for aspect ratio {aspect_ratio}: {e}")
        return None, None

# Function to select the correct version that fits within the input dimensions
def select_correct_version(width, height, aspect_ratio):
    corrected_width_based_on_height, corrected_height_based_on_width = calculate_corrected_dimensions(width, height, aspect_ratio)

    # Determine if cropping is required based on the input height as the threshold
    if corrected_height_based_on_width <= height:
        # Fits within the height, so use the width with cropped height
        return width, corrected_height_based_on_width
    elif corrected_width_based_on_height <= width:
        # Fits within the width, so use the height with cropped width
        return corrected_width_based_on_height, height
    else:
        # If neither fits without exceeding, return None
        return None, None

# Main function to process user input
def process_input(user_input, width, height):
    imdb_id = get_imdb_id(user_input)
    if not imdb_id:
        print("Invalid IMDb URL or ID.")
        return
    
    # Fetch the technical details (aspect ratios and negative format)
    aspect_ratios, negative_formats = get_technical_details(imdb_id)
    
    if not aspect_ratios:
        print("Could not retrieve aspect ratios.")
        return

    # Handle multiple aspect ratios
    if len(aspect_ratios) > 1:
        print("Multiple aspect ratios found. You should consult a scene pack manager for help.")
    
    # Display all found aspect ratios
    print(f"Aspect Ratios Found:")
    for aspect_ratio, context in aspect_ratios:
        print(f"{aspect_ratio} {context}")
    
    # Display the negative format (film or digital)
    if negative_formats:
        print("Negative Format(s): " + ", ".join(negative_formats))
    else:
        print("Negative Format: Not found")
    
    # Calculate and display corrected dimensions for each aspect ratio
    for aspect_ratio, _ in aspect_ratios:
        corrected_width, corrected_height = select_correct_version(width, height, aspect_ratio)
        if corrected_width and corrected_height:
            print(f"\nAspect Ratio: {aspect_ratio}\nWidth: {width} px\nHeight: {height} px")
            print(f"Corrected Dimensions: {corrected_width} x {corrected_height}")
        else:
            print(f"\nAspect Ratio: {aspect_ratio}\nUnable to calculate corrected dimensions.")

# Example usage
user_input = input("Enter IMDb URL, ID, or random string with IMDb ID: ")
width = int(input("Enter movie width in pixels: "))
height = int(input("Enter movie height in pixels: "))
process_input(user_input, width, height)
