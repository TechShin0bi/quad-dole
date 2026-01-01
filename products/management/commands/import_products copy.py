import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.utils.text import slugify
from products.models import (
    Product, 
    ProductImage, 
    Category, 
    ProductModel, 
    Brand
)

class Command(BaseCommand):
    help = 'Import products from a JSON file into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data/products.json',
            help='Path to the JSON file containing product data (default: data/products.json in project root)'
        )

    def handle(self, *args, **options):
        file_path = options["file"]
        
        # Construct absolute path if a relative path is provided
        if not os.path.isabs(file_path):
            file_path = os.path.join(settings.BASE_DIR, file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
                
                if not isinstance(products_data, list):
                    self.stdout.write(self.style.ERROR('Invalid JSON format. Expected a list of products.'))
                    return
                
                created_count = 0
                updated_count = 0
                
                for product_data in products_data:
                    # Ensure required fields exist
                    required_fields = ['id', 'name', 'model_id', 'category_id']
                    if not all(key in product_data for key in required_fields):
                        self.stdout.write(self.style.WARNING(
                            f'Skipping invalid product data (missing required fields): {product_data}'
                        ))
                        continue
                    
                    try:
                        # Get related objects
                        brand = Brand.objects.get(brand_id=product_data.get('brand_id'))
                        product_model = ProductModel.objects.get(model_id=product_data['model_id'])
                        category = Category.objects.get(category_id=product_data['category_id'])
                        
                        # Create or update the product
                        product, created = Product.objects.update_or_create(
                            id=product_data['id'],
                            defaults={
                                'name': product_data['name'],
                                'description': product_data.get('description', ''),
                                'price': product_data.get('price', 0),
                                'image': product_data.get('image_url', ''),
                                'category': category,
                                'sku': product_data.get('sku', ''),
                            }
                        )
                        
                        # Add the main image if it exists
                        if product_data.get('image_url'):
                            ProductImage.objects.get_or_create(
                                product=product,
                                image=product_data['image_url']
                            )
                        
                        # Add extra images
                        for image_url in product_data.get('extra_images', []):
                            ProductImage.objects.get_or_create(
                                product=product,
                                image=image_url
                            )
                        
                        if created:
                            created_count += 1
                            self.stdout.write(self.style.SUCCESS(
                                f'Created product: {product.name}'
                            ))
                        else:
                            updated_count += 1
                            self.stdout.write(self.style.SUCCESS(
                                f'Updated product: {product.name}'
                            ))
                            
                    except (Brand.DoesNotExist, ProductModel.DoesNotExist, Category.DoesNotExist) as e:
                        self.stdout.write(self.style.ERROR(
                            f'Related object not found for product {product_data.get("name", "unknown")}: {str(e)}'
                        ))
                    except Exception as e:
                        raise e
                        self.stdout.write(self.style.ERROR(
                            f'Error processing product {product_data.get("name", "unknown")}: {str(e)}'
                        ))
                
                self.stdout.write(self.style.SUCCESS(
                    f'Successfully imported {created_count} products. Updated {updated_count} products.'
                ))
                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'Invalid JSON file: {str(e)}'))
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))
