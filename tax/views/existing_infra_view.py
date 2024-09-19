from django.shortcuts import render, redirect
from tax.forms import WaiverForm, RemittanceForm, BulkUploadForm
from django.contrib.auth.decorators import login_required
from account.models import AdminSetting
from tax.models import InfrastructureType, Waiver, Remittance, Infrastructure, DemandNotice
from datetime import date, datetime
from django_htmx.http import HttpResponseClientRedirect
from django.db.models import (F, ExpressionWrapper, Q, Sum, Count, CharField, DecimalField, DateTimeField,
                                IntegerField, Value, Case, When, Func)
from django.db.models.functions import Concat, Cast, Now
from django.contrib import messages
from agency.models import Agency
from core.decorator import tax_payer_only
# from agency.penalty_calculation import penalty_calculation
from core.services import current_year, generate_ref_id, total_due, penalty_calculation, subtotal_due
from core import settings
import json


@login_required
@tax_payer_only
def apply_for_waver(request):
    if request.method == 'POST':
        if Waiver.objects.filter(Q(company=request.user) & Q(referenceid=request.POST.get('referenceid'))).exists():
            messages.error(request, 'You have already applied for waver.')
            # return redirect('dispute-ex-demand-notice', request.POST.get('referenceid'))

        form = WaiverForm(request.POST or None, request.FILES or None)
        
        if form.is_valid():
            print("WAVER HERE FORM IS VALID ")
            wave = form.save(commit=False)
            wave.referenceid = request.POST.get('referenceid')
            wave.company = request.user
            wave.save()

            messages.success(request, 'Your request for waver was sent successfully.')
            return redirect('dispute-ex-demand-notice', request.POST.get('referenceid'))
        else:
            print("FILE FORMAT INVALID", form.errors)
      
        messages.error(request, 'Your request for waver failed.')
        return redirect('dispute-ex-demand-notice', request.POST.get('referenceid'))

@login_required
@tax_payer_only
def apply_remittance(request):
    if request.method == 'POST':
        # if Remittance.objects.filter(Q(company=request.user) & Q(referenceid=request.POST.get('referenceid'))).exists():
        #     messages.error(request, 'You have already applied for waver.')
        #     return redirect('dispute-ex-demand-notice', request.POST.get('referenceid'))
        
        # if Remittance.objects.filter(Q(company=request.user) & Q(referenceid = request.POST.get('referenceid'))).exists():
        #     remit = Remittance.objects.get(Q(company=request.user) & Q(referenceid = request.POST.get('referenceid')))
        #     form = RemittanceForm(request.POST or None, request.FILES or None, instance=remit)
        #     print("REMIT: = ", remit)
        # else:
        #     form = RemittanceForm(request.POST or None, request.FILES or None)
        rem = DemandNotice.objects.get(Q(company=request.user) & Q(referenceid = request.POST.get('referenceid')))
        if Remittance.objects.filter(Q(company=request.user) & Q(referenceid = request.POST.get('referenceid'))).exists():
            remit = Remittance.objects.get(Q(company=request.user) & Q(referenceid = request.POST.get('referenceid')))
            form = RemittanceForm(request.POST or None, request.FILES or None, instance=remit)
            # print("REMIT: = ", remit)
        else:
            form = RemittanceForm(request.POST or None, request.FILES or None)


        
        if form.is_valid():
            print("WAVER HERE FORM IS VALID ")

            if not int(request.POST.get('remitted_amount')):
                total_due = rem.subtotal + rem.annual_fee + rem.penalty + rem.application_fee + \
                    rem.admin_fee + rem.site_assessment - int(request.POST.get('remitted_amount'))
            else:
                total_due = rem.subtotal + rem.annual_fee + rem.application_fee + \
                rem.admin_fee + rem.site_assessment - int(request.POST.get('remitted_amount'))
            
            print("TOTAL DUE: ", total_due)

            remit = DemandNotice.objects.filter(Q(company=request.user) & Q(referenceid = request.POST.get('referenceid')))
            # print("TOTAL DUE: ", total_due)
            remit.update(remittance=request.POST.get('remitted_amount'), total_due=total_due)
            
            remittance = form.save(commit=False)
            remittance.referenceid = request.POST.get('referenceid')
            remittance.company = request.user
            remittance.apply_for_waver = request.POST.get('apply_for_waver')
            remittance.save()

            messages.success(request, 'Your remittance was added successfully.')
            return redirect('dispute-ex-demand-notice', request.POST.get('referenceid'))
        else:
            print("FILE FORMAT INVALID", form.errors)
      
        messages.error(request, 'Your remittance failed.')
        return redirect('dispute-ex-demand-notice', request.POST.get('referenceid'))


def age(the_date):
    date_format = "%m/%d/%Y"

    a = datetime.strptime(the_date, date_format)
    b = datetime.now()

    delta = b - a
    return delta.days


@login_required
@tax_payer_only
def apply_for_existing_permit(request):
    ref_id = generate_ref_id()
    print("EXISITING: APPLY FOR EXISTING PERMIT")
    # form = PermitExForm()
    upload_form = BulkUploadForm()
    current_year = []
    for year in range(int(datetime.now().year), 2001, -1):
        current_year.append(year)
        
    infrastructures= Infrastructure.objects\
        .filter(Q(is_existing = True) \
            & Q(company=request.user) & Q(processed=False) & Q(created_by=request.user)) \
            .order_by('-created_at')
        
    context = {
        # 'form':form,
        'infra': 'Mast',
        'referenceid': ref_id,
        'current_year': current_year,
        'company': request.user,
        'infrastructures': infrastructures,
        'infra_types': InfrastructureType.objects.all(),
        'infrastructure': InfrastructureType.objects.all().first(),
        'infra_types': InfrastructureType.objects.all().order_by('pk'),
        'upload_form': upload_form
    }

    return render(request, 'tax-payers/existing_infra_temp/apply_for_exist.html', context)



@login_required
def generate_ex_demand_notice(request, ref_id):
    company = request.user
    
    total_sum, subtotal, sum_cost_infrastructure, application_cost, admin_fees, sar_cost, infra = total_due(company, True)
    # print("TOTAL DUES: ", total_sum, sum_cost_infrastructure, application_cost, admin_fees, sar_cost)

    penalty_fee, total_annual_fees = penalty_calculation(request, company)
    penalty = penalty_fee.filter(Q(is_existing=True) & Q(processed=False)).values('penalty_fee').aggregate(penal = Sum('penalty_fee'))
    penalty = (penalty['penal'] // 10000) * 10000

    annual_fees = total_annual_fees.filter(Q(is_existing=True) & Q(processed=False)).values('total_annual_fees').aggregate(total = Sum('total_annual_fees'))['total']
    
    print("ANNUAL FEES: ", annual_fees, type(annual_fees))
    
    # Save to Demand Notice Table
    # referenceid, company, created_by, status (unpaid, disputed, revised, paid, resolved)
    # infrastructure cost, 
    obj, created = DemandNotice.objects.update_or_create(
        referenceid=ref_id,
        created_by=request.user,
        company=request.user,
        is_exisiting = True,
        infra = infra,
        subtotal = subtotal,
        amount_due = subtotal + application_cost + admin_fees + sar_cost,
        annual_fee = annual_fees,
        penalty = penalty,
        application_fee = application_cost,
        admin_fee = admin_fees,
        site_assessment = sar_cost,
        total_due = total_sum + penalty + annual_fees,
        status="DEMAND NOTICE",
        defaults={'referenceid': ref_id},
    )
    if obj or created:
        infra = Infrastructure.objects.filter(Q(is_existing=True) & Q(processed=False))
        infra.update(processed=True, referenceid=ref_id)
        messages.success(request, 'Demand notice created.')
        return redirect('generate_ex_receipt', ref_id)
    
    messages.error(request, 'Failed to generate demand notice')
    return redirect('apply_existing_infra')


@login_required
def generate_ex_receipt(request, ref_id):
    admin_settings = AdminSetting.objects.all()

    demand_notice = DemandNotice.objects.get(referenceid=ref_id)

    infra = demand_notice.infra
    infra = infra.replace("'", '"')
    infra = json.loads(infra)
    # print(type(infra), infra)

    context = {
        # 'infrastructure': infrastructure,
        'ref_id': ref_id,
        'subtotal': demand_notice.subtotal,
        'agency': Agency.objects.all().first(),
        'app_fee': admin_settings.get(slug='application-fee'),
        'total_app_fee': demand_notice.application_fee,
        'admin_pm_fees': demand_notice.admin_fee,
        'admin_pm_fees_sum': demand_notice.admin_fee,
        'annual_fees': demand_notice.annual_fee,
        'annual_fee': admin_settings.get(slug='annual-fee').rate,
        'total_due': demand_notice.total_due,
        'admin_rate':admin_settings.get(slug='admin-pm-fees').rate,
        'sar_fee':admin_settings.get(slug='site-assessment').rate,
        'infrastructure': infra,
        'penalty': demand_notice.penalty,
        'total_liability': demand_notice.total_due,
        'site_assessment_cost': demand_notice.site_assessment       
    }
    return render(request, 'tax-payers/receipts/demand-notice-ex-receipt.html', context)


@login_required # Dispute Demand Notice - Issues
@tax_payer_only
def dispute_ex_demand_notice(request, ref_id):
    company = request.user
    remittance = DemandNotice.objects.get(Q(company=company) & Q(referenceid=ref_id))
    if Remittance.objects.filter(Q(company=company) & Q(referenceid=ref_id)).exists():
        remit = Remittance.objects.get(Q(company=company) & Q(referenceid=ref_id))
        form = RemittanceForm(request.POST or None, request.FILES or None, instance=remit)
        print("REMIT: = ", remit)
    else:
        form = RemittanceForm(request.POST or None, request.FILES or None)

    demand_notice = DemandNotice.objects.get(referenceid=ref_id)
    penalty = demand_notice.penalty
    remittance = demand_notice.remittance
    waiver_applied = demand_notice.waiver_applied
    amount_paid = demand_notice.amount_paid
    amount_due = demand_notice.amount_due
    annual_fee = demand_notice.annual_fee
    total_liability = demand_notice.total_due #- demand_notice.penalty

    print("REMITTANCE: ", remittance, type(remittance))

    context = {
        'ref_id': ref_id,
        'demand_notice': demand_notice,
        'penalty': penalty,
        'amount_paid': amount_paid,
        'amount_due': amount_due,
        'annual_fee': annual_fee,
        'remittance': remittance,
        'waiver_applied': waiver_applied,
        'total_liability': total_liability,
        'agency': Agency.objects.all().first(),
        'remittance': remittance,
        'form': form
    }
    return render(request, 'tax-payers/existing_infra_temp/apply_for_ex_permit_edit.html', context)


@login_required
# @tax_payer_only
def undispute_ex_demand_notice_receipt(request, ref_id):
    company = request.user

    admin_settings = AdminSetting.objects.all()

    demand_notice = DemandNotice.objects.get(referenceid=ref_id)
    if demand_notice:
        DemandNotice.objects.filter(referenceid=ref_id).update(status="UNDISPUTED UNPAID")

    infra = demand_notice.infra
    infra = infra.replace("'", '"')
    infra = json.loads(infra)
    # print(type(infra), infra)

    context = {
        'infra': infra,
        'ref_id': ref_id,
        'subtotal': demand_notice.subtotal,
        'agency': Agency.objects.all().first(),
        'app_fee': admin_settings.get(slug='application-fee'),
        'total_app_fee': demand_notice.application_fee,
        'admin_pm_fees': demand_notice.admin_fee,
        'admin_pm_fees_sum': demand_notice.admin_fee,
        'site_assessment': demand_notice.site_assessment,
        'total_due': demand_notice.total_due,
        'admin_rate':admin_settings.get(slug='admin-pm-fees').rate,
        'sar_fee':admin_settings.get(slug='site-assessment').rate,
        'annual_fee':admin_settings.get(slug='annual-fee').rate,
        'infrastructure': infra,
        'penalty': demand_notice.penalty,
        'remittance': demand_notice.remittance,
        'annual_fees': demand_notice.annual_fee,
        'total_liability': demand_notice.total_due,
        'site_assessment_cost': demand_notice.site_assessment       
    }
    return render(request, 'tax-payers/receipts/undisputed_ex_dn_receipt.html', context)


# @login_required
# # @tax_payer_only
# def add_permit_ex_form(request):
#     print("ADDING EXISITING INFRASTRUCTURE FORM")
#     if Permit.objects.all().exists(): 
#         last = Permit.objects.latest("pk").id
#         ref_id = "LA"+generate_ref_id() + str(last + 1).zfill(5)
#     else:
#         ref_id = "LA"+generate_ref_id() + "00001"
    
#     permits = Permit.objects.all()
#     if request.method == "POST":
#         form = PermitForm(request.POST or None, request.FILES or None)
#         if form.is_valid():
#             permit = form.save(commit=False)
#             permit.referenceid = ref_id
#             permit.company = request.user
#             permit.is_existing = True
#             permit.save()
#             permits = Permit.objects.all()
#             context = {
#                 'permits': permits
#             }

#             return render(request, 'tax-payers/partials/permit_details.html', context)
#         else:
#             print("ERROR: ", form.errors)

#     context = {
#         'form':form,
#         'referenceid': ref_id,
#         'company': request.user
#     }
#     return render(request, 'tax-payers/partials/apply_permit_ex_form.html', context)


# # Receipt (DN)
# @login_required
# # @tax_payer_only
# def demand_notice_ex_receipt(request, ref_id):
#     permits = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_existing=True))

#     if not permits.exists(): # If permit does not exist
#         return redirect('apply_for_permit')
    
#     if not permits.first().company == request.user: # If permite does not belong to signed in company
#         return redirect('apply_for_permit')
    
#     ref = permits.first()
#     app_fee = AdminSetting.objects.get(slug="application-fee")
#     site_assessment = AdminSetting.objects.get(slug="site-assessment")
#     admin_pm_fees = AdminSetting.objects.get(slug="admin-pm-fees")
#     penalty = AdminSetting.objects.get(slug="penalty")

#     mast_roof = Permit.objects.filter((Q(referenceid = ref_id) & Q(is_disputed=False) & Q(is_existing=True)) & (Q(infra_type__infra_name__istartswith='Mast') | Q(infra_type__infra_name__istartswith='Roof')))
    
#     length = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_disputed=False) & Q(is_existing=True) & (Q(infra_type__infra_name__istartswith='Optic') | Q(infra_type__infra_name__istartswith='Gas') | Q(infra_type__infra_name__istartswith='Power') | Q(infra_type__infra_name__istartswith='Pipe')))
#     #application number = number of masts and rooftops 

#     if mast_roof.exists():
#         mast_roof_no = mast_roof.aggregate(no_sites = Sum('amount'))['no_sites']
#     else:
#         mast_roof_no = 0
#     # print("MAST & ROOF NO: ", mast_roof.count())
#     if length.exists():
#         app_count = mast_roof_no + length.count()
#         others_sum = length.aggregate(no_sites = Sum('amount'))['no_sites']
#         print("GAS SUM: ", others_sum)
#     else:
#         app_count = mast_roof_no + 0

#     total_app_fee = app_count * app_fee.rate
#     tot_sum_infra = Permit.objects.filter(Q(referenceid = ref_id) & Q(is_existing=True)).aggregate(no_sum = Sum('infra_cost'))
#     # Site assessment report rate
#     sar_rate = mast_roof_no * site_assessment.rate
#     admin_pm_fees_sum = (admin_pm_fees.rate * tot_sum_infra['no_sum']) / 100

#     total_due = tot_sum_infra['no_sum'] + total_app_fee + admin_pm_fees_sum + sar_rate

#     print("TOTAL SUM INFRA: ", tot_sum_infra['no_sum'])
#     # ADD WAVER
#     if Waiver.objects.filter(referenceid=ref).exists():
#         waver = Waiver.objects.get(referenceid=ref).wave_amount
#     else:
#         waver = 0
#     # PENALTY CALCULATION
#     refid = Q(referenceid = ref_id)
#     is_exist = Q(is_existing=True)
#     not_dispute = Q(is_disputed=False)
#     not_paid = Q(is_paid=False)
#     # current_user = Q(comapny = request.user)
#     if Permit.objects.filter(refid & is_exist).exists():
#         penalty_sum = penalty_calculation() 
#         penalty_sum = penalty_sum.filter(refid & is_exist & not_paid)
#         if penalty_sum.exists():
#             penalty_sum = penalty_sum.aggregate(sum_penalties = Sum('penalty'))['sum_penalties'] // 10000 * 10000
#             print("PENALTY SUM: ", penalty_sum)
#         else:
#             penalty_sum = 0

#     else:
#         penalty_sum = 0

#     total_liability = total_due + penalty_sum - waver

#     context = {
#         'permits': permits,
#         'ref': ref,
#         'site_assessment': site_assessment,
#         'site_assess_count': mast_roof_no,
#         'admin_pm_fees': admin_pm_fees,
#         'app_fee': app_fee,
#         'app_count': app_count,
#         'total_app_fee': total_app_fee,
#         'sar_rate': sar_rate,
#         'tot_sum_infra': tot_sum_infra,
#         'admin_pm_fees_sum': admin_pm_fees_sum,
#         'total_due': total_due,
#         'waver': waver,
#         'total_liability': total_liability,
#         'ref_id': ref_id,
#         'penalty_sum': penalty_sum,
#         'penalty': penalty,
#         'agency': Agency.objects.all().first()
#     }
#     return render(request, 'tax-payers/receipts/demand-notice-ex-receipt .html', context)



# @login_required
# @tax_payer_only
# def accept_ex_undisputed_edit(request, pk):
#     permit = Permit.objects.get(pk=pk)

#     print("ACCEPT URL WORKING.....")
#     print(permit)

#     permit = Permit.objects.create(
#         company= permit.company,
#         referenceid= permit.referenceid,
#         infra_type= permit.infra_type,
#         amount= permit.amount,
#         length= permit.length,
#         add_from= permit.add_from,
#         add_to= permit.add_to,
#         year_installed= str(permit.year_installed), 
#         age= permit.age,
#         upload_application_letter= permit.upload_application_letter,
#         upload_asBuilt_drawing= permit.upload_asBuilt_drawing,
#         upload_payment_receipt= permit.upload_payment_receipt,
#         status= permit.status,
#         is_disputed= True,
#         is_undisputed= permit.is_undisputed,
#         is_revised= permit.is_revised,
#         is_paid= permit.is_paid,
#         is_existing= True
#     )
#     messages.success(request, "Accepted.")
#     return redirect('dispute-ex-demand-notice', permit.referenceid)
#     # return HttpResponseClientRedirect('/tax/apply/permit/dispute_ex_notice/'+permit.referenceid)


# @login_required
# @tax_payer_only
# def del_ex_undisputed_edit(request, pk):
#     permit = Permit.objects.get(pk=pk)
#     permit.delete()

#     print("DELETE EX WORKING....: ")

#     return HttpResponseClientRedirect('/tax/apply/permit/dispute_ex_notice/'+permit.referenceid)



@login_required
# @tax_payer_only
def revised_demand_notice_receipt(request, ref_id):
    company = request.user
    admin_settings = AdminSetting.objects.all()

    demand_notice = DemandNotice.objects.get(referenceid=ref_id)

    infra = demand_notice.infra
    infra = infra.replace("'", '"')
    infra = json.loads(infra)
    # print(type(infra), infra)

    context = {
        'company': company,
        'ref_id': ref_id,
        'subtotal': demand_notice.subtotal,
        'agency': Agency.objects.all().first(),
        'app_fee': admin_settings.get(slug='application-fee'),
        'total_app_fee': demand_notice.application_fee,
        'admin_pm_fees': demand_notice.admin_fee,
        'admin_pm_fees_sum': demand_notice.admin_fee,
        'annual_fees': demand_notice.annual_fee,
        'annual_fee': admin_settings.get(slug='annual-fee').rate,
        'amount_due': demand_notice.amount_due + demand_notice.annual_fee,
        'admin_rate':admin_settings.get(slug='admin-pm-fees').rate,
        'sar_fee':admin_settings.get(slug='site-assessment').rate,
        'infrastructure': infra,
        'penalty': demand_notice.penalty,
        'total_liability': demand_notice.total_due,
        'waiver_applied': demand_notice.waiver_applied,
        'site_assessment_cost': demand_notice.site_assessment       
    }
    return render(request, 'tax-payers/receipts/revised_receipt.html', context)


# @login_required
# @tax_payer_only
# def add_dispute_ex_dn_edit(request):
#     ref_id = str(request.POST['referenceid'])
#     # print("REF: ", ref_id)
#     if request.method == 'POST':
#         form = PermitEditForm(request.POST or None, request.FILES or None)

#         infra_rate = InfrastructureType.objects.get(pk=request.POST['infra_type'])
        
#         if "mast" in infra_rate.infra_name.lower():
#             len = 0
#             qty = request.POST['amount']
#             infra_cost = infra_rate.rate * int(request.POST['amount'])
#         elif "roof" in infra_rate.infra_name.lower():
#             len = 0
#             qty = request.POST['amount']
#             infra_cost = infra_rate.rate * int(request.POST['amount'])
#         else:
#             infra_cost = infra_rate.rate * int(request.POST['length'])
#             len = request.POST['length']
#             qty = 0

#         # Convert year to int and add 1 then convert to datetime
#         year = int(request.POST['year']) + 1
#         str_year = str(year)+"-01-01"
#         installed_date = datetime.strptime(str(str_year), '%Y-%m-%d').date()
#         print("INSTALLED DATE: ", installed_date, type(installed_date))

#         if form.is_valid():
#             # print("Form is valid")
#             permit = form.save(commit=False)
#             permit.referenceid = ref_id
#             permit.company = request.user
#             permit.amount = qty
#             permit.length = len
#             permit.year_installed = installed_date
#             permit.infra_cost = infra_cost
#             permit.is_disputed = True
#             permit.is_existing = True
#             permit.save()

#             context = {
#                 'form':form,
#                 'referenceid': ref_id,
#                 'company': request.user
#             }
#             return HttpResponseClientRedirect('/tax/apply/permit/dispute_ex_notice/'+permit.referenceid)

#         else:
#             print("FILE FORMAT INVALID")
#     form = PermitForm()

#     context = {
#         'form':form,
#         'referenceid': ref_id,
#         'company': request.user
#     }
#     return HttpResponseClientRedirect('/tax/apply/permit/dispute_notice/'+permit.referenceid)


# @login_required
# @tax_payer_only
# def dispute_ex_dn_edit(request, pk):
#     permit = Permit.objects.get(pk=pk)
#     form = PermitEditForm(instance = permit)
#     context = {
#         'form': form
#     }
#     return render(request, 'tax-payers/partials/apply_ex_permit_edit_form.html', context)
