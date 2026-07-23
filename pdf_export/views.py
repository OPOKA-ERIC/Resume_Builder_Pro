import logging
from django.shortcuts import render, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from xhtml2pdf import pisa
from resumes.models import Resume

logger = logging.getLogger(__name__)


def generate_pdf_html(resume):
    """Render resume data into HTML for PDF conversion using the selected template."""
    user = resume.user
    template_path = 'pdf/resume_pdf.html'
    if resume.template and resume.template.html_file:
        template_path = resume.template.html_file
    return render_to_string(template_path, {
        'resume': resume,
        'user': user,
    })


def render_to_pdf(html_string, filename):
    """Convert HTML string to PDF response using xhtml2pdf."""
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    pisa_status = pisa.CreatePDF(html_string, dest=response)
    if pisa_status.err:
        return None
    return response


@login_required
def download_pdf(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    try:
        html_string = generate_pdf_html(resume)
        filename = f"{resume.title.replace(' ', '_')}.pdf"
        response = render_to_pdf(html_string, filename)
        if response:
            logger.info(f"PDF generated for resume '{resume.title}' by user {request.user.username}")
            return response
        logger.error(f"PDF rendering failed for resume {resume_id}")
        return HttpResponse("PDF generation failed. Please try again.", status=500)
    except Exception as e:
        logger.error(f"PDF generation failed for resume {resume_id}: {str(e)}")
        return HttpResponse(
            "An error occurred while generating the PDF. Please try again later.",
            status=500
        )


@login_required
def pdf_preview(request, resume_id):
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)
    html_string = generate_pdf_html(resume)
    return render(request, 'pdf/pdf_preview.html', {
        'resume': resume,
        'pdf_html': html_string,
    })
