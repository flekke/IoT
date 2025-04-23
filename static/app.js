function showPopup(message){
    const popup = document.getElementById("popup");
    popup.querySelector("p").textContent = message;
    popup.classList.remove("hidden");
}

function closePopup(){
    const popup = document.getElementById("popup");
    popup.classList.add("hidden");
}



async function fetchData() {
    const latest = await fetch("/latest").then(res => res.json());
    const rec = await fetch("/recommendation").then(res => res.json());

    document.getElementById("timestamp").textContent = latest.timestamp;
    document.getElementById("temp").textContent = latest.temp;
    document.getElementById("hum").textContent = latest.hum;

    document.getElementById("rec-temp").textContent = rec.recommended_temp;
    document.getElementById("rec-hum").textContent = rec.recommended_hum;
}

async function sendFeedback(temp_feedback, hum_feedback) {
    console.log("sending:", temp_feedback, hum_feedback);
    await fetch("/feedback", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ 
		temp: Number(temp_feedback),
		hum: Number(hum_feedback)
        }),
    });
    showPopup("feedback submitted");
    fetchData(); // 피드백 후 추천값 새로고침
}


fetchData();
setInterval(fetchData, 10000); // 10초마다 자동 새로고침
