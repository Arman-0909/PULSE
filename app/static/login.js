// Switch between login and signup tabs
function switchTab(tab) {
    document.getElementById('pLogin').classList.toggle('on', tab === 'login');
    document.getElementById('pSignup').classList.toggle('on', tab === 'signup');
    document.querySelectorAll('.tab').forEach((btn, i) => {
        btn.classList.toggle('on', i === (tab === 'login' ? 0 : 1));
    });
}
