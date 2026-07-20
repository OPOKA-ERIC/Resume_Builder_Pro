from django.shortcuts import get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from resumes.models import Resume


def generate_pdf(resume, user):
    """Convert resume HTML to PDF using xhtml2pdf."""
    html_string = render_to_string('pdf/resume_pdf.html', {
        'resume': resume,
        'user': user,
    })
    response = HttpResponse(content_type='application/pdf')
    filename = f"{resume.title.replace(' ', '_')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return HttpResponse('PDF generation failed', status=500)
    return response


@login_required
def download_pdf(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    return generate_pdf(resume, request.user)
