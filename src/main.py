import os
import streamlit as st
from streamlit_chat import message

from pandasai import PandasAI
from constants import file_format, models
import matplotlib.pyplot as plt
from io import BytesIO
from PIL import Image

@st.cache_data
def load_data(uploaded_file):
    ext = os.path.splitext(uploaded_file.name)[1][1:].lower()
    if ext in file_format:
        return file_format[ext](uploaded_file)

def generate_response(question_input, dataframe, option, api_key):
    llm = models[option](api_key)
    pandas_ai = PandasAI(llm, conversational=False)
    return pandas_ai(dataframe, prompt=question_input, is_conversational_answer=True)    

st.set_page_config(page_title="PandasAI Chat", page_icon=":panda_face:")
st.title("PandasAI Chat :panda_face:")

if "generated" not in st.session_state:
    st.session_state["generated"] = []

if "past" not in st.session_state:
    st.session_state["past"] = []

if "plots" not in st.session_state:
    st.session_state["plots"] = []

left, right = st.columns([1, 2])
with left:
    model_option = st.selectbox('Model', models.keys())

with right:
    api_key = st.text_input('API Key', '', type = 'password')
    if not api_key:
        st.info(f"Please input API Token for {model_option}.")

question_input = None
uploaded_file = st.file_uploader("Upload a file", type=list(file_format.keys()))

if not uploaded_file:
    st.info("Please upload your dataset to begin asking questions!")

if uploaded_file:
    question_input = st.text_input("Enter question")

st.markdown("---")

if question_input and uploaded_file and api_key:
    with st.spinner("Generating..."):
        dataframe = load_data(uploaded_file)
        response = generate_response(question_input, dataframe, model_option, api_key)

        if len(plt.get_fignums()) > 0:
            fig = plt.gcf()
            buffer = BytesIO()
            fig.savefig(buffer, format='png')
            buffer.seek(0)

            image = Image.open(buffer)

            width, height = image.size
            new_width = int(width * 0.6)
            new_height = int(height * 0.6)
            resized_image = image.resize((new_width, new_height))

            st.session_state.plots.append(resized_image)
        else:
            st.session_state.plots.append("None")

        st.session_state.past.append(question_input)
        st.session_state.generated.append(response)
else:
    response = None

if "generated" in st.session_state and st.session_state['generated']:
    for i in range(len(st.session_state['generated'])-1, -1, -1):
        if st.session_state["plots"][i] != "None":
            st.image(st.session_state["plots"][i], use_column_width=True)
        message(st.session_state["generated"][i], key=str(i))
        message(st.session_state['past'][i], is_user=True, key=str(i) + '_user')
    