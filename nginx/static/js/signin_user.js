async function funcApikey() {
    let apiKey = 'api-key';
    let data
    // при нажатии на кнопку отправки формы идет запрос к /login для получения api-key
    if (document.getElementById("email").value !== "" && document.getElementById("psw").value !== "")
        data = await fetch("/api/login", {
            method: "POST",
            headers: {
                "Accept": "application/json",
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                email: document.getElementById("email").value,
                password: document.getElementById("psw").value
            })
        }).then(response => response.json());
    if (data) {
        document.getElementById('id01').style.display = "none";
        sessionStorage.setItem(apiKey, data.apikey);
    }
}