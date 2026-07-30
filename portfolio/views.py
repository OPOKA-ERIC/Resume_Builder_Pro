import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Portfolio

logger = logging.getLogger(__name__)


@login_required
def portfolio_list(request):
    portfolios = Portfolio.objects.filter(user=request.user)
    return render(request, 'portfolio/list.html', {'portfolios': portfolios})


@login_required
def portfolio_create(request, resume_id):
    from resumes.models import Resume
    resume = get_object_or_404(Resume, id=resume_id, user=request.user)

    exists = Portfolio.objects.filter(user=request.user, resume=resume).first()
    if exists:
        messages.info(request, f'Portfolio already exists for "{resume.title}".')
        return redirect('portfolio:manage', portfolio_id=exists.id)

    if request.method == 'POST':
        portfolio = Portfolio.objects.create(user=request.user, resume=resume)
        logger.info(f'Portfolio created: {portfolio.id} for resume {resume.id} by user {request.user.username}')
        messages.success(request, 'Portfolio created! Share it with the link below.')
        return redirect('portfolio:manage', portfolio_id=portfolio.id)

    return render(request, 'portfolio/create.html', {'resume': resume})


@login_required
def portfolio_manage(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    return render(request, 'portfolio/manage.html', {'portfolio': portfolio})


@login_required
def portfolio_toggle_publish(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    portfolio.is_published = not portfolio.is_published
    portfolio.save(update_fields=['is_published'])
    status = 'published' if portfolio.is_published else 'unpublished'
    messages.success(request, f'Portfolio {status} successfully.')
    return redirect('portfolio:manage', portfolio_id=portfolio.id)


@login_required
def portfolio_delete(request, portfolio_id):
    portfolio = get_object_or_404(Portfolio, id=portfolio_id, user=request.user)
    if request.method == 'POST':
        resume_title = portfolio.resume.title
        portfolio.delete()
        messages.success(request, f'Portfolio for "{resume_title}" deleted.')
        return redirect('portfolio:list')
    return render(request, 'portfolio/confirm_delete.html', {'portfolio': portfolio})


def _normalize_url(url):
    if not url or not url.strip():
        return None
    url = url.strip()
    if url.startswith(('http://', 'https://')):
        return url
    return f'https://{url}'


def public_portfolio_view(request, slug):
    portfolio = get_object_or_404(Portfolio, slug=slug, is_published=True)
    portfolio.views += 1
    portfolio.save(update_fields=['views'])

    resume = portfolio.resume

    # Normalize project links so relative URLs don't break
    for project in resume.projects.all():
        project.safe_link = _normalize_url(project.link)

    user_profile = getattr(resume.user, 'profile', None)
    public_url = f'{request.scheme}://{request.get_host()}{portfolio.get_public_url()}'

    user = resume.user
    display_name = user.get_full_name().strip() or user.username.replace('_', ' ').replace('-', ' ').strip().title()

    return render(request, 'portfolio/public.html', {
        'portfolio': portfolio,
        'resume': resume,
        'profile': user_profile,
        'public_url': public_url,
        'display_name': display_name,
    })
