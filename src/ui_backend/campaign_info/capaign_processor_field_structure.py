

campaign_field_structure = {
  'default': {
    'name': 'default_name',
    'result_function': 'default',
    'result_function_args': {},
    'decorator_function': 'default_decorator',
    'updated_at': '',
    'retry_count': 0,
    'result': '',
    'priority': 10 # чем меньше тем важнее
  },
  'watching_status': {
    'name': 'watching_status',
    'result_function': 'get_advert_status',
    'decorator_function': 'advert_status_decorator',
    'priority': 2
  },
  'budget': {
    'name': 'budget',
    'result_function': 'get_advert_budget',
    'decorator_function': 'advert_budget_decorator',
    'priority': 3
  }
}