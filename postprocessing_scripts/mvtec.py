from pathlib import Path
import argparse
import shutil
from imantics import Mask
import cv2


def remove_redundant_spaces(inpainted_data_folder):
    categories = ['broken_large', 'broken_small', 'contamination']
    bottle_folder = inpainted_data_folder / 'bottle'
    
    for category in categories:
        category_folder = bottle_folder / category
        image_paths = list(category_folder.glob('*.png'))
        for image_path in image_paths:
            image_path.rename(str(image_path).replace(' ', ''))


def make_cvs(orig_data, inpainted_data_folder, cvs_folder, inp_img_per_orig_img=15, not_inpainted_cvs_folder=None):
    orig_data = orig_data / 'bottle'
    inpainted_data_folder = inpainted_data_folder / 'bottle'
    cvs_folder = cvs_folder / 'bottle'
    not_inpainted_cvs_folder = not_inpainted_cvs_folder / 'bottle' if not_inpainted_cvs_folder is not None else None
    
    categories = ['broken_large', 'broken_small', 'contamination']
    cv_test_intervals = [(0, 5), (5, 10), (10, 15), (15, 22)]


    for cv_idx, interval in enumerate(cv_test_intervals):
        cv_folder = cvs_folder / f'cv{cv_idx}'
        cv_folder.mkdir(exist_ok=True)
        val_folder = cv_folder / 'images' / 'val'
        val_folder.mkdir(exist_ok=True, parents=True)
        train_folder = cv_folder / 'images' / 'train'
        train_folder.mkdir(exist_ok=True, parents=True)
        
        for category in categories:
            min_test_index, max_test_index = interval
            orig_category_folder = orig_data / 'test' / category
            inpainted_category_folder = inpainted_data_folder / category
            orig_images = list(orig_category_folder.glob('*.png'))
            inpainted_images = list(inpainted_category_folder.glob('*.png'))
            max_test_index = min(max_test_index, len(orig_images))
            
            for image in orig_images:
                if int(image.stem.split('-')[0]) in range(min_test_index, max_test_index):
                    shutil.copy(image, val_folder / f'{image.stem}-{category}{image.suffix}')
                else:
                    shutil.copy(image, train_folder / f'{image.stem}-{category}{image.suffix}')
            
            for image in inpainted_images:
                if int(image.stem.split('-')[0]) in range(min_test_index, max_test_index):
                    continue
                else:
                    shutil.copy(image, train_folder / f'{image.stem}-{category}{image.suffix}')
        
        good_train_folder = orig_data / 'train' / 'good'
        good_train_images = list(good_train_folder.glob('*.png'))
        for image in good_train_images:
            shutil.copy(image, train_folder / f'{image.stem}-good{image.suffix}')
        
        good_test_folder = orig_data / 'test' / 'good'
        good_test_images = list(good_test_folder.glob('*.png'))
        for image in good_test_images:
            shutil.copy(image, val_folder / f'{image.stem}-good{image.suffix}')        

    if not_inpainted_cvs_folder is not None:
        for cv_idx, interval in enumerate(cv_test_intervals):
            cv_folder = not_inpainted_cvs_folder / f'cv{cv_idx}'
            cv_folder.mkdir(exist_ok=True)
            val_folder = cv_folder / 'images' / 'val'
            val_folder.mkdir(exist_ok=True, parents=True)
            train_folder = cv_folder / 'images' / 'train'
            train_folder.mkdir(exist_ok=True, parents=True)
            
            for category in categories:
                min_test_index, max_test_index = interval
                orig_category_folder = orig_data / 'test' / category
                orig_images = list(orig_category_folder.glob('*.png'))
                max_test_index = min(max_test_index, len(orig_images))
                
                for image in orig_images:
                    if int(image.stem.split('-')[0]) in range(min_test_index, max_test_index):
                        shutil.copy(image, val_folder / f'{image.stem}-{category}{image.suffix}')
                    else:
                        for i in range(inp_img_per_orig_img + 1):
                            shutil.copy(image, train_folder / f'{image.stem}-{i}-{category}{image.suffix}')
                
            good_train_folder = orig_data / 'train' / 'good'
            good_train_images = list(good_train_folder.glob('*.png'))
            for image in good_train_images:
                shutil.copy(image, train_folder / f'{image.stem}-good{image.suffix}')
            
            good_test_folder = orig_data / 'test' / 'good'
            good_test_images = list(good_test_folder.glob('*.png'))
            for image in good_test_images:
                shutil.copy(image, val_folder / f'{image.stem}-good{image.suffix}')
    
    
def gen_yolo_labels(orig_data, image_folder, label_folder):
    gt_folder = orig_data / 'ground_truth'
    categories = {'broken_large': 0, 'broken_small': 1, 'contamination': 2, 'good': 3}
    
    for image_path in image_folder.glob('*.png'):        
        category = ''
        for cat in categories.keys():
            if cat in image_path.stem:
                category = cat
                break
        
        if category == 'good':
            # save empty txt file
            with open(label_folder / f'{image_path.stem}.txt', 'w') as f:
                pass
        else:
            mask = cv2.imread(str(gt_folder / category / f'{image_path.stem.split("-")[0]}-mask.png'), cv2.IMREAD_GRAYSCALE)
            polygons = Mask(mask).polygons()
            with open(label_folder / f'{image_path.stem}.txt', 'w') as f:
                for point_list in polygons.points:
                    f.write(f'{categories[category]}')
                    for point in point_list:
                        f.write(f' {point[0] / mask.shape[1]} {point[1] / mask.shape[0]}')
                    f.write('\n')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--orig_data_path', type=str, help='Path to the original data')
    parser.add_argument('--inpainted_data_path', type=str, help='Path to the inpainted data')
    parser.add_argument('--final_dataset_path', type=str, help='Path to final dataset folder')
    parser.add_argument('--inp_img_per_orig_img', type=int, help='Number of inpainted images per original image', default=15)
    parser.add_argument('--not_inpainted_data_path', type=str, help='Path to the not inpainted data', default='/app/None')
    args = parser.parse_args()
    
    orig_data = Path(args.orig_data_path)
    inpainted_data_folder = Path(args.inpainted_data_path)
    cvs_folder = Path(args.final_dataset_path)
    inp_img_per_orig_img = args.inp_img_per_orig_img
    if args.not_inpainted_data_path != '/app/None':
        not_inpainted_cvs_folder = Path(args.not_inpainted_data_path)
    else:
        not_inpainted_cvs_folder = None
    
    remove_redundant_spaces(inpainted_data_folder)
    make_cvs(orig_data, inpainted_data_folder, cvs_folder, inp_img_per_orig_img, not_inpainted_cvs_folder)
    
    for cv_idx in range(4):
        cv_folder = cvs_folder / f'cv{cv_idx}'
        train_images_folder = cv_folder / 'images' / 'train'
        val_images_folder = cv_folder / 'images' / 'val'
        
        train_labels_folder = cv_folder / 'labels' / 'train'
        val_labels_folder = cv_folder / 'labels' / 'val'
        train_labels_folder.mkdir(exist_ok=True, parents=True)
        val_labels_folder.mkdir(exist_ok=True, parents=True)
        
        gen_yolo_labels(train_images_folder, train_labels_folder)
        gen_yolo_labels(val_images_folder, val_labels_folder)

    if not_inpainted_cvs_folder is not None:
        for cv_idx in range(4):
            cv_folder = not_inpainted_cvs_folder / f'cv{cv_idx}'
            train_images_folder = cv_folder / 'images' / 'train'
            val_images_folder = cv_folder / 'images' / 'val'
            
            train_labels_folder = cv_folder / 'labels' / 'train'
            val_labels_folder = cv_folder / 'labels' / 'val'
            train_labels_folder.mkdir(exist_ok=True, parents=True)
            val_labels_folder.mkdir(exist_ok=True, parents=True)
            
            gen_yolo_labels(train_images_folder, train_labels_folder)
            gen_yolo_labels(val_images_folder, val_labels_folder)
    