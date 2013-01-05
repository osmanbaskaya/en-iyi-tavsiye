from django import forms

#class UnratedForm(forms.Form):
    #item_id = forms.CharField(widget=forms.HiddenInput)
    #item_name = forms.CharField(widget=forms.TextInput(attrs={'size':40,'readonly':True}))
    #rating = forms.ChoiceField(required=False,widget=forms.RadioSelect, choices=([(i,i) for i in xrange(1,6)]))
    #rating = forms.ChoiceField(required=False,
    #widget=forms.RadioSelect, choices=([('1','1'),('2','2')]))



from django import forms
from book.models import *
#from django.forms import ModelForm
from django.utils.safestring import mark_safe

class HorizRadioRenderer(forms.RadioSelect.renderer):
    """ this overrides widget method to put radio buttons horizontally
        instead of vertically.
    """
    def render(self):
            """Outputs radios"""
            #return mark_safe(u''.join([u'%s' % w for w in self])) + u'</br>' 
            return mark_safe('\n'.join(['\n%s\n' % w for w in self]))

class UnratedForm(forms.Form):
    item_id = forms.CharField(widget=forms.HiddenInput)
    item_name = forms.CharField(widget=forms.TextInput(attrs={'size':40,
                                                            'readonly':True}))
    rating = forms.ChoiceField(required=False,widget=forms.RadioSelect(renderer=HorizRadioRenderer), choices=([(i,i) for i in xrange(1,6)]))


class ItemForm(forms.ModelForm):
    class Meta:
        model=Item
class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ('rating',)
"""
class RatingForm(forms.ModelForm):
    item_name = forms.CharField(widget=forms.TextInput(attrs={'size':40,
                                                        'readonly':True}))
    rating = forms.ChoiceField(required=True,widget=forms.RadioSelect(renderer=HorizRadioRenderer),choices=([(i,i) for i in xrange(1,6)]))
    item_id = forms.CharField(widget=forms.HiddenInput)
    class Meta:
        model = Rating
        fields = ('item_name', 'rating', 'item_id')
"""


class RecommendationForm(forms.Form):
    item_name = forms.CharField(widget=forms.TextInput(attrs={'size':40,
                                                        'readonly':True}))
