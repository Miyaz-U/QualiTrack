function showSection(id) {
    document.querySelectorAll('.section').forEach(s => s.style.display = 'none');
    document.getElementById(id).style.display = 'block';
}

// Generic AJAX form handler (GET forms)
function setupAjaxForm(formId, resultId) {
    const form = document.getElementById(formId);
    if (!form) return;

    form.addEventListener("submit", function (e) {
        e.preventDefault();

        const endpoint = form.getAttribute("data-endpoint"); // ✅ read from data-endpoint
        const formData = new FormData(form);
        const params = new URLSearchParams(formData).toString();

        fetch(endpoint + "?" + params)
            .then(res => res.text())
            .then(html => {
                document.getElementById(resultId).innerHTML = html;
            })
            .catch(err => {
                document.getElementById(resultId).innerHTML = "<p class='text-danger'>Error loading data</p>";
                console.error(err);
            });
    });
}

document.addEventListener("DOMContentLoaded", function () {
    // Setup AJAX forms
    setupAjaxForm("userstories-form", "userstories-table");
    setupAjaxForm("defects-form", "defects-table");
    setupAjaxForm("testcases-form", "testcases-table");
    setupAjaxForm("efforts-form", "efforts-table");

    // Dependent dropdown: Defects -> User Stories filtered by Sprint
    const sprintDef = document.getElementById("sprint_def");
    const userStoryDef = document.getElementById("user_story_def");

    if (sprintDef && userStoryDef) {
        sprintDef.addEventListener("change", function () {
            const sprintId = sprintDef.value;

            if (!sprintId) {
                userStoryDef.innerHTML = '<option value="">-- All --</option>';
                return;
            }

            fetch(`/userstories-for-sprint/?sprint_id=${sprintId}`)
                .then(res => res.json())
                .then(data => {
                    userStoryDef.innerHTML = '<option value="">-- All --</option>';
                    data.forEach(story => {
                        const opt = document.createElement("option");
                        opt.value = story.id;
                        opt.textContent = story.title;
                        userStoryDef.appendChild(opt);
                    });
                })
                .catch(err => {
                    console.error("Error fetching user stories:", err);
                });
        });
    }

    // Upload form AJAX (POST with file)
    const uploadForm = document.getElementById("upload-form");
    if (uploadForm) {
        uploadForm.addEventListener("submit", function (e) {
            e.preventDefault();

            const uploadUrl = this.getAttribute("data-upload-url"); // ✅ dynamic
            let formData = new FormData(this);

            fetch(uploadUrl, {
                method: "POST",
                body: formData,
                headers: {
                    "X-CSRFToken": document.querySelector("[name=csrfmiddlewaretoken]").value
                }
            })
            .then(res => res.json())
            .then(data => {
                if (data.success) {
                    showToast("✅ " + data.message, "success");
                } else {
                    showToast("❌ Error: " + data.error, "danger");
                }
            })
            .catch(err => {
                console.error("Upload failed:", err);
                showToast("❌ Upload failed due to network error.", "danger");
            });
        });
    }

    // Bootstrap Toast helper
    function showToast(message, type = "info") {
        const toastContainer = document.createElement("div");
        toastContainer.className = `toast align-items-center text-bg-${type} border-0 show position-fixed bottom-0 end-0 m-3`;
        toastContainer.role = "alert";
        toastContainer.innerHTML = `
          <div class="d-flex">
            <div class="toast-body">${message}</div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
          </div>
        `;
        document.body.appendChild(toastContainer);

        setTimeout(() => {
            toastContainer.remove();
        }, 400000);
    }
});