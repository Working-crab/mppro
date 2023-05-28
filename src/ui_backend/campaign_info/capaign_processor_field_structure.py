

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
  },
  'campaign_name': {
    'name': 'campaign_name',
    'result_function': 'get_campaign_name',
    'decorator_function': 'campaign_name_decorator',
    'priority': 2
  },
  'id_advert': {
    'name': 'id_advert',
    'result_function': 'get_id_advert',
    'decorator_function': 'id_advert_decorator',
    'priority': 1
  },
  'settings': {
    'name': 'settings',
    'result_function': 'get_settings',
    'decorator_function': 'settings_decorator',
    'priority': 4
  },
  'analitics': {
    'name': 'analitics',
    'result_function': 'get_analitics_command_str',
    'decorator_function': 'analitics_decorator',
    'priority': 5
  }
}