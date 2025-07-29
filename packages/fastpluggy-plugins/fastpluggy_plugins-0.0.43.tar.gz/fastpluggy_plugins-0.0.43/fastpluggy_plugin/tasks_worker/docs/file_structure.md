
# Folder Structure

tasks_worker/
    ├── README.md                  # Project overview and features
    ├── __init__.py                # Package initialization
    ├── config.py                  # Configuration settings
    ├── log_handler.py             # Live logs & stream logs logic
    ├── plugin.py                  # FastPluggy plugin integration
    ├── pyproject.toml             # Project metadata and dependencies
    ├── requirements.txt           # Project dependencies
    ├── runner.py                  # Task runner implementation
    ├── task_registry.py           # Task registration and discovery
    ├── utils.py                   # Utility functions
    ├── docs/                      # Documentation
    │   ├── TODO.md                # Planned enhancements and tasks
    │   ├── file_structure.md      # This file - project structure
    │   ├── task_registry.md       # Task registry documentation
    │   ├── task_scheduler.md      # Task scheduler documentation
    │   └── widgets.md             # Widgets documentation
    ├── executor/                  # Task execution logic
    │   ├── __init__.py
    │   └── thread_executor.py     # Thread-based task execution
    ├── models/                    # Data models
    │   ├── __init__.py
    │   ├── context.py             # Task context model
    │   ├── notification.py        # Notification models
    │   ├── report.py              # Task report models
    │   └── scheduled.py           # Scheduled task models
    ├── notifiers/                 # Notification system
    │   ├── __init__.py
    │   ├── base.py                # BaseNotifier class
    │   ├── console.py             # ConsoleNotifier
    │   ├── database.py            # DatabaseNotifier
    │   ├── loader.py              # Notifier loader
    │   ├── registry.py            # Notifier registry
    │   └── webhook.py             # WebhookNotifier
    ├── repository/                # Data storage and retrieval
    │   ├── __init__.py
    │   ├── context.py             # Task context repository
    │   ├── report.py              # Task report repository
    │   ├── schedule_monitoring.py # Schedule monitoring repository
    │   ├── scheduled.py           # Scheduled task repository
    │   └── task_events.py         # Task events repository
    ├── router/                    # API and UI routes
    │   ├── __init__.py
    │   ├── api_notifier.py        # Notifier API
    │   ├── api_registry.py        # Registry API
    │   ├── api_tasks.py           # Tasks API
    │   ├── debug.py               # Debug routes
    │   ├── front.py               # Frontend routes
    │   ├── front_lock.py          # Lock management UI
    │   ├── front_notifier.py      # Notifier UI
    │   ├── front_schedule.py      # Schedule UI
    │   └── metrics.py             # Metrics routes
    ├── schema/                    # Data schemas
    │   ├── __init__.py
    │   ├── context.py             # Task context schema
    │   ├── dummy_celery.py        # Celery compatibility
    │   ├── notifier.py            # Notifier schema
    │   ├── report.py              # Task report schema
    │   ├── request_input.py       # API request schemas
    │   ├── status.py              # Status schemas
    │   └── task_event.py          # Task event schemas
    ├── services/                  # Business logic services
    │   ├── __init__.py
    │   ├── celery_discovery.py    # Celery task discovery
    │   ├── lock_manager.py        # Task lock management
    │   ├── notification_service.py # Notification service
    │   └── task_discovery.py      # Task discovery service
    ├── static/                    # Static assets
    │   ├── css/
    │   └── js/
    ├── tasks/                     # Task implementations
    │   ├── __init__.py
    │   ├── maintenance.py         # Maintenance tasks
    │   ├── plugin_update.py       # Plugin update tasks
    │   ├── scheduler.py           # Scheduler tasks
    │   └── watchdog.py            # Watchdog tasks
    ├── templates/                 # HTML templates
    │   ├── dashboard.html.j2
    │   ├── graph.html.j2
    │   ├── monitoring/
    │   ├── notifier_modal.html.j2
    │   ├── scheduled_monitor.html.j2
    │   ├── task_details.html.j2
    │   └── task_form.html.j2
    ├── tests/                     # Test suite
    │   ├── __init__.py
    │   ├── fake_celery_app/
    │   └── test_celery_discovery.py
    └── widgets/                   # UI widgets
        ├── __init__.py
        ├── task_form.py           # Task form widget
        └── task_run_button.py     # Task run button widget
