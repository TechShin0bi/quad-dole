document.addEventListener('DOMContentLoaded', function() {
    // Handle image preview when a file is selected
    function handleImagePreview(input) {
        if (input.files && input.files[0]) {
            const reader = new FileReader();
            const container = input.closest('.image-form');
            const preview = container.querySelector('img');
            const placeholder = container.querySelector('svg');
            
            reader.onload = function(e) {
                if (preview) {
                    preview.src = e.target.result;
                } else {
                    const img = document.createElement('img');
                    img.src = e.target.result;
                    img.className = 'mx-auto h-32 w-auto object-contain';
                    img.alt = 'Preview';
                    container.querySelector('.space-y-1').insertBefore(img, container.querySelector('.flex.text-sm'));
                    
                    if (placeholder) {
                        placeholder.remove();
                    }
                }
            };
            
            reader.readAsDataURL(input.files[0]);
        }
    }

    // Handle click on "Ajouter une autre image" button
    const addImageButton = document.getElementById('add-image');
    if (addImageButton) {
        addImageButton.addEventListener('click', function() {
            const formCount = document.getElementById('id_images-TOTAL_FORMS');
            const formNum = parseInt(formCount.value);
            const forms = document.querySelectorAll('.image-form');
            
            if (forms.length === 0) return;
            
            const newForm = forms[0].cloneNode(true);
            const formRegex = /images-(\d+)-/g;
            
            // Update the form index
            newForm.innerHTML = newForm.innerHTML.replace(formRegex, `images-${formNum}-`);
            
            // Clear file input and preview
            const fileInput = newForm.querySelector('input[type="file"]');
            if (fileInput) {
                fileInput.value = '';
            }
            
            const preview = newForm.querySelector('img');
            if (preview) {
                preview.remove();
            }
            
            // Clear alt text
            const altText = newForm.querySelector('input[type="text"]');
            if (altText) altText.value = '';
            
            // Uncheck featured and delete checkboxes
            const checkboxes = newForm.querySelectorAll('input[type="checkbox"]');
            checkboxes.forEach(checkbox => {
                checkbox.checked = false;
            });
            
            // Make sure the delete checkbox is visible
            const deleteDiv = newForm.querySelector('div:has(> input[name$="-DELETE"])');
            if (deleteDiv) {
                deleteDiv.style.display = 'flex';
            }
            
            // Add the new form to the container
            document.getElementById('image-forms').appendChild(newForm);
            
            // Update the form count
            formCount.value = formNum + 1;
            
            // Rebind the change event to the new file input
            const newFileInput = newForm.querySelector('input[type="file"]');
            if (newFileInput) {
                newFileInput.addEventListener('change', function() {
                    handleImagePreview(this);
                });
            }
        });
    }
    
    // Handle image preview for existing file inputs
    document.querySelectorAll('.image-form input[type="file"]').forEach(input => {
        input.addEventListener('change', function() {
            handleImagePreview(this);
        });
    });
    
    // Handle featured image selection (only one can be featured)
    document.addEventListener('change', function(e) {
        if (e.target && e.target.matches('input[name$="-is_featured"]')) {
            if (e.target.checked) {
                // Uncheck all other featured checkboxes
                document.querySelectorAll('input[name$="-is_featured"]').forEach(checkbox => {
                    if (checkbox !== e.target) {
                        checkbox.checked = false;
                    }
                });
            }
        }
    });
});
