const form = document.createElement('form');
    form.method = 'POST';
    form.action = '';

    form.innerHTML = `
      <h2>Регистрация</h2>
      <label>Имя пользователя: <input type="text" name="username" required></label><br>
      <label>Email: <input type="email" name="email" required></label><br>
      <label>Пароль: <input type="password" name="password" required></label><br>
      <button type="submit">Зарегистрироваться</button>
    `;

    document.body.appendChild(form);

    form.addEventListener('submit', function(e) {
      e.preventDefault();

      const formData = new FormData(form);
      const username = formData.get('username');
      const email = formData.get('email');
      const password = formData.get('password');

      if (!username || !email || !password) {
        alert('Пожалуйста, заполните все поля');
        return;
      };

      console.log('Регистрация успешна:', { username, email, password });

      form.reset();
    });
console.log("Дарова");