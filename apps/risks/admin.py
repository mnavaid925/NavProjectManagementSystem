from django.contrib import admin

from .models import Issue, Risk, RiskAnalysis, RiskResponse, RiskReview


@admin.register(Risk)
class RiskAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'category', 'probability', 'impact',
                    'status', 'owner', 'tenant', 'created_at')
    list_filter = ('status', 'category', 'probability', 'impact', 'tenant')
    search_fields = ('number', 'title', 'description')


@admin.register(RiskAnalysis)
class RiskAnalysisAdmin(admin.ModelAdmin):
    list_display = ('risk', 'analysis_type', 'probability_pct', 'impact_cost',
                    'risk_level', 'analyzed_by', 'tenant', 'created_at')
    list_filter = ('analysis_type', 'risk_level', 'tenant')
    search_fields = ('notes', 'risk__title')


@admin.register(RiskResponse)
class RiskResponseAdmin(admin.ModelAdmin):
    list_display = ('risk', 'strategy', 'action_owner', 'cost', 'status',
                    'tenant', 'created_at')
    list_filter = ('strategy', 'status', 'tenant')
    search_fields = ('planned_action', 'description', 'risk__title')


@admin.register(Issue)
class IssueAdmin(admin.ModelAdmin):
    list_display = ('number', 'title', 'severity', 'priority', 'status',
                    'assigned_to', 'tenant', 'created_at')
    list_filter = ('status', 'severity', 'priority', 'tenant')
    search_fields = ('number', 'title', 'description')


@admin.register(RiskReview)
class RiskReviewAdmin(admin.ModelAdmin):
    list_display = ('title', 'project', 'review_date', 'reviewed_by',
                    'risks_reviewed', 'status', 'tenant')
    list_filter = ('status', 'tenant')
    search_fields = ('title', 'summary')
