import json
import os
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from products.models import Category, ProductModel

# Constants
DEFAULT_BATCH_SIZE = 1000

class Command(BaseCommand):
    help = 'Import model categories from a JSON file into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            default='data/model_categories.json',
            help='Path to the JSON file containing category data (default: data/model_categories.json)'
        )
        parser.add_argument(
            '--batch-size',
            type=int,
            default=DEFAULT_BATCH_SIZE,
            help=f'Number of categories to process in each batch (default: {DEFAULT_BATCH_SIZE})'
        )
        parser.add_argument(
            '--quiet',
            action='store_true',
            help='Run in quiet mode (only errors will be shown)'
        )

    def _log(self, message, style=None):
        """Helper method to log messages based on verbosity."""
        if style:
            self.stdout.write(style(message))
        elif not self.quiet:
            self.stdout.write(message)

    def _process_batch(self, batch, model_cache):
        """Process a batch of category data."""
        # Prepare data for bulk operations
        categories_to_create = []
        categories_to_update = []
        category_models = {}
        
        # First pass: collect all model_ids to prefetch
        model_ids = {data['model_id'] for data in batch if 'model_id' in data}
        
        # Prefetch models in bulk
        models_dict = {
            model.model_id: model 
            for model in ProductModel.objects.filter(model_id__in=model_ids).select_related('brand')
        }
        
        # Second pass: process each category
        for data in batch:
            if not all(key in data for key in ['id', 'name', 'model_id']):
                self._log(
                    self.style.WARNING(
                        f'Skipping invalid category data (missing required fields): {data}'
                    )
                )
                continue
            
            model_id = data['model_id']
            if model_id not in models_dict:
                self._log(
                    self.style.ERROR(
                        f'ProductModel with ID {model_id} not found for category {data["name"]}'
                    )
                )
                continue
            
            product_model = models_dict[model_id]
            category_id = data['id']
            
            # Prepare category data
            category_data = {
                'name': data['name'],
                'description': f"Category for {product_model.brand.name} {product_model.name}",
                'updated_at': timezone.now()
            }
            
            # Check if category exists
            existing_category = Category.objects.filter(category_id=category_id).first()
            
            if existing_category:
                # Update existing category
                for attr, value in category_data.items():
                    setattr(existing_category, attr, value)
                categories_to_update.append(existing_category)
                category_key = (existing_category.id, existing_category.category_id)
            else:
                # Create new category
                new_category = Category(
                    category_id=category_id,
                    created_at=timezone.now(),
                    **category_data
                )
                categories_to_create.append(new_category)
                category_key = (None, category_id)  # Will be updated after creation
            
            # Store model-category relationship
            if category_key not in category_models:
                category_models[category_key] = []
            category_models[category_key].append(product_model.id)
        
        # Bulk create categories
        if categories_to_create:
            Category.objects.bulk_create(categories_to_create, batch_size=1000)
            # Update the category_models keys with the new category IDs
            new_category_models = {}
            for (_, category_id), model_ids in category_models.items():
                if _ is None:  # This was a new category
                    category = Category.objects.get(category_id=category_id)
                    new_category_models[(category.id, category_id)] = model_ids
                else:
                    new_category_models[(_[0], category_id)] = model_ids
            category_models = new_category_models
        
        # Bulk update categories
        if categories_to_update:
            Category.objects.bulk_update(
                categories_to_update, 
                ['name', 'description', 'updated_at'],
                batch_size=1000
            )
        
        # Process model-category relationships in bulk
        for (category_id, _), model_ids in category_models.items():
            try:
                category = Category.objects.get(id=category_id)
                # Get existing model IDs to avoid duplicate additions
                existing_model_ids = set(category.models.values_list('id', flat=True))
                new_model_ids = [mid for mid in model_ids if mid not in existing_model_ids]
                
                if new_model_ids:
                    # Add new relationships in bulk
                    through_model = Category.models.through
                    through_model.objects.bulk_create([
                        through_model(category_id=category_id, productmodel_id=model_id)
                        for model_id in new_model_ids
                    ])
            except Exception as e:
                self._log(
                    self.style.ERROR(
                        f'Error updating relationships for category {category_id}: {str(e)}'
                    )
                )
        
        return len(categories_to_create), len(categories_to_update)

    def handle(self, *args, **options):
        file_path = options['file']
        batch_size = options['batch_size']
        self.quiet = options['quiet']
        
        # Construct absolute path if a relative path is provided
        if not os.path.isabs(file_path):
            file_path = os.path.join(settings.BASE_DIR, file_path)
        
        try:
            start_time = timezone.now()
            self._log(f'Starting import from {file_path}...')
            
            with open(file_path, 'r', encoding='utf-8') as f:
                categories_data = json.load(f)
                
                if not isinstance(categories_data, list):
                    self._log(
                        self.style.ERROR('Invalid JSON format. Expected a list of categories.')
                    )
                    return
                
                total_categories = len(categories_data)
                created_count = 0
                updated_count = 0
                processed = 0
                
                # Process in batches
                for i in range(0, total_categories, batch_size):
                    batch = categories_data[i:i + batch_size]
                    try:
                        with transaction.atomic():
                            created, updated = self._process_batch(batch, {})
                            created_count += created
                            updated_count += updated
                            
                        processed += len(batch)
                        if not self.quiet:
                            self._log(
                                f'Processed {min(processed, total_categories)}/{total_categories} categories ' 
                                f'({created} created, {updated} updated)',
                                self.style.SUCCESS
                            )
                            
                    except Exception as e:
                        self._log(
                            self.style.ERROR(f'Error processing batch {i//batch_size + 1}: {str(e)}')
                        )
                        # Continue with next batch even if one fails
                        continue
                
                duration = (timezone.now() - start_time).total_seconds()
                self._log(
                    self.style.SUCCESS(
                        f'Import completed in {duration:.2f} seconds. '
                        f'Created: {created_count}, Updated: {updated_count}, Total: {total_categories}'
                    )
                )
                
        except FileNotFoundError:
            self._log(self.style.ERROR(f'File not found: {file_path}'))
        except json.JSONDecodeError as e:
            self._log(self.style.ERROR(f'Invalid JSON file: {str(e)}'))
        except Exception as e:
            self._log(self.style.ERROR(f'An error occurred: {str(e)}'))
            if hasattr(e, '__traceback__'):
                import traceback
                self._log(traceback.format_exc())
