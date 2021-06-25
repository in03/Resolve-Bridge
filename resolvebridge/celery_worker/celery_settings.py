""" Celery settings.
Submodules have their own adjacent settings files.
"""
# Always need an outer dict
defaults = dict(

    broker = dict(
        # Structure: <protocol>://<user>:<password>@<IP address>:<port>/<virtual host>
        # By default the virtual host is a trailing slash! Don't forget it.
        broker_url = 'amqp://guest:guest@192.168.10:5672/',

        # List of modules to import when the Celery worker starts.
        imports = (
            'proxy_encoder.tasks',
        ),

        result_backend = 'rpc://',
    ),
    worker = dict(

        # Additional settings
        worker_prefetch_multiplier = 1,
        celery_acks_late = True,


        enable_utc = True,
        timezone ='Australia/Brisbane',
        result_expires = 18000, # 5 hours
        worker_pool_restarts = True,

    )
)
