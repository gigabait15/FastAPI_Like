from utils.utils_import.watermark_import import *

async def watermark_photo(input_image: UploadFile, output_image_name: str):
    loop = asyncio.get_running_loop()
    output_image_path = PROJECT_ROOT / output_image_name

    with ThreadPoolExecutor() as pool:
        base_image = Image.open(input_image.file)
        watermark = await loop.run_in_executor(pool, Image.open, watermark_image_path)

        # Наложение водяного знака и сохранение
        base_image.paste(watermark, (0, 0), watermark)
        await loop.run_in_executor(pool, base_image.save, PROJECT_ROOT / output_image_path)

    return str(output_image_path)