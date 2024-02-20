from django import template

register = template.Library()

@register.filter(name='arabic_number')
def arabic_number(value):
    arabic_numerals = ['٠', '١', '٢', '٣', '٤', '٥', '٦', '٧', '٨', '٩']
    return ''.join(arabic_numerals[int(digit)] for digit in str(value))
