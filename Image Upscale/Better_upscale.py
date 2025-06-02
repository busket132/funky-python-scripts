from basicsr.archs.rrdbnet_arch import RRDBNet
from realesrgan import RealESRGANer
import cv2
import os
import torch

def upscale_image(input_path, img_name, output_path, output_name, scale=4):
    try:
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Входной файл не найден: {input_path}")

        
        os.makedirs('weights', exist_ok=True)

        
        model_path = 'weights/RealESRGAN_x4plus.pth'

        
        if not os.path.exists(model_path):
            print("Загрузка весов модели...")
            torch.hub.download_url_to_file(
                'https://github.com/xinntao/Real-ESRGAN/releases/download/v0.1.0/RealESRGAN_x4plus.pth',
                model_path
            )

       
        model = RRDBNet(num_in_ch=3, num_out_ch=3, num_feat=64, num_block=23, num_grow_ch=32, scale=1)

        
        device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        print(f"Используется устройство: {device}")

        
        upsampler = RealESRGANer(
            scale=scale,
            model_path=model_path,  
            model=model,
            tile=400,  
            tile_pad=10,
            pre_pad=0,
            half=device.type == 'cuda'  
        )

        
        print("Чтение изображения...")
        img = cv2.imread(input_path+"/"+img_name, cv2.IMREAD_UNCHANGED)
        if img is None:
            raise ValueError(f"Не удалось прочитать изображение: {input_path}")

        
        print("Обработка изображения...")
        output, _ = upsampler.enhance(img, outscale=scale)

       
        os.makedirs(os.path.dirname(output_path+"/"+output_name), exist_ok=True)

        
        print("Сохранение результата...")
        cv2.imwrite(output_path+"/"+output_name, output)
        print(f"Изображение успешно сохранено в {output_path+"/"+output_name}")

    except Exception as e:
        print(f"Произошла ошибка: {str(e)}")
        raise

inputPath = input("Введите путь до папки с изображениями: ")
inputPath = inputPath.replace("\\", "/")

inputImage = input("Введите название изображения: ")
inputImage = inputImage.replace("\\", "/")

inputUpscaleImgPath = input("Введите путь до папки для сохранения изображений: ")

inputUpscaleimg = input("Введите желаемое название конечного файла: ")

inputUpscaleScale = input("Введите во сколько раз увеличить изображение: ")
# Пример использования
upscale_image(inputPath, inputImage,
            inputUpscaleImgPath,
            inputUpscaleimg, 
            int(inputUpscaleScale))
