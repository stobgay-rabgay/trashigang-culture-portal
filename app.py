from flask import Flask, render_template, request, redirect, url_for, send_file, session
import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

app = Flask(__name__)
app.secret_key = 'bhutan_portal_secret_key'

# Official Settings for Supervisors & Officiating Officers
officials_settings = {
    "Cultural Officer": {
        "name": "Karma Tenzin",
        "designation": "Cultural Officer",
        "is_officiating": False
    },
    "Dzongdag": {
        "name": "Dasho Karma Dorji",
        "designation": "Dzongdag",
        "is_officiating": False
    },
    "Dzongrab": {
        "name": "Sonam Tobgay",
        "designation": "Dzongrab",
        "is_officiating": True
    }
}

# Work Categories based on Department of Culture Guidelines (June 2022)
WORK_CATEGORIES = {
    "New Construction": {
        "tat": "30 days (1 month)",
        "path": "PATH A",
        "approval_authority": "Department of Culture"
    },
    "Reconstruction": {
        "tat": "30 days (1 month)",
        "path": "PATH A",
        "approval_authority": "Department of Culture"
    },
    "Major Renovation": {
        "tat": "30 days (1 month)",
        "path": "PATH A / PATH B",
        "approval_authority": "Dzongkhag / Department of Culture"
    },
    "Minor Renovation": {
        "tat": "7 days (1 week)",
        "path": "PATH B",
        "approval_authority": "Dzongkhag Administration"
    },
    "Site Development Work": {
        "tat": "7 days (1 week)",
        "path": "PATH B",
        "approval_authority": "Dzongkhag Administration"
    }
}

applications = [
    {
        "id": "104B-TRASHIGANG-2026-001",
        "applicant": "Sonam Chophel",
        "site": "Radhi Pakshaling Lhakhang",
        "gewog": "Radhi Gewog",
        "construction_type": "Renovation (Major)",
        "purpose": "Roofing Structural Timber Replacement & Traditional Wall Painting",
        "status": "Approved & Endorsed by Dzongdag",
        "recommendation": "Recommended for endorsement as per structural assessment report.",
        "supervisor_remarks": "Approved as recommended.",
        "assigned_supervisor": "Dzongdag",
        "approved_by": "Dzongdag",
        "tat": "30 days (1 month)",
        "path": "PATH A",
        "type": "construction"
    }
]

notesheets = [
    {
        "id": "NS-2026-001",
        "title": "Restoration of Radhi Lhakhang Main Wall",
        "submitted_by": "Cultural Officer",
        "details": "Urgent structural reinforcement required before upcoming monsoon.",
        "amount": "250,000",
        "assigned_supervisor": "Dzongdag",
        "approved_by": "Dzongdag",
        "status": "Approved & Endorsed by Dzongdag",
        "remarks": "Approved as requested. Sanction from annual culture fund."
    }
]

@app.route('/')
def index():
    active_role = session.get('active_role', 'Applicant')
    view = request.args.get('view', 'construction')
    msg = request.args.get('msg', None)
    
    if view == 'notesheet':
        return render_template('index.html', active_role=active_role, view=view, msg=msg, notesheets=notesheets, apps=[], settings=officials_settings, work_categories=WORK_CATEGORIES)
    elif view == 'settings':
        return render_template('index.html', active_role=active_role, view=view, msg=msg, apps=[], notesheets=[], settings=officials_settings, work_categories=WORK_CATEGORIES)
    else:
        return render_template('index.html', active_role=active_role, view='construction', msg=msg, apps=applications, notesheets=notesheets, settings=officials_settings, work_categories=WORK_CATEGORIES)

@app.route('/switch-role')
def switch_role():
    role = request.args.get('role', 'Applicant')
    session['active_role'] = role
    return redirect(url_for('index', msg=f"Switched mode to {role}"))

@app.route('/update-settings', methods=['POST'])
def update_settings():
    officials_settings["Dzongdag"]["name"] = request.form.get('dzongdag_name', 'Dasho Dzongdag')
    officials_settings["Dzongdag"]["is_officiating"] = 'dzongdag_offtg' in request.form
    
    officials_settings["Dzongrab"]["name"] = request.form.get('dzongrab_name', 'Dzongrab')
    officials_settings["Dzongrab"]["is_officiating"] = 'dzongrab_offtg' in request.form

    officials_settings["Cultural Officer"]["name"] = request.form.get('co_name', 'Cultural Officer')
    officials_settings["Cultural Officer"]["is_officiating"] = 'co_offtg' in request.form

    return redirect(url_for('index', view='settings', msg="Official Settings saved!"))

@app.route('/apply-construction', methods=['POST'])
def apply_construction():
    applicant = request.form.get('applicant')
    site = request.form.get('site')
    gewog = request.form.get('gewog')
    construction_type = request.form.get('construction_type', 'New Construction')
    purpose = request.form.get('purpose')
    target_supervisor = request.form.get('target_supervisor', 'Dzongdag')
    
    category_meta = WORK_CATEGORIES.get(construction_type, {
        "tat": "30 days (1 month)",
        "path": "PATH A"
    })

    app_id = f"104B-TRASHIGANG-2026-00{len(applications) + 1}"
    applications.append({
        "id": app_id,
        "applicant": applicant,
        "site": site,
        "gewog": gewog,
        "construction_type": construction_type,
        "purpose": purpose,
        "status": "Submitted & Under Initial Review",
        "recommendation": "",
        "supervisor_remarks": "",
        "assigned_supervisor": target_supervisor,
        "approved_by": "",
        "tat": category_meta['tat'],
        "path": category_meta['path'],
        "type": "construction"
    })
    return redirect(url_for('index', view='construction', msg=f"Heritage Clearances Application {app_id} ({construction_type}) submitted successfully!"))

@app.route('/add-notesheet', methods=['POST'])
def add_notesheet():
    title = request.form.get('title')
    details = request.form.get('details')
    amount = request.form.get('amount', '0.00')
    target_supervisor = request.form.get('target_supervisor', 'Dzongdag')
    
    notesheet_id = f"NS-2026-00{len(notesheets) + 1}"
    notesheets.append({
        "id": notesheet_id,
        "title": title,
        "submitted_by": session.get('active_role', 'Admin'),
        "details": details,
        "amount": amount,
        "assigned_supervisor": target_supervisor,
        "approved_by": "",
        "status": f"Pending {target_supervisor} Review",
        "remarks": ""
    })
    return redirect(url_for('index', view='notesheet', msg=f"Notesheet {notesheet_id} created & forwarded to {target_supervisor}!"))

@app.route('/notesheet-action', methods=['POST'])
def notesheet_action():
    ns_id = request.form.get('ns_id')
    action_type = request.form.get('action_type')
    remarks = request.form.get('remarks', '')
    forward_to = request.form.get('forward_to', '')
    active_role = session.get('active_role', 'Dzongdag')
    
    for ns in notesheets:
        if ns['id'] == ns_id:
            if remarks:
                ns['remarks'] = remarks
            if action_type == 'approve':
                ns['approved_by'] = active_role
                ns['status'] = f'Approved & Endorsed by {active_role}'
            elif action_type == 'forward':
                ns['assigned_supervisor'] = forward_to
                ns['status'] = f'Forwarded to {forward_to} by {active_role}'
            else:
                ns['status'] = f'Returned by {active_role}'
                
    return redirect(url_for('index', view='notesheet', msg="Notesheet status updated successfully."))

@app.route('/download-construction-pdf/<app_id>')
def download_construction_pdf(app_id):
    app_data = next((item for item in applications if item["id"] == app_id), None)
    if not app_data:
        return "Application not found", 404

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('HeaderTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=12, leading=14, alignment=TA_CENTER, textColor=colors.HexColor('#6b1d1d'))
    normal_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, alignment=TA_LEFT)
    bold_style = ParagraphStyle('BoldTextCustom', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14)

    header_html = "<b>ROYAL GOVERNMENT OF BHUTAN</b><br/><b>DZONGKHAG ADMINISTRATION: TRASHIGANG</b><br/><font size=9 color='#555555'>CULTURE SECTOR</font>"
    story.append(Paragraph(header_html, title_style))
    story.append(Spacer(1, 15))
    
    story.append(Table([['']], colWidths=[540], rowHeights=[2], style=TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#6b1d1d')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0), ('TOPPADDING', (0,0), (-1,-1), 0)
    ])))
    story.append(Spacer(1, 15))
    
    meta_data = [
        [Paragraph(f"<b>Clearance Ref No:</b> {app_data['id']}", normal_style), Paragraph(f"<b>Date:</b> October 5, 2026", ParagraphStyle('RightText', parent=normal_style, alignment=TA_RIGHT))],
        [Paragraph(f"<b>Subject:</b> Cultural Heritage Approval Clearance", normal_style), Paragraph("", normal_style)]
    ]
    meta_table = Table(meta_data, colWidths=[300, 240])
    meta_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b><u>APPLICATION & WORK CATEGORY DETAILS</u></b>", bold_style))
    story.append(Spacer(1, 8))
    
    table_data = [
        [Paragraph("<b>Field</b>", bold_style), Paragraph("<b>Details</b>", bold_style)],
        [Paragraph("Applicant Name", normal_style), Paragraph(app_data['applicant'], normal_style)],
        [Paragraph("Heritage Site", normal_style), Paragraph(app_data['site'], normal_style)],
        [Paragraph("Gewog / Location", normal_style), Paragraph(app_data['gewog'], normal_style)],
        [Paragraph("Category of Work", normal_style), Paragraph(app_data['construction_type'], normal_style)],
        [Paragraph("Turnaround Time (TAT)", normal_style), Paragraph(app_data.get('tat', '30 days'), normal_style)],
        [Paragraph("Scope of Work", normal_style), Paragraph(app_data['purpose'], normal_style)],
    ]
    
    details_table = Table(table_data, colWidths=[160, 380])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0e6e6')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#6b1d1d')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 20))
    
    if app_data.get('supervisor_remarks'):
        story.append(Paragraph(f"<b>Approval & Endorsement Remarks:</b> {app_data['supervisor_remarks']}", normal_style))
        story.append(Spacer(1, 25))
    
    approver_role = app_data.get('approved_by') or app_data.get('assigned_supervisor', 'Dzongdag')
    sup_info = officials_settings.get(approver_role, officials_settings['Dzongdag'])
    co_info = officials_settings.get('Cultural Officer', officials_settings['Cultural Officer'])

    co_offtg_str = "Offtg. " if co_info.get('is_officiating') else ""
    sup_offtg_str = "Offtg. " if sup_info.get('is_officiating') else ""

    co_title = f"{co_offtg_str}Cultural Officer"
    sup_title = f"{sup_offtg_str}{'Dasho Dzongdag' if approver_role == 'Dzongdag' else 'Dzongrab'}"

    sig_data = [
        [
            Paragraph(f"<b>Verified By:</b><br/><br/><br/>_______________________<br/><b>({co_info['name']})</b><br/><b>{co_title}</b><br/>Trashigang Dzongkhag", normal_style),
            Paragraph(f"<b>Approved & Endorsed By:</b><br/><br/><br/>_______________________<br/><b>({sup_info['name']})</b><br/><b>{sup_title}</b><br/>Trashigang Dzongkhag", normal_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    sig_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(Spacer(1, 30))
    story.append(sig_table)
    
    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"Approved_Construction_{app_id}.pdf", mimetype='application/pdf')

@app.route('/download-notesheet-pdf/<ns_id>')
def download_notesheet_pdf(ns_id):
    ns = next((item for item in notesheets if item["id"] == ns_id), None)
    if not ns:
        return "Notesheet not found", 404

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('HeaderTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=12, leading=14, alignment=TA_CENTER, textColor=colors.HexColor('#6b1d1d'))
    normal_style = ParagraphStyle('BodyTextCustom', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, alignment=TA_LEFT)
    bold_style = ParagraphStyle('BoldTextCustom', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14)

    header_html = "<b>ROYAL GOVERNMENT OF BHUTAN</b><br/><b>DZONGKHAG ADMINISTRATION: TRASHIGANG</b><br/><font size=9 color='#555555'>CULTURE SECTOR</font>"
    story.append(Paragraph(header_html, title_style))
    story.append(Spacer(1, 15))
    
    story.append(Table([['']], colWidths=[540], rowHeights=[2], style=TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor('#6b1d1d')),
        ('BOTTOMPADDING', (0,0), (-1,-1), 0), ('TOPPADDING', (0,0), (-1,-1), 0)
    ])))
    story.append(Spacer(1, 15))
    
    meta_data = [
        [Paragraph(f"<b>Ref No:</b> {ns['id']}", normal_style), Paragraph(f"<b>Date:</b> October 5, 2026", ParagraphStyle('RightText', parent=normal_style, alignment=TA_RIGHT))],
        [Paragraph(f"<b>Subject:</b> {ns['title']}", normal_style), Paragraph("", normal_style)]
    ]
    meta_table = Table(meta_data, colWidths=[300, 240])
    meta_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b><u>FINANCIAL & PURPOSE DETAILS</u></b>", bold_style))
    story.append(Spacer(1, 8))
    
    table_data = [
        [Paragraph("<b>Sl. No.</b>", bold_style), Paragraph("<b>Purpose / Description of Proposal</b>", bold_style), Paragraph("<b>Estimated Amount (Nu.)</b>", ParagraphStyle('CenterBold', parent=bold_style, alignment=TA_CENTER))],
        [
            Paragraph("1", normal_style),
            Paragraph(f"<b>{ns['title']}</b><br/>{ns['details']}", normal_style),
            Paragraph(f"Nu. {ns.get('amount', '0.00')}/-", ParagraphStyle('CenterText', parent=normal_style, alignment=TA_CENTER))
        ],
        [
            Paragraph("<b>TOTAL AMOUNT SANCTIONED</b>", bold_style),
            Paragraph("", normal_style),
            Paragraph(f"<b>Nu. {ns.get('amount', '0.00')}/-</b>", ParagraphStyle('CenterBold', parent=bold_style, alignment=TA_CENTER))
        ]
    ]
    
    details_table = Table(table_data, colWidths=[50, 340, 150])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0e6e6')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#6b1d1d')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('SPAN', (0,2), (1,2)),
        ('TOPPADDING', (0,0), (-1,-1), 6), ('BOTTOMPADDING', (0,0), (-1,-1), 6),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 20))
    
    if ns.get('remarks'):
        story.append(Paragraph(f"<b>Approving / Review Remarks:</b> {ns['remarks']}", normal_style))
        story.append(Spacer(1, 25))
    
    approver_role = ns.get('approved_by') or ns.get('assigned_supervisor', 'Dzongdag')
    sup_info = officials_settings.get(approver_role, officials_settings['Dzongdag'])
    co_info = officials_settings.get('Cultural Officer', officials_settings['Cultural Officer'])

    co_offtg_str = "Offtg. " if co_info.get('is_officiating') else ""
    sup_offtg_str = "Offtg. " if sup_info.get('is_officiating') else ""

    co_title = f"{co_offtg_str}Cultural Officer"
    sup_title = f"{sup_offtg_str}{'Dasho Dzongdag' if approver_role == 'Dzongdag' else 'Dzongrab'}"

    sig_data = [
        [
            Paragraph(f"<b>Submitted / Initiated By:</b><br/><br/><br/>_______________________<br/><b>({co_info['name']})</b><br/><b>{co_title}</b><br/>Trashigang Dzongkhag", normal_style),
            Paragraph(f"<b>Approved & Endorsed By:</b><br/><br/><br/>_______________________<br/><b>({sup_info['name']})</b><br/><b>{sup_title}</b><br/>Trashigang Dzongkhag", normal_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    sig_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(Spacer(1, 30))
    story.append(sig_table)
    
    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"Approved_Notesheet_{ns_id}.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
