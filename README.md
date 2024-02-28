
# Image Augmentation for Object Detection and Segmentation with Diffusion Models

**Authors**: [Leon Useinov](https://github.com/PnthrLeo)\,
Valeria Efimova\,
Sergey Muravyov

![image](https://github.com/PnthrLeo/big-data-2023-part4/assets/29786176/f2050fbc-56a0-4588-a455-6f458d0938c4)

We propose an image augmentation approach for object detection and segmentation tasks based on the [Stable Diffusion XL](https://arxiv.org/abs/2307.01952) diffusion model. This repository contains code to verify our research. The following things are implemented:

- [x] Preprocessing scripts for PCB Defects and Potholes datasets. 
- [x] Inpainting (augmentation) scripts for MVTec AD Bottle, PCB Defects and Potholes datasets.
- [x] Postprocessing scripts for MVTec AD Bottle, PCB Defects and Potholes datasets.
- [ ] YOLOv8n training scripts.




## Requirements
Docker and Docker Compose.


### Installation
```bash
    git clone https://github.com/PnthrLeo/diffusion-augmentation.git
    cd diffusion-augmentation
    docker compose build
```


### Models
Download:
1. [SDXL Base](https://huggingface.co/stabilityai/stable-diffusion-xl-base-1.0/resolve/main/sd_xl_base_1.0.safetensors?download=true) (put it in `models/comfyUI_models/checkpoints/sd_xl_base_1.0.safetensors`)
2. [SDXL Refiner](https://huggingface.co/stabilityai/stable-diffusion-xl-refiner-1.0/resolve/main/sd_xl_refiner_1.0.safetensors?download=true) (put it in `models/comfyUI_models/checkpoints/sd_xl_refiner_1.0.safetensors`)
3. [ControlNet Depth for SDXL](https://huggingface.co/diffusers/controlnet-depth-sdxl-1.0/resolve/main/diffusion_pytorch_model.fp16.safetensors?download=true) (put it in `models/comfyUI_models/controlnet/controlnet-depth-sdxl-1.0.safetensors`)
4. [ControlNet Canny for SDXL](https://huggingface.co/diffusers/controlnet-canny-sdxl-1.0/resolve/main/diffusion_pytorch_model.fp16.safetensors?download=true) (put it in `models/comfyUI_models/controlnet/controlnet-canny-sdxl-1.0.safetensors`)
5. [CLIP Vision](https://huggingface.co/laion/CLIP-ViT-H-14-laion2B-s32B-b79K/resolve/main/model.safetensors?download=true) (put it in `models/comfyUI_models/clip_vision/CLIP-ViT-H-14.safetensors`)
6. [IP-Adapter](https://huggingface.co/h94/IP-Adapter/resolve/main/sdxl_models/ip-adapter-plus_sdxl_vit-h.safetensors?download=true) (put it in `models/IPAdapter_models/ip-adapter-plus_sdxl_vit-h.safetensors`)


### Datasets
Download:
1. [MVTec AD](https://www.kaggle.com/datasets/thtuan/mvtecad-mvtec-anomaly-detection/download?datasetVersionNumber=2) dataset from Kaggle (put archive contents in `data/mvtec/orig/`)
2. [PCB Defects](https://universe.roboflow.com/diplom-qz7q6/defects-2q87r/dataset/16/download) dataset from Roboflow in YOLOv8 format (put archive contents in `data/pcb/orig`)
3. [Potholes](https://universe.roboflow.com/final-project-iic7d/pothole-detection-system-new/dataset/1/download) dataset from Roboflow in YOLOv8 format (put archive contents in `data/pothole/orig`)
## Usage
First, run preprocessing scripts (only for PCB Defects and Potholes datasets):
```bash
    # Example of running preprocessing for PCB Defects dataset

    # Example of running preprocessing for Potholes dataset
    
```

Second, run inpainting scripts:
```bash
    # Example of running inpainting (1, 2, 3 versions) for MVTec AD Bottle dataset

    # Example of running inpainting (1, 2, 3 versions) for PCB Defects dataset

    # Example of running inpainting (1, 2, 3 versions) for Potholes dataset

```

Third, run postprocessing scripts:
```bash
    # Example of running postprocessing for MVTec AD Bottle dataset

    # Example of running postprocessing for PCB Defects dataset

    # Example of running postprocessing for Potholes dataset

```
## Acknowledgements

The research was supported by the ITMO University, project 623097 ”Development of libraries containing perspective machine learning methods”.
