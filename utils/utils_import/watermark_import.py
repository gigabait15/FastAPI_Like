from pathlib import Path
from PIL import Image
import asyncio
from concurrent.futures import ThreadPoolExecutor
from fastapi import UploadFile

PROJECT_ROOT = Path(__file__).parent.parent / 'users/avatars/'
watermark_image_path = PROJECT_ROOT / 'watermark.png'
