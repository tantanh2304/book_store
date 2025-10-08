// Main JavaScript for Bookstore

document.addEventListener('DOMContentLoaded', function() {
    
    // Auto hide alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Smooth scroll to top
    const backToTopBtn = createBackToTopButton();
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            backToTopBtn.style.display = 'block';
        } else {
            backToTopBtn.style.display = 'none';
        }
    });
    
    // Add to cart animation
    const addToCartForms = document.querySelectorAll('form[action*="add_to_cart"]');
    addToCartForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const btn = this.querySelector('button[type="submit"]');
            const originalText = btn.innerHTML;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang thêm...';
            btn.disabled = true;
            
            // Re-enable after submission
            setTimeout(() => {
                btn.innerHTML = originalText;
                btn.disabled = false;
            }, 1000);
        });
    });
    
    // Quantity input validation
    const quantityInputs = document.querySelectorAll('input[name="quantity"]');
    quantityInputs.forEach(input => {
        input.addEventListener('change', function() {
            const min = parseInt(this.min) || 1;
            const max = parseInt(this.max) || 999;
            let value = parseInt(this.value);
            
            if (isNaN(value) || value < min) {
                this.value = min;
            } else if (value > max) {
                this.value = max;
                showToast('Số lượng tối đa là ' + max, 'warning');
            }
        });
    });
    
    // Confirm before removing from cart
    const removeLinks = document.querySelectorAll('a[href*="remove_from_cart"]');
    removeLinks.forEach(link => {
        link.addEventListener('click', function(e) {
            if (!confirm('Bạn có chắc muốn xóa sách này khỏi giỏ hàng?')) {
                e.preventDefault();
            }
        });
    });
    
    // Search enhancement
    const searchForm = document.querySelector('form[action*="books"]');
    const searchInput = searchForm?.querySelector('input[name="search"]');
    
    if (searchInput) {
        // Add search icon inside input
        searchInput.placeholder = '🔍 ' + searchInput.placeholder;
        
        // Clear search button
        if (searchInput.value) {
            addClearButton(searchInput);
        }
        
        searchInput.addEventListener('input', function() {
            if (this.value) {
                addClearButton(this);
            } else {
                removeClearButton(this);
            }
        });
    }
    
    // Lazy load images
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.removeAttribute('data-src');
                observer.unobserve(img);
            }
        });
    });
    
    images.forEach(img => imageObserver.observe(img));
    
    // Price formatting
    formatPrices();
    
    // Add loading state to checkout button
    const checkoutBtn = document.querySelector('form[action*="checkout"] button');
    if (checkoutBtn) {
        checkoutBtn.closest('form').addEventListener('submit', function(e) {
            checkoutBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> Đang xử lý...';
            checkoutBtn.disabled = true;
        });
    }
    
    // Initialize tooltips
    const tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });
    
    // Add animation class to cards
    const cards = document.querySelectorAll('.book-card');
    cards.forEach((card, index) => {
        setTimeout(() => {
            card.classList.add('fade-in');
        }, index * 50);
    });
});

// Helper Functions

function createBackToTopButton() {
    const btn = document.createElement('button');
    btn.innerHTML = '<i class="fas fa-arrow-up"></i>';
    btn.className = 'btn btn-primary';
    btn.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        display: none;
        z-index: 1000;
        border-radius: 50%;
        width: 50px;
        height: 50px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.3);
    `;
    
    btn.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    document.body.appendChild(btn);
    return btn;
}

function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed`;
    toast.style.cssText = `
        top: 80px;
        right: 20px;
        z-index: 9999;
        min-width: 300px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.2);
    `;
    toast.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
        toast.remove();
    }, 5000);
}

function addClearButton(input) {
    if (input.nextElementSibling?.classList.contains('clear-search')) {
        return;
    }
    
    const clearBtn = document.createElement('button');
    clearBtn.type = 'button';
    clearBtn.className = 'btn btn-sm btn-outline-secondary clear-search';
    clearBtn.innerHTML = '<i class="fas fa-times"></i>';
    clearBtn.style.cssText = `
        position: absolute;
        right: 50px;
        top: 50%;
        transform: translateY(-50%);
        z-index: 10;
    `;
    
    clearBtn.addEventListener('click', () => {
        input.value = '';
        input.focus();
        clearBtn.remove();
    });
    
    input.parentElement.style.position = 'relative';
    input.parentElement.appendChild(clearBtn);
}

function removeClearButton(input) {
    const clearBtn = input.nextElementSibling;
    if (clearBtn?.classList.contains('clear-search')) {
        clearBtn.remove();
    }
}

function formatPrices() {
    const priceElements = document.querySelectorAll('.price, [data-price]');
    priceElements.forEach(el => {
        const price = el.dataset.price || el.textContent;
        const formatted = new Intl.NumberFormat('vi-VN', {
            style: 'currency',
            currency: 'VND'
        }).format(price);
        el.textContent = formatted;
    });
}

// Cart counter update
function updateCartCounter() {
    fetch('/api/cart/count')
        .then(response => response.json())
        .then(data => {
            const cartLink = document.querySelector('a[href*="cart"]');
            if (cartLink && data.count > 0) {
                let badge = cartLink.querySelector('.badge');
                if (!badge) {
                    badge = document.createElement('span');
                    badge.className = 'badge bg-danger rounded-pill ms-1';
                    cartLink.appendChild(badge);
                }
                badge.textContent = data.count;
            }
        })
        .catch(error => console.error('Error updating cart counter:', error));
}

// Call on page load
if (document.querySelector('a[href*="cart"]')) {
    updateCartCounter();
}