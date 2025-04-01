def get_brain_animation_html():
    """
    Returns HTML/CSS/JS code for a 3D brain animation
    to be displayed on the login page.
    """
    return """
    <div id="brain-animation-container">
        <div class="brain">
            <div class="hemisphere left"></div>
            <div class="hemisphere right"></div>
            <div class="synapse s1"></div>
            <div class="synapse s2"></div>
            <div class="synapse s3"></div>
            <div class="synapse s4"></div>
            <div class="synapse s5"></div>
            <div class="pulse-ring"></div>
        </div>
    </div>
    
    <style>
    #brain-animation-container {
        display: flex;
        justify-content: center;
        align-items: center;
        height: 300px;
        perspective: 1000px;
        margin-bottom: 20px;
    }
    
    .brain {
        position: relative;
        width: 180px;
        height: 140px;
        transform-style: preserve-3d;
        animation: rotate 20s infinite linear;
    }
    
    @keyframes rotate {
        0% { transform: rotateY(0) rotateX(15deg); }
        100% { transform: rotateY(360deg) rotateX(15deg); }
    }
    
    .hemisphere {
        position: absolute;
        width: 90px;
        height: 140px;
        border-radius: 100px 0 0 100px;
        background: linear-gradient(135deg, #4361EE, #7209B7);
        opacity: 0.8;
        box-shadow: 0 0 15px rgba(67, 97, 238, 0.6);
    }
    
    .hemisphere.left {
        left: 0;
        transform-origin: right;
        animation: pulse 4s infinite alternate;
    }
    
    .hemisphere.right {
        right: 0;
        transform: scaleX(-1);
        background: linear-gradient(135deg, #7209B7, #4CC9F0);
        animation: pulse 4s infinite alternate-reverse;
    }
    
    @keyframes pulse {
        0% { transform-origin: right; transform: scaleY(1) scaleX(1); }
        50% { transform-origin: right; transform: scaleY(1.05) scaleX(1.02); }
        100% { transform-origin: right; transform: scaleY(1) scaleX(1); }
    }
    
    .synapse {
        position: absolute;
        width: 5px;
        height: 5px;
        background-color: #4CC9F0;
        border-radius: 50%;
        box-shadow: 0 0 8px #4CC9F0;
        opacity: 0;
        z-index: 10;
    }
    
    .synapse.s1 {
        top: 30px;
        left: 85px;
        animation: flash 2s infinite 0.2s;
    }
    
    .synapse.s2 {
        top: 60px;
        left: 95px;
        animation: flash 2s infinite 0.5s;
    }
    
    .synapse.s3 {
        top: 90px;
        left: 80px;
        animation: flash 2s infinite 0.7s;
    }
    
    .synapse.s4 {
        top: 40px;
        left: 115px;
        animation: flash 2s infinite 1s;
    }
    
    .synapse.s5 {
        top: 110px;
        left: 100px;
        animation: flash 2s infinite 1.3s;
    }
    
    @keyframes flash {
        0% { opacity: 0; transform: scale(1); }
        50% { opacity: 1; transform: scale(1.5); }
        100% { opacity: 0; transform: scale(1); }
    }
    
    .pulse-ring {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        width: 160px;
        height: 120px;
        border: 2px solid rgba(67, 97, 238, 0.3);
        border-radius: 50%;
        opacity: 0;
        animation: pulse-ring 4s infinite;
    }
    
    @keyframes pulse-ring {
        0% { opacity: 0.8; transform: translate(-50%, -50%) scale(0.8); }
        50% { opacity: 0; transform: translate(-50%, -50%) scale(1.2); }
        100% { opacity: 0; transform: translate(-50%, -50%) scale(1.5); }
    }
    </style>
    
    <script>
    // Add any interactive JavaScript if needed
    document.addEventListener('DOMContentLoaded', function() {
        const brain = document.querySelector('.brain');
        
        // Add mouse interaction to control brain rotation
        let isMouseDown = false;
        let startX, startY;
        let rotateX = 15, rotateY = 0;
        
        brain.addEventListener('mousedown', function(e) {
            isMouseDown = true;
            startX = e.clientX;
            startY = e.clientY;
            brain.style.animation = 'none';
        });
        
        document.addEventListener('mousemove', function(e) {
            if (!isMouseDown) return;
            
            const deltaX = e.clientX - startX;
            const deltaY = e.clientY - startY;
            
            rotateY += deltaX * 0.5;
            rotateX -= deltaY * 0.5;
            
            // Limit rotation on X axis
            rotateX = Math.max(-30, Math.min(30, rotateX));
            
            brain.style.transform = `rotateY(${rotateY}deg) rotateX(${rotateX}deg)`;
            
            startX = e.clientX;
            startY = e.clientY;
        });
        
        document.addEventListener('mouseup', function() {
            isMouseDown = false;
            // Resume animation after 3 seconds
            setTimeout(() => {
                brain.style.animation = 'rotate 20s infinite linear';
            }, 3000);
        });
    });
    </script>
    """

def get_welcome_animation():
    """
    Returns HTML for the welcome animation and message on the login page.
    """
    return """
    <div class="welcome-container">
        <h1 class="welcome-title">Welcome to NeuroSync</h1>
        <div class="welcome-subtitle">Your Privacy-First AI Mental Health Companion</div>
        <div class="welcome-features">
            <div class="feature">
                <div class="feature-icon">🔒</div>
                <div class="feature-text">Privacy-Focused</div>
            </div>
            <div class="feature">
                <div class="feature-icon">🧠</div>
                <div class="feature-text">AI-Powered</div>
            </div>
            <div class="feature">
                <div class="feature-icon">📊</div>
                <div class="feature-text">Data Insights</div>
            </div>
        </div>
    </div>
    
    <style>
    .welcome-container {
        text-align: center;
        margin-top: 20px;
        margin-bottom: 30px;
        animation: fadeIn 1.5s ease-out;
    }
    
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .welcome-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #4361EE;
        margin-bottom: 10px;
        text-shadow: 0px 2px 4px rgba(0, 0, 0, 0.1);
    }
    
    .welcome-subtitle {
        font-size: 1.2rem;
        color: #718096;
        margin-bottom: 30px;
        font-weight: 400;
    }
    
    .welcome-features {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin-top: 20px;
    }
    
    .feature {
        display: flex;
        flex-direction: column;
        align-items: center;
        animation: slideUp 0.8s ease-out forwards;
        opacity: 0;
    }
    
    .feature:nth-child(1) { animation-delay: 0.2s; }
    .feature:nth-child(2) { animation-delay: 0.4s; }
    .feature:nth-child(3) { animation-delay: 0.6s; }
    
    @keyframes slideUp {
        from { opacity: 0; transform: translateY(20px); }
        to { opacity: 1; transform: translateY(0); }
    }
    
    .feature-icon {
        font-size: 2.5rem;
        margin-bottom: 10px;
        background: #EDF2F7;
        width: 70px;
        height: 70px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        box-shadow: 0px 4px 10px rgba(0, 0, 0, 0.1);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .feature:hover .feature-icon {
        transform: translateY(-5px);
        box-shadow: 0px 6px 15px rgba(0, 0, 0, 0.15);
    }
    
    .feature-text {
        font-size: 1rem;
        font-weight: 600;
        color: #4A5568;
    }
    </style>
    """