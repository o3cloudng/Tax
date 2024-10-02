from django.db import models
from account.models import User
from datetime import datetime
# import timezone
# from simple_history.models import HistoricalRecords
    


class InfrastructureType(models.Model):
    infra_name = models.CharField(max_length=200, null=False)
    rate = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.infra_name

    

class Infrastructure(models.Model):
    infra_type = models.ForeignKey(InfrastructureType, related_name="infra_type", on_delete=models.CASCADE)
    company = models.ForeignKey(User, related_name="com", on_delete=models.CASCADE)
    length = models.IntegerField(null=True, default=0)
    address = models.CharField(max_length=200, blank=True)
    created_by = models.CharField(max_length=200, blank=True)
    year_installed = models.PositiveIntegerField(default=datetime.now().year)
    upload_application_letter = models.FileField(upload_to='uploads/applications/', blank=True, null=True)
    upload_asBuilt_drawing = models.FileField(upload_to='uploads/drawings/', blank=True, null=True)
    is_existing = models.BooleanField(default=False)
    processed = models.BooleanField(default=False)
    referenceid=models.CharField(max_length=20, null=True)
    cost = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # history = HistoricalRecords()
    # penalty calculations
    def __str__(self):
        return f"{self.company} - ({self.infra_type})"

class DemandNotice(models.Model):
    PAY_CHOICES = (
        ("DEMAND NOTICE", "Demand Notice"),
        ("UNDISPUTED UNPAID", "Undisputed Unpaid"),
        ("UNDISPUTED PAID", "Undisputed Paid"),
        ("REVISED", "Revised"),
        ("RESOLVED", "Resolved"),
    )
    
    referenceid = models.CharField(max_length=200, null=True) 
    company = models.ForeignKey(User, related_name="company", on_delete=models.CASCADE, null=True)
    is_exisiting = models.BooleanField(default=False)
    infra = models.CharField(max_length=1000)
    amount_due = models.PositiveIntegerField(default=0)
    subtotal = models.PositiveIntegerField(default=0)
    penalty = models.PositiveIntegerField(default=0)
    application_fee = models.PositiveIntegerField(default=0)
    admin_fee = models.PositiveIntegerField(default=0)
    site_assessment = models.PositiveIntegerField(default=0)
    annual_fee = models.PositiveIntegerField(default=0)
    remittance = models.PositiveIntegerField(default=0)
    waiver_applied = models.PositiveIntegerField(default=0)
    amount_paid = models.PositiveIntegerField(default=0)
    total_due = models.IntegerField(default=0)

    status = models.CharField(max_length=30, choices=PAY_CHOICES, default="UNPAID")
    created_by = models.CharField(max_length=200, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # history = HistoricalRecords()

    def save(self, *args, **kwargs):
        if self.pk:
            self.updated_at = datetime.now()
            original = DemandNotice.objects.get(pk=self.pk)
            self.amount_due = self.total_due
            if original.remittance != self.remittance or original.waiver_applied != self.waiver_applied:
                self.total_due = self.calculated_total_due()
        else:
            self.updated_at = datetime.now()
            self.total_due = self.calculated_total_due()
        super(DemandNotice, self).save(*args, **kwargs)

    def calculated_total_due(self):
        self.total_due = self.subtotal + self.penalty + self.application_fee + self.admin_fee + \
            self.site_assessment - self.remittance - self.waiver_applied + self.annual_fee
        return self.total_due

    # def update(self, *args, **kwargs):
    #     self.total_due = self.subtotal + self.penalty + self.application_fee + self.admin_fee + self.site_assessment - self.remittance - self.waiver
    #     super(DemandNotice, self).save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.referenceid}"



class Waiver(models.Model):
    referenceid = models.CharField(max_length=20)
    company = models.ForeignKey(User, related_name="companyid", on_delete=models.CASCADE)
    wave_amount = models.IntegerField(default=0)
    receipt = models.FileField(upload_to='uploads/receipts/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.wave_amount}"


class Remittance(models.Model):
    referenceid = models.CharField(max_length=20)
    company = models.ForeignKey(User, related_name="remit_comp", on_delete=models.CASCADE)
    remitted_amount = models.IntegerField(blank=True)
    receipt = models.FileField(upload_to='uploads/receipts/', blank=True, null=True)
    approved = models.BooleanField(default=False)
    apply_for_waver = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.referenceid} - {self.remitted_amount}"
    
# class Permit(models.Model):
#     PAY_CHOICES = (
#         ("UNPAID", "Unpaid"),
#         ("PAID", "Paid"),
#         ("DISPUTED", "Disputed"),
#         ("Revised", "Revised"),
#     )
    
#     company = models.ForeignKey(User, related_name="comp", on_delete=models.CASCADE, null=True)
#     referenceid = models.CharField(max_length=200, null=True) 
#     infra_type = models.ForeignKey(InfrastructureType, related_name="infra", on_delete=models.CASCADE)
#     amount = models.IntegerField(null=True, default=0) 
#     length = models.IntegerField(null=True, default=0)
#     add_from = models.CharField(max_length=200, blank=True)
#     add_to = models.CharField(max_length=200, blank=True)
#     created_by = models.CharField(max_length=200, blank=True)
#     year_installed = models.DateTimeField(max_length=200, null=True, default=datetime.now())
#     age = models.PositiveIntegerField(blank=True, default=0)
#     upload_application_letter = models.FileField(upload_to='uploads/applications/', blank=True, null=True)
#     upload_asBuilt_drawing = models.FileField(upload_to='uploads/drawings/', blank=True, null=True)
#     upload_payment_receipt = models.FileField(upload_to='uploads/receipts/', blank=True, null=True)
#     status = models.CharField(max_length=10, choices=PAY_CHOICES, default="UNPAID")
#     is_profile_complete = models.BooleanField(default=False)
#     is_disputed = models.BooleanField(default=False)
#     is_undisputed = models.BooleanField(default=False)
#     is_revised = models.BooleanField(default=False)
#     is_paid = models.BooleanField(default=False)
#     is_existing = models.BooleanField(default=False)
#     infra_cost = models.IntegerField(default=0)
#     created_at = models.DateTimeField(auto_now_add=True)
#     modified_at = models.DateTimeField(auto_now=True)

#     def save(self, *args, **kwargs):
#         if self.is_existing:
#             installed_date = self.year_installed
#         else:
#             installed_date = datetime.strptime(str(self.year_installed), '%Y-%m-%d')
#         today = datetime.now()
#         age = (today - installed_date).days

#         if "mast" in self.infra_type.infra_name.lower():
#             cummulative_age = int(self.amount) * age
#         elif "roof" in self.infra_type.infra_name.lower():
#             cummulative_age = int(self.amount) * age
#         else:
#             cummulative_age = age * 1

#         self.age = cummulative_age

#         super(Permit, self).save(*args, **kwargs)

#     def __str__(self):
#         if self.is_existing:
#             prem = "Existing Infrastructure"
#         else:
#             prem = "New Infrastructure"
#         return f"{self.referenceid} - ({prem}) ---- {self.infra_type}"
    