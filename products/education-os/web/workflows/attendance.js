export function loadWorkflow(root){
  if(!root) return;
  root.innerHTML = '<section class="workflow-placeholder"><h2>Attendance Workflow</h2><p>Workflow module regenerated.</p></section>';
}

export function initWorkflow(root){
  return;
}

export function openAttendanceWorkflow(){
  const root=document.querySelector("#workflow-root")||document.body;
  loadWorkflow(root);
}
