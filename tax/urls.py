from django.urls import path
from .views import new_infra_view, existing_infra_view, page_view, import_export, htmx_view
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('apply/permit/', new_infra_view.new_infrastructure, name="apply_for_permit"),
    path('apply/demand_notice/<str:ref_id>/', new_infra_view.generate_demand_notice, name="generate_demand_notice"),
    path('apply/demand_notice/receipt/<str:ref_id>/', new_infra_view.generate_receipt, name="generate_receipt"),
    # path('apply/permit/edit/<str:ref_id>/', new_infra_view.apply_for_permit_edit, name="apply_for_permit_edit"),
    # path('apply/permit/demand_notice/<str:ref_id>/', new_infra_view.demand_notice_receipt, name="demand-notice-receipt"),
    # path('apply/permit/dispute_notice/<str:ref_id>/', new_infra_view.dispute_demand_notice, name="dispute-demand-notice"),
    # path('apply/permit/demand_notice/receipt/<str:ref_id>/', new_infra_view.dispute_demand_notice_receipt, name="dispute-demand-notice-receipt"),
    # path('apply/permit/undisputed_notice_receipt/<str:ref_id>/', new_infra_view.undispute_demand_notice_receipt, name="undispute_demand_notice_receipt"),
    path('apply/permit/resources/', new_infra_view.resources, name="resources"),
    # path('apply/permit/dn/edit/<int:pk>/', new_infra_view.dispute_dn_edit, name="dispute-dn-edit"),
    
    # path('apply/permit/add/new/<str:ref_id>/', new_infra_view.add_new_permit_form, name="add_new_permit_form"),
    # path('apply/permit/add/new/ex/<str:ref_id>/', new_infra_view.add_new_ex_permit_form, name="add_new_ex_permit_form"),
    
    # HTMX endpoint
    path('apply/infra/', htmx_view.add_infrastructure_form, name="add_infrastructure_form"),
    path('apply/infra/ex/', htmx_view.add_ex_infrastructure_form, name="add_ex_infrastructure_form"),
    path('apply/infra/add/', htmx_view.add_infrastructure, name="add_infrastructure"),
    path('apply/infra/add2/', htmx_view.add_infrastructure2, name="add_infrastructure2"),
    path('apply/infra/ex/add/', htmx_view.add_ex_infrastructure, name="add_ex_infrastructure"),
    path('apply/infra/ex/add2/', htmx_view.add_ex_infrastructure2, name="add_ex_infrastructure2"),

    # HTMX SEARCH
    path('apply/search/', htmx_view.search_tax_dn, name="search_tax_dn"),

    # path('apply/permit/add/', new_infra_view.add_permit_form, name="add_permit_form"),
    # path('apply/permit/dn/edit/add/', new_infra_view.add_dispute_dn_edit, name="add_dispute_dn_edit"),
    # path('apply/permit/dn/add/', new_infra_view.add_undispute_edit, name="add_undispute_edit"),
    # path('apply/permit/dn/add/ex/', new_infra_view.add_ex_undispute_edit, name="add_ex_undispute_edit"),
    # path('apply/permit/dn/delete/<int:pk>/', new_infra_view.del_undisputed_edit, name="del_undisputed_edit"),
    # path('apply/permit/dn/accept/<int:pk>/', new_infra_view.accept_undisputed_edit, name="accept_undisputed_edit"),

    ####### Exisiting Infrastructures
    # path('apply/permit/existing_permit', view.existing_permit, name="existing_permit"),
    path('apply/permit/exist/', existing_infra_view.apply_for_existing_permit, name="apply_existing_infra"),
    path('apply/demand_notice/ex/<str:ref_id>/', existing_infra_view.generate_ex_demand_notice, name="generate_ex_demand_notice"),
    path('apply/demand_notice/ex/receipt/<str:ref_id>/', existing_infra_view.generate_ex_receipt, name="generate_ex_receipt"),
    # path('apply/permit/add_permit_ex_form/', existing_infra_view.add_permit_ex_form, name="add_permit_ex_form"),
    # path('apply/permit/demand_notice_ex/receipt/<str:ref_id>/', existing_infra_view.demand_notice_ex_receipt, name="demand_notice_ex_receipt"),
    # path('apply/permit/upload_existing_facilities/', existing_infra_view.upload_existing_facilities, name="upload-existing-facilities"),
    path('apply/permit/dispute_ex_notice/<str:ref_id>/', existing_infra_view.dispute_ex_demand_notice, name="dispute-ex-demand-notice"),
    path('apply/permit/undisputed_ex_notice_receipt/<str:ref_id>/', existing_infra_view.undispute_ex_demand_notice_receipt, name="undispute_ex_demand_notice_receipt"),
    path('apply/permit/revised/receipt/<str:ref_id>/', existing_infra_view.revised_demand_notice_receipt, name="revised_demand_notice_receipt"),
    # path('apply/permit/ex/dn/edit/add/', existing_infra_view.add_dispute_ex_dn_edit, name="add_ex_dispute_dn_edit"),
    # path('apply/permit/ex/dn/edit/<int:pk>/', existing_infra_view.dispute_ex_dn_edit, name="dispute_ex_dn_edit"),
    path('apply/waver/', existing_infra_view.apply_for_waver, name="apply_for_waver"),
    path('apply/remittance/', existing_infra_view.apply_remittance, name="apply_remittance"),
    # path('apply/permit/dn/ex/accept/<int:pk>/', existing_infra_view.accept_ex_undisputed_edit, name="accept_ex_undisputed_edit"),
    # path('apply/permit/dn/ex/delete/<int:pk>/', existing_infra_view.del_ex_undisputed_edit, name="del_ex_undisputed_edit"),

    #  PAGES URL
    path('dashboard/', page_view.dashboard, name="dashboard"),
    path('demand_notice/', page_view.demand_notice, name="demand-notice"),
    path('disputes/', page_view.disputes, name="disputes"),
    path('infrastructures/', page_view.infrastructures, name="infrastructures"),
    path('downloads/', page_view.downloads, name="downloads"),
    path('resources/', page_view.resources, name="resources"),
    # settings/ is in the account app

    # BULK UPLOAD (CSV / EXCEL)
    path('upload/new/', import_export.upload_new, name="upload_new"),
]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) 
