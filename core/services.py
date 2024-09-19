from account.models import AdminSetting
from tax.models import Infrastructure, DemandNotice, Infrastructure
from django.db.models import (F, ExpressionWrapper, Q, Sum, Count, CharField, DecimalField, DateTimeField,
                                IntegerField, Value, Case, When, Func)
from django.db.models.functions import Concat, Cast, Now
from datetime import datetime, date

def current_year():
    current_year = []
    for year in range(int(datetime.now().year), 2001, -1):
        current_year.append(year)
    return current_year

def total_due(company, ex):
    # infra = Infrastructure.objects.filter(company=company, is_existing=ex)
    all = Infrastructure.objects.select_related('infra_type') \
        .filter(Q(company=company) & Q(is_existing=ex) & Q(processed=False) & Q(created_by=company))
    
    infrastructure = all.values('infra_type__infra_name', 'cost')\
        .annotate(num = Count('infra_type'), costing = Sum('cost'))\
            .order_by('infra_type')
    # Cost of all Infrastructure
    sum_cost_infrastructure = infrastructure.aggregate(total_sum = Sum('cost'))['total_sum']
    subtotal = infrastructure.aggregate(total = Sum('costing'))['total']
    print("SUBTOTAL: ", subtotal)
    # Application cost
    application_cost = infrastructure.count() * AdminSetting.objects.get(slug='application-fee').rate
    print("APPLICATION FEES: ", application_cost)
    # Administartive fees
    admin_fees = AdminSetting.objects.get(slug='admin-pm-fees').rate * sum_cost_infrastructure / 100
    print("ADMIN FEES: ", admin_fees)

    sar_count = Infrastructure.objects.filter(Q(company=company) & Q(processed=False) & (Q(infra_type__infra_name__icontains='mast') | Q(infra_type__infra_name__icontains='rooftop'))).count()
    if sar_count:
        sar_cost = sar_count * AdminSetting.objects.get(slug='site-assessment').rate
    else:
        sar_cost =0

    print("SAR COUNT: ", sar_count, "SAR COST: ", sar_cost)

    infra = list(infrastructure)

    print("INFRA LIST: ", infra)

    total_sum = sum_cost_infrastructure + application_cost + admin_fees + sar_cost
    print("TOTAL SUM: ", total_sum)

    return total_sum, subtotal, sum_cost_infrastructure, application_cost, admin_fees, sar_cost, infra

def subtotal_due(company):
    all = Infrastructure.objects.select_related('infra_type').filter(company=company)
    infrastructure = all.values('infra_type__infra_name', 'cost')\
        .annotate(num = Count('infra_type'), costing = Sum('cost'))\
            .order_by('infra_type')
    admin_settings = AdminSetting.objects.all()
    # Sub Total
    subtotal = infrastructure.aggregate(total = Sum('costing'))
    # Application
    app_fees = admin_settings.get(slug='application-fee')

    total_app_fee = all.count() * app_fees.rate

    admin_pm_fees = admin_settings.get(slug='admin-pm-fees')
    # print(admin_pm_fees.rate, type(admin_pm_fees.rate))

    admin_pm_fees_sum = admin_pm_fees.rate * subtotal['total'] / 100

    sar_count = all.filter(Q(infra_type__infra_name__icontains='mast') | Q(infra_type__infra_name__icontains='roof')).count()
    # print("SAR: ", admin_settings.get(slug='site-assessment'))
    site_assessment = admin_settings.get(slug='site-assessment')
    site_assessment_cost = sar_count * site_assessment.rate

    # print("SUB TOTAL: ", site_assessment_cost)
    total_due = subtotal['total'] + total_app_fee + admin_pm_fees_sum + site_assessment_cost

    # print("TOTAL DUE: ", total_due)

    return total_due, subtotal #sum_cost_infrastructure, application_cost, admin_fees, sar_cost

def generate_demand_notice():
    demand_notice = Infrastructure.objects.annotate(
        age_in_days = ExpressionWrapper(
            (Now() - F('year_installed')),
            # ExtractDay(Now() - F('year_installed')),
            output_field=IntegerField()
        ),

        penalty_rate = Value(AdminSetting.objects.get(slug="penalty").rate),

        infra_count =  Case(
                When(length=0, then=F('amount')),
                default=Value(1),
                output_field=IntegerField(),
        ),
        # Calculate penalty based on age in days and the daily penalty fee
        penalty = ExpressionWrapper(
            F('age_in_days') * F('penalty_rate') * F('infra_count'),
            output_field=IntegerField()
        )
    )
    return demand_notice

def generate_ref_id():
    today = date.today()
    year = str(today.year)[-2:]
    month = str(today.month).zfill(2)
    
    if DemandNotice.objects.all().exists(): 
        last = DemandNotice.objects.all().count()
    else:
        last = 0
    referenceid = "LA"+year+month + str(last + 1).zfill(5)
    return referenceid

# def penalty_calculation():
#     penalty_sum = Infrastructure.objects.annotate(
#         age_in_days = ExpressionWrapper(
#             (Now() - F('year_installed')) / 86400000000,
#             # ExtractDay(Now() - F('year_installed')),
#             output_field=IntegerField()
#         ),

#         penalty_rate = Value(AdminSetting.objects.get(slug="penalty").rate),

#         infra_count =  Case(
#                 When(length=0, then=F('amount')),
#                 default=Value(1),
#                 output_field=IntegerField(),
#         ),
#         # Calculate penalty based on age in days and the daily penalty fee
#         penalty = ExpressionWrapper(
#             F('age_in_days') * F('penalty_rate') * F('infra_count'),
#             output_field=IntegerField()
#         )
#     )
#     return penalty_sum

def cal_infrastructure():
    total_infra_count = Infrastructure.objects.annotate(
        mast_roof_count = ExpressionWrapper(
            (F('amount')),
            output_field=IntegerField()
        ),

        penalty_rate = Value(AdminSetting.objects.get(slug="penalty").rate),

        infra_count =  Case(
                When(F(infra_type__infra_name__icontains='mast'), then=F('amount')),
                default=Value(1),
                output_field=IntegerField(),
        ),
        # Calculate penalty based on age in days and the daily penalty fee
        penalty = ExpressionWrapper(
            F('age_in_days') * F('penalty_rate') * F('infra_count'),
            output_field=IntegerField()
        )
    )
    return total_infra_count

def penalty_calculation(request, company):
    infrastructure = Infrastructure.objects.filter(Q(company=company) \
                        & Q(is_existing=True) & Q(created_by=request.user) & Q(processed=False))
    admin_settings = AdminSetting.objects.all()
    penalty_fee = infrastructure.annotate(
            days_from_year_till_today = ExpressionWrapper(
                Func(
                    Func(
                        Concat(
                            F('year_installed')+1,
                            Value('-01-02')
                        ),
                        function='julianday'
                    ) - Func(Now(), function='julianday'),
                    function='abs'  # Use abs to ensure the result is positive
                ),
                output_field=IntegerField()
            ),

            num_of_years = ExpressionWrapper(
                Func(Now() - (F('year_installed')+1)),
                output_field=IntegerField()
            ),

            total_annual_fees = F('num_of_years') * Value(admin_settings.get(slug="annual-fee").rate),


            penalty_cost = Value(AdminSetting.objects.get(slug="penalty").rate),

            penalty_fee = F('penalty_cost') *  F('days_from_year_till_today'),

            # penalty = penalty_fee // 10000 * 10000

        )
    total_annual_fees = infrastructure.annotate(
            num_of_years = ExpressionWrapper(
                Now() - (F('year_installed')),
                output_field=IntegerField()
            ),

            total_annual_fees = F('num_of_years') * Value(admin_settings.get(slug="annual-fee").rate),
        )
    return penalty_fee, total_annual_fees


def agency_penalty_calculation(company):
    infrastructure = Infrastructure.objects.filter(Q(company=company) & Q(is_existing=True))
    admin_settings = AdminSetting.objects.all()
    penalty_fee = infrastructure.annotate(
            days_from_year_till_today = ExpressionWrapper(
                Func(
                    Func(
                        Concat(
                            F('year_installed')+1,
                            Value('-01-02')
                        ),
                        function='julianday'
                    ) - Func(Now(), function='julianday'),
                    function='abs'  # Use abs to ensure the result is positive
                ),
                output_field=IntegerField()
            ),

            num_of_years = ExpressionWrapper(
                Func(Now() - (F('year_installed')+1)),
                output_field=IntegerField()
            ),

            total_annual_fees = F('num_of_years') * Value(admin_settings.get(slug="annual-fee").rate),


            penalty_cost = Value(AdminSetting.objects.get(slug="penalty").rate),

            penalty_fee = F('penalty_cost') *  F('days_from_year_till_today'),

            # penalty = penalty_fee // 10000 * 10000

        )
    total_annual_fees = infrastructure.annotate(
            num_of_years = ExpressionWrapper(
                Now() - (F('year_installed')),
                output_field=IntegerField()
            ),

            total_annual_fees = F('num_of_years') * Value(admin_settings.get(slug="annual-fee").rate),
        )
    return penalty_fee, total_annual_fees

def agency_total_due(company, ex, agency):
    # infra = Infrastructure.objects.filter(company=company, is_existing=ex)
    all = Infrastructure.objects.select_related('infra_type') \
        .filter(Q(company=company) & Q(is_existing=ex) & Q(processed=False) & Q(created_by=agency))
    print("ALL TOTAL: ", all)
    
    infrastructure = all.values('infra_type__infra_name', 'cost')\
        .annotate(num = Count('infra_type'), costing = Sum('cost'))\
            .order_by('infra_type')
    # Cost of all Infrastructure
    sum_cost_infrastructure = infrastructure.aggregate(total_sum = Sum('cost'))['total_sum']
    subtotal = infrastructure.aggregate(total = Sum('costing'))['total']
    print("SUBTOTAL: ", subtotal)
    # Application cost
    application_cost = infrastructure.count() * AdminSetting.objects.get(slug='application-fee').rate
    print("APPLICATION FEES: ", application_cost)
    # Administartive fees
    admin_fees = AdminSetting.objects.get(slug='admin-pm-fees').rate * sum_cost_infrastructure / 100
    print("ADMIN FEES: ", admin_fees)

    sar_count = Infrastructure.objects.filter(Q(company=company) & Q(processed=False) & (Q(infra_type__infra_name__icontains='mast') | Q(infra_type__infra_name__icontains='rooftop'))).count()
    if sar_count:
        sar_cost = sar_count * AdminSetting.objects.get(slug='site-assessment').rate
    else:
        sar_cost =0

    print("SAR COUNT: ", sar_count, "SAR COST: ", sar_cost)

    infra = list(infrastructure)

    print("INFRA LIST: ", infra)

    total_sum = sum_cost_infrastructure + application_cost + admin_fees + sar_cost
    print("TORAL SUM: ", total_sum)

    return total_sum, subtotal, sum_cost_infrastructure, application_cost, admin_fees, sar_cost, infra
