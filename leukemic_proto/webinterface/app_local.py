import cv2 as cv
import streamlit as st
import numpy as np
import base64
from fastapi import FastAPI
from google.cloud import storage
import tensorflow
import requests
from leukemic_proto.ml_logic.data import load_test_img_prelim, show_img_prelim
from leukemic_proto.params import *
from leukemic_proto.api.fast import predict


# Create a client object using the credentials file
client = storage.Client()
bucket = client.bucket(BUCKET_NAME)

model = tensorflow.keras.models.load_model('../models/new_cnn_simple')


def add_bg_from_local(image_file):
    with open(image_file, "rb") as image_file:
        encoded_string = base64.b64encode(image_file.read())
    st.markdown(
    f"""
    <style>
    .stApp {{
        background-image: url(data:image/{"jpg"};base64,{encoded_string.decode()});
        background-size: cover
    }}
    </style>
    """,
    unsafe_allow_html=True
    )


st.set_page_config(layout='wide')

CSS = """
h1 {
    color: white;
}
h2 {color: black;
}
.stApp {
    background-image: webinterface/app_cloud.py;
    background-size: cover;
"""
st.write(f'<style>{CSS}</style>', unsafe_allow_html=True)

add_bg_from_local('images/lympho.png')

st.title('Leukemic Cell Detective')


st.markdown('### *Detecting healthy vs malignant cells from human white blood cells microscopic images*')

st.markdown('')

st.markdown('***')

st.markdown('')


st.markdown('Original dataset: https://wiki.cancerimagingarchive.net/pages/viewpage.action?pageId=52758223')

st.markdown('Dataset publication: Gupta, A., & Gupta, R. (2019). ALL Challenge dataset of ISBI 2019 [Data set]   \nThe Cancer Imaging Archive https://doi.org/10.7937/tcia.2019.dc64i46r')

st.markdown('')

st.markdown('This is a research preview of a convolution neural network deep learning app meant to deliver real-time predictions classifiying   \nhuman white blood cells microscopic images as healthy or malignant (acute lymphoblastic leukaemia)')

st.markdown('***')

st.markdown('')


# create multiselect widget for choosing an image
st.markdown('Please select an image to be classified (1800 available):')

img_number = [k for k in list(range(1, 1801))]
selected_img_number = st.multiselect('', img_number)

# func to classify demo images
def predict(img_sample : int):
    """
    Make a single image prediction
    Assumes `img_sample' is provided as an integer index by the user
    """

    X_pred = load_test_img_prelim(img_sample)

    assert model is not None

    X_pred = np.expand_dims(X_pred, 0)
    y_pred = model.predict(np.array(X_pred))

    y_pred = (y_pred > 0.5).astype(int)

    return y_pred

# classifying demo images
if selected_img_number:
    j = selected_img_number[-1]
    j=j-1

    # show img selected by the user
    im = show_img_prelim(j)
    st.image(im, width=200, caption=f'Human white blood cell #{j+1}')

    # predict chosen image

    ### with api
    # leukemic_api_url = 'http://127.0.0.1:8000/predict'
    # params = {'img_sample':selected_img_number[-1]}
    # response = requests.get(leukemic_api_url, params=params)

    # prediction = response.json()

    # predicted_class = prediction['The sample cell is']


    ### without api
    predicted_class = predict(selected_img_number[-1])

    if predicted_class == 0:
        st.write('Healthy')
    else:
        st.write('Malignant')


# classifying images uploaded by the user
st.markdown('')

st.markdown('***')

st.markdown('')

st.markdown('Or upload an image from your browser:')

uploaded_file = st.file_uploader("", type=["jpg", "jpeg", "png", "bmp"])

if uploaded_file is not None:
    file_bytes = np.asarray(bytearray(uploaded_file.read()), dtype=np.uint8)
    image_u = cv.imdecode(file_bytes, cv.IMREAD_COLOR)
    st.image(image_u, width=200, channels="BGR", caption='uploaded image')


    # predict uploaded image

    u = np.resize((image_u), (450, 450, 3))
    resized_u = np.array(u)

    X_pred = np.expand_dims(resized_u, 0)
    y_pred = model.predict(np.array(X_pred))

    predicted_class_u = (y_pred > 0.5).astype(int)

    if predicted_class_u == 0:
        st.write('Healthy')
    else:
        st.write('Malignant')


st.markdown('')

st.markdown('')

st.markdown('-The model works best if your image shows an individual white blood cell well defined from a black background-')
