import json
import os
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from products.models import Brand, ProductModel

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import product models from a JSON file into the database using bulk operations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data/brand_models.json',
            help='Path to the JSON file containing product model data (default: data/brand_models.json in project root)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=1000,
            help='Number of records to process in a single batch (default: 1000)'
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='Suppress output except for errors'
        )

    def handle(self, *args, **options):
        file_path = options['file']
        batch_size = options['batch_size']
        quiet = options['quiet']
        
        # Construct absolute path if a relative path is provided
        if not os.path.isabs(file_path):
            file_path = os.path.join(settings.BASE_DIR, file_path)
        
        try:
            # Load all data first
            with open(file_path, 'r', encoding='utf-8') as f:
                models_data = json.load(f)
            
            if not isinstance(models_data, list):
                self.stdout.write(self.style.ERROR('Invalid JSON format. Expected a list of product models.'))
                return
            
            stats = {'created': 0, 'updated': 0, 'skipped': 0, 'errors': 0}
            
            # Pre-fetch all brands and existing models for faster lookups
            brand_cache = {str(brand.brand_id): brand for brand in Brand.objects.all()}
            existing_models = set(ProductModel.objects.values_list('model_id', flat=True))
            
            # Process in batches
            for i in range(0, len(models_data), batch_size):
                batch = models_data[i:i + batch_size]
                self._process_batch(batch, brand_cache, existing_models, stats, quiet)
            
            # Print summary
            self.stdout.write(self.style.SUCCESS(
                f'Import complete. Created: {stats["created"]}, Updated: {stats["updated"]}, ' 
                f'Skipped: {stats["skipped"]}, Errors: {stats["errors"]}'
            ))
                
        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f'Invalid JSON file: {str(e)}'))
        except Exception as e:
            logger.exception('An unexpected error occurred during model import')
            self.stdout.write(self.style.ERROR(f'An error occurred: {str(e)}'))
    
    def _process_batch(self, batch, brand_cache, existing_models, stats, quiet):
        """Process a batch of model data using bulk operations."""
        from django.db import transaction
        
        try:
            with transaction.atomic():
                to_create = []
                to_update = []
                
                for model_data in batch:
                    # Skip invalid entries
                    if not all(key in model_data for key in ['id', 'name', 'brand_id']):
                        stats['skipped'] += 1
                        if not quiet:
                            logger.warning(f'Skipping invalid model data: {model_data}')
                        continue
                    
                    model_id = model_data['id']
                    brand_id = str(model_data['brand_id'])
                    
                    # Check if brand exists
                    if brand_id not in brand_cache:
                        stats['skipped'] += 1
                        if not quiet:
                            logger.warning(f'Brand with ID {brand_id} not found for model {model_id}')
                        continue
                    
                    brand = brand_cache[brand_id]
                    
                    # Prepare model data
                    model_values = {
                        'name': model_data['name'],
                        'brand': brand,
                        'image': model_data.get('image_url', '')
                    }
                    
                    if model_id in existing_models:
                        # For updates, we'll use bulk_update after fetching the objects
                        to_update.append((model_id, model_values))
                    else:
                        # For creates, prepare objects for bulk_create
                        to_create.append(ProductModel(
                            model_id=model_id,
                            **model_values
                        ))
                
                # Bulk create new models
                if to_create:
                    try:
                        created = ProductModel.objects.bulk_create(
                            to_create,
                            batch_size=len(to_create),
                            ignore_conflicts=False
                        )
                        stats['created'] += len(created)
                        if not quiet:
                            logger.info(f'Created {len(created)} models in batch')
                    except Exception as e:
                        logger.error(f'Error creating models: {str(e)}')
                        stats['errors'] += len(to_create)
                
                # Bulk update existing models
                if to_update:
                    try:
                        update_count = 0
                        # Process updates in smaller chunks to avoid large IN clauses
                        for i in range(0, len(to_update), 100):
                            chunk = to_update[i:i+100]
                            model_ids = [item[0] for item in chunk]
                            updates = {item[0]: item[1] for item in chunk}
                            
                            # Get all models that need updating
                            models = ProductModel.objects.filter(model_id__in=model_ids)
                            
                            # Update each model's fields
                            updated = []
                            for model in models:
                                values = updates[model.model_id]
                                for field, value in values.items():
                                    setattr(model, field, value)
                                updated.append(model)
                            
                            # Perform bulk update
                            if updated:
                                ProductModel.objects.bulk_update(
                                    updated,
                                    ['name', 'brand', 'image', 'updated_at']
                                )
                                update_count += len(updated)
                        
                        stats['updated'] += update_count
                        if not quiet and update_count > 0:
                            logger.info(f'Updated {update_count} models in batch')
                            
                    except Exception as e:
                        logger.error(f'Error updating models: {str(e)}')
                        stats['errors'] += len(to_update)
                
        except Exception as e:
            logger.error(f'Error processing batch: {str(e)}')
            raise
