# Migration compatibility only

The former `videos` application no longer has runtime models, views, admin,
templates or template tags. Its migration package and app label are retained
because `courses.0002_auto_20260414_0232` reads historical `videos.Course` rows.

`0025_retire_legacy_models` runs only after course redirects have been saved and
deletes Course, ProgrammTask, InputOutputData and their many-to-many tables.
This keeps both upgrades of existing databases and clean installations valid.

Do not remove this migration package or its entry in INSTALLED_APPS until the
cross-app migration history has been deliberately squashed in a later release.
No `videos` model is registered with Django after the final migration state.

Back up the database before deployment: reversing DeleteModel recreates empty
tables and cannot restore the archived rows. Legacy practice tasks are retired,
not migrated into course blocks. Missing/ambiguous lesson matches redirect to
the associated course, or to the course catalogue when no course is known.
