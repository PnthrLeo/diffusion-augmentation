import numpy as np
import cv2
import os
import cv2
from .cv_ox_det import inference_detector as inference_yolox
from .yolo_nas import inference_detector as inference_yolo_nas
from .cv_ox_pose import inference_pose
from typing import List, Optional
from .types import PoseResult, BodyResult, Keypoint
from timeit import default_timer
from controlnet_aux.dwpose.util import guess_onnx_input_shape_dtype
import json

def drawBetweenKeypoints(pose_img, keypoints, indexes, color, scaleFactor):
    ind0 = indexes[0] - 1
    ind1 = indexes[1] - 1
    
    point1 = (keypoints[ind0][0], keypoints[ind0][1])
    point2 = (keypoints[ind1][0], keypoints[ind1][1])

    thickness = int(5 // scaleFactor)


    cv2.line(pose_img, (int(point1[0]), int(point1[1])), (int(point2[0]), int(point2[1])), color, thickness)


def drawBetweenKeypointsList(pose_img, keypoints, keypointPairsList, colorsList, scaleFactor):
    for ind, keypointPair in enumerate(keypointPairsList):
        drawBetweenKeypoints(pose_img, keypoints, keypointPair, colorsList[ind], scaleFactor)

def drawBetweenSetofKeypointLists(pose_img, keypoints_set, keypointPairsList, colorsList, scaleFactor):
    for keypoints in keypoints_set:
        drawBetweenKeypointsList(pose_img, keypoints, keypointPairsList, colorsList, scaleFactor)


def padImg(img, size, blackBorder=True):
    left, right, top, bottom = 0, 0, 0, 0

    # pad x
    if img.shape[1] < size[1]:
        sidePadding = int((size[1] - img.shape[1]) // 2)
        left = sidePadding
        right = sidePadding

        # pad extra on right if padding needed is an odd number
        if img.shape[1] % 2 == 1:
            right += 1

    # pad y
    if img.shape[0] < size[0]:
        topBottomPadding = int((size[0] - img.shape[0]) // 2)
        top = topBottomPadding
        bottom = topBottomPadding
        
        # pad extra on bottom if padding needed is an odd number
        if img.shape[0] % 2 == 1:
            bottom += 1

    if blackBorder:
        paddedImg = cv2.copyMakeBorder(src=img, top=top, bottom=bottom, left=left, right=right, borderType=cv2.BORDER_CONSTANT, value=(0,0,0))
    else:
        paddedImg = cv2.copyMakeBorder(src=img, top=top, bottom=bottom, left=left, right=right, borderType=cv2.BORDER_REPLICATE)

    return paddedImg

def smartCrop(img, size, center):

    width = img.shape[1]
    height = img.shape[0]
    xSize = size[1]
    ySize = size[0]
    xCenter = center[0]
    yCenter = center[1]

    if img.shape[0] > size[0] or img.shape[1] > size[1]:


        leftMargin = xCenter - xSize//2
        rightMargin = xCenter + xSize//2
        upMargin = yCenter - ySize//2
        downMargin = yCenter + ySize//2


        if(leftMargin < 0):
            xCenter += (-leftMargin)
        if(rightMargin > width):
            xCenter -= (rightMargin - width)

        if(upMargin < 0):
            yCenter -= -upMargin
        if(downMargin > height):
            yCenter -= (downMargin - height)


        img = cv2.getRectSubPix(img, size, (xCenter, yCenter))



    return img



def calculateScaleFactor(img, size, poseSpanX, poseSpanY):

    poseSpanX = max(poseSpanX, size[0])

    scaleFactorX = 1


    if poseSpanX > size[0]:
        scaleFactorX = size[0] / poseSpanX

    scaleFactorY = 1
    if poseSpanY > size[1]:
        scaleFactorY = size[1] / poseSpanY

    scaleFactor = min(scaleFactorX, scaleFactorY)


    return scaleFactor



def scaleImg(img, size, poseSpanX, poseSpanY, scaleFactor):
    scaledImg = img

    scaledImg = cv2.resize(img, (0, 0), fx=scaleFactor, fy=scaleFactor) 

    return scaledImg, scaleFactor

ONNX_PROVIDERS = ["CUDAExecutionProvider", "DirectMLExecutionProvider", "OpenVINOExecutionProvider", "ROCMExecutionProvider"]
SUPPORT_PROVIDERS = []
def check_ort_gpu():
    try:
        import onnxruntime as ort
        for provider in ONNX_PROVIDERS:
            if provider in ort.get_available_providers():
                SUPPORT_PROVIDERS.append(provider)
                return True
        return False
    except:
        return False

#Global caching as the startup of onnxruntime is a bit slow
ort_session_det, ort_session_pose = None, None
cached_onnx_det_name, cached_onnx_pose_name = '', ''

class AnimalPoseImage:
    def __init__(self, onnx_det: str, onnx_pose: str):
        global ort_session_det, ort_session_pose, cached_onnx_det_name, cached_onnx_pose_name
        if check_ort_gpu():
            import onnxruntime as ort
            pose_filename = os.path.basename(onnx_pose)
            if pose_filename != cached_onnx_pose_name and ort_session_pose is None:
                print(f"AnimalPose: Caching pose session {pose_filename}...")
                SUPPORT_PROVIDERS.append('CPUExecutionProvider')
                ort_session_pose = ort.InferenceSession(onnx_pose, providers=SUPPORT_PROVIDERS)
                cached_onnx_pose_name = pose_filename
            
            det_filename = os.path.basename(onnx_det)
            if det_filename != cached_onnx_det_name or ort_session_det is None:
                print(f"AnimalPose: Caching bbox detection session {det_filename}...")
                ort_session_det = ort.InferenceSession(onnx_det, providers=SUPPORT_PROVIDERS)
                cached_onnx_det_name = det_filename

            self.session_det = ort_session_det
            self.session_pose = ort_session_pose
            return
        
        cached_onnx_pose_name = os.path.basename(onnx_pose)
        cached_onnx_det_name = os.path.basename(onnx_det)
        # Always loads to CPU to avoid building OpenCV.
        device = 'cpu'
        backend = cv2.dnn.DNN_BACKEND_OPENCV if device == 'cpu' else cv2.dnn.DNN_BACKEND_CUDA
        # You need to manually build OpenCV through cmake to work with your GPU.
        providers = cv2.dnn.DNN_TARGET_CPU if device == 'cpu' else cv2.dnn.DNN_TARGET_CUDA

        self.session_det = cv2.dnn.readNetFromONNX(onnx_det)
        self.session_det.setPreferableBackend(backend)
        self.session_det.setPreferableTarget(providers)

        self.session_pose = cv2.dnn.readNetFromONNX(onnx_pose)
        self.session_pose.setPreferableBackend(backend)
        self.session_pose.setPreferableTarget(providers)
    
    def __call__(self, oriImg) -> Optional[np.ndarray]:
        pose_input_size, pose_dtype = guess_onnx_input_shape_dtype(cached_onnx_pose_name)
        inference_detector = inference_yolox if "yolox" in cached_onnx_det_name else inference_yolo_nas
        detect_classes = list(range(14, 23 + 1)) #https://github.com/ultralytics/ultralytics/blob/main/ultralytics/cfg/datasets/coco.yaml

        det_start = default_timer()
        #FP16 and INT8 YOLO NAS accept uint8 input
        det_result = inference_detector(self.session_det, oriImg, detect_classes=detect_classes, dtype=np.float32 if "yolox" in cached_onnx_det_name else np.uint8)
        print(f"AnimalPose: Bbox {((default_timer() - det_start) * 1000):.2f}ms")
        if det_result is None:
            json_output = json.dumps({
                'version': 'ap10k',
                'animals': [],
                'canvas_height': oriImg.shape[0],
                'canvas_width': oriImg.shape[1]
            }, indent=4)
            return np.zeros_like(oriImg), json_output
        
        pose_start = default_timer()
        keypoint_sets, scores = inference_pose(self.session_pose, det_result, oriImg, pose_input_size, pose_dtype)
        print(f"AnimalPose: Pose {((default_timer() - pose_start) * 1000):.2f}ms on {det_result.shape[0]} animals\n")

        animal_kps_scores = []
        pose_img = np.zeros((oriImg.shape[0], oriImg.shape[1], 3), dtype = np.uint8)
        for (idx, keypoints) in enumerate(keypoint_sets):
            # don't use keypoints that go outside the frame in calculations for the center
            interorKeypoints = keypoints[((keypoints[:,0] > 0) & (keypoints[:,0] < oriImg.shape[1])) & ((keypoints[:,1] > 0) & (keypoints[:,1] < oriImg.shape[0]))]

            xVals = interorKeypoints[:,0]
            yVals = interorKeypoints[:,1]

            minX = np.amin(xVals)
            minY = np.amin(yVals)
            maxX = np.amax(xVals)
            maxY = np.amax(yVals)

            poseSpanX = maxX - minX
            poseSpanY = maxY - minY

            # find mean center

            xSum = np.sum(xVals)
            ySum = np.sum(yVals)

            xCenter = xSum // xVals.shape[0]
            yCenter = ySum // yVals.shape[0]
            center_of_keypoints = (xCenter,yCenter)

            # order of the keypoints for AP10k and a standardized list of colors for limbs
            keypointPairsList = [(1,2), (2,3), (1,3), (3,4), (4,9), (9,10), (10,11), (4,6), (6,7), (7,8), (4,5), (5,15), (15,16), (16,17), (5,12), (12,13), (13,14)]
            colorsList = [(255,255,255), (100,255,100), (150,255,255), (100,50,255), (50,150,200), (0,255,255), (0,150,0), (0,0,255), (0,0,150), (255,50,255), (255,0,255), (255,0,0), (150,0,0), (255,255,100), (0,150,0), (255,255,0), (150,150,150)] # 16 colors needed

            drawBetweenKeypointsList(pose_img, keypoints, keypointPairsList, colorsList, scaleFactor=1.0)
            score = scores[idx, ..., None]
            score[score > 1.0] = 1.0
            score[score < 0.0] = 0.0
            animal_kps_scores.append(np.concatenate((keypoints, score), axis=-1))
        
        json_output = json.dumps({
            'version': 'ap10k',
            'animals': [keypoints.tolist() for keypoints in animal_kps_scores],
            'canvas_height': oriImg.shape[0],
            'canvas_width': oriImg.shape[1]
        }, indent=4)
        return pose_img, json_output