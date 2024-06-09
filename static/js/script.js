 document.getElementById('menu-toggle').addEventListener('click', function() {
            var navLinks = document.getElementById('nav-links');
            if (navLinks.style.display === 'block') {
                navLinks.style.display = 'none';
            } else {
                navLinks.style.display = 'block';
            }
        });

       document.addEventListener('DOMContentLoaded', (event) => {
        const menuToggleBtn = document.getElementById('menu-toggle-btn');
        const menu = document.getElementById('menuu');

        menuToggleBtn.addEventListener('click', () => {
            menu.classList.toggle('hiddenn');
        });
    });

       document.addEventListener('DOMContentLoaded', function() {
    var newPasswordInput = document.getElementById('new_password');
    newPasswordInput.addEventListener('input', function() {
        var newPassword = newPasswordInput.value;
        var md5Password = md5(newPassword); // Assuming you have a function named md5 to calculate MD5 hash
        newPasswordInput.value = md5Password;
    });
});

 document.addEventListener('DOMContentLoaded', function() {
            // Dapatkan elemen formulir
            const form = document.getElementById('roleForm');

            // Tambahkan event listener untuk perubahan pada opsi peran
            form.addEventListener('change', function() {
                // Submit formulir saat perubahan terjadi
                form.submit();
            });
        });