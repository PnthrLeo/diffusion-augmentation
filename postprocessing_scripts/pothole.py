import shutil
import argparse
from pathlib import Path


def remove_redundant_spaces(inpainted_data_folder):
    images_folder = inpainted_data_folder / 'train' / 'images'
    
    image_paths = list(images_folder.glob('*.png'))
    for image_path in image_paths:
        image_path.rename(str(image_path).replace(' ', ''))


def make_dataset_folders(orig_data, inpainted_data_folder, dataset_folder, inp_img_per_orig_img=6, not_inpainted_dataset_folder=None):
    inpainted_images_folder = inpainted_data_folder / 'train' / 'images'
    original_train_images_folder = orig_data / 'train' / 'images'
    original_val_images_folder = orig_data / 'valid' / 'images'
    
    images_folder = dataset_folder / 'images'
    train_images_folder = images_folder / 'train'
    val_images_folder = images_folder / 'val'
    
    train_images_folder.mkdir(exist_ok=True, parents=True)
    val_images_folder.mkdir(exist_ok=True, parents=True)
    
    inpainted_images_paths = list(inpainted_images_folder.glob('*.png'))
    original_train_images_paths = list(original_train_images_folder.glob('*.jpg'))
    original_val_images_paths = list(original_val_images_folder.glob('*.jpg'))
    
    for image_path in inpainted_images_paths:
        shutil.copy(image_path, train_images_folder / image_path.name)
    
    for image_path in original_train_images_paths:
        shutil.copy(image_path, train_images_folder / image_path.name)
    
    for image_path in original_val_images_paths:
        shutil.copy(image_path, val_images_folder / image_path.name)
    
    if not_inpainted_dataset_folder is not None:
        not_inpainted_images_folder = not_inpainted_dataset_folder / 'images'
        train_images_folder = not_inpainted_images_folder / 'train'
        val_images_folder = not_inpainted_images_folder / 'val'
        
        train_images_folder.mkdir(exist_ok=True, parents=True)
        val_images_folder.mkdir(exist_ok=True, parents=True)
        
        for i in range(inp_img_per_orig_img + 1):
            for image_path in original_train_images_paths:
                shutil.copy(image_path,  train_images_folder / f'{image_path.stem}-{i}{image_path.suffix}')
        
        for image_path in original_val_images_paths:
            shutil.copy(image_path, val_images_folder / image_path.name)


def add_labels(orig_data, dataset_folder):
    images_folder = dataset_folder / 'images'
    labels_folder = dataset_folder / 'labels'
    
    original_train_labels_folder = orig_data / 'train' / 'labels'
    train_labels_folder = labels_folder / 'train'
    train_labels_folder.mkdir(exist_ok=True, parents=True)
    
    train_images_paths_jpg = list((images_folder / 'train').glob('*.jpg'))
    train_images_paths_png = list((images_folder / 'train').glob('*.png'))
    train_images_paths = train_images_paths_png + train_images_paths_jpg
    
    for image_path in train_images_paths:
        label_name = image_path.stem.split('-')[0] + '.txt'
        label = original_train_labels_folder / label_name
        shutil.copy(label, train_labels_folder / f'{image_path.stem}.txt')
    
    original_val_labels_folder = orig_data / 'valid' / 'labels'
    val_labels_folder = labels_folder / 'val'
    val_labels_folder.mkdir(exist_ok=True, parents=True)
    
    val_images_paths_jpg = list((images_folder / 'val').glob('*.jpg'))
    val_images_paths_png = list((images_folder / 'val').glob('*.png'))
    val_images_paths = val_images_paths_png + val_images_paths_jpg
    
    for image_path in val_images_paths:
        label_name = image_path.stem + '.txt'
        label = original_val_labels_folder / label_name
        shutil.copy(label, val_labels_folder / f'{image_path.stem}.txt')


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser = argparse.ArgumentParser()
    parser.add_argument('--orig_data_path', type=str, help='Path to the original data')
    parser.add_argument('--inpainted_data_path', type=str, help='Path to the inpainted data')
    parser.add_argument('--final_dataset_path', type=str, help='Path to final dataset folder')
    parser.add_argument('--inp_img_per_orig_img', type=int, help='Number of inpainted images per original image', default=6)
    parser.add_argument('--not_inpainted_data_path', type=str, help='Path to the not inpainted data', default='/app/None')
    args = parser.parse_args()
    
    orig_data = Path(args.orig_data_path)
    inpainted_data_folder = Path(args.inpainted_data_path)
    dataset_folder = Path(args.final_dataset_path)
    inp_img_per_orig_img = args.inp_img_per_orig_img
    if args.not_inpainted_data_path != '/app/None':
        not_inpainted_dataset_folder = Path(args.not_inpainted_data_path)
    else:
        not_inpainted_dataset_folder = None
    
    remove_redundant_spaces(inpainted_data_folder)
    make_dataset_folders(orig_data, inpainted_data_folder, dataset_folder, inp_img_per_orig_img, not_inpainted_dataset_folder)
    add_labels(orig_data, dataset_folder)
    add_labels(orig_data, not_inpainted_dataset_folder)
