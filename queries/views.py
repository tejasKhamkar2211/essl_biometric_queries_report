from django.shortcuts import render, redirect
from django.http import HttpResponse
from datetime import datetime, timedelta
from .models import Query, Functionality
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas


# ================= DASHBOARD =================
def dashboard(request):
    last_queries = Query.objects.order_by('-created_at')[:10]
    last_functionalities = Functionality.objects.order_by('-created_at')[:10]

    biometric_count = Query.objects.filter(related_system='Biometric Device').count()
    ydl_crm_count = Query.objects.filter(related_system='YDL CRM').count()
    total_queries = Query.objects.count()
    functionality_count = Functionality.objects.count()

    return render(request, 'queries/dashboard.html', {
        'queries': last_queries,
        'functionalities': last_functionalities,
        'biometric_count': biometric_count,
        'ydl_crm_count': ydl_crm_count,
        'total_queries': total_queries,
        'functionality_count': functionality_count,
    })


# ================= ADD QUERY =================
def add_query(request):
    if request.method == 'POST':
        Query.objects.create(
            date=request.POST.get('date'),
            fc_id_name=request.POST.get('fc_id_name'),
            description=request.POST.get('description'),
            related_system=request.POST.get('related_system')
        )
        return redirect('dashboard')

    return render(request, 'queries/add_query.html')


# ================= ADD FUNCTIONALITY =================
def add_functionality(request):
    if request.method == 'POST':
        Functionality.objects.create(
            date=request.POST.get('date'),
            fc_id_name=request.POST.get('fc_id_name'),
            description=request.POST.get('description')
        )
        return redirect('dashboard')

    return render(request, 'queries/add_functionality.html')


# ================= DOWNLOAD REPORT FORM =================
def download_report_page(request):
    return render(request, 'queries/download_report.html')


# ================= DOWNLOAD REPORT (PDF) =================



'''

from django.http import HttpResponse
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from .models import Query, Functionality

def download_report(request):
    report_range = request.GET.get('range')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    queries = Query.objects.all()
    functionalities = Functionality.objects.all()
    today = datetime.today().date()

    # ===== DATE FILTER =====
    if report_range == 'today':
        queries = queries.filter(date=today)
        functionalities = functionalities.filter(date=today)
    elif report_range == 'yesterday':
        day = today - timedelta(days=1)
        queries = queries.filter(date=day)
        functionalities = functionalities.filter(date=day)
    elif report_range == 'last7':
        start = today - timedelta(days=7)
        queries = queries.filter(date__range=[start, today])
        functionalities = functionalities.filter(date__range=[start, today])
    elif report_range == 'last30':
        start = today - timedelta(days=30)
        queries = queries.filter(date__range=[start, today])
        functionalities = functionalities.filter(date__range=[start, today])
    elif report_range == 'custom' and start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        queries = queries.filter(date__range=[start, end])
        functionalities = functionalities.filter(date__range=[start, end])

    # ===== SUMMARY COUNTS =====
    biometric_count = queries.filter(related_system='Biometric Device').count()
    ydl_crm_count = queries.filter(related_system='YDL CRM').count()
    total_queries = queries.count()
    functionality_count = functionalities.count()

    # ===== CREATE PDF =====
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="essl_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4,
                            rightMargin=20, leftMargin=20,
                            topMargin=20, bottomMargin=20)
    elements = []
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading2']

    # ===== HEADER =====
    elements.append(Paragraph("ESSL BIOMETRIC QUERIES", styles['Title']))
    elements.append(Spacer(1, 12))

    # ===== QUERIES TABLE WIDTH =====
    total_width = 18 * cm  # Width of Queries table (all tables will match this)
    
    # ===== SUMMARY TABLE =====
    summary_data = [
        ["Biometric Device", "YDL CRM", "Total Queries", "New Functionalities"],
        [str(biometric_count), str(ydl_crm_count), str(total_queries), str(functionality_count)]
    ]
    col_widths_summary = [total_width / 4] * 4  # distribute evenly
    summary_table = Table(summary_data, colWidths=col_widths_summary, hAlign='CENTER')
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 12))

    # ===== QUERIES TABLE =====
    elements.append(Paragraph("Queries", styleH))
    query_data = [["No", "Date", "FC ID & Name", "Description", "System"]]
    for i, q in enumerate(queries, 1):
        query_data.append([
            str(i),
            str(q.date),
            Paragraph(q.fc_id_name, styleN),
            Paragraph(q.description, styleN),
            Paragraph(q.related_system, styleN)
        ])
    col_widths_queries = [1.2*cm, 2.5*cm, 4*cm, 8*cm, 2.3*cm]  # sum ~= total_width
    query_table = Table(query_data, colWidths=col_widths_queries)
    query_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
    ]))
    elements.append(query_table)
    elements.append(Spacer(1, 12))

    # ===== FUNCTIONALITIES TABLE =====
    elements.append(Paragraph("New Functionalities", styleH))
    func_data = [["No", "Date", "FC ID & Name", "Description"]]
    for i, f in enumerate(functionalities, 1):
        func_data.append([
            str(i),
            str(f.date),
            Paragraph(f.fc_id_name, styleN),
            Paragraph(f.description, styleN)
        ])
    # Adjust column widths proportional to match Queries table width
    col_widths_func = [1.2*cm, 2.5*cm, 4*cm, 10.3*cm]  # sum ~= total_width
    func_table = Table(func_data, colWidths=col_widths_func)
    func_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
    ]))
    elements.append(func_table)

    doc.build(elements)
    return response
'''
















from django.http import HttpResponse
from datetime import datetime, timedelta
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import cm
from .models import Query, Functionality

def download_report(request):
    report_range = request.GET.get('range')
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    queries = Query.objects.all()
    functionalities = Functionality.objects.all()
    today = datetime.today().date()

    # ===== DATE FILTER =====
    if report_range == 'today':
        queries = queries.filter(date=today)
        functionalities = functionalities.filter(date=today)
    elif report_range == 'yesterday':
        day = today - timedelta(days=1)
        queries = queries.filter(date=day)
        functionalities = functionalities.filter(date=day)
    elif report_range == 'last7':
        start = today - timedelta(days=7)
        queries = queries.filter(date__range=[start, today])
        functionalities = functionalities.filter(date__range=[start, today])
    elif report_range == 'last30':
        start = today - timedelta(days=30)
        queries = queries.filter(date__range=[start, today])
        functionalities = functionalities.filter(date__range=[start, today])
    elif report_range == 'custom' and start_date and end_date:
        start = datetime.strptime(start_date, "%Y-%m-%d").date()
        end = datetime.strptime(end_date, "%Y-%m-%d").date()
        queries = queries.filter(date__range=[start, end])
        functionalities = functionalities.filter(date__range=[start, end])

    # ===== SUMMARY COUNTS =====
    biometric_count = queries.filter(related_system='Biometric Device').count()
    ydl_crm_count = queries.filter(related_system='YDL CRM').count()
    total_queries = queries.count()
    functionality_count = functionalities.count()

    # ===== CREATE PDF =====
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="essl_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=A4,
                            rightMargin=20, leftMargin=20,
                            topMargin=20, bottomMargin=20)
    elements = []
    styles = getSampleStyleSheet()
    styleN = styles['Normal']
    styleH = styles['Heading2']

    # ===== HEADER =====
    elements.append(Paragraph("ESSL BIOMETRIC QUERIES", styles['Title']))
    elements.append(Spacer(1, 12))

    # ===== QUERIES TABLE WIDTH =====
    total_width = 18 * cm  # All tables will match this width

    # ===== SUMMARY TABLE =====
    summary_data = [
        ["Biometric Device", "YDL CRM", "Total Queries", "New Functionalities"],
        [str(biometric_count), str(ydl_crm_count), str(total_queries), str(functionality_count)]
    ]
    col_widths_summary = [total_width / 4] * 4
    summary_table = Table(summary_data, colWidths=col_widths_summary, hAlign='CENTER')
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN',(0,0),(-1,-1),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'MIDDLE'),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTNAME', (0,1), (-1,1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 12))

    # ===== QUERIES TABLE =====
    elements.append(Paragraph("<para align='center'><b>Queries</b></para>", styleH))
    query_data = [["No", "Date", "FC ID & Name", "Description", "System"]]
    for i, q in enumerate(queries, 1):
        query_data.append([
            str(i),
            str(q.date),
            Paragraph(q.fc_id_name, styleN),
            Paragraph(q.description, styleN),
            Paragraph(q.related_system, styleN)
        ])
    col_widths_queries = [1.2*cm, 2.5*cm, 4*cm, 8*cm, 2.3*cm]
    query_table = Table(query_data, colWidths=col_widths_queries, hAlign='CENTER')
    query_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
    ]))
    elements.append(query_table)
    elements.append(Spacer(1, 12))

    # ===== FUNCTIONALITIES TABLE =====
    elements.append(Paragraph("<para align='center'><b>New Functionalities Added</b></para>", styleH))
    func_data = [["No", "Date", "FC ID & Name", "Description"]]
    for i, f in enumerate(functionalities, 1):
        func_data.append([
            str(i),
            str(f.date),
            Paragraph(f.fc_id_name, styleN),
            Paragraph(f.description, styleN)
        ])
    col_widths_func = [1.2*cm, 2.5*cm, 4*cm, 10.3*cm]
    func_table = Table(func_data, colWidths=col_widths_func, hAlign='CENTER')
    func_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('ALIGN',(0,0),(-1,0),'CENTER'),
        ('VALIGN',(0,0),(-1,-1),'TOP'),
        ('GRID',(0,0),(-1,-1),0.5,colors.black),
        ('FONTNAME',(0,0),(-1,0),'Helvetica-Bold'),
    ]))
    elements.append(func_table)

    doc.build(elements)
    return response





from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Query, Functionality

# ================= DELETE QUERY =================
def delete_query(request, query_id):
    query = get_object_or_404(Query, id=query_id)
    query.delete()
    messages.success(request, "Query deleted successfully!")
    return redirect('dashboard')

# ================= DELETE FUNCTIONALITY =================
def delete_functionality(request, functionality_id):
    func = get_object_or_404(Functionality, id=functionality_id)
    func.delete()
    messages.success(request, "Functionality deleted successfully!")
    return redirect('dashboard')
