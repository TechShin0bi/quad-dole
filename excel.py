from openpyxl import Workbook
import os

wb = Workbook()
ws = wb.active
ws.title = "ProductModel_Import"

headers = [
    "product_name",
    "description",
    "price",
    "brand_name",
    "category_name",
    "image_1",
    "image_2",
    "image_3",
    "image_4",
    "image_5"
]

ws.append(headers)
ws.append(["", "", "", "", "", "", "", "", "", ""])

# Save to a folder that exists, e.g., Desktop
desktop_path = os.path.expanduser("~/Desktop")
file_path = os.path.join(desktop_path, "productmodel_import.xlsx")
wb.save(file_path)

print(f"Excel file saved at: {file_path}")
