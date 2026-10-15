
const API = "http://127.0.0.1:5000/api/opportunities";

const form = document.getElementById("opportunityForm");
const list = document.getElementById("opportunityList");
const message = document.getElementById("message");

function showMessage(text, error = false) {
    message.textContent = text;
    message.className = error ? "error" : "success";
}

async function request(url, options = {}) {
    const response = await fetch(url, options);
    const data = await response.json().catch(() => ({}));

    if (!response.ok) {
        throw new Error(data.error || "Request failed.");
    }

    return data;
}

async function loadOpportunities() {
    list.textContent = "Loading opportunities...";

    try {
        const data = await request(API);
        const opportunities = Array.isArray(data)
            ? data
            : data.opportunities || [];

        list.replaceChildren();

        if (opportunities.length === 0) {
            list.textContent = "No opportunities found.";
            return;
        }

        opportunities.forEach(op => {
            const card = document.createElement("article");
            card.className = "opportunity-card";

            const title = document.createElement("h3");
            title.textContent = op.title;

            const details = document.createElement("p");
            details.textContent =
                `ID: ${op.id} | Area: ${op.research_area} | ` +
                `Faculty: ${op.faculty_name} | Status: ${op.status}`;

            const description = document.createElement("p");
            description.textContent = op.description;

            const skills = document.createElement("p");
            skills.textContent = "Skills: " + op.required_skills;

            const deadline = document.createElement("p");
            deadline.textContent =
                "Deadline: " + op.application_deadline;

            const edit = document.createElement("button");
            edit.textContent = "Edit";
            edit.onclick = () => editOpportunity(op);

            const close = document.createElement("button");
            close.textContent = "Close Opportunity";
            close.disabled = op.status === "Closed";
            close.onclick = () => closeOpportunity(op.id);

            const remove = document.createElement("button");
            remove.textContent = "Delete";
            remove.onclick = () => deleteOpportunity(op.id);

            card.append(title, details, description, skills, deadline,
                edit, close, remove);
            list.appendChild(card);
        });
    } catch (error) {
        list.textContent = "Could not load opportunities: " + error.message;
    }
}

form.addEventListener("submit", async function(event) {
    event.preventDefault();

    if (!form.reportValidity()) return;

    const id = document.getElementById("opportunityId").value;

    const body = {
        title: document.getElementById("title").value.trim(),
        description: document.getElementById("description").value.trim(),
        research_area: document.getElementById("research_area").value.trim(),
        faculty_name: document.getElementById("faculty_name").value.trim(),
        department: document.getElementById("department").value.trim(),
        required_skills: document.getElementById("required_skills").value.trim(),
        available_positions: Number(
            document.getElementById("available_positions").value
        ),
        application_deadline:
            document.getElementById("application_deadline").value,
        status: "Open"
    };

    if (Object.values(body).some(v => v === "" || v === null) ||
        body.available_positions < 1) {
        showMessage("Please complete every field correctly.", true);
        return;
    }

    try {
        await request(id ? `${API}/${id}` : API, {
            method: id ? "PUT" : "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(body)
        });

        showMessage(id ? "Opportunity updated!" : "Opportunity created!");
        resetForm();
        await loadOpportunities();
    } catch (error) {
        showMessage(error.message, true);
    }
});

function editOpportunity(op) {
    document.getElementById("opportunityId").value = op.id;

    [
        "title", "description", "research_area", "faculty_name",
        "department", "required_skills", "available_positions",
        "application_deadline"
    ].forEach(key => {
        document.getElementById(key).value = op[key] ?? "";
    });

    document.getElementById("formTitle").textContent = "Edit Opportunity";
    document.getElementById("cancelEdit").hidden = false;
    window.scrollTo({ top: 0, behavior: "smooth" });
}

function resetForm() {
    form.reset();
    document.getElementById("opportunityId").value = "";
    document.getElementById("formTitle").textContent =
        "Add Research Opportunity";
    document.getElementById("cancelEdit").hidden = true;
}

document.getElementById("cancelEdit").onclick = resetForm;
document.getElementById("refreshButton").onclick = loadOpportunities;

async function closeOpportunity(id) {
    if (!confirm("Close this opportunity?")) return;

    try {
        await request(`${API}/${id}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ status: "Closed" })
        });

        showMessage("Opportunity closed.");
        await loadOpportunities();
    } catch (error) {
        showMessage(error.message, true);
    }
}

async function deleteOpportunity(id) {
    if (!confirm("Are you sure you want to delete this opportunity?")) return;

    try {
        await request(`${API}/${id}`, { method: "DELETE" });
        showMessage("Opportunity deleted.");
        await loadOpportunities();
    } catch (error) {
        showMessage(error.message, true);
    }
}

loadOpportunities();
