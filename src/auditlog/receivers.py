from __future__ import unicode_literals

import json

from auditlog.diff import model_instance_diff
from auditlog.models import LogEntry
from auditlog.signals import pre_log, post_log


def log_create(sender, instance, created, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is first saved to the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """
    if created:
        changes = model_instance_diff(None, instance)

        _create_log_entry(
            action=LogEntry.Action.CREATE, 
            instance=instance, 
            sender=sender, 
            changes=changes
        )


def log_update(sender, instance, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is changed and saved to the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """
    if instance.pk is not None:
        try:
            old = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            pass
        else:
            new = instance

            changes = model_instance_diff(old, new)

            # Log an entry only if there are changes
            if changes:
                _create_log_entry(
                    action=LogEntry.Action.UPDATE, 
                    instance=instance, 
                    sender=sender, 
                    changes=changes
                )


def log_delete(sender, instance, **kwargs):
    """
    Signal receiver that creates a log entry when a model instance is deleted from the database.

    Direct use is discouraged, connect your model through :py:func:`auditlog.registry.register` instead.
    """
    if instance.pk is not None:
        changes = model_instance_diff(instance, None)

        _create_log_entry(
            action=LogEntry.Action.DELETE, 
            instance=instance, 
            sender=sender, 
            changes=changes
        )

    
def _create_log_entry(action, instance, sender, changes):
    pre_log_results = pre_log.send(
        sender,
        instance=instance,
        action=action,
    )

    if any(item[1] is False for item in pre_log_results):
        return

    json_changes = json.dumps(changes)
    log_entry = None
    error = None

    try:
        log_entry = LogEntry.objects.log_create(
            instance,
            action=action,
            changes=json_changes,
        )
    except BaseException as e:
        error = e
    finally:
        if log_entry or error:
            post_log.send(
                sender,
                instance=instance,
                action=action,
                changes=json_changes,
                log_entry=log_entry,
                log_created=log_entry is not None,
                error=error,
                pre_log_results=pre_log_results,
            )

        if error:
            raise error
