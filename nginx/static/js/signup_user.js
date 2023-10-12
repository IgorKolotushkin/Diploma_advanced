async function userRegister() {
    let apiKey = 'api-key';
    let data
    // при нажатии на кнопку отправки формы идет запрос к /register
    if (document.getElementById("email_reg").value !== "" && document.getElementById("psw_reg").value !== "")
        data = await fetch("/api/register", {
            method: "POST",
            headers: {"Accept": "application/json", "Content-Type": "application/json"},
            body: JSON.stringify({
                email: document.getElementById("email_reg").value,
                password: document.getElementById("psw_reg").value,
                password_repeat: document.getElementById("psw2").value
            })
        }).then(response => response.json());
    if (data) {
        sessionStorage.setItem(apiKey, data.apikey);
        document.getElementById('id02').style.display = 'none';
    }
}