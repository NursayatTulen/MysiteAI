let apiURL = "https://nursayattulen.onrender.com/ask"; // Локал емес, интернеттегі сервер

function askQuestion() {
    let question = document.getElementById("question").value;
    if (question.trim() === "") return;

    let chatBox = document.getElementById("chat-box");

    let questionElement = document.createElement("div");
    questionElement.classList.add("question");
    questionElement.innerText = "You: " + question;
    chatBox.appendChild(questionElement);

    fetch(apiURL, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ question: question })
    })
    .then(response => response.json())
    .then(data => {
        let answerElement = document.createElement("div");
        answerElement.classList.add("answer");
        answerElement.innerText = "Nursayat: " + data.answer;
        chatBox.appendChild(answerElement);

        chatBox.scrollTop = chatBox.scrollHeight; // Авто-прокрутка
    })
    .catch(error => {
        console.error("Қате:", error);
        let errorElement = document.createElement("div");
        errorElement.classList.add("answer");
        errorElement.innerText = "Бот: Серверге қосылу мүмкін емес.";
        chatBox.appendChild(errorElement);
    });

    document.getElementById("question").value = "";
}