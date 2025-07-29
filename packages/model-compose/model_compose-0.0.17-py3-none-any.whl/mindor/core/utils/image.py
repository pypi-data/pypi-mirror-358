from typing import Optional
from PIL import Image as PILImage
import io, base64

def load_image_from_base64(value: str) -> Optional[PILImage.Image]:
    try:
        return PILImage.open(io.BytesIO(base64.b64decode(value)))
    except:
        return None
