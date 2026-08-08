from app.services.crop_analysis_service import analyze_crop

image_path = "test.jpg"

result = analyze_crop(image_path)

print("\nCrop Analysis Output:\n")

print(result)