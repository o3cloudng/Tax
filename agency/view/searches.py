from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from tax.models import Infrastructure, DemandNotice
from django.db.models import Q
from account.models import User


@login_required
def company_search(request):
    search = request.POST.get('search')
    print("SEARCH: ", search)
    all_companies = User.objects.filter(is_tax_admin=False)
    if search:
        companies = all_companies.filter((Q(company_name__icontains=search) \
                                          | Q(sector__name__icontains=search) | Q(phone_number__icontains=search)) \
                                         & Q(is_superuser=False)) #& Q(is_tax_admin=False))
    else:
        companies = User.objects.filter(Q(is_tax_admin=False) & Q(is_superuser=False))

    context = {
        "search": search,
        "companies": companies
    }

    print("COMPANIES: ", companies)
    # return HttpResponse(companies)
    return render(request, "agency/partials/search-result-company.html", context)


@login_required
def search_disputed(request):
    search = request.POST.get('search')
    print("SEARCH: ", search)
    all_disputed = DemandNotice.objects.filter(status__icontains='DISPUTED')
    if search:
        disputed = all_disputed.filter(Q(referenceid__icontains=search)\
            | Q(company__company_name__icontains=search) | Q(company_id__company_name__icontains=search))
    else:
        disputed = DemandNotice.objects.all()[:20]
    context = {
        "search": search,
        "all": disputed
    }
    return render(request, "agency/partials/search-result-disputed.html", context)

@login_required
def search_infrastructure(request):
    search = request.POST.get('search')
    print("SEARCH: ", search)
    all_infrastructure = Infrastructure.objects.all()
    if search:
        infrastructures = all_infrastructure.filter(Q(infra_type__infra_name__icontains=search)\
            | Q(company__company_name__icontains=search) \
                | Q(address__icontains=search))
        # print("INFRA: ", infrastructure.count())
    else:
        infrastructures = Infrastructure.objects.all()[:20]
    context = {
        "search": search,
        "infrastructures": infrastructures
    }
    return render(request, "agency/partials/search-result-infrastructure.html", context)

@login_required
def search_demand_notices(request):
    search = request.POST.get('search')
    print("SEARCH: ", search)
    all_demand_notices = DemandNotice.objects.all()
    if search:
        demand_notices = all_demand_notices.filter(Q(referenceid__icontains=search)\
            | Q(company__company_name__icontains=search) \
                | Q(status__icontains=search))
    else:
        demand_notices = DemandNotice.objects.all()[:20]

    # print("DEMAND NOTICES: ", demand_notices)
    context = {
        "search": search,
        "all": demand_notices
    }
    return render(request, "agency/partials/search-result-dn.html", context)


@login_required
def search_company_details(request):
    search = request.POST.get('search')
    # print("SEARCH: ", search)
    all_demand_notices = DemandNotice.objects.all()
    if search:
        demand_notices = all_demand_notices.filter(Q(referenceid__icontains=search)\
            | Q(infra_type__infra_name__icontains=search) | Q(company_id__company_name__icontains=search))
    else:
        demand_notices = DemandNotice.objects.all()[:20]
    context = {
        "search": search,
        "all": demand_notices
    }
    return render(request, "agency/partials/search-result-details.html", context)


