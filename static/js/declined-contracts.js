/**
 * Declined Contracts Page JavaScript
 * Red edilen sozlesmeler sayfasi icin JavaScript fonksiyonlari
 */

function deleteContract(contractId) {
    console.log('[DELETE] Delete function called for contract:', contractId);
    
    var confirmMessage = 'Bu sozlesmeyi silmek istediginizden emin misiniz? Bu islem geri alinamaz.';
    
    if (confirm(confirmMessage)) {
        console.log('[DELETE] User confirmed deletion');
        
        // Form oluştur
        var form = document.createElement('form');
        form.method = 'POST';
        form.action = '/contracts/' + contractId + '/delete/';
        
        console.log('[DELETE] Form action:', form.action);

        // CSRF token ekle
        var csrfToken = document.querySelector('[name=csrfmiddlewaretoken]');
        if (csrfToken) {
            var clonedToken = csrfToken.cloneNode(true);
            form.appendChild(clonedToken);
            console.log('[DELETE] CSRF token added');
        } else {
            console.error('[DELETE] CSRF token not found!');
            alert('CSRF token bulunamadi. Sayfayi yenileyin.');
            return;
        }

        // Form'u gönder
        document.body.appendChild(form);
        console.log('[DELETE] Form submitted');
        form.submit();
    } else {
        console.log('[DELETE] User cancelled deletion');
    }
}

// Debug log
console.log('[DECLINED] Declined contracts JavaScript loaded successfully');
