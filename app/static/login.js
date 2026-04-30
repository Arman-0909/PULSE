function switchTab(t) {
    document.getElementById('loginPanel').classList.toggle('active', t === 'login');
    document.getElementById('signupPanel').classList.toggle('active', t === 'signup');
    document.querySelectorAll('.tab').forEach((b, i) => b.classList.toggle('active', i === (t === 'login' ? 0 : 1)));
    document.getElementById('formTitle').textContent = t === 'login' ? 'Sign in to Pulse' : 'Create an account';
    document.getElementById('formSubtitle').textContent = t === 'login' ? 'Enter your details to access the console' : 'Register to start monitoring services';
}
