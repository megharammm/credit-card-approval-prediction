document.addEventListener('DOMContentLoaded', () => {
    const CHEVRON_DOWN_SVG = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" width="24" height="24" color="currentColor" fill="none"><path d="M18 9.00005C18 9.00005 13.5811 15 12 15C10.4188 15 6 9 6 9" stroke="currentColor" stroke-width="1.5" stroke-linecap="round" stroke-linejoin="round" /></svg>`;
    const CHECK_SVG = `<svg aria-hidden="true" fill="none" height="24" stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2" viewBox="0 0 24 24" width="24" xmlns="http://www.w3.org/2000/svg"><path d="M5.252 12.7 10.2 18.63 18.748 5.37" /></svg>`;

    // Find all standard selects in the form
    const nativeSelects = document.querySelectorAll('select.form-control');

    nativeSelects.forEach(nativeSelect => {
        // 1. Hide the native select
        nativeSelect.classList.add('custom-select-hidden');

        // 2. Create wrapper
        const wrapper = document.createElement('div');
        wrapper.className = 'custom-select-wrapper';
        nativeSelect.parentNode.insertBefore(wrapper, nativeSelect);
        wrapper.appendChild(nativeSelect);

        // 3. Create Trigger Button
        const trigger = document.createElement('button');
        trigger.type = 'button';
        trigger.className = 'custom-select-trigger';
        trigger.setAttribute('aria-haspopup', 'listbox');
        trigger.setAttribute('aria-expanded', 'false');
        
        const triggerText = document.createElement('span');
        triggerText.className = 'trigger-text';
        
        // Find the selected option's text
        let initialSelectedOption = nativeSelect.options[nativeSelect.selectedIndex];
        if (!initialSelectedOption && nativeSelect.options.length > 0) {
            initialSelectedOption = nativeSelect.options[0];
        }
        triggerText.textContent = initialSelectedOption ? initialSelectedOption.text : 'Select...';
        
        const triggerIcon = document.createElement('div');
        triggerIcon.className = 'trigger-icon';
        triggerIcon.innerHTML = CHEVRON_DOWN_SVG;

        trigger.appendChild(triggerText);
        trigger.appendChild(triggerIcon);
        wrapper.appendChild(trigger);

        // 4. Create Popup
        const popup = document.createElement('div');
        popup.className = 'custom-select-popup';
        popup.setAttribute('role', 'listbox');
        
        const list = document.createElement('div');
        list.className = 'custom-select-list';
        popup.appendChild(list);
        wrapper.appendChild(popup);

        // 5. Populate Popup Items
        Array.from(nativeSelect.options).forEach((option, index) => {
            const item = document.createElement('div');
            item.className = 'custom-select-item';
            if (option.selected) item.classList.add('selected');
            item.setAttribute('role', 'option');
            item.setAttribute('aria-selected', option.selected ? 'true' : 'false');
            item.setAttribute('data-value', option.value);

            const iconContainer = document.createElement('div');
            iconContainer.className = 'custom-select-item-icon';
            iconContainer.innerHTML = CHECK_SVG;

            const textContainer = document.createElement('span');
            textContainer.className = 'custom-select-item-text';
            textContainer.textContent = option.text;

            item.appendChild(iconContainer);
            item.appendChild(textContainer);
            list.appendChild(item);

            // 6. Handle Item Click
            item.addEventListener('click', (e) => {
                e.stopPropagation();
                // Update native select
                nativeSelect.value = option.value;
                // Dispatch change event so form validation works
                nativeSelect.dispatchEvent(new Event('change'));

                // Update Trigger text
                triggerText.textContent = option.text;
                trigger.classList.remove('placeholder-active');

                // Update selected states
                Array.from(list.children).forEach(child => {
                    child.classList.remove('selected');
                    child.setAttribute('aria-selected', 'false');
                });
                item.classList.add('selected');
                item.setAttribute('aria-selected', 'true');

                // Close popup
                closePopup();
            });
        });

        // 7. Toggle logic
        function togglePopup() {
            const isOpen = popup.classList.contains('open');
            if (isOpen) {
                closePopup();
            } else {
                // Close all other popups first
                document.querySelectorAll('.custom-select-popup.open').forEach(p => {
                    p.classList.remove('open');
                    p.previousElementSibling.setAttribute('aria-expanded', 'false');
                });
                
                popup.classList.add('open');
                trigger.setAttribute('aria-expanded', 'true');
                
                // Adjust position if it goes off screen
                const rect = popup.getBoundingClientRect();
                if (rect.bottom > window.innerHeight) {
                    popup.style.top = 'auto';
                    popup.style.bottom = 'calc(100% + 4px)';
                    popup.style.transformOrigin = 'bottom';
                } else {
                    popup.style.top = 'calc(100% + 4px)';
                    popup.style.bottom = 'auto';
                    popup.style.transformOrigin = 'top';
                }
            }
        }

        function closePopup() {
            popup.classList.remove('open');
            trigger.setAttribute('aria-expanded', 'false');
            trigger.focus(); // Return focus to trigger
        }

        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();
            togglePopup();
        });

        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!wrapper.contains(e.target)) {
                if (popup.classList.contains('open')) {
                    closePopup();
                }
            }
        });
    });
});
