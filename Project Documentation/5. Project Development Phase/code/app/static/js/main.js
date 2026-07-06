document.addEventListener('DOMContentLoaded', () => {
    
    // --- 1. Auto-Dismiss Flash Messages ---
    const flashMessages = document.querySelectorAll('.flash-message');
    flashMessages.forEach((msg) => {
        setTimeout(() => {
            msg.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
            msg.style.opacity = '0';
            msg.style.transform = 'translateY(-10px)';
            setTimeout(() => {
                msg.remove();
            }, 600);
        }, 5000);
    });

    // --- 2. Predict Form: Toggle Experience Input ---
    const employmentStatus = document.getElementById('employment_status');
    const experienceGroup = document.getElementById('experience-group');
    const experienceInput = document.getElementById('experience');

    if (employmentStatus && experienceGroup) {
        const toggleExperienceField = () => {
            if (employmentStatus.value === 'Unemployed') {
                experienceGroup.style.display = 'none';
                if (experienceInput) {
                    experienceInput.required = false;
                    experienceInput.value = '0';
                }
            } else {
                experienceGroup.style.display = 'block';
                if (experienceInput) {
                    experienceInput.required = true;
                }
            }
        };

        // Initialize on load
        toggleExperienceField();

        // Listen for changes
        employmentStatus.addEventListener('change', toggleExperienceField);
    }
});
