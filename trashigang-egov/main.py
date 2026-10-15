from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

app = FastAPI(title="Trashigang Dzongkhag Integrated Governance Platform")
templates = Jinja2Templates(directory="templates")

FISCAL_YEAR = "2026-2027"
dispatch_counter = 142

@app.get("/")
async def read_root(request: Request, view: str = "public"):
    return templates.TemplateResponse(
        request=request,
        name="index.html",
        context={"active_view": view}
    )

@app.post("/api/submit-application")
async def submit_application(
    applicant_name: str = Form(...),
    cid_number: str = Form(...),
    sector: str = Form(...),
    gewog: str = Form(...),
    purpose: str = Form(...)
):
    global dispatch_counter
    dispatch_counter += 1
    dispatch_no = f"TRASHIGANG/{sector[:4].upper()}/{FISCAL_YEAR}/{dispatch_counter:05d}"
    print(f"[NEW APPLICATION] Ref: {dispatch_no} | Applicant: {applicant_name} ({cid_number})")
    return RedirectResponse(url="/?view=supervisor-workflow", status_code=303)

@app.post("/api/process-action")
async def process_action(
    app_id: str = Form(...),
    action: str = Form(...),
    remarks: str = Form(...)
):
    print(f"[ACTION] {app_id} -> Action: {action} | Remarks: {remarks}")
    return RedirectResponse(url="/?view=supervisor-workflow", status_code=303)

@app.post("/api/create-notesheet")
async def create_notesheet(
    target_supervisor: str = Form(...),
    budget_head: str = Form(...),
    subject: str = Form(...)
):
    print(f"[NOTESHEET] Target: {target_supervisor} | Head: {budget_head} | Subject: {subject}")
    return RedirectResponse(url="/?view=notesheets", status_code=303)
