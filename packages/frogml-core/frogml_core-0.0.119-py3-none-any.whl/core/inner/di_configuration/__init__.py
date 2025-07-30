import os

from .account import UserAccountConfiguration
from .containers import FrogmlContainer


def wire_dependencies():
    container = FrogmlContainer()

    default_config_file = os.path.join(os.path.dirname(__file__), "config.yml")
    container.config.from_yaml(default_config_file)

    from frogml.core.clients import (
        build_management,
        kube_deployment_captain,
    )
    from ...clients import model_version_manager
    from ...clients import analytics
    from ...clients import system_secret
    from ...clients import autoscaling
    from ...clients import build_orchestrator
    from ...clients import batch_job_management
    from ...clients import instance_template
    from ...clients import feature_store
    from ...clients import deployment
    from ...clients import user_application_instance
    from ...clients import jfrog_gateway
    from ...clients import alert_management
    from ...clients import integration_management
    from ...clients import model_management
    from ...clients import audience
    from ...clients import data_versioning
    from ...clients import project
    from ...clients import logging_client
    from ...clients import automation_management
    from ...clients import file_versioning
    from ...clients import alerts_registry
    from ...clients import administration

    container.wire(
        packages=[
            administration,
            alert_management,
            audience,
            automation_management,
            autoscaling,
            analytics,
            batch_job_management,
            build_management,
            build_orchestrator,
            data_versioning,
            deployment,
            file_versioning,
            instance_template,
            kube_deployment_captain,
            logging_client,
            model_management,
            project,
            feature_store,
            user_application_instance,
            alerts_registry,
            integration_management,
            system_secret,
            model_version_manager,
            jfrog_gateway,
        ]
    )

    return container
