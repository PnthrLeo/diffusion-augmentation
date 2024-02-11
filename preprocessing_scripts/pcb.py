import numpy as np
import cv2
from pathlib import Path
import argparse


train_folder = Path('./train')
val_folder = Path('./valid')
test_folder = Path('./test')


def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]


def convert_yolo_annotations2masks(folder):
    images_folder = folder / 'images'
    labels_folder = folder / 'labels'
    masks_folder = folder / 'masks'
    
    masks_folder.mkdir(exist_ok=True)
    
    for label_file in labels_folder.glob('*.txt'):
        image = cv2.imread(str(images_folder / (label_file.stem + '.jpg')))
        height, width, _ = image.shape
        
        mask = np.zeros((height, width), dtype=np.uint8)
        
        polygons = []
        with open(str(label_file), 'r') as file:
            for line in file:
                values = line.split()[1:]
                values = [float(value) for value in values]
                polygon = list(chunks(values, 2))
                polygon = [(int(x * width), int(y * height)) for x, y in polygon]
                polygons.append(polygon)
        
        for polygon in polygons:
            polygon = np.array(polygon, dtype=np.int32)
            cv2.fillPoly(mask, [polygon], 255)
    
        cv2.imwrite(str(masks_folder / (label_file.stem + '.png')), mask)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--orig_data_path', type=str, help='Path to the original data')
    args = parser.parse_args()
    
    orig_data = Path(args.orig_data_path)
    train_folder = orig_data / 'train'
    val_folder = orig_data / 'valid'

    convert_yolo_annotations2masks(train_folder)
    convert_yolo_annotations2masks(val_folder)
