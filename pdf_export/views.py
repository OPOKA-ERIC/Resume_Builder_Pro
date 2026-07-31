import logging
from django.shortcuts import render, get_object_or_404, redirect, HttpResponse
from django.contrib.auth.decorators import login_required
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.http import urlencode
from xhtml2pdf import pisa
from resumes.models import Resume

logger = logging.getLogger(__name__)


def _pay_gate_redirect(request, resume, view_name):
    """Return a redirect to payment if the resume is not paid, else None."""
    if resume.is_paid:
        return None
    pay_url = reverse('resumes:resume_pay', args=[resume.id])
    next_url = reverse(view_name, args=[resume.id])
    return redirect(f'{pay_url}?{urlencode({"next": next_url})}')

TEMPLATE_STYLES = {
    'galaxy': {
        'header_align': 'center', 'font_family': "Georgia, 'Times New Roman', serif",
        'header_border_bottom': 'none',
    },
    'aether': {
        'header_align': 'left', 'font_family': "'Inter', 'Segoe UI', Arial, sans-serif",
    },
    'astral': {
        'header_align': 'left', 'font_family': "'Inter', 'Segoe UI', Arial, sans-serif",
    },
    'axis': {
        'header_align': 'left', 'font_family': "'Inter', 'Segoe UI', Arial, sans-serif",
    },
    'celestial': {
        'header_align': 'left', 'font_family': "'Inter', 'Segoe UI', Arial, sans-serif",
    },
    'classic-europass': {
        'header_align': 'center', 'font_family': "Georgia, 'Times New Roman', serif",
    },
    'comet': {
        'header_align': 'left', 'font_family': "'Inter', 'Segoe UI', Arial, sans-serif",
    },
    'eclipse': {
        'header_align': 'left', 'font_family': "'Inter', 'Segoe UI', Arial, sans-serif",
    },
    'executive': {
        'header_align': 'left', 'font_family': "'Inter', 'Segoe UI', Arial, sans-serif",
    },
    'modern-clean': {
        'header_align': 'left', 'font_family': "'Inter', 'Segoe UI', Arial, sans-serif",
    },
    'nebula': {
        'header_align': 'left', 'font_family': "'Inter', 'Segoe UI', Arial, sans-serif",
    },
    'nebular': {
        'header_align': 'center', 'font_family': "Georgia, 'Times New Roman', serif",
    },
    'orbit': {
        'header_align': 'left', 'font_family': "'Inter', 'Segoe UI', Arial, sans-serif",
    },
    'professional-sidebar': {
        'header_align': 'left', 'font_family': "'Inter', 'Segoe UI', Arial, sans-serif",
    },
    'pulsar': {
        'header_align': 'left', 'font_family': "'Inter', 'Segoe UI', Arial, sans-serif",
    },
    'quasar': {
        'header_align': 'center', 'font_family': "Georgia, 'Times New Roman', serif",
    },
    'stellar': {
        'header_align': 'center', 'font_family': "Georgia, 'Times New Roman', serif",
    },
    'zenith': {
        'header_align': 'left', 'font_family': "'Inter', 'Segoe UI', Arial, sans-serif",
    },
}


def _lighten_color(hex_color):
    hex_color = hex_color.lstrip('#')
    r, g, b = int(hex_color[:2], 16), int(hex_color[2:4], 16), int(hex_color[4:6], 16)
    r = int(r + (255 - r) * 0.9)
    g = int(g + (255 - g) * 0.9)
    b = int(b + (255 - b) * 0.9)
    return f'#{r:02x}{g:02x}{b:02x}'


def generate_pdf_html(resume):
    """Render resume data into PDF-optimized HTML using the selected template's colors."""
    user = resume.user
    context = {
        'resume': resume,
        'user': user,
        'accent': '#1d4ed8',
        'accent_soft': '#dbeafe',
        'text_primary': '#111827',
        'text_secondary': '#4b5563',
        'header_align': 'left',
        'header_border_bottom': '2px solid #1d4ed8',
        'font_family': "'Inter', 'Segoe UI', Arial, sans-serif",
    }

    if resume.template:
        tmpl = resume.template
        if tmpl.swatches:
            context['accent'] = tmpl.swatches[0]
            context['accent_soft'] = _lighten_color(tmpl.swatches[0])
            context['header_border_bottom'] = f'2px solid {tmpl.swatches[0]}'

        skin_name = ''
        if tmpl.skin_file:
            skin_name = tmpl.skin_file.replace('skins/', '').replace('.html', '')
        elif tmpl.html_file:
            skin_name = tmpl.html_file.replace('templates/', '').replace('.html', '')

        style = TEMPLATE_STYLES.get(skin_name, {})
        context['header_align'] = style.get('header_align', 'left')
        context['font_family'] = style.get('font_family', "'Inter', 'Segoe UI', Arial, sans-serif")
        if 'header_border_bottom' in style:
            context['header_border_bottom'] = style['header_border_bottom']

    html = render_to_string('pdf/resume_pdf_themed.html', context)
    return html


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
    pay_gate = _pay_gate_redirect(request, resume, 'pdf_export:download_pdf')
    if pay_gate:
        return pay_gate

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
    pay_gate = _pay_gate_redirect(request, resume, 'pdf_export:pdf_preview')
    if pay_gate:
        return pay_gate
    html_string = generate_pdf_html(resume)
    return render(request, 'pdf/pdf_preview.html', {
        'resume': resume,
        'pdf_html': html_string,
    })
