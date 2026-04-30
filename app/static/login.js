// login tab switch
function sw(t) {
    document.getElementById('pLogin').classList.toggle('on', t === 'login');
    document.getElementById('pSignup').classList.toggle('on', t === 'signup');
    document.querySelectorAll('.tab').forEach((b, i) => b.classList.toggle('on', i === (t === 'login' ? 0 : 1)));
}
