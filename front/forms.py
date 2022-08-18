from django import forms
from django.contrib.auth import get_user_model


from .models import Contract, CONDITIONS_CHOICE, SERVICE_CHOICE

User = get_user_model()

NumberFormControl = lambda: forms.NumberInput(attrs={"class": "form-control"})
TextFormControl = lambda: forms.TextInput(attrs={"class": "form-control"})
TextAreaFormControl = lambda: forms.Textarea(attrs={"class": "form-control"})
SelectFromControl = lambda: forms.Select(attrs={"class": "form-select"})
SelectFromControlTitle = lambda: forms.Select(attrs={"class": "form-select", "placeholder": "information" })
CheckBoxFormControl = lambda: forms.CheckboxInput(attrs={"type": "radio"})
CheckboxSelectMultiple = lambda : forms.CheckboxInput(attrs={"class": "form-check-input"})





class LoginForm(forms.ModelForm):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ['username', 'password']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].label = 'Логин'
        self.fields['password'].label = 'Пароль'

    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        if not User.objects.filter(username=username).exists():
            raise forms.ValidationError('Несуществующий логин | Error #500') #Несуществующий логин
        user = User.objects.filter(username=username).first()
        if user:
            if not user.check_password(password):
                raise forms.ValidationError('Неправильный пароль | Error #501') #Несуществующий пароль
        return self.cleaned_data


def readonly(widget):
    widget.attrs["readonly"] = True
    widget.attrs["disabled"] = True
    return widget


def rows(widget, size):
    widget.attrs["rows"] = size
    return widget


def cols(widget, size):
    widget.attrs["cols"] = size
    return widget


class ContractCreateForm(forms.ModelForm):
    priority_service = forms.MultipleChoiceField(widget=forms.CheckboxSelectMultiple, choices=SERVICE_CHOICE)
    class Meta:
        model = Contract
        widgets = {
            "name": rows(TextFormControl(), 1),
            "city": TextFormControl(),
            "address": TextFormControl(),
            "phone": TextFormControl(),
            "from_office": CheckBoxFormControl(),
        }
        fields = widgets.keys()


class ContractInfoForm(forms.ModelForm):
    class Meta:
        model = Contract
        widgets = {
            "name": (TextFormControl()),
            "city": (TextFormControl()),
            "address": (TextFormControl()),
            "phone": (TextFormControl()),
            "service_first": readonly(TextFormControl()),  # Услуга №1
            "service_two": readonly(TextFormControl()),  # Услуга №2
            "conditions_first": (SelectFromControlTitle()),  # условия подключения услуги №1
            "conditions_two": (SelectFromControl()),  # условия подключения услуги №2
            "equipment_first": (SelectFromControl()),  # оборудование для услуги №1
            "equipment_two": (SelectFromControl()),  # оборудование для услуги №2
            "request_number": (TextFormControl()),  # номер заявки
            "status": (SelectFromControl()),  # статус заявки
            "exodus_in": (SelectFromControl()),
            "exodus_tv": (SelectFromControl()),
        }
        fields = widgets.keys()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        #status_excluded = [0, 1]
        #self.fields["status"].choices = [(k,v) for k,v in self.fields["status"].choices if k not in status_excluded]


class ContractHistorySearchForm(forms.Form):
    created_by = forms.ChoiceField(required=False)
    conditions_first = forms.ChoiceField(choices=CONDITIONS_CHOICE, required=False)
