from flask import Flask, render_template, request, redirect, url_for, session, send_from_directory
import os
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.graphics.shapes import Drawing, Circle, String, Rect

app = Flask(__name__)
app.secret_key = 'bhutan_portal_secret_key'

UPLOAD_FOLDER = os.path.join(os.getcwd(), 'uploads')
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

WORK_CATEGORIES = {
    "New Construction": {"tat": "30 days (1 month)", "path": "PATH A"},
    "Reconstruction": {"tat": "30 days (1 month)", "path": "PATH A"},
    "Major Renovation": {"tat": "30 days (1 month)", "path": "PATH A / PATH B"},
    "Minor Renovation": {"tat": "7 days (1 week)", "path": "PATH B"},
    "Site Development Work": {"tat": "7 days (1 week)", "path": "PATH B"}
}

events = [
    {"id": 1, "date": "2026-10-15", "title": "Trashigang Tshechu Preparation Meeting", "location": "Dzongkhag Hall", "type": "Cultural Event"},
    {"id": 2, "date": "2026-10-22", "title": "Quarterly Heritage Conservation Site Inspection", "location": "Radhi Gewog", "type": "Inspection"},
    {"id": 3, "date": "2026-11-01", "title": "Annual Lhakhang Management Review", "location": "Culture Sector Office", "type": "Meeting"}
]

applications = [
    {
        "id": "104B-TRASHIGANG-2026-001",
        "applicant": "Sonam Chophel",
        "cid_number": "11508002341",
        "phone_number": "17654321",
        "coordinator": "Tshering Dorji (Gewog Admin)",
        "site": "Radhi Pakshaling Lhakhang",
        "gewog": "Radhi Gewog",
        "construction_type": "Major Renovation",
        "purpose": "Roofing Structural Timber Replacement & Traditional Wall Painting",
        "thram_no": "TH-8921",
        "plot_no": "PL-102",
        "gis_location": "27.3241° N, 91.6142° E",
        "work_modality": "Gewog Engineering Cell",
        "management_entity": "Community Lhakhang Management Committee",
        "budget_source": "Gewog Development Grant",
        "budget_surety_details": "Guaranteed under Gewog Development Grant FY 2026-2027 (Ref: GDG-TRG-8812). Nu. 1,500,000.",
        "drawings_file": "Architectural_Drawing_Radhi.pdf",
        "estimates_file": "BoQ_Cost_Estimates_Radhi.pdf",
        "community_clearance_file": "Community_Clearance_Radhi.pdf",
        "status": "Approved",
        "admin_remarks": "",
        "supervisor_remarks": "Approved as submitted.",
        "assigned_supervisor": "Dzongdag",
        "approved_by": "Dzongdag",
        "generated_pdf": "Approval_Clearance_104B-TRASHIGANG-2026-001.pdf",
        "tat": "30 days (1 month)",
        "path": "PATH A"
    }
]

notesheets = []

def draw_official_seal(approved_by_role):
    seal_drawing = Drawing(520, 90)
    
    # Seal Circle
    seal_drawing.add(Circle(420, 45, 40, fillColor=colors.HexColor('#fef2f2'), strokeColor=colors.HexColor('#991b1b'), strokeWidth=2))
    seal_drawing.add(Circle(420, 45, 36, fillColor=None, strokeColor=colors.HexColor('#991b1b'), strokeWidth=0.8))
    
    # Seal Stamp Text
    seal_drawing.add(String(392, 60, "DZONGKHAG", fontSize=6, fontName="Helvetica-Bold", fillColor=colors.HexColor('#991b1b')))
    seal_drawing.add(String(391, 51, "ADMINISTRATION", fontSize=5.5, fontName="Helvetica-Bold", fillColor=colors.HexColor('#991b1b')))
    seal_drawing.add(String(395, 36, "APPROVED", fontSize=7, fontName="Helvetica-Bold", fillColor=colors.HexColor('#065f46')))
    seal_drawing.add(String(395, 25, "TRASHIGANG", fontSize=6, fontName="Helvetica-Bold", fillColor=colors.HexColor('#991b1b')))

    # Official Signature Line
    seal_drawing.add(Rect(30, 45, 180, 1, fillColor=colors.HexColor('#1c1917'), strokeColor=None))
    seal_drawing.add(String(30, 32, f"Signed by: Dasho {approved_by_role}", fontSize=8, fontName="Helvetica-Bold", fillColor=colors.HexColor('#1c1917')))
    seal_drawing.add(String(30, 20, "Dzongkhag Administration Trashigang", fontSize=8, fontName="Helvetica", fillColor=colors.HexColor('#44403c')))
    seal_drawing.add(String(30, 8, "Royal Government of Bhutan", fontSize=8, fontName="Helvetica-Oblique", fillColor=colors.HexColor('#6b7280')))
    
    return seal_drawing

# 1. Construction PDF Generator
def generate_approval_pdf(app_item):
    pdf_filename = f"Approval_Clearance_{app_item['id']}.pdf"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)

    doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontSize=11, leading=14, alignment=1, textColor=colors.HexColor('#6b1111'), fontName="Helvetica-Bold")
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontSize=10, leading=13, alignment=1, textColor=colors.HexColor('#1c1917'), fontName="Helvetica-Bold")
    sub_style = ParagraphStyle('SubStyle', parent=styles['Normal'], fontSize=9, leading=12, alignment=1, textColor=colors.HexColor('#44403c'), fontName="Helvetica")
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#1c1917'), fontName="Helvetica")
    bold_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#1c1917'), fontName="Helvetica-Bold")

    elements = [
        Paragraph("ROYAL GOVERNMENT OF BHUTAN", header_style),
        Paragraph("DZONGKHAG ADMINISTRATION TRASHIGANG", title_style),
        Paragraph("CULTURE SECTOR", sub_style),
        Spacer(1, 10),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#854d0e'), spaceAfter=15)
    ]

    ref_table = Table([[Paragraph("<b>Ref No:</b> DAT/CULTURE-APP/2026/089", body_style), Paragraph("<b>Date:</b> October 05, 2026", ParagraphStyle('R', parent=body_style, alignment=2))]], colWidths=[260, 260])
    elements.extend([ref_table, Spacer(1, 15)])

    cert_title = ParagraphStyle('CertTitle', parent=styles['Normal'], fontSize=12, leading=15, alignment=1, textColor=colors.HexColor('#065f46'), fontName="Helvetica-Bold")
    elements.extend([Paragraph("OFFICIAL HERITAGE CONSTRUCTION & RENOVATION CLEARANCE", cert_title), Spacer(1, 15)])

    data = [
        [Paragraph("<b>Application ID:</b>", bold_style), Paragraph(app_item['id'], body_style)],
        [Paragraph("<b>Heritage Site / Structure:</b>", bold_style), Paragraph(app_item['site'], body_style)],
        [Paragraph("<b>Applicant Name:</b>", bold_style), Paragraph(f"{app_item['applicant']} (CID: {app_item['cid_number']})", body_style)],
        [Paragraph("<b>Gewog / Location:</b>", bold_style), Paragraph(app_item['gewog'], body_style)],
        [Paragraph("<b>Construction Category:</b>", bold_style), Paragraph(app_item['construction_type'], body_style)],
        [Paragraph("<b>Purpose of Work:</b>", bold_style), Paragraph(app_item['purpose'], body_style)],
        [Paragraph("<b>Thram & Plot No:</b>", bold_style), Paragraph(f"Thram: {app_item['thram_no']} | Plot: {app_item['plot_no']}", body_style)],
        [Paragraph("<b>Budget Source & Surety:</b>", bold_style), Paragraph(f"{app_item['budget_source']} - {app_item['budget_surety_details']}", body_style)],
        [Paragraph("<b>Approval Status:</b>", bold_style), Paragraph(f"<font color='#065f46'><b>{app_item['status']}</b></font>", body_style)],
        [Paragraph("<b>Supervisor Remarks:</b>", bold_style), Paragraph(app_item.get('supervisor_remarks', 'Approved as per submitted specifications.'), body_style)]
    ]

    t = Table(data, colWidths=[150, 370])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#fbfbfe')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#e2e8f0')),
        ('PADDING', (0,0), (-1,-1), 6),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
    ]))
    elements.extend([t, Spacer(1, 25), draw_official_seal(app_item.get('approved_by', 'Dzongdag'))])

    doc.build(elements)
    return pdf_filename

# 2. Notesheet PDF Generator
def generate_notesheet_pdf(ns_item):
    pdf_filename = f"Approved_Notesheet_{ns_item['id']}.pdf"
    file_path = os.path.join(app.config['UPLOAD_FOLDER'], pdf_filename)

    doc = SimpleDocTemplate(file_path, pagesize=letter, rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle('TitleStyle', parent=styles['Normal'], fontSize=11, leading=14, alignment=1, textColor=colors.HexColor('#6b1111'), fontName="Helvetica-Bold")
    header_style = ParagraphStyle('HeaderStyle', parent=styles['Normal'], fontSize=10, leading=13, alignment=1, textColor=colors.HexColor('#1c1917'), fontName="Helvetica-Bold")
    body_style = ParagraphStyle('BodyStyle', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#1c1917'), fontName="Helvetica")
    bold_style = ParagraphStyle('BoldStyle', parent=styles['Normal'], fontSize=9, leading=13, textColor=colors.HexColor('#1c1917'), fontName="Helvetica-Bold")

    elements = [
        Paragraph("ROYAL GOVERNMENT OF BHUTAN", header_style),
        Paragraph("DZONGKHAG ADMINISTRATION TRASHIGANG", title_style),
        Paragraph("CULTURE SECTOR NOTESHEET", ParagraphStyle('Sub', parent=header_style, fontSize=9, textColor=colors.HexColor('#44403c'))),
        Spacer(1, 10),
        HRFlowable(width="100%", thickness=1.5, color=colors.HexColor('#854d0e'), spaceAfter=15)
    ]

    meta_table = Table([
        [Paragraph(f"<b>Ref No:</b> {ns_item['ref_no']}", body_style), Paragraph(f"<b>Date:</b> {ns_item['date']}", ParagraphStyle('R', parent=body_style, alignment=2))],
        [Paragraph(f"<b>To:</b> {ns_item['addressed_to']}", body_style), Paragraph(f"<b>Submitted By:</b> {ns_item['created_by']}", ParagraphStyle('R', parent=body_style, alignment=2))]
    ], colWidths=[260, 260])
    elements.extend([meta_table, Spacer(1, 12)])

    elements.extend([Paragraph(f"<b>SUBJECT:</b> {ns_item['subject']}", bold_style), Spacer(1, 12)])

    # Table of items
    table_data = [["Sl.", "Detail", "Purpose", "Qty", "Rate (Nu.)", "Total (Nu.)"]]
    for idx, item in enumerate(ns_item['item_list'], start=1):
        table_data.append([
            str(idx),
            item['detail'],
            item['purpose'],
            str(item['number']),
            f"{item['rate']:.2f}",
            f"{item['total']:.2f}"
        ])
    table_data.append(["", "GRAND TOTAL", "", "", "", f"Nu. {ns_item['grand_total']:.2f}"])

    t = Table(table_data, colWidths=[30, 150, 140, 40, 70, 90])
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#292524')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.white),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('PADDING', (0,0), (-1,-1), 5),
        ('ALIGN', (3,0), (-1,-1), 'RIGHT'),
        ('ALIGN', (0,0), (0,-1), 'CENTER'),
        ('BACKGROUND', (0,-1), (-1,-1), colors.HexColor('#f1f5f9')),
        ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
    ]))

    elements.extend([t, Spacer(1, 15)])
    elements.append(Paragraph(f"<b>Supervisor Approval Remarks:</b> {ns_item.get('supervisor_remarks', 'Approved as proposed.')}", body_style))
    elements.extend([Spacer(1, 25), draw_official_seal(ns_item.get('approved_by', 'Dzongdag'))])

    doc.build(elements)
    return pdf_filename

# Initial PDF generation for sample data
for app_item in applications:
    if app_item['status'] == 'Approved':
        app_item['generated_pdf'] = generate_approval_pdf(app_item)

@app.route('/')
def index():
    active_role = session.get('active_role', 'Applicant')
    view = request.args.get('view', 'construction' if active_role == 'Applicant' else 'applications')
    msg = request.args.get('msg', None)
    
    next_ref_no = f"DAT/CULTURE-NS/2026/{len(notesheets) + 1:03d}"
    
    return render_template(
        'index.html',
        active_role=active_role,
        view=view,
        msg=msg,
        apps=applications,
        notesheets=notesheets,
        events=events,
        work_categories=WORK_CATEGORIES,
        next_ref_no=next_ref_no
    )

@app.route('/uploads/<path:filename>')
def download_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

@app.route('/switch-role')
def switch_role():
    role = request.args.get('role', 'Applicant')
    session['active_role'] = role
    default_view = 'construction' if role == 'Applicant' else 'applications'
    return redirect(url_for('index', view=default_view, msg=f"Switched mode to {role}"))

def save_uploaded_file(file_obj):
    if file_obj and file_obj.filename:
        filename = file_obj.filename
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file_obj.save(file_path)
        return filename
    return "Not Attached"

@app.route('/apply-construction', methods=['POST'])
def apply_construction():
    construction_type = request.form.get('construction_type', 'New Construction')
    category_meta = WORK_CATEGORIES.get(construction_type, {"tat": "30 days (1 month)", "path": "PATH A"})
    app_id = f"104B-TRASHIGANG-2026-00{len(applications) + 1}"

    drawings_file = save_uploaded_file(request.files.get('drawings_file'))
    estimates_file = save_uploaded_file(request.files.get('estimates_file'))
    community_clearance_file = save_uploaded_file(request.files.get('community_clearance_file'))

    applications.append({
        "id": app_id,
        "applicant": request.form.get('applicant'),
        "cid_number": request.form.get('cid_number', 'N/A'),
        "phone_number": request.form.get('phone_number', 'N/A'),
        "coordinator": request.form.get('coordinator', 'N/A'),
        "site": request.form.get('site'),
        "gewog": request.form.get('gewog'),
        "construction_type": construction_type,
        "purpose": request.form.get('purpose'),
        "thram_no": request.form.get('thram_no', 'N/A'),
        "plot_no": request.form.get('plot_no', 'N/A'),
        "gis_location": request.form.get('gis_location', 'N/A'),
        "work_modality": request.form.get('work_modality', 'N/A'),
        "management_entity": request.form.get('management_entity', 'N/A'),
        "budget_source": request.form.get('budget_source', 'N/A'),
        "budget_surety_details": request.form.get('budget_surety_details', 'N/A'),
        "drawings_file": drawings_file,
        "estimates_file": estimates_file,
        "community_clearance_file": community_clearance_file,
        "status": "Pending Admin Review",
        "admin_remarks": "",
        "supervisor_remarks": "",
        "assigned_supervisor": "Dzongdag",
        "approved_by": "",
        "generated_pdf": None,
        "tat": category_meta['tat'],
        "path": category_meta['path']
    })
    return redirect(url_for('index', view='construction', msg=f"Application {app_id} submitted successfully!"))

@app.route('/create-notesheet', methods=['POST'])
def create_notesheet():
    note_id = f"NS-TRASHIGANG-2026-{len(notesheets) + 1:03d}"
    ref_no = request.form.get('ref_no') or f"DAT/CULTURE-NS/2026/{len(notesheets) + 1:03d}"

    item_details = request.form.getlist('item_detail[]')
    item_purposes = request.form.getlist('item_purpose[]')
    item_numbers = request.form.getlist('item_number[]')
    item_rates = request.form.getlist('item_rate[]')
    item_totals = request.form.getlist('item_total[]')
    item_remarks = request.form.getlist('item_remarks[]')

    items_list = []
    grand_total = 0.0

    for i in range(len(item_details)):
        if item_details[i].strip():
            try:
                qty = float(item_numbers[i]) if item_numbers[i] else 1.0
                rate = float(item_rates[i]) if item_rates[i] else 0.0
                tot = float(item_totals[i]) if item_totals[i] else (qty * rate)
            except ValueError:
                qty, rate, tot = 1.0, 0.0, 0.0

            grand_total += tot
            items_list.append({
                "detail": item_details[i],
                "purpose": item_purposes[i],
                "number": qty,
                "rate": rate,
                "total": tot,
                "remarks": item_remarks[i]
            })

    notesheets.append({
        "id": note_id,
        "ref_no": ref_no,
        "date": request.form.get('note_date'),
        "subject": request.form.get('subject'),
        "addressed_to": request.form.get('target_supervisor', 'Dzongdag'),
        "item_list": items_list,
        "grand_total": grand_total,
        "created_by": "Cultural Officer (Admin)",
        "assigned_supervisor": request.form.get('target_supervisor', 'Dzongdag'),
        "status": f"Pending Approval with {request.form.get('target_supervisor', 'Dzongdag')}",
        "supervisor_remarks": "",
        "approved_by": "",
        "generated_pdf": None
    })
    return redirect(url_for('index', view='notesheets', msg=f"Notesheet created with Ref: {ref_no}!"))

@app.route('/forward-application/<app_id>', methods=['POST'])
def forward_application(app_id):
    target_supervisor = request.form.get('target_supervisor', 'Dzongdag')
    admin_remarks = request.form.get('admin_remarks', '')

    for app_item in applications:
        if app_item['id'] == app_id:
            app_item['admin_remarks'] = admin_remarks
            app_item['assigned_supervisor'] = target_supervisor
            app_item['status'] = f"Forwarded to {target_supervisor} for Approval"
            break

    return redirect(url_for('index', view='applications', msg=f"Application {app_id} reviewed and forwarded!"))

@app.route('/action-supervisor/<item_type>/<item_id>', methods=['POST'])
def action_supervisor(item_type, item_id):
    action = request.form.get('action')
    remarks = request.form.get('supervisor_remarks', '')
    active_role = session.get('active_role', 'Dzongdag')

    if item_type == 'application':
        for app_item in applications:
            if app_item['id'] == item_id:
                app_item['supervisor_remarks'] = remarks
                app_item['status'] = f"Approved" if action == "Approved" else f"Rejected"
                app_item['approved_by'] = active_role
                if action == "Approved":
                    pdf_filename = generate_approval_pdf(app_item)
                    app_item['generated_pdf'] = pdf_filename
                break
        return redirect(url_for('index', view='applications', msg=f"Application {item_id} status updated to {action}!"))
    else:
        for ns in notesheets:
            if ns['id'] == item_id:
                ns['supervisor_remarks'] = remarks
                ns['status'] = f"Approved" if action == "Approved" else f"Rejected"
                ns['approved_by'] = active_role
                if action == "Approved":
                    pdf_filename = generate_notesheet_pdf(ns)
                    ns['generated_pdf'] = pdf_filename
                break
        return redirect(url_for('index', view='notesheets', msg=f"Notesheet {item_id} status updated to {action}!"))

@app.route('/add-event', methods=['POST'])
def add_event():
    new_event = {
        "id": len(events) + 1,
        "title": request.form.get('title'),
        "date": request.form.get('date'),
        "location": request.form.get('location'),
        "type": request.form.get('type')
    }
    events.append(new_event)
    return redirect(url_for('index', view='calendar', msg="New event added to calendar!"))

@app.route('/delete-event/<int:event_id>', methods=['POST'])
def delete_event(event_id):
    global events
    events = [e for e in events if e.get('id') != event_id]
    return redirect(url_for('index', view='calendar', msg="Event deleted successfully!"))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
