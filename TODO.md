# TODO


[ ] Multi-Supplier Serial Numbers for Components
Add support for a component to have one or more (número de série, fornecedor) pairs. The first entry is treated as the "padrão" (default). The existing serie_number field on 
Component
 will be deprecated/kept as null for data already saved and replaced by the new model.

Proposed Changes
1. New Model — ComponentSupplier
[MODIFY] 
components/models.py
Add a new intermediate model:

python
class ComponentSupplier(models.Model):
    component   = ForeignKey(Component, related_name="suppliers")
    supplier    = ForeignKey(Supplier, on_delete=PROTECT)
    serie_number = CharField(max_length=200, blank=True)
    is_default  = BooleanField(default=False)
    class Meta: ordering = ["-is_default", "id"]
Keep the old serie_number on 
Component
 as null=True, blank=True (backward compat — will not be shown in forms anymore but data is preserved).
2. Migration
[NEW] components/migrations/0009_componentsupplier.py
Auto-generated via makemigrations.

3. Form — ComponentSupplierFormSet
[MODIFY] 
components/forms.py
Add:

ComponentSupplierForm — a single row (supplier select + serie_number input + is_default radio)
ComponentSupplierFormSet via inlineformset_factory — allows adding/removing rows dynamically, min_num=1, extra=0
4. Views — create & update pass the formset
[MODIFY] 
components/views.py
ComponentCreateView
 → override 
get_context_data
 and 
form_valid
 to handle the formset
ComponentUpdateView
 → same, pre-populate the formset with existing ComponentSupplier rows
5. Templates
[MODIFY] 
components/templates/component_create.html
[MODIFY] 
components/templates/component_update.html
Add a "Fornecedores / Números de Série" section with:
An add row button (JS)
Each row: Supplier selector, Serie number input, Default radio, Remove button
Hidden Django management form inputs
[MODIFY] 
components/templates/component_detail.html
Replace the single Nº de série stat pill with a table/list showing all 
(supplier, serie_number, is_default)
 rows
6. Admin
[MODIFY] 
components/admin.py
Register ComponentSupplier as an inline on ComponentAdmin.

Verification Plan
Run python manage.py makemigrations && python manage.py migrate
Open create/update component — add 2 supplier rows, verify save
Open detail — verify both suppliers appear, default is marked
Delete a row — verify it is removed

# In the future
[ ] Create backup.sh script to backup the app/media and PostgreSQL database
[ ] Create route to run the backup and download backup_datetime.tar file
[ ] Update route to upload the backup.tar file
[ ] Update route function to restore media, PostgreSQL database, checkbox for user to choose
