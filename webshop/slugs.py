from django.urls.converters import SlugConverter
from django.core.validators import RegexValidator
from django.db.models import SlugField

# Upper and lower case slug converters
class USlug(SlugConverter): regex = '[A-Z0-9][-a-zA-Z0-9_]{2,49}'
class LSlug(SlugConverter): regex = '[a-z][-a-zA-Z0-9_]{2,49}'

validate_uslug = RegexValidator(f"^{USlug.regex}$",
    "Enter a capitalized 'slug' of at least three letters, numbers, underscores or hyphens. The first character must be upper case or number.",
    'invalid'
)

validate_lslug = RegexValidator(f"^{LSlug.regex}$",
    "Enter a lower-case 'slug' of at least three letters, numbers, underscores or hyphens. The first character must be lower case.",
    'invalid'
)

# Model fields
class USlugField(SlugField): default_validators = validate_uslug,
class LSlugField(SlugField): default_validators = validate_lslug,
