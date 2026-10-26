"""Shared image preparation without upscaling or modifying source images."""
import base64
import io
from dataclasses import dataclass

from PIL import Image, ImageOps

try:
    from pillow_heif import register_heif_opener
except ImportError:
    register_heif_opener = None
if register_heif_opener is not None:
    register_heif_opener()


@dataclass(frozen=True)
class ImagePolicy:
    long_edge: int = 1568
    jpeg_quality: int = 92
    lower_crop: float | None = None
    draft_decode: bool = False

    def __post_init__(self):
        if type(self.long_edge) is not int or self.long_edge <= 0:
            raise ValueError('long_edge must be a positive integer.')
        if type(self.jpeg_quality) is not int or not 1 <= self.jpeg_quality <= 95:
            raise ValueError('jpeg_quality must be between 1 and 95.')
        if self.lower_crop is not None and not 0 < self.lower_crop < 1:
            raise ValueError('lower_crop must be strictly between 0 and 1.')


def upright(source, rotation=0, *, draft_decode=False):
    if rotation not in (0, 90, 180, 270):
        raise ValueError('Rotation must be 0, 90, 180, or 270 degrees.')
    with Image.open(source) as original:
        if draft_decode and original.format in ('JPEG', 'MPO'):
            original.draft('RGB', (3000, 3000))
        image = ImageOps.exif_transpose(original).convert('RGB')
    return image.rotate(-rotation, expand=True) if rotation else image


def encoded(image, long_edge=1568, *, jpeg_quality=92):
    ImagePolicy(long_edge=long_edge, jpeg_quality=jpeg_quality)
    image = image.copy()
    image.thumbnail((long_edge, long_edge), Image.Resampling.LANCZOS)
    buffer = io.BytesIO()
    image.save(buffer, 'JPEG', quality=jpeg_quality)
    return {'type': 'image', 'source': {'type': 'base64', 'media_type': 'image/jpeg',
            'data': base64.standard_b64encode(buffer.getvalue()).decode()}}


def prepare_images(content, policy=ImagePolicy()):
    sheet = upright(io.BytesIO(content), draft_decode=policy.draft_decode)
    selected = [sheet]
    if policy.lower_crop is not None:
        top = min(sheet.height - 1, round(sheet.height * policy.lower_crop))
        selected.append(sheet.crop((0, top, sheet.width, sheet.height)))
    return [encoded(image, policy.long_edge, jpeg_quality=policy.jpeg_quality)
            for image in selected]
