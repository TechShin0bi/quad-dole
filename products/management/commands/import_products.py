import json
import os
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from django.utils.text import slugify
from products.models import (
    Product, 
    ProductImage, 
    Category, 
    ProductModel, 
    Brand
)

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import products from a JSON file into the database using bulk operations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data/products.json',
            help='Path to the JSON file containing product data (default: data/products.json in project root)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=500,
            help='Number of records to process in a single batch (default: 500)'
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='Suppress output except for errors'
        )
        parser.add_argument(
            '--skip-images',
            action='store_true',
            help='Skip importing product images to speed up the process'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        batch_size = options['batch_size']
        quiet = options['quiet']
        skip_images = options['skip_images']
        
        # Construct absolute path if a relative path is provided
        if not os.path.isabs(file_path):
            file_path = os.path.join(settings.BASE_DIR, file_path)
        
        try:
            # Load all data first
            with open(file_path, 'r', encoding='utf-8') as f:
                products_data = json.load(f)
            
            if not isinstance(products_data, list):
                self.stdout.write(self.style.ERROR('Invalid JSON format. Expected a list of products.'))
                return
            
            stats = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0, 'images_processed': 0}
            
            # Pre-fetch related objects for faster lookups
            brand_cache = {str(brand.brand_id): brand for brand in Brand.objects.all()}
            model_cache = {str(model.model_id): model for model in ProductModel.objects.all()}
            category_cache = {str(category.category_id): category for category in Category.objects.all()}
            
            # Process in batches
            for i in range(0, len(products_data), batch_size):
                batch = products_data[i:i + batch_size]
                self._process_batch(
                    batch, 
                    brand_cache, 
                    model_cache, 
                    category_cache, 
                    stats, 
                    quiet,
                    skip_images
                )
            
            # Print summary
            self.stdout.write(self.style.SUCCESS(
                f'Import complete. Created: {stats["created"]}, Updated: {stats["updated"]}, ' 
                f'Skipped: {stats["skipped"]}, Errors: {stats["errors"]}, ' 
                f'Images processed: {stats["images_processed"]}'
            ))
                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'Invalid JSON file: {str(e)}'))
        except Exception as e:
            logger.exception('An unexpected error occurred during product import')
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))
    
    def _process_batch(self, batch, brand_cache, model_cache, category_cache, stats, quiet, skip_images):
        """Process a batch of product data using bulk operations."""
        from django.db import transaction
        
        try:
            with transaction.atomic():
                to_create = []
                to_update = []
                image_batch = []
                
                # First pass: validate and prepare data
                for product_data in batch:
                    # Skip invalid entries
                    required_fields = ['id', 'name', 'model_id', 'category_id']
                    if not all(key in product_data for key in required_fields):
                        stats['skipped'] += 1
                        if not quiet:
                            logger.warning(f'Skipping invalid product data (missing required fields): {product_data}')
                        continue
                    
                    product_id = product_data['id']
                    model_id = str(product_data['model_id'])
                    category_id = str(product_data['category_id'])
                    brand_id = str(product_data.get('brand_id', ''))
                    
                    # Check if related objects exist
                    if model_id not in model_cache:
                        stats['skipped'] += 1
                        if not quiet:
                            logger.warning(f'Model with ID {model_id} not found for product {product_id}')
                        continue
                    
                    if category_id not in category_cache:
                        stats['skipped'] += 1
                        if not quiet:
                            logger.warning(f'Category with ID {category_id} not found for product {product_id}')
                        continue
                    
                    if brand_id and brand_id not in brand_cache:
                        stats['skipped'] += 1
                        if not quiet:
                            logger.warning(f'Brand with ID {brand_id} not found for product {product_id}')
                        continue
                    
                    # Prepare product data
                    product_values = {
                        'name': product_data['name'],
                        'description': product_data.get('description', ''),
                        'price': float(product_data.get('price', 0)),
                        'image': product_data.get('image_url', ''),
                        'category': category_cache[category_id],
                        'sku': product_data.get('sku', ''),
                    }
                    
                    # Check if product exists
                    try:
                        existing_product = Product.objects.get(id=product_id)
                        # For updates, we'll use bulk_update after fetching the objects
                        to_update.append((product_id, product_values))
                    except Product.DoesNotExist:
                        # For creates, prepare objects for bulk_create
                        to_create.append(Product(
                            id=product_id,
                            **product_values
                        ))
                    
                    # Prepare image data if not skipping
                    if not skip_images:
                        # Add main image
                        if product_data.get('image_url'):
                            image_batch.append({
                                'product_id': product_id,
                                'image_url': product_data['image_url']
                            })
                        
                        # Add extra images
                        for image_url in product_data.get('extra_images', []):
                            image_batch.append({
                                'product_id': product_id,
                                'image_url': image_url
                            })
                
                # Bulk create new products
                if to_create:
                    try:
                        created = Product.objects.bulk_create(
                            to_create,
                            batch_size=len(to_create),
                            ignore_conflicts=False
                        )
                        stats['created'] += len(created)
                        if not quiet:
                            logger.info(f'Created {len(created)} products in batch')
                    except Exception as e:
                        logger.error(f'Error creating products: {str(e)}')
                        stats['errors'] += len(to_create)
                
                # Bulk update existing products
                if to_update:
                    try:
                        update_count = 0
                        # Process updates in smaller chunks to avoid large IN clauses
                        for i in range(0, len(to_update), 100):
                            chunk = to_update[i:i+100]
                            product_ids = [item[0] for item in chunk]
                            updates = {item[0]: item[1] for item in chunk}
                            
                            # Get all products that need updating
                            products = Product.objects.filter(id__in=product_ids)
                            
                            # Update each product's fields
                            updated = []
                            for product in products:
                                values = updates[product.id]
                                for field, value in values.items():
                                    setattr(product, field, value)
                                updated.append(product)
                            
                            # Perform bulk update
                            if updated:
                                Product.objects.bulk_update(
                                    updated,
                                    ['name', 'description', 'price', 'image', 'category', 'sku', 'updated_at']
                                )
                                update_count += len(updated)
                        
                        stats['updated'] += update_count
                        if not quiet and update_count > 0:
                            logger.info(f'Updated {update_count} products in batch')
                            
                    except Exception as e:
                        logger.error(f'Error updating products: {str(e)}')
                        stats['errors'] += len(to_update)
                
                # Process images if not skipped
                if not skip_images and image_batch:
                    try:
                        # Process images in chunks to avoid memory issues
                        for i in range(0, len(image_batch), 500):
                            chunk = image_batch[i:i+500]
                            self._process_image_batch(chunk, stats, quiet)
                    except Exception as e:
                        logger.error(f'Error processing images: {str(e)}')
                        stats['errors'] += len(image_batch)
                
        except Exception as e:
            logger.error(f'Error processing batch: {str(e)}')
            raise
    
    def _process_image_batch(self, image_batch, stats, quiet):
        """Process a batch of product images using bulk operations."""
        from django.db import transaction
        
        try:
            with transaction.atomic():
                # Get existing images to avoid duplicates
                existing_images = set(
                    ProductImage.objects.filter(
                        product_id__in={img['product_id'] for img in image_batch}
                    ).values_list('product_id', 'image')
                )
                
                # Prepare new images
                new_images = []
                for img_data in image_batch:
                    if (img_data['product_id'], img_data['image_url']) not in existing_images:
                        new_images.append(ProductImage(
                            product_id=img_data['product_id'],
                            image=img_data['image_url']
                        ))
                
                # Bulk create new images
                if new_images:
                    created = ProductImage.objects.bulk_create(
                        new_images,
                        batch_size=len(new_images),
                        ignore_conflicts=True
                    )
                    stats['images_processed'] += len(created)
                    if not quiet:
                        logger.info(f'Added {len(created)} product images in batch')
                        
        except Exception as e:
            logger.error(f'Error processing image batch: {str(e)}')
            raise
