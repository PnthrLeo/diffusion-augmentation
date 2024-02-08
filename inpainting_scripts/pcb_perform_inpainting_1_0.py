import json
from pathlib import Path
from urllib import request
import argparse


def queue_prompt(prompt):
    p = {"prompt": prompt}
    data = json.dumps(p).encode('utf-8')
    req =  request.Request("http://127.0.0.1:8188/prompt", data=data)
    request.urlopen(req)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Perform inpainting on PCB images')
    parser.add_argument('--dataset_path', type=str, required=True, help='Path to the PCB dataset')
    parser.add_argument('--inpainting_output_path', type=str, required=True, help='Path to the inpainting output')
    parser.add_argument('--inp_img_per_orig_img', type=int, required=True, help='Number of inpainted images per image required (should be divisible by 3)', default=6)
    args = parser.parse_args()
    
    pipeline_path = 'batch_inpainting_SDXL_refiner_controlnet-v1.2-p-ready-no-depth-pcb-api.json'
    images_paths = [f'{args.dataset_path}/train/images']
    masks_paths = [f'{args.dataset_path}/train/masks']
    inpainting_paths = [f'{args.inpainting_output_path}/train/images']

    # verify that paths exist
    for path in images_paths:
        assert Path(path).exists(), f'Path {path} does not exist'
    for path in masks_paths:
        assert Path(path).exists(), f'Path {path} does not exist'
    
    # create directories if they do not exist
    for path in inpainting_paths:
        Path(path).mkdir(parents=True, exist_ok=True)

    for part_idx in range(len(images_paths)):
        number_of_inpainted_images_per_image_required = args.inp_img_per_orig_img
        inpainted_images_counter = 0

        with open(f'/app/comfyUI/workflows/{pipeline_path}') as f:
            pipeline = json.load(f)

        # set images loader path
        pipeline['49']['inputs']['path'] = images_paths[part_idx]
        # set masks loader path
        pipeline['55']['inputs']['path'] = masks_paths[part_idx]
        # set inpainting images saver path
        pipeline['72']['inputs']['path'] = inpainting_paths[part_idx]

        # depth conditioning strength
        pipeline['12']['inputs']['strength'] = 1
        # canny conditioning strength
        pipeline['88']['inputs']['strength'] = 1


        positive_prompts = ['a photo of a green printed circuit board, (((ultrarealistic))), hdr, 8k',
                            'a photo of a blue printed circuit board, (((ultrarealistic))), hdr, 8k',
                            'a photo of a red printed circuit board, (((ultrarealistic))), hdr, 8k']
        negative_prompt = 'comics, cartoon, blur, (((text)))'
        number_of_inpainted_images_per_image_required /= len(positive_prompts)


        while inpainted_images_counter < number_of_inpainted_images_per_image_required:
            # set seed
            pipeline['98']['inputs']['seed'] = inpainted_images_counter
            inpainted_images_counter += 1
            
            for idx, prompt in enumerate(positive_prompts):
                # set positive prompt
                pipeline['104']['inputs']['text'] = prompt
                # set negative prompt
                pipeline['106']['inputs']['text'] = negative_prompt

                for jdx in range(len(list(Path(images_paths[part_idx]).glob('*.jpg')))):
                    pipeline['49']['inputs']['index'] = jdx
                    pipeline['55']['inputs']['index'] = jdx
                    pipeline['127']['inputs']['text'] = str(inpainted_images_counter)
                    pipeline['128']['inputs']['text'] = str(idx)
                    queue_prompt(pipeline)
