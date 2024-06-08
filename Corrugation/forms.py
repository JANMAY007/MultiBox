from django import forms
from .models import PurchaseOrder


class PurchaseOrderForm(forms.ModelForm):
    class Meta:
        model = PurchaseOrder
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        tenant = self.instance.tenant
        if tenant:
            if tenant.name == 'Shiv Packaging':
                self.fields['po_given_by'].choices = [
                    ('Sweety Industries', 'Sweety Industries'),
                    ('Sweetco Foods', 'Sweetco Foods'),
                    ('VR Agro Processors LLP', 'VR Agro Processors LLP'),
                    ('Lao More Biscuits Pvt Ltd', 'Lao More Biscuits Pvt Ltd'),
                    ('Makson Pharmaceuticals I Pvt Ltd', 'Makson Pharmaceuticals I Pvt Ltd'),
                    ('GP Manglani Foods Pvt Ltd', 'GP Manglani Foods Pvt Ltd'),
                    ('KMM Foods Pvt Ltd', 'KMM Foods Pvt Ltd'),
                    ('Parle Product Pvt Ltd', 'Parle Product Pvt Ltd'),
                    ('JRJ Foods Pvt Ltd', 'JRJ Foods Pvt Ltd'),
                    ('RZ Dholakia', 'RZ Dholakia'),
                    ('Ishwar Snuff Works', 'Ishwar Snuff Works'),
                    ('Parag Perfumes', 'Parag Perfumes'),
                ]
            else:
                self.fields['po_given_by'].choices = []
        else:
            self.fields['po_given_by'].choices = []
