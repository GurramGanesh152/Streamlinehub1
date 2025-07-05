document.getElementById("register-btn").addEventListener("click", async () => {
    const username = document.getElementById("reg-username").value;
    const password = document.getElementById("reg-password").value;

    const response = await fetch("http://localhost:5001/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
    });
    const data = await response.json();
    alert(data.message);
});

document.getElementById("login-btn").addEventListener("click", async () => {
    const username = document.getElementById("login-username").value;
    const password = document.getElementById("login-password").value;

    const response = await fetch("http://localhost:5001/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password }),
    });
    const data = await response.json();
    alert(data.message);
    if (response.ok) {
        document.getElementById("auth").style.display = "none";
        document.getElementById("video-section").style.display = "block";
        loadvideos();
    }
});

document.getElementById("video-btn").addEventListener("click", async () => {
    const videoInput = document.getElementById("video-input");
    const caption = document.getElementById("caption-input").value;

    const formData = new FormData();
    formData.append("video", videoInput.files[0]);
    formData.append("caption", caption);

    const response = await fetch("http://localhost:5003/videos", {
        method: "POST",
        body: formData,
    });
    const data = await response.json();
    alert(data.message);
    if (response.ok) {
        loadvideos();
        document.getElementById("caption-input").value = '';
        videoInput.value = '';
    }
});

async function loadvideos() {
    const response = await fetch("http://localhost:5003/videos");
    const videos = await response.json();
    const videoList = document.getElementById("video-list");
    videoList.innerHTML = '';
    videos.forEach((video) => {
        const videoDiv = document.createElement("div");
        videoDiv.innerHTML = `<video controls style="width:100%;">
                                    <source src="${video.video_path}" type="video/mp4">
                                    Your browser does not support the video tag.
                                  </video><p>${video.caption}</p>`;
        videoList.appendChild(videoDiv);
    });
}
