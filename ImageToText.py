import streamlit as st
import google.generativeai as genai
from PIL import Image
import requests
from io import BytesIO

# Configure the API key
genai.configure(api_key="AIzaSyCKWeSIDhA4d7sZ_6z_zk868sRkaP5kc1I")

# Define the function for uploading and processing the image
def image_text(image_path, prompt):
    def upload_to_gemini(path, mime_type=None):
        """Uploads the given file to Gemini."""
        file = genai.upload_file(path, mime_type=mime_type)
        return file

    # Upload the image
    mime_type = "image/jpeg"  # Adjust MIME type if needed
    file = upload_to_gemini(image_path, mime_type=mime_type)

    # Create the model with the necessary configuration
    generation_config = {
        "temperature": 0.9,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 1024,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )

    # Generate a response from the model
    response = model.generate_content([prompt, "Image: ", file])

    return response.text

# Streamlit app setup
st.set_page_config(page_title="Test ImageToText")
st.header('Test ImageToText')

# Options for image source
option = st.radio("Select the image source:", ('Upload Image', 'Use Camera', 'Image from URL'))

uploaded_image = None

# File uploader for local image upload
if option == 'Upload Image':
    uploaded_file = st.file_uploader("Upload an image", type=['jpg', 'jpeg', 'png'])
    if uploaded_file is not None:
        uploaded_image = Image.open(uploaded_file)

# Camera input for capturing a photo
elif option == 'Use Camera':
    camera_image = st.camera_input("Take a picture")
    if camera_image is not None:
        uploaded_image = Image.open(camera_image)

# URL input for using an image link
elif option == 'Image from URL':
    image_url = st.text_input("Enter the image URL")
    if image_url:
        try:
            response = requests.get(image_url)
            uploaded_image = Image.open(BytesIO(response.content))
        except Exception as e:
            st.error(f"Error fetching image: {e}")

# Display the uploaded image (if available) in an expander
if uploaded_image is not None:
    with st.expander("View Uploaded Image"):
        st.image(uploaded_image, caption="Uploaded Image", use_column_width=True)

# Text input for prompt
prompt_text = st.text_input("Enter your prompt")

# Button to trigger the processing
if st.button("Generate Text from Image"):
    if uploaded_image is not None and prompt_text:
        # Convert image to RGB mode if necessary before saving
        if uploaded_image.mode != 'RGB':
            uploaded_image = uploaded_image.convert('RGB')

        # Save the image temporarily
        uploaded_image.save("temp_image.jpg")

        # Call the image_text function
        result = image_text("temp_image.jpg", prompt_text)

        # Display the result
        st.write("Generated Text:")
        st.write(result)
    else:
        st.write("Please upload an image or enter a valid URL and provide a prompt.")
