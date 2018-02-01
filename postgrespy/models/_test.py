from .testmodels import Student

columns = [
    ('is_smart', 'boolean'),
    ('name', 'text')
]

assert Student._get_columns() == columns
