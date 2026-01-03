import os
from PIL import Image

def compress_images(source_dir, dest_dir, quality=85, resize_factor=None):
    """
    Compresses images in the source directory and saves them to the destination directory.

    Args:
        source_dir (str): Path to the directory containing images.
        dest_dir (str): Path to the directory to save compressed images.
        quality (int): Quality of the output images (1-100). Default is 85.
        resize_factor (float): Factor to resize the image (e.g., 0.5 for half size). Default is None.
    """
    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    supported_formats = ('.jpg', '.jpeg', '.png', '.bmp', '.webp')

    for filename in os.listdir(source_dir):
        if filename.lower().endswith(supported_formats):
            file_path = os.path.join(source_dir, filename)
            try:
                with Image.open(file_path) as img:
                    # Resize if requested
                    if resize_factor:
                        new_width = int(img.width * resize_factor)
                        new_height = int(img.height * resize_factor)
                        img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)

                    # Save compressed image
                    output_path = os.path.join(dest_dir, filename)
                    
                    # Handle PNG separately to preserve transparency if needed, 
                    # but for compression usually we might convert to RGB for JPEG or keep PNG with optimization
                    if filename.lower().endswith('.png'):
                         # PNG compression is lossless, 'optimize=True' helps. 
                         # To reduce size significantly, one might convert to JPEG if transparency isn't needed,
                         # but here we stick to the original format.
                        img.save(output_path, optimize=True, quality=quality)
                    else:
                        # JPEG and others
                        if img.mode in ("RGBA", "P"):
                            img = img.convert("RGB")
                        img.save(output_path, quality=quality, optimize=True)
                    
                    print(f"Compressed: {filename}")
            except Exception as e:
                print(f"Error processing {filename}: {e}")

if __name__ == "__main__":
    # Example usage
    # Change these paths to your actual folders
    source_folder = "D:\\desktop\\武明亮材料\\8fea7681a27028f653ac7d0b92a9e86.jpg" 
    destination_folder = "compressed_images"
    
    # Create dummy folders for demonstration if they don't exist
    if not os.path.exists(source_folder):
        os.makedirs(source_folder)
        print(f"Created folder: {source_folder}. Please put your images there.")
    
    compress_images(source_folder, destination_folder, quality=70, resize_factor=0.8)
    print("Compression complete.")
