# Generador de Contraseñas Seguras con Frontend Web
# Proyecto simple pero profesional para CV

from flask import Flask, render_template, request, jsonify
import random
import string
import secrets
import json
from datetime import datetime
import hashlib
import os

app = Flask(__name__)

class PasswordGenerator:
    def __init__(self):
        self.lowercase = string.ascii_lowercase
        self.uppercase = string.ascii_uppercase
        self.digits = string.digits
        self.symbols = "!@#$%^&*()_+-=[]{}|;:,.<>?"
        
    def generate_password(self, length=12, include_uppercase=True, 
                          include_lowercase=True, include_digits=True, 
                          include_symbols=True, exclude_ambiguous=False):
        """Generar contraseña segura con opciones personalizables"""
        
        if length < 4:
            return {"error": "La longitud mínima es 4 caracteres"}
        
        character_pool = ""
        required_chars = []
        
        # Construir pool de caracteres
        if include_lowercase:
            character_pool += self.lowercase
            required_chars.append(secrets.choice(self.lowercase))
            
        if include_uppercase:
            character_pool += self.uppercase
            required_chars.append(secrets.choice(self.uppercase))
            
        if include_digits:
            character_pool += self.digits
            required_chars.append(secrets.choice(self.digits))
            
        if include_symbols:
            character_pool += self.symbols
            required_chars.append(secrets.choice(self.symbols))
        
        if not character_pool:
            return {"error": "Debe seleccionar al menos un tipo de caracter"}
        
        # Excluir caracteres ambiguos si se solicita
        if exclude_ambiguous:
            ambiguous = "0O1lI"
            character_pool = ''.join(c for c in character_pool if c not in ambiguous)
        
        # Generar contraseña
        password = required_chars[:]
        
        # Completar con caracteres aleatorios
        for _ in range(length - len(required_chars)):
            password.append(secrets.choice(character_pool))
        
        # Mezclar caracteres
        secrets.SystemRandom().shuffle(password)
        
        password_str = ''.join(password)
        
        # Calcular fortaleza
        strength = self.calculate_strength(password_str)
        
        return {
            "password": password_str,
            "strength": strength,
            "length": length,
            "entropy": self.calculate_entropy(password_str)
        }
    
    def calculate_strength(self, password):
        """Calcular fortaleza de contraseña"""
        score = 0
        feedback = []
        
        # Longitud
        if len(password) >= 12:
            score += 25
        elif len(password) >= 8:
            score += 15
        else:
            feedback.append("Muy corta")
        
        # Caracteres diversos
        if any(c.islower() for c in password):
            score += 10
        else:
            feedback.append("Falta minúsculas")
            
        if any(c.isupper() for c in password):
            score += 10
        else:
            feedback.append("Falta mayúsculas")
            
        if any(c.isdigit() for c in password):
            score += 10
        else:
            feedback.append("Falta números")
            
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            score += 15
        else:
            feedback.append("Falta símbolos")
        
        # Patrones comunes
        if not any(password[i:i+3] in "abc123qwe" for i in range(len(password)-2)):
            score += 10
        
        # Repeticiones
        if len(set(password)) > len(password) * 0.7:
            score += 10
        
        # Determinar nivel
        if score >= 80:
            level = "Muy Fuerte"
            color = "success"
        elif score >= 60:
            level = "Fuerte"
            color = "primary"
        elif score >= 40:
            level = "Moderada"
            color = "warning"
        else:
            level = "Débil"
            color = "danger"
        
        return {
            "score": min(score, 100),
            "level": level,
            "color": color,
            "feedback": feedback
        }
    
    def calculate_entropy(self, password):
        """Calcular entropía de la contraseña"""
        import math
        
        charset_size = 0
        
        if any(c.islower() for c in password):
            charset_size += 26
        if any(c.isupper() for c in password):
            charset_size += 26
        if any(c.isdigit() for c in password):
            charset_size += 10
        if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
            charset_size += 23
        
        if charset_size == 0:
            return 0
        
        entropy = len(password) * math.log2(charset_size)
        return round(entropy, 2)
    
    def generate_multiple_passwords(self, count=5, **kwargs):
        """Generar múltiples contraseñas"""
        passwords = []
        for _ in range(count):
            result = self.generate_password(**kwargs)
            if "error" not in result:
                passwords.append(result)
        return passwords
    
    def check_common_passwords(self, password):
        """Verificar si la contraseña está en lista de contraseñas comunes"""
        common_passwords = [
            "123456", "password", "123456789", "12345678", "12345",
            "1234567", "1234567890", "qwerty", "abc123", "111111",
            "123123", "admin", "letmein", "welcome", "monkey"
        ]
        
        return password.lower() in [p.lower() for p in common_passwords]

# Instancia del generador
generator = PasswordGenerator()

@app.route('/')
def index():
    """Página principal"""
    # Ahora renderiza el archivo index.html desde la carpeta 'templates'
    return render_template('index.html')

@app.route('/generate', methods=['POST'])
def generate_password_route(): # Renombrado para evitar conflicto con el método de la clase
    """Endpoint para generar contraseña"""
    try:
        data = request.get_json()
        
        length = int(data.get('length', 12))
        include_uppercase = data.get('uppercase', True)
        include_lowercase = data.get('lowercase', True)
        include_digits = data.get('digits', True)
        include_symbols = data.get('symbols', True)
        exclude_ambiguous = data.get('exclude_ambiguous', False)
        
        result = generator.generate_password(
            length=length,
            include_uppercase=include_uppercase,
            include_lowercase=include_lowercase,
            include_digits=include_digits,
            include_symbols=include_symbols,
            exclude_ambiguous=exclude_ambiguous
        )
        
        # Verificar contraseñas comunes
        if "password" in result:
            result["is_common"] = generator.check_common_passwords(result["password"])
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/generate_multiple', methods=['POST'])
def generate_multiple():
    """Generar múltiples contraseñas"""
    try:
        data = request.get_json()
        count = min(int(data.get('count', 5)), 10)  # Máximo 10
        
        # Extraer parámetros
        params = {
            'length': int(data.get('length', 12)),
            'include_uppercase': data.get('uppercase', True),
            'include_lowercase': data.get('lowercase', True),
            'include_digits': data.get('digits', True),
            'include_symbols': data.get('symbols', True),
            'exclude_ambiguous': data.get('exclude_ambiguous', False)
        }
        
        passwords = generator.generate_multiple_passwords(count, **params)
        
        return jsonify({"passwords": passwords})
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route('/check_strength', methods=['POST'])
def check_strength():
    """Verificar fortaleza de contraseña personalizada"""
    try:
        data = request.get_json()
        password = data.get('password', '')
        
        if not password:
            return jsonify({"error": "Contraseña requerida"}), 400
        
        strength = generator.calculate_strength(password)
        entropy = generator.calculate_entropy(password)
        is_common = generator.check_common_passwords(password)
        
        return jsonify({
            "strength": strength,
            "entropy": entropy,
            "is_common": is_common,
            "length": len(password)
        })
        
    except Exception as e:
        return jsonify({"error": str(e)}), 400

if __name__ == '__main__':
    print("Proyecto listo para ejecutar!")
    print("\nPara ejecutar:")
    print("1. Asegúrate de tener la siguiente estructura de carpetas y archivos:")
    print("   tu_proyecto/")
    print("   ├── app.py")
    print("   └── templates/")
    print("       └── index.html")
    print("2. pip install flask")
    print("3. python app.py")
    print("4. Abrir http://localhost:5000")
    print("\nCaracterísticas del proyecto:")
    print("- Frontend responsive con Bootstrap")
    print("- Generador de contraseñas seguras")
    print("- Verificador de fortaleza")
    print("- Cálculo de entropía")
    print("- Interfaz moderna y atractiva")
    print("- Código limpio y documentado")
    
    app.run(debug=True, port=5000)