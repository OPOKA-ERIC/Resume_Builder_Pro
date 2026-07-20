import logging
from django.shortcuts import render, get_object_or_404, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from resumes.models import Resume

logger = logging.getLogger(__name__)


def generate_pdf_html(resume):
    """Render resume data into HTML for PDF conversion."""
    user = resume.user
    return render_to_string('pdf/resume_pdf.html', {
        'resume': resume,
        'user': user,
    })


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
        logger.info(f"PDF generated for resume '{resume.title}' by user {request.user.username}")
        return response
    except ImportError:
        logger.error("WeasyPrint is not installed")
        return HttpResponse(
            "PDF generation requires WeasyPrint. Install it with: pip install weasyprint",
            status=501
        )
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
