FROM nvcr.io/nvidia/pytorch:24.01-py3

WORKDIR /app
COPY ./comfyUI /app/comfyUI

RUN pip install -r /app/comfyUI/requirements.txt
RUN pip install optimum \
    && pip install onnxruntime \
    && pip install opencv-python==4.6.0.66 \
    && pip install opencv-python-headless==4.6.0.66 \
    && pip install timm \
    && pip install Pillow==9.5.0
    && pip install imantics

COPY ./preprocessing_scripts /app/preprocessing_scripts
COPY ./inpainting_scripts /app/inpainting_scripts
COPY ./postprocessing_scripts /app/postprocessing_scripts
