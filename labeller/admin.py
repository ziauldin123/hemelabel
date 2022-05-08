from django.contrib import admin

# Register your models here.
from labeller.models import Patient, Slide, Region, Cell, Project, CellType, CellFeature, Diagnosis

admin.site.register(Patient)

class SlideAdmin(admin.ModelAdmin):
    list_display = ('id', 'sid', 'name', 'created_by', 'date_added')
    list_filter = ('date_added', 'diagnoses', 'created_by')
    search_fields = ('sid', 'diagnoses')

admin.site.register(Slide, SlideAdmin)

class RegionAdmin(admin.ModelAdmin):
    list_display = ('id', 'rid', 'slide', 'created_by', 'date_added')
    list_filter = ('slide', 'date_added', 'created_by')
    search_fields = ('slide', 'created_by')

admin.site.register(Region, RegionAdmin)

class CellAdmin(admin.ModelAdmin):
    list_display = ('cid', 'region', 'created_by', 'date_added')
    list_filter = ('created_by', 'date_added')
    search_fields = ('region', 'created_by')

admin.site.register(Cell, CellAdmin)

class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_by', 'date_added')

admin.site.register(Project, ProjectAdmin)

class CellTypeAdmin(admin.ModelAdmin):
    list_display = ('id', 'cell_type', 'cell', 'user')
    list_filter = ('cell_type',)
    search_fields = ('cell_type',)

admin.site.register(CellType, CellTypeAdmin)

class CellFeatureAdmin(admin.ModelAdmin):
    list_display = ('featureName', 'featureAbbreviation')

admin.site.register(CellFeature, CellFeatureAdmin)

class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'abbreviation')

admin.site.register(Diagnosis, DiagnosisAdmin)