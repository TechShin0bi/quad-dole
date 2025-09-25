document.addEventListener('DOMContentLoaded', function() {
    // Handle brand change to update models
    const brandSelect = document.getElementById('id_brand');
    const modelSelect = document.getElementById('id_model');
    
    if (brandSelect && modelSelect) {
        brandSelect.addEventListener('change', function() {
            const brandId = this.value;
            if (brandId) {
                fetch(`/api/models/?brand_id=${brandId}`)
                    .then(response => response.json())
                    .then(data => {
                        // Clear existing options
                        modelSelect.innerHTML = '<option value="">---------</option>';
                        
                        // Add new options
                        data.forEach(model => {
                            const option = document.createElement('option');
                            option.value = model.id;
                            option.textContent = model.name;
                            modelSelect.appendChild(option);
                        });
                        
                        // Enable the select
                        modelSelect.disabled = false;
                    })
                    .catch(error => console.error('Error fetching models:', error));
            } else {
                // No brand selected, disable model select
                modelSelect.innerHTML = '<option value="">---------</option>';
                modelSelect.disabled = true;
            }
        });
    }
    
    // Auto-generate slug from name
    const nameField = document.getElementById('id_name');
    const slugField = document.getElementById('id_slug');
    
    if (nameField && slugField) {
        nameField.addEventListener('blur', function() {
            if (!slugField.value) {
                const slug = this.value
                    .toLowerCase()
                    .replace(/[^a-z0-9]+/g, '-')
                    .replace(/(^-|-$)/g, '');
                slugField.value = slug;
            }
        });
    }
});
