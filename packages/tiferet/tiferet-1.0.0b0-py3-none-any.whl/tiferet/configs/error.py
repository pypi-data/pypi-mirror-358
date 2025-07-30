# *** imports


# *** configs

# ** config: errors
ERRORS = [
    dict(
        id='parameter_parsing_failed',
        name='Parameter Parsing Failed',
        error_code='PARAMETER_PARSING_FAILED',
        message=[
            dict(lang='en_US', text='Failed to parse parameter: {}. Error: {}')
        ]
    ),
    dict(
        id='import_dependency_failed',
        name='Import Dependency Failed',
        error_code='IMPORT_DEPENDENCY_FAILED',
        message=[
            dict(lang='en_US', text='Failed to import dependency: {} from module {}. Error: {}')
        ]
    ),
    dict(
        id='app_repository_import_failed',
        name='App Repository Import Failed',
        error_code='APP_REPOSITORY_IMPORT_FAILED',
        message=[
            dict(lang='en_US', text='Failed to import app repository: {}.')
        ]
    ),
    dict(
        id='app_interface_not_found',
        name='App Interface Not Found',
        error_code='APP_INTERFACE_NOT_FOUND',
        message=[
            dict(lang='en_US', text='App interface with ID {} not found.')
        ]
    ),
    dict(
        id='feature_command_loading_failed',
        name='Feature Command Loading Failed',
        error_code='FEATURE_COMMAND_LOADING_FAILED',
        message=[
            dict(lang='en_US', text='Failed to load feature command attribute: {}. Ensure the container attributes are configured with the appropriate default settings/flags. {}')
        ]
    )
]