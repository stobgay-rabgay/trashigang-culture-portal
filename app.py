from flask import Flask, render_template, request, redirect, url_for, send_file, session
import os
import io

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
        "status": "Pending Dzongdag Approval",
        "remarks": ""
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
    target_supervisor = request.form.get('target_supervisor', 'Dzongdag')
    
    notesheet_id = f"NS-2026-00{len(notesheets) + 1}"
    notesheets.append({
        "id": notesheet_id,
        "title": title,
        "submitted_by": session.get('active_role', 'Admin'),
        "details": details,
        "status": f"Pending {target_supervisor} Approval",
        "remarks": ""
    })
    return redirect(url_for('index', view='notesheet', msg=f"Notesheet {notesheet_id} created successfully!"))

@app.route('/notesheet-action', methods=['POST'])
def notesheet_action():
    ns_id = request.form.get('ns_id')
    action_type = request.form.get('action_type')
    remarks = request.form.get('remarks')
    active_role = session.get('active_role', 'Dzongdag')
    
    for ns in notesheets:
        if ns['id'] == ns_id:
            ns['remarks'] = remarks
            if action_type == 'approve':
                ns['status'] = f'Approved & Endorsed by {active_role}'
            else:
                ns['status'] = f'Returned by {active_role}'
                
    return redirect(url_for('index', view='notesheet', msg="Notesheet action recorded successfully."))

@app.route('/admin-action', methods=['POST'])
def admin_action():
    app_id = request.form.get('app_id')
    target_supervisor = request.form.get('target_supervisor', 'Dzongdag')
    rec_to = request.form.get('recipient_to')
    rec_dept = request.form.get('recipient_dept')
    rec_addr = request.form.get('recipient_address')
    recommendation = request.form.get('recommendation')
    
    for app in applications:
        if app['id'] == app_id:
            app['assigned_supervisor'] = target_supervisor
            app['recipient_to'] = rec_to
            app['recipient_dept'] = rec_dept
            app['recipient_address'] = rec_addr
            if recommendation:
                app['recommendation'] = recommendation
            app['status'] = f"Forwarded to {target_supervisor}"
            
    return redirect(url_for('index', msg=f"Forwarded successfully to {target_supervisor}!"))

@app.route('/supervisor-action', methods=['POST'])
def supervisor_action():
    app_id = request.form.get('app_id')
    action_type = request.form.get('action_type')
    remarks = request.form.get('supervisor_remarks')
    
    for app in applications:
        if app['id'] == app_id:
            app['supervisor_remarks'] = remarks
            if action_type == 'approve_agency':
                app['status'] = 'Approved & Endorsed'
            else:
                app['status'] = 'Returned to Cultural Officer'
                
    return redirect(url_for('index', msg="Action recorded successfully."))

@app.route('/download-signed-package/<app_id>')
def download_package(app_id):
    content = f"Clearance Package Document for Ref: {app_id}\nStatus: Approved & Endorsed"
    pdf_data = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        b"4 0 obj\n<< /Length 75 >>\nstream\n"
        b"BT\n/F1 16 Tf\n50 720 Td\n(TRASHIGANG DZONGKHAG HERITAGE CLEARANCE) Tj\n0 -30 Td\n/F1 12 Tf\n(" + content.encode('ascii', errors='ignore') + b") Tj\nET\n"
        b"endstream\nendobj\n"
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"xref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000117 00000 n \n0000000242 00000 n \n0000000366 00000 n \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n435\n%%EOF\n"
    )
    buffer = io.BytesIO(pdf_data)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"Clearance_{app_id}.pdf", mimetype='application/pdf')

@app.route('/download-notesheet-pdf/<ns_id>')
def download_notesheet_pdf(ns_id):
    ns = next((item for item in notesheets if item["id"] == ns_id), None)
    title = ns["title"] if ns else "Notesheet"
    content = f"Notesheet Ref: {ns_id}\nSubject: {title}\nStatus: Approved & Endorsed"
    
    pdf_data = (
        b"%PDF-1.4\n"
        b"1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n"
        b"2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n"
        b"3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n"
        b"4 0 obj\n<< /Length 85 >>\nstream\n"
        b"BT\n/F1 16 Tf\n50 720 Td\n(TRASHIGANG DZONGKHAG APPROVED NOTESHEET) Tj\n0 -30 Td\n/F1 12 Tf\n(" + content.encode('ascii', errors='ignore') + b") Tj\nET\n"
        b"endstream\nendobj\n"
        b"5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\n"
        b"xref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000060 00000 n \n0000000117 00000 n \n0000000242 00000 n \n0000000366 00000 n \n"
        b"trailer\n<< /Size 6 /Root 1 0 R >>\nstartxref\n445\n%%EOF\n"
    )
    buffer = io.BytesIO(pdf_data)
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"Notesheet_{ns_id}.pdf", mimetype='application/pdf')

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
