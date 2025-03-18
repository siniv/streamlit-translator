import streamlit as st
from gtts import gTTS
import io
import pandas as pd
import pdfplumber
import openai

openai.api_key = st.secrets["OPENAI_API_KEY"]

def translate_with_gpt(text, target_language='English'):
    """Translates text using OpenAI's GPT-3.5-turbo."""
    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": f"Translate the following text to {target_language}: '{text}'"}
            ]
        )
        translated_text = response['choices'][0]['message']['content'].strip()
        return translated_text
    except Exception as e:
        st.error(f"Error during GPT translation: {e}")
        return None

def text_to_speech(text, target_language_code='en'):
    """Converts text to speech and returns audio bytes."""
    try:
        tts = gTTS(text, lang=target_language_code)
        audio_bytes = io.BytesIO()
        tts.write_to_fp(audio_bytes)
        st.audio(audio_bytes.getvalue(), format='audio/mpeg')
        return audio_bytes.getvalue()
    except Exception as e:
        st.error(f"Error during speech synthesis: {e}")
        return None

def extract_text_from_file(uploaded_file):
    """Extracts text from various file formats."""
    file_type = uploaded_file.type

    if "text/plain" in file_type:
        return uploaded_file.getvalue().decode("utf-8")
    elif "application/pdf" in file_type:
        try:
            with pdfplumber.open(uploaded_file) as pdf:
                text = "".join([page.extract_text() or '' for page in pdf.pages])
                return text
        except Exception as e:
            st.error(f"Error extracting text from PDF: {e}")
            return None
    elif "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet" in file_type or "application/vnd.ms-excel" in file_type:
        try:
            df = pd.read_excel(uploaded_file)
            return df.to_string()
        except Exception as e:
            st.error(f"Error reading Excel file: {e}")
            return None
    elif "text/csv" in file_type:
        try:
            df = pd.read_csv(uploaded_file)
            return df.to_string()
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")
            return None
    else:
        st.error("Unsupported file type.")
        return None

def main():
    st.title("Multilingual Translator")

    input_option = st.radio("Input Text:", ("Enter Text", "Upload File"))

    if input_option == "Enter Text":
        input_text = st.text_area("Enter text to translate:")
    else:
        uploaded_file = st.file_uploader("Upload a file (PDF, TXT, Excel, CSV)", type=["pdf", "txt", "xlsx", "xls", "csv"])
        if uploaded_file:
            input_text = extract_text_from_file(uploaded_file)
        else:
            input_text = None

    target_lang = st.selectbox("Select target language:",
                               ['English', 'Spanish', 'French', 'German', 'Japanese', 'Korean', 'Chinese', 'Arabic', 'Russian', 'Portuguese'])

    lang_code_map = {
        'English': 'en', 'Spanish': 'es', 'French': 'fr', 'German': 'de',
        'Japanese': 'ja', 'Korean': 'ko', 'Chinese': 'zh-cn', 'Arabic': 'ar',
        'Russian': 'ru', 'Portuguese': 'pt'
    }

    if st.button("Translate and Speak"):
        if input_text:
            translated_text = translate_with_gpt(input_text, target_lang)
            if translated_text:
                st.write("Translated Text:", translated_text)
                audio_data = text_to_speech(translated_text, lang_code_map[target_lang])
                if audio_data:
                    st.download_button(
                        label="Save Audio",  # Change the button label
                        data=audio_data,
                        file_name="output.mp3",
                        mime="audio/mpeg"
                    )
        else:
            st.warning("Please enter some text or upload a file.")

if __name__ == "__main__":
    main()