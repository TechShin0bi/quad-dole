import json
import os
import logging
from django.core.management.base import BaseCommand
from django.conf import settings
from django.db import transaction
from products.models import Brand

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = "Import brands from a JSON file into the database using bulk operations"

    def add_arguments(self, parser):
        parser.add_argument(
            "--file",
            type=str,
            default="data/brands.json",
            help="Path to the JSON file containing brand data (default: data/brands.json in project root)",
        )
        parser.add_argument(
            "--batch-size",
            type=int,
            default=1000,
            help="Number of records to process in a single batch (default: 1000)",
        )
        parser.add_argument(
            "--quiet",
            action="store_true",
            help="Suppress output except for errors",
        )

    def handle(self, *args, **options):
        file_path = options["file"]
        batch_size = options["batch_size"]
        quiet = options["quiet"]

        # Construct absolute path if a relative path is provided
        if not os.path.isabs(file_path):
            file_path = os.path.join(settings.BASE_DIR, file_path)

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                brands_data = json.load(f)

            if not isinstance(brands_data, list):
                self.stdout.write(
                    self.style.ERROR("Invalid JSON format. Expected a list of brands.")
                )
                return

            stats = {"created": 0, "updated": 0, "skipped": 0}
            batch = []
            existing_brand_ids = set(Brand.objects.values_list('brand_id', flat=True))

            for i, brand_data in enumerate(brands_data, 1):
                # Skip invalid entries
                if not all(key in brand_data for key in ["id", "name"]):
                    stats["skipped"] += 1
                    if not quiet:
                        logger.warning(f"Skipping invalid brand data at index {i}: {brand_data}")
                    continue

                batch.append(brand_data)

                # Process batch when it reaches the specified size
                if len(batch) >= batch_size:
                    self._process_batch(batch, existing_brand_ids, stats, quiet)
                    batch = []

            # Process any remaining items in the last batch
            if batch:
                self._process_batch(batch, existing_brand_ids, stats, quiet)

            # Print summary
            self.stdout.write(self.style.SUCCESS(
                f"Import complete. Created: {stats['created']}, "
                f"Updated: {stats['updated']}, Skipped: {stats['skipped']}"
            ))

        except FileNotFoundError:
            self.stdout.write(self.style.ERROR(f"File not found: {file_path}"))
        except json.JSONDecodeError as e:
            self.stdout.write(self.style.ERROR(f"Invalid JSON file: {str(e)}"))
        except Exception as e:
            logger.exception("An unexpected error occurred during brand import")
            self.stdout.write(self.style.ERROR(f"An error occurred: {str(e)}"))

    def _process_batch(self, batch, existing_brand_ids, stats, quiet):
        """Process a batch of brand data using bulk operations."""
        from django.db import transaction
        
        try:
            with transaction.atomic():
                # Separate creates and updates
                to_create = []
                to_update = []
                
                for brand_data in batch:
                    brand_id = brand_data["id"]
                    brand_values = {
                        "name": brand_data["name"],
                        "image": brand_data.get("image_url", ""),
                    }
                    
                    if brand_id in existing_brand_ids:
                        # For updates, we'll use bulk_update after fetching the objects
                        to_update.append((brand_id, brand_values))
                    else:
                        # For creates, prepare objects for bulk_create
                        to_create.append(Brand(
                            brand_id=brand_id,
                            **brand_values
                        ))
                
                # Bulk create new brands
                if to_create:
                    created = Brand.objects.bulk_create(
                        to_create,
                        batch_size=len(to_create),
                        ignore_conflicts=False
                    )
                    stats["created"] += len(created)
                    if not quiet:
                        logger.info(f"Created {len(created)} brands in batch")
                
                # Bulk update existing brands
                if to_update:
                    update_count = 0
                    # Process updates in smaller chunks to avoid large IN clauses
                    for i in range(0, len(to_update), 100):
                        chunk = to_update[i:i+100]
                        brand_ids = [item[0] for item in chunk]
                        updates = {item[0]: item[1] for item in chunk}
                        
                        # Get all brands that need updating
                        brands = Brand.objects.filter(brand_id__in=brand_ids)
                        
                        # Update each brand's fields
                        updated = []
                        for brand in brands:
                            values = updates[brand.brand_id]
                            for field, value in values.items():
                                setattr(brand, field, value)
                            updated.append(brand)
                        
                        # Perform bulk update
                        if updated:
                            Brand.objects.bulk_update(
                                updated,
                                ['name', 'image', 'updated_at']
                            )
                            update_count += len(updated)
                    
                    stats["updated"] += update_count
                    if not quiet and update_count > 0:
                        logger.info(f"Updated {update_count} brands in batch")
                        
        except Exception as e:
            logger.error(f"Error processing batch: {str(e)}")
            raise
