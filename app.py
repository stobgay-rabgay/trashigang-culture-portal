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

applications = [
    {
        "id": "104B-TRASHIGANG-2026-001",
        "applicant": "Sonam Chophel",
        "site": "Radhi Pakshaling Lhakhang",
        "gewog": "Radhi Gewog",
        "construction_type": "Construction",
        "purpose": "Roofing Structural Timber Replacement & Traditional Wall Painting",
        "status": "Approved & Endorsed",
        "recommendation": "Recommended for endorsement as per structural assessment report.",
        "supervisor_remarks": "Approved as recommended.",
        "recipient_to": "Director General",
        "recipient_dept": "Department of Culture & Dzongkha Development",
        "recipient_address": "Thimphu",
        "assigned_supervisor": "Dzongdag",
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
        "status": "Approved & Endorsed by Dzongdag",
        "remarks": "Approved as requested. Sanction from annual culture fund."
    }
]

@app.route('/')
def index():
    active_role = session.get('active_role', 'Admin')
    view = request.args.get('view', 'construction')
    msg = request.args.get('msg', None)
    
    if view == 'notesheet':
        return render_template('index.html', active_role=active_role, view=view, msg=msg, notesheets=notesheets, apps=[])
    elif view.startswith('report_') or view in ['summary_docs', 'inventory']:
        filtered_apps = [a for a in applications if a.get('type') == view.replace('report_', '') or view == 'summary_docs']
        return render_template('index.html', active_role=active_role, view=view, msg=msg, apps=filtered_apps, notesheets=notesheets)
    else:
        return render_template('index.html', active_role=active_role, view=view, msg=msg, apps=applications, notesheets=notesheets)

@app.route('/switch-role')
def switch_role():
    role = request.args.get('role', 'Admin')
    session['active_role'] = role
    return redirect(url_for('index', msg=f"Switched mode to {role}"))

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
                ns['status'] = f'Approved & Endorsed by {active_role}'
            elif action_type == 'forward':
                ns['assigned_supervisor'] = forward_to
                ns['status'] = f'Forwarded to {forward_to} by {active_role}'
            else:
                ns['status'] = f'Returned by {active_role}'
                
    return redirect(url_for('index', view='notesheet', msg="Notesheet status updated successfully."))

@app.route('/download-notesheet-pdf/<ns_id>')
def download_notesheet_pdf(ns_id):
    ns = next((item for item in notesheets if item["id"] == ns_id), None)
    if not ns:
        return "Notesheet not found", 404

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, leftMargin=36, rightMargin=36, topMargin=36, bottomMargin=36)
    story = []
    
    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'HeaderTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=12, leading=14, alignment=TA_CENTER, textColor=colors.HexColor('#6b1d1d')
    )
    normal_style = ParagraphStyle(
        'BodyTextCustom', parent=styles['Normal'], fontName='Helvetica', fontSize=10, leading=14, alignment=TA_LEFT
    )
    bold_style = ParagraphStyle(
        'BoldTextCustom', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=10, leading=14
    )

    # Dzongkhag Header / Letterhead
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
        [Paragraph(f"<b>Subject:</b> {ns['title']}", normal_style), Paragraph(f"<b>Status:</b> <font color='green'>{ns['status']}</font>", ParagraphStyle('RightText', parent=normal_style, alignment=TA_RIGHT))]
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
    
    sig_data = [
        [
            Paragraph("<b>Submitted / Initiated By:</b><br/><br/><br/>_______________________<br/><b>Cultural Officer</b><br/>Trashigang Dzongkhag", normal_style),
            Paragraph("<b>Approved & Endorsed By:</b><br/><br/><br/>_______________________<br/><b>Dasho Dzongdag / Dzongrab</b><br/>Trashigang Dzongkhag", normal_style)
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
