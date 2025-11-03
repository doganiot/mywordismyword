/**
 * Sözüm Sözüm - Ana JavaScript Dosyası
 * Eğlenceli sözleşme platformu için etkileşimli özellikler
 */

document.addEventListener('DOMContentLoaded', function() {
    // Sayfa yüklendiğinde çalışacak fonksiyonlar
    initializePage();
    setupEventListeners();
    initializeAnimations();
});

/**
 * Sayfa başlatma fonksiyonu
 */
function initializePage() {
    // Loading spinner'ları gizle
    hideLoadingSpinners();

    // Toast mesajlarını göster
    showToastMessages();

    // Sayfa geçiş animasyonları
    animatePageElements();

    // Form validasyonları
    setupFormValidations();

    // Lazy loading için görselleri kontrol et
    setupLazyLoading();
}

/**
 * Event listener'ları kur
 */
function setupEventListeners() {
    // Sözleşme arama
    setupContractSearch();

    // Modal'lar için event listener
    setupModalHandlers();

    // Form submit'leri için
    setupFormHandlers();

    // Copy to clipboard
    setupCopyToClipboard();

    // Infinite scroll (sözleşme havuzu için)
    setupInfiniteScroll();

    // Real-time notifications (şimdilik simüle)
    setupNotifications();
}

/**
 * Animasyonları başlat
 */
function initializeAnimations() {
    // Elementleri fade-in ile göster
    const animatedElements = document.querySelectorAll('.fade-in-up');
    animatedElements.forEach((element, index) => {
        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 100);
    });

    // Hover efektleri
    setupHoverEffects();
}

/**
 * Loading spinner'ları gizle
 */
function hideLoadingSpinners() {
    const spinners = document.querySelectorAll('.spinner');
    spinners.forEach(spinner => {
        spinner.style.display = 'none';
    });
}

/**
 * Toast mesajlarını göster
 */
function showToastMessages() {
    const toastElList = [].slice.call(document.querySelectorAll('.toast'));
    const toastList = toastElList.map(function(toastEl) {
        return new bootstrap.Toast(toastEl);
    });

    toastList.forEach(toast => toast.show());
}

/**
 * Sayfa elementlerini animasyonla göster
 */
function animatePageElements() {
    const elements = document.querySelectorAll('.card, .btn, .alert');
    elements.forEach((element, index) => {
        element.style.opacity = '0';
        element.style.transform = 'translateY(20px)';
        element.style.transition = 'opacity 0.5s ease, transform 0.5s ease';

        setTimeout(() => {
            element.style.opacity = '1';
            element.style.transform = 'translateY(0)';
        }, index * 50);
    });
}

/**
 * Form validasyonları
 */
function setupFormValidations() {
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            if (!form.checkValidity()) {
                e.preventDefault();
                e.stopPropagation();

                // Hata mesajlarını göster
                showFormErrors(form);
            }
            form.classList.add('was-validated');
        });
    });
}

/**
 * Sözleşme arama
 */
function setupContractSearch() {
    const searchInput = document.querySelector('#contractSearch');
    if (searchInput) {
        let searchTimeout;

        searchInput.addEventListener('input', function() {
            clearTimeout(searchTimeout);
            searchTimeout = setTimeout(() => {
                performSearch(this.value);
            }, 300);
        });
    }
}

/**
 * Arama gerçekleştir
 */
function performSearch(query) {
    const searchResults = document.querySelector('#searchResults');
    if (!searchResults) return;

    if (query.length < 2) {
        searchResults.innerHTML = '';
        return;
    }

    // Loading göster
    searchResults.innerHTML = '<div class="text-center py-3"><div class="spinner"></div> Aranıyor...</div>';

    // AJAX ile arama (şimdilik simüle)
    setTimeout(() => {
        searchResults.innerHTML = `
            <div class="list-group">
                <a href="#" class="list-group-item list-group-item-action">
                    <div class="d-flex w-100 justify-content-between">
                        <h6 class="mb-1">Dostluk Sözleşmesi</h6>
                        <small>3 gün önce</small>
                    </div>
                    <p class="mb-1">${query} ile ilgili sözleşme bulundu.</p>
                    <small class="text-muted">Ahmet Yılmaz tarafından oluşturuldu</small>
                </a>
            </div>
        `;
    }, 500);
}

/**
 * Modal handler'ları
 */
function setupModalHandlers() {
    // Modal açılma animasyonları
    const modals = document.querySelectorAll('.modal');
    modals.forEach(modal => {
        modal.addEventListener('show.bs.modal', function() {
            const modalContent = this.querySelector('.modal-content');
            modalContent.style.transform = 'scale(0.9)';
            modalContent.style.opacity = '0';

            setTimeout(() => {
                modalContent.style.transform = 'scale(1)';
                modalContent.style.opacity = '1';
                modalContent.style.transition = 'transform 0.3s ease, opacity 0.3s ease';
            }, 50);
        });
    });
}

/**
 * Form handler'ları
 */
function setupFormHandlers() {
    // AJAX form submit'leri
    const ajaxForms = document.querySelectorAll('form[data-ajax="true"]');
    ajaxForms.forEach(form => {
        form.addEventListener('submit', function(e) {
            e.preventDefault();
            submitAjaxForm(this);
        });
    });
}

/**
 * AJAX form submit
 */
function submitAjaxForm(form) {
    const formData = new FormData(form);
    const submitBtn = form.querySelector('button[type="submit"]');

    // Loading state
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<span class="spinner me-2"></span>Gönderiliyor...';

    fetch(form.action, {
        method: 'POST',
        body: formData,
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
        },
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showSuccessMessage(data.message);
            if (data.redirect) {
                setTimeout(() => window.location.href = data.redirect, 1000);
            }
        } else {
            showErrorMessage(data.message);
        }
    })
    .catch(error => {
        showErrorMessage('Bir hata oluştu. Lütfen tekrar deneyin.');
        console.error('Form submit error:', error);
    })
    .finally(() => {
        submitBtn.disabled = false;
        submitBtn.innerHTML = 'Gönder';
    });
}

/**
 * Copy to clipboard
 */
function setupCopyToClipboard() {
    const copyButtons = document.querySelectorAll('[data-copy]');
    copyButtons.forEach(button => {
        button.addEventListener('click', function() {
            const textToCopy = this.dataset.copy;
            copyToClipboard(textToCopy);
        });
    });
}

/**
 * Metni panoya kopyala
 */
function copyToClipboard(text) {
    if (navigator.clipboard && window.isSecureContext) {
        navigator.clipboard.writeText(text).then(() => {
            showSuccessMessage('Link kopyalandı!');
        });
    } else {
        // Fallback
        const textArea = document.createElement('textarea');
        textArea.value = text;
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        showSuccessMessage('Link kopyalandı!');
    }
}

/**
 * Infinite scroll
 */
function setupInfiniteScroll() {
    const scrollContainer = document.querySelector('#contractPool');
    if (!scrollContainer) return;

    let isLoading = false;

    window.addEventListener('scroll', function() {
        if (isLoading) return;

        const { scrollTop, scrollHeight, clientHeight } = document.documentElement;

        if (scrollTop + clientHeight >= scrollHeight - 100) {
            loadMoreContracts();
        }
    });
}

/**
 * Daha fazla sözleşme yükle
 */
function loadMoreContracts() {
    const loadingIndicator = document.querySelector('#loadingIndicator');
    if (!loadingIndicator) return;

    loadingIndicator.style.display = 'block';

    // Simüle edilmiş API çağrısı
    setTimeout(() => {
        const newContracts = `
            <div class="col-md-6 col-lg-4 mb-4">
                <div class="card contract-pool-item">
                    <div class="card-body">
                        <h6 class="card-title">Yeni Sözleşme</h6>
                        <p class="card-text">Daha fazla içerik yükleniyor...</p>
                        <small class="text-muted">Şimdi yüklendi</small>
                    </div>
                </div>
            </div>
        `;

        const container = document.querySelector('#contractContainer');
        container.insertAdjacentHTML('beforeend', newContracts);

        loadingIndicator.style.display = 'none';
    }, 1000);
}

/**
 * Bildirim sistemi
 */
function setupNotifications() {
    // Sayfa yüklendiğinde bir kez çalıştır
    updateNotificationCounts();

    // Her 30 saniyede bir bildirimleri güncelle
    setInterval(() => {
        updateNotificationCounts();
    }, 30000);
}

/**
 * Bildirim sayılarını API'den al ve güncelle
 */
function updateNotificationCounts() {
    // Kullanıcı giriş yapmamışsa çalışmasın
    if (!document.body.hasAttribute('data-user-authenticated')) {
        console.log('👤 Kullanıcı giriş yapmamış, bildirimler atlandı');
        return;
    }

    console.log('🔄 Bildirimler güncelleniyor...');

    fetch('/api/notifications/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
    })
    .then(response => {
        console.log('API yanıt durumu:', response.status);
        return response.json();
    })
    .then(data => {
        console.log('📊 Bildirim verileri:', data);
        
        if (data.invited_contracts_count !== undefined) {
            console.log(`✉️ Davet edildiğim: ${data.invited_contracts_count}`);
            updateNotificationBadge('invited-contracts-count', data.invited_contracts_count);
        }
        if (data.declined_contracts_count !== undefined) {
            console.log(`Red edilenler: ${data.declined_contracts_count}`);
            updateNotificationBadge('declined-contracts-count', data.declined_contracts_count);
            updateNotificationBadge('declined-contracts-count-warning', data.declined_contracts_count);
        }
        if (data.unread_notifications_count !== undefined) {
            console.log(`Okunmamis bildirimler: ${data.unread_notifications_count}`);
            updateNotificationBadge('unread-notifications-count', data.unread_notifications_count);
        }
        
        console.log('Bildirimler güncellendi');
    })
    .catch(error => {
        console.error('❌ Bildirim güncelleme hatası:', error);
    });
}

/**
 * Bildirim rozetini güncelle
 */
function updateNotificationBadge(elementId, count) {
    const badge = document.querySelector(`[data-notification-id="${elementId}"]`);
    
    if (!badge) {
        console.warn(`Badge bulunamadı: ${elementId}`);
        return;
    }
    
    // Sayıyı güncelle
    badge.textContent = count;
    
    if (count > 0) {
        badge.style.display = 'inline-block';
        badge.classList.add('animate-pulse');
        
        // Sayfa yüklendikten sonra animasyonu kaldır
        setTimeout(() => {
            badge.classList.remove('animate-pulse');
        }, 2000);
    } else {
        badge.style.display = 'none';
        badge.classList.remove('animate-pulse');
    }
}

/**
 * Hover efektleri
 */
function setupHoverEffects() {
    const hoverElements = document.querySelectorAll('.hover-lift');
    hoverElements.forEach(element => {
        element.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-3px)';
        });

        element.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

/**
 * Lazy loading
 */
function setupLazyLoading() {
    const images = document.querySelectorAll('img[data-src]');
    const imageObserver = new IntersectionObserver((entries, observer) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const img = entry.target;
                img.src = img.dataset.src;
                img.classList.remove('lazy');
                observer.unobserve(img);
            }
        });
    });

    images.forEach(img => imageObserver.observe(img));
}

/**
 * Form hata mesajlarını göster
 */
function showFormErrors(form) {
    const invalidFields = form.querySelectorAll(':invalid');
    invalidFields.forEach(field => {
        field.classList.add('is-invalid');

        // Hata mesajı ekle
        if (!field.nextElementSibling?.classList.contains('invalid-feedback')) {
            const errorMsg = document.createElement('div');
            errorMsg.className = 'invalid-feedback';
            errorMsg.textContent = getFieldErrorMessage(field);
            field.parentNode.insertBefore(errorMsg, field.nextSibling);
        }
    });
}

/**
 * Alan hata mesajını al
 */
function getFieldErrorMessage(field) {
    if (field.validity.valueMissing) {
        return 'Bu alan zorunludur.';
    }
    if (field.validity.typeMismatch) {
        return 'Geçersiz format.';
    }
    if (field.validity.tooShort) {
        return `En az ${field.minLength} karakter olmalı.`;
    }
    return 'Geçersiz değer.';
}

/**
 * Başarı mesajı göster
 */
function showSuccessMessage(message) {
    showToast(message, 'success');
}

/**
 * Hata mesajı göster
 */
function showErrorMessage(message) {
    showToast(message, 'error');
}

/**
 * Toast mesajı göster
 */
function showToast(message, type = 'info') {
    const toastContainer = document.querySelector('.toast-container') || createToastContainer();

    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type} border-0`;
    toast.setAttribute('role', 'alert');

    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    toastContainer.appendChild(toast);
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    // Otomatik kaldır
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

/**
 * Toast container oluştur
 */
function createToastContainer() {
    const container = document.createElement('div');
    container.className = 'toast-container position-fixed top-0 end-0 p-3';
    container.style.zIndex = '1050';
    document.body.appendChild(container);
    return container;
}

/**
 * API çağrısı wrapper
 */
function apiCall(url, options = {}) {
    const defaultOptions = {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
        },
        credentials: 'same-origin',
        mode: 'same-origin',
    };

    return fetch(url, { ...defaultOptions, ...options })
        .then(response => {
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return response.json();
        })
        .catch(error => {
            console.error('API call failed:', error);
            showErrorMessage('Bir hata oluştu. Lütfen tekrar deneyin.');
            throw error; // Re-throw to allow calling code to handle
        });
}

/**
 * Debounce fonksiyonu
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * Throttle fonksiyonu
 */
function throttle(func, limit) {
    let inThrottle;
    return function() {
        const args = arguments;
        const context = this;
        if (!inThrottle) {
            func.apply(context, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * Local storage helper
 */
const storage = {
    set: (key, value) => {
        try {
            localStorage.setItem(key, JSON.stringify(value));
        } catch (e) {
            console.warn('LocalStorage not available:', e);
        }
    },

    get: (key) => {
        try {
            const item = localStorage.getItem(key);
            return item ? JSON.parse(item) : null;
        } catch (e) {
            console.warn('LocalStorage not available:', e);
            return null;
        }
    },

    remove: (key) => {
        try {
            localStorage.removeItem(key);
        } catch (e) {
            console.warn('LocalStorage not available:', e);
        }
    }
};

/**
 * Bildirim dropdown fonksiyonları
 */
function loadNotificationDropdown() {
    const dropdownContent = document.getElementById('notificationDropdownContent');
    if (!dropdownContent) return;
    
    fetch('/api/notifications/recent/', {
        method: 'GET',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]')?.value || '',
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
    })
    .then(response => response.json())
    .then(data => {
        if (data.notifications && data.notifications.length > 0) {
            let html = '';
            data.notifications.forEach(notification => {
                html += `
                    <li>
                        <a class="dropdown-item notification-item ${!notification.is_read ? 'notification-unread' : ''}" 
                           href="${notification.action_url || '#'}"
                           onclick="markNotificationAsRead('${notification.id}')">
                            <div class="d-flex">
                                <i class="${notification.icon_class} text-${notification.color_class} me-2 mt-1"></i>
                                <div class="flex-grow-1">
                                    <div class="fw-bold small">${notification.title}</div>
                                    <div class="text-muted small">${notification.message.substring(0, 60)}...</div>
                                    <small class="text-muted">${notification.time_since_created}</small>
                                </div>
                                ${!notification.is_read ? '<span class="badge bg-primary">Yeni</span>' : ''}
                            </div>
                        </a>
                    </li>
                `;
            });
            dropdownContent.innerHTML = html;
        } else {
            dropdownContent.innerHTML = `
                <li class="text-center py-3">
                    <i class="fas fa-bell-slash text-muted"></i>
                    <small class="text-muted d-block">Henüz bildirim yok</small>
                </li>
            `;
        }
    })
    .catch(error => {
        console.error('Bildirim dropdown yükleme hatası:', error);
        dropdownContent.innerHTML = `
            <li class="text-center py-3">
                <small class="text-danger">Bildirimler yüklenemedi</small>
            </li>
        `;
    });
}

function markNotificationAsRead(notificationId) {
    fetch(`/api/notification/${notificationId}/read/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
    })
    .then(() => {
        updateNotificationCounts();
    })
    .catch(error => {
        console.error('Bildirim okundu işaretleme hatası:', error);
    });
}

function markAllNotificationsRead() {
    fetch('/api/notifications/mark-all-read/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value,
            'Content-Type': 'application/json',
        },
        credentials: 'same-origin',
    })
    .then(() => {
        updateNotificationCounts();
        loadNotificationDropdown();
    })
    .catch(error => {
        console.error('Tüm bildirimleri okundu işaretleme hatası:', error);
    });
}

// Notification dropdown açıldığında bildirimleri yükle
document.addEventListener('DOMContentLoaded', function() {
    const notificationDropdown = document.getElementById('notificationDropdown');
    if (notificationDropdown) {
        notificationDropdown.addEventListener('shown.bs.dropdown', function() {
            loadNotificationDropdown();
        });
    }
});

// Global değişkenler
window.SozumSozum = {
    apiCall,
    debounce,
    throttle,
    storage,
    showSuccessMessage,
    showErrorMessage,
    copyToClipboard,
    updateNotificationCounts,
    updateNotificationBadge,
    loadNotificationDropdown,
    markNotificationAsRead,
    markAllNotificationsRead
};

