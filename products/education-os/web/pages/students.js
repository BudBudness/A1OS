
import { api } from "../js/education-api.js";

import { loadWorkflow } from "../workflows/students.js";

export async function renderStudents() {

    queueMicrotask(() => {
        const workflowRoot=document.querySelector("#workflow-root");
        if (typeof loadWorkflow==="function" && workflowRoot) {
            loadWorkflow(workflowRoot);
        }

        const ids={
            renderStudents:"#register-student",
            renderAdmissions:"#new-admission",
            renderFees:"#record-payment",
            renderOperations:"#new-operation"
        };

        const id=ids[renderStudents];

        if(id){
            document.querySelector(id)?.addEventListener("click",()=>{}, {once:true});
        }
    });


    const students = await api.students.list();

    return `
        <section class="card">
            <div class="toolbar">
                <h2 class="section-title">Student Registry</h2>
                <button class="btn btn-primary" id="register-student">
                    + Register Student
                </button>
            </div>

            <div class="table-wrap">
                ${
                    students.length
                        ? `
                            <table>
                                <thead>
                                    <tr>
                                        <th>ID</th>
                                        <th>Name</th>
                                        <th>Date of Birth</th>
                                        <th>Gender</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${students
                                        .map(
                                            s => `
                                                <tr>
                                                    <td>${s.id}</td>
                                                    <td>${s.first_name || ""} ${s.last_name || ""}</td>
                                                    <td>${s.date_of_birth || "-"}</td>
                                                    <td>${s.gender || "-"}</td>
                                                </tr>
                                            `
                                        )
                                        .join("")}
                                </tbody>
                            </table>
                        `
                        : "<div class='empty'>No students registered yet.</div>"
                }
            </div>
        </section>
    `;
}



