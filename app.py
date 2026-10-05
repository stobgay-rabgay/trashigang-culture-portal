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

officials_settings = {
    "Cultural Officer": {"name": "Karma Tenzin", "designation": "Cultural Officer", "is_officiating": False},
    "Dzongdag": {"name": "Dasho Karma Dorji", "designation": "Dzongdag", "is_officiating": False},
    "Dzongrab": {"name": "Sonam Tobgay", "designation": "Dzongrab", "is_officiating": True}
}

WORK_CATEGORIES = {
    "New Construction": {"tat": "30 days (1 month)", "path": "PATH A"},
    "Reconstruction": {"tat": "30 days (1 month)", "path": "PATH A"},
    "Major Renovation": {"tat": "30 days (1 month)", "path": "PATH A / PATH B"},
    "Minor Renovation": {"tat": "7 days (1 week)", "path": "PATH B"},
    "Site Development Work": {"tat": "7 days (1 week)", "path": "PATH B"}
}

applications = [
    {
        "id": "104B-TRASHIGANG-2026-001",
        "applicant": "Sonam Chophel",
        "site": "Radhi Pakshaling Lhakhang",
        "gewog": "Radhi Gewog",
        "construction_type": "Major Renovation",
        "purpose": "Roofing Structural Timber Replacement & Traditional Wall Painting",
        "thram_no": "TH-8921",
        "plot_no": "PL-102",
        "gis_location": "27.3241° N, 91.6142° E",
        "work_modality": "Gewog Engineering Cell",
        "management_entity": "Community Lhakhang Management",
        "budget_source": "Government Funding",
        "status": "Approved & Endorsed by Dzongdag",
        "supervisor_remarks": "Approved as recommended.",
        "assigned_supervisor": "Dzongdag",
        "approved_by": "Dzongdag",
        "tat": "30 days (1 month)",
        "path": "PATH A",
        "type": "construction"
    }
]

notesheets = []

@app.route('/')
def index():
    active_role = session.get('active_role', 'Applicant')
    view = request.args.get('view', 'construction')
    msg = request.args.get('msg', None)
    return render_template('index.html', active_role=active_role, view=view, msg=msg, apps=applications, notesheets=notesheets, settings=officials_settings, work_categories=WORK_CATEGORIES)

@app.route('/switch-role')
def switch_role():
    role = request.args.get('role', 'Applicant')
    session['active_role'] = role
    return redirect(url_for('index', msg=f"Switched mode to {role}"))

@app.route('/apply-construction', methods=['POST'])
def apply_construction():
    construction_type = request.form.get('construction_type', 'New Construction')
    category_meta = WORK_CATEGORIES.get(construction_type, {"tat": "30 days (1 month)", "path": "PATH A"})

    app_id = f"104B-TRASHIGANG-2026-00{len(applications) + 1}"
    applications.append({
        "id": app_id,
        "applicant": request.form.get('applicant'),
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
        "status": "Submitted & Under Initial Review",
        "supervisor_remarks": "",
        "assigned_supervisor": request.form.get('target_supervisor', 'Dzongdag'),
        "approved_by": "",
        "tat": category_meta['tat'],
        "path": category_meta['path'],
        "type": "construction"
    })
    return redirect(url_for('index', view='construction', msg=f"Heritage Clearance Application {app_id} submitted successfully with all required details!"))

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
        [Paragraph(f"<b>Subject:</b> Cultural Heritage Clearance Certificate", normal_style), Paragraph("", normal_style)]
    ]
    meta_table = Table(meta_data, colWidths=[300, 240])
    meta_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP'), ('BOTTOMPADDING', (0,0), (-1,-1), 4)]))
    story.append(meta_table)
    story.append(Spacer(1, 15))
    
    story.append(Paragraph("<b><u>APPLICATION & COMPLIANCE DETAILS</u></b>", bold_style))
    story.append(Spacer(1, 8))
    
    table_data = [
        [Paragraph("<b>Field</b>", bold_style), Paragraph("<b>Details</b>", bold_style)],
        [Paragraph("Applicant Name", normal_style), Paragraph(app_data['applicant'], normal_style)],
        [Paragraph("Heritage Site", normal_style), Paragraph(app_data['site'], normal_style)],
        [Paragraph("Gewog / Location", normal_style), Paragraph(app_data['gewog'], normal_style)],
        [Paragraph("Category of Work", normal_style), Paragraph(app_data['construction_type'], normal_style)],
        [Paragraph("Thram No / Plot No", normal_style), Paragraph(f"{app_data.get('thram_no')} / {app_data.get('plot_no')}", normal_style)],
        [Paragraph("GIS Coordinates", normal_style), Paragraph(app_data.get('gis_location', 'N/A'), normal_style)],
        [Paragraph("Work Modality", normal_style), Paragraph(app_data.get('work_modality', 'N/A'), normal_style)],
        [Paragraph("Post-Work Manager", normal_style), Paragraph(app_data.get('management_entity', 'N/A'), normal_style)],
        [Paragraph("Budget Source", normal_style), Paragraph(app_data.get('budget_source', 'N/A'), normal_style)],
        [Paragraph("Turnaround Time (TAT)", normal_style), Paragraph(app_data.get('tat', '30 days'), normal_style)],
        [Paragraph("Scope of Work", normal_style), Paragraph(app_data['purpose'], normal_style)],
    ]
    
    details_table = Table(table_data, colWidths=[160, 380])
    details_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#f0e6e6')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#6b1d1d')),
        ('VALIGN', (0,0), (-1,-1), 'TOP'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cccccc')),
        ('TOPPADDING', (0,0), (-1,-1), 5), ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(details_table)
    story.append(Spacer(1, 20))
    
    if app_data.get('supervisor_remarks'):
        story.append(Paragraph(f"<b>Approval Remarks:</b> {app_data['supervisor_remarks']}", normal_style))
        story.append(Spacer(1, 20))
    
    approver_role = app_data.get('approved_by') or app_data.get('assigned_supervisor', 'Dzongdag')
    sup_info = officials_settings.get(approver_role, officials_settings['Dzongdag'])
    co_info = officials_settings.get('Cultural Officer', officials_settings['Cultural Officer'])

    sig_data = [
        [
            Paragraph(f"<b>Verified By:</b><br/><br/><br/>_______________________<br/><b>({co_info['name']})</b><br/><b>Cultural Officer</b><br/>Trashigang Dzongkhag", normal_style),
            Paragraph(f"<b>Approved & Endorsed By:</b><br/><br/><br/>_______________________<br/><b>({sup_info['name']})</b><br/><b>{sup_info['designation']}</b><br/>Trashigang Dzongkhag", normal_style)
        ]
    ]
    sig_table = Table(sig_data, colWidths=[270, 270])
    sig_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
    story.append(Spacer(1, 25))
    story.append(sig_table)
    
    doc.build(story)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"Approved_Construction_{app_id}.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
