// ID único para esta conversación
let sessionId = 'sesion_' + Date.now();

async function enviarMensaje() {
    const input = document.getElementById('userInput');
    const texto = input.value.trim();
    
    if (!texto) return;
    
    // Mostrar mensaje del usuario en el chat
    agregarMensaje(texto, 'user');
    input.value = '';
    
    // Mostrar indicador de "escribiendo"
    const indicador = agregarMensaje('🤔 Pensando...', 'bot', true);
    
    try {
        // Enviar al main.py
        const respuesta = await fetch('http://localhost:8000/chat', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                texto: texto,
                session_id: sessionId
            })
        });
        
        const datos = await respuesta.json();
        
        // Eliminar el indicador 
        indicador.remove();
        
        // Mostrar la respuesta real
        agregarMensaje(datos.respuesta, 'bot');
        
    } catch (error) {
        indicador.remove();
        agregarMensaje('❌ Error: ¿El servidor está corriendo?', 'bot');
        console.error('Error:', error);
    }
}

function agregarMensaje(texto, tipo, esTemporal = false) {
    const messagesContainer = document.getElementById('messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${tipo}`;
    messageDiv.textContent = texto;
    
    messagesContainer.appendChild(messageDiv);
    messagesContainer.scrollTop = messagesContainer.scrollHeight;
    
    return messageDiv;
}

// Conectar botones
document.getElementById('sendBtn').addEventListener('click', enviarMensaje);
document.getElementById('userInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') enviarMensaje();
});

console.log('✅ Frontend cargado correctamente');