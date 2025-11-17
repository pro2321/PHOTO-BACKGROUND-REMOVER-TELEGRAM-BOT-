import aiohttp
import config
from PIL import Image
import io
import zipfile

async def remove_background(image_path):
    """
    Removes background from an image.
    Returns bytes of the processed image (PNG) or None if failed.
    """
    if not config.RBG_API:
        print("Error: Remove.bg API key (RBG_API) not set.")
        return None
        
    try:
        async with aiohttp.ClientSession() as session:
            data = aiohttp.FormData()
            data.add_field('image_file', open(image_path, 'rb'))
            data.add_field('size', 'auto')

            headers = {'X-Api-Key': config.RBG_API}
            
            async with session.post('https://api.remove.bg/v1.0/removebg', data=data, headers=headers) as response:
                if response.status == 200:
                    return await response.read()
                else:
                    print(f"Remove.bg Error: {response.status} - {await response.text()}")
                    return None
    except Exception as e:
        print(f"Error in remove_background: {e}")
        return None

async def convert_format(image_bytes, target_format):
    """
    Converts image bytes (PNG) to a target format.
    Returns (file_bytes, filename) tuple.
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))
        output_bytes = io.BytesIO()
        
        target_format = target_format.upper()
        
        if target_format == 'JPG':
            # Convert to RGB (for JPEG)
            img = img.convert('RGB')
            img.save(output_bytes, format='JPEG')
            filename = 'converted.jpg'
        
        elif target_format == 'PNG':
            img.save(output_bytes, format='PNG')
            filename = 'converted.png'
            
        elif target_format == 'PDF':
            # Convert to RGB (PDF doesn't handle RGBA well)
            img = img.convert('RGB')
            img.save(output_bytes, format='PDF', resolution=100.0)
            filename = 'converted.pdf'
            
        elif target_format == 'ZIP':
            with zipfile.ZipFile(output_bytes, 'w') as zf:
                # Save the PNG inside the zip
                img.save(io.BytesIO(), format='PNG')
                zf.writestr('bg_removed.png', io.BytesIO(image_bytes).getvalue())
            filename = 'converted.zip'

        # ... আপনি এখানে আরও ফরম্যাট যোগ করতে পারেন (e.g., WEBP, BMP)
            
        else:
            return None, None # Unsupported format

        output_bytes.seek(0)
        return output_bytes.getvalue(), filename
        
    except Exception as e:
        print(f"Error in convert_format: {e}")
        return None, None
