function getCookie(name) {
    const value = `; ${document.cookie}`
    const parts = value.split(`; ${name}=`)
    if (parts.length === 2) return parts.pop().split(';').shift()
}


async function saveScore(url, subject_id, csrftoken, cookie_patten, answer) {
    if (answer.classList.contains("answered")) {
        return
    }
    const formData = new FormData()
    formData.append("csrfmiddlewaretoken", csrftoken)
    formData.append("subject_id", subject_id)
    formData.append("score", answer.dataset.score)
    try {
        const response = await fetch(url, {
            method: "POST",
            body: formData,
            headers: {
                "X-Requested-With": "XMLHttpRequest",
            }
        })
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`)
        }
        const json = await response.json()
        if (json.status === "ok") {
            const answers = answer.closest(".answers")
            for (const node of answers.querySelectorAll(".answer.answered")) {
                node.classList.remove("answered")
            }
            answer.classList.add("answered")
            const frame = answer.closest(".help-rating-frame")
            const feedbackMessage = frame.querySelector(".feedback-message div")
            feedbackMessage.style.display = "block"
            setTimeout(function() {
                feedbackMessage.style.display = "none"
            }, 2000)
        }
    } catch (error) {
        console.error(error.message)
    }
}


document.addEventListener("DOMContentLoaded", function() {
    for (const frame of document.querySelectorAll(".help-rating-frame")) {
        const answers = frame.querySelector(".answers")
        const cookie_name = answers.dataset.cookie_pattern.replace(new RegExp(answers.dataset.cookie_replacement), answers.dataset.subject_id)
        const cookie_value = getCookie(cookie_name)
        if (answers.dataset.url) {
            for (const answer of answers.querySelectorAll(".answer")) {
                if (answer.dataset.score == cookie_value) {
                    answer.classList.add("answered")
                }
                answer.addEventListener("click", function () {
                    saveScore(
                        answers.dataset.url,
                        answers.dataset.subject_id,
                        answers.dataset.csrftoken,
                        answers.dataset.cookie_patten,
                        answer
                    )
                })
                answer.style.cursor = "pointer"
            }
        } else {
            console.error("Incorrectly set HELP_RATING_PATH_NAME_SAVE_SCORE in django.settings. See README in the project djangocms-help-rating.")
        }
    }
})
