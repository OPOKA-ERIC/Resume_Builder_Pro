from django.shortcuts import render, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from resumes.models import Resume


def generate_pdf_html(resume):
    """Render resume data into HTML for PDF conversion."""
    return render_to_string('pdf/resume_pdf.html', {'resume': resume})


@login_required
def download_pdf(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    try:
        from weasyprint import HTML
        html_string = generate_pdf_html(resume)
        pdf = HTML(string=html_string).write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')
        filename = f"{resume.title.replace(' ', '_')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
    except ImportError:
        return HttpResponse(
            "PDF generation requires WeasyPrint. Install it with: pip install weasyprint",
            status=501
        )
