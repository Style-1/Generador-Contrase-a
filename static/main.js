// main.js

// Actualizar valores de sliders
document.getElementById('lengthSlider').addEventListener('input', function() {
    document.getElementById('lengthValue').textContent = this.value;
});

document.getElementById('countSlider').addEventListener('input', function() {
    document.getElementById('countValue').textContent = this.value;
});

// Generar contraseña
async function generatePassword() {
    const data = {
        length: parseInt(document.getElementById('lengthSlider').value),
        uppercase: document.getElementById('uppercase').checked,
        lowercase: document.getElementById('lowercase').checked,
        digits: document.getElementById('digits').checked,
        symbols: document.getElementById('symbols').checked,
        exclude_ambiguous: document.getElementById('excludeAmbiguous').checked,
        count: parseInt(document.getElementById('countSlider').value)
    };

    try {
        // Las rutas están correctas para un backend local en el mismo origen
        const endpoint = data.count > 1 ? '/generate_multiple' : '/generate';
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });

        const result = await response.json();
        displayResults(result, data.count > 1);
    } catch (error) {
        console.error('Error:', error);
        alert('Error al generar contraseña. Asegúrate de que el backend esté funcionando.');
    }
}

// Mostrar resultados
function displayResults(result, multiple) {
    const resultsDiv = document.getElementById('results');
    const passwordList = document.getElementById('passwordList');
    
    if (result.error) {
        passwordList.innerHTML = `<div class="alert alert-danger">${result.error}</div>`;
        resultsDiv.style.display = 'block';
        return;
    }

    let html = '';
    
    if (multiple && result.passwords) {
        result.passwords.forEach((pwd, index) => {
            html += createPasswordCard(pwd, index + 1);
        });
    } else {
        html = createPasswordCard(result);
    }

    passwordList.innerHTML = html;
    resultsDiv.style.display = 'block';
}

// Crear tarjeta de contraseña
function createPasswordCard(pwd, index = null) {
    const title = index ? `Contraseña ${index}` : 'Contraseña Generada';
    const commonAlert = pwd.is_common ? 
        '<div class="alert alert-warning mt-2"><i class="fas fa-exclamation-triangle"></i> ¡Atención! Esta contraseña es muy común</div>' : '';
    
    return `
        <div class="card mb-3">
            <div class="card-body">
                <h6>${title}</h6>
                <div class="password-display">
                    <span>${pwd.password}</span>
                    <button class="btn btn-sm" onclick="copyPassword('${pwd.password}')">
                        <i class="fas fa-copy"></i> Copiar
                    </button>
                </div>
                <div class="row mt-3">
                    <div class="col-md-6">
                        <small>Fortaleza: <span class="badge bg-${pwd.strength.color}">${pwd.strength.level}</span></small>
                        <div class="progress mt-1">
                            <div class="progress-bar bg-${pwd.strength.color}" role="progressbar" style="width: ${pwd.strength.score}%" aria-valuenow="${pwd.strength.score}" aria-valuemin="0" aria-valuemax="100"></div>
                        </div>
                    </div>
                    <div class="col-md-6 text-md-end">
                        <small>Entropía: ${pwd.entropy} bits</small><br>
                        <small>Longitud: ${pwd.length} caracteres</small>
                    </div>
                </div>
                ${commonAlert}
            </div>
        </div>
    `;
}

// Copiar contraseña
function copyPassword(password) {
    navigator.clipboard.writeText(password).then(() => {
        alert('Contraseña copiada al portapapeles');
    }).catch(err => {
        console.error('Error al copiar:', err);
        alert('Error al copiar la contraseña. Por favor, cópiala manualmente.');
    });
}

// Verificar fortaleza de contraseña personalizada
async function checkStrength() {
    const password = document.getElementById('customPassword').value;
    
    if (!password) {
        alert('Por favor, ingresa una contraseña para verificarla.');
        return;
    }

    try {
        const response = await fetch('/check_strength', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ password })
        });

        const result = await response.json();
        displayCustomResult(result);
    } catch (error) {
        console.error('Error:', error);
        alert('Error al verificar contraseña. Asegúrate de que el backend esté funcionando.');
    }
}

// Mostrar resultado personalizado
function displayCustomResult(result) {
    const div = document.getElementById('customResult');
    
    if (result.error) {
        div.innerHTML = `<div class="alert alert-danger">${result.error}</div>`;
        return;
    }

    const commonAlert = result.is_common ? 
        '<div class="alert alert-danger mt-2"><i class="fas fa-exclamation-triangle"></i> ¡Peligro! Esta contraseña está en la lista de contraseñas comunes</div>' : '';
    
    const feedback = result.strength.feedback.length > 0 ? 
        `<div class="mt-2"><small>Mejoras sugeridas: ${result.strength.feedback.join(', ')}</small></div>` : '';

    div.innerHTML = `
        <div class="card">
            <div class="card-body">
                <div class="row">
                    <div class="col-md-6">
                        <h6>Fortaleza: <span class="badge bg-${result.strength.color}">${result.strength.level}</span></h6>
                        <div class="progress">
                            <div class="progress-bar bg-${result.strength.color}" role="progressbar" style="width: ${result.strength.score}%" aria-valuenow="${result.strength.score}" aria-valuemin="0" aria-valuemax="100"></div>
                        </div>
                    </div>
                    <div class="col-md-6 text-md-end">
                        <small>Entropía: ${result.entropy} bits</small><br>
                        <small>Longitud: ${result.length} caracteres</small>
                    </div>
                </div>
                ${feedback}
                ${commonAlert}
            </div>
        </div>
    `;
}

// Mostrar/ocultar contraseña
function togglePassword() {
    const input = document.getElementById('customPassword');
    const icon = document.getElementById('eyeIcon');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.className = 'fas fa-eye-slash';
    } else {
        input.type = 'password';
        icon.className = 'fas fa-eye';
    }
}

// Generar contraseña inicial
window.onload = function() {
    generatePassword();
};