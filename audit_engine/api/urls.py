from . import views
from . import engagements_views, audit_views, internal_views
from django.urls import path

urlpatterns = [
    path("", views.getRoutes, name="get-routes"),

    # Paths for screen 2.
    path('getAllAudits', engagements_views.getAllAudits),
    path('viewAuditSummary', engagements_views.viewAuditSummary),
    path('addAudit', engagements_views.addAudit),
    path('editAudit', engagements_views.editAudit),
    path('deleteAudit',  engagements_views.deleteAudit),
    path('viewAuditInfo', engagements_views.viewAuditInfo),
    path('inactiveAuditInfo', engagements_views.inactiveateAuditInfo),
    path('getAuditScore', engagements_views.getAuditScore),

    # Paths for screen 4.
    path('companyAuditStatusSummary', engagements_views.companyAuditStatusSummary), # Top boxes,
    path('companyAuditSummary', engagements_views.companyAuditSummary), # engagement boxes,
    path('filterAudit', engagements_views.filterAudit),
    path('searchAudit', engagements_views.searchAudit),
    path('sortAudit', engagements_views.sortAudit),
    path('triggerScoreGeneration', internal_views.triggerScoreGeneration),

    # Paths for screen 10 and 11.
    path('viewAuditGrid', audit_views.getAuditDetails),
    
    # path("status/", views.getStatus, name="get-status"),
    # path("compliance-score/", views.getOverallScore, name="get-compliance-score"),
    # path("ViewAuditSummary/", views.getEngagements.as_view()),
    # path("getAllAudits", engagements_views.getEngagementDetails),
    # path("create-engagements", engagements_views.createEngagement.as_view()),
    # path("edit-engagements", engagements_views.editEngagement),
    # path("delete-engagements", engagements_views.deleteEngagement),
    # path("company-engagements", engagements_views.companyEngagements),
    # path("company-detailed-audit", audit_views.getAuditDetails),
]
