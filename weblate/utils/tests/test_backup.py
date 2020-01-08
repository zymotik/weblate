# -*- coding: utf-8 -*-
#
# Copyright © 2012 - 2020 Michal Čihař <michal@cihar.com>
#
# This file is part of Weblate <https://weblate.org/>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import json
from unittest import skipIf

import six
from django.conf import settings
from django.test import SimpleTestCase

from weblate.memory.tasks import memory_backup
from weblate.utils.backup import backup, get_paper_key, initialize, prune
from weblate.utils.data import data_dir
from weblate.utils.tasks import settings_backup
from weblate.utils.unittest import tempdir_setting


class BackupTest(SimpleTestCase):
    @tempdir_setting("DATA_DIR")
    @skipIf(six.PY2, 'override_settings seems to be broken on Python 2')
    def test_settings_backup(self):
        settings_backup()
        filename = data_dir("backups", "settings.py")
        with open(filename) as handle:
            self.assertIn(settings.DATA_DIR, handle.read())

    @tempdir_setting("DATA_DIR")
    def test_memory_backup(self):
        memory_backup()
        filename = data_dir("backups", "memory.json")
        with open(filename) as handle:
            data = json.load(handle)
        self.assertEqual(data, [])

    @tempdir_setting("DATA_DIR")
    @tempdir_setting("BACKUP_DIR")
    @skipIf(six.PY2, 'borgbackup does not support Python 2')
    def test_backup(self):
        initialize(settings.BACKUP_DIR, "key")
        output = get_paper_key(settings.BACKUP_DIR)
        self.assertIn("BORG PAPER KEY", output)
        output = backup(settings.BACKUP_DIR, "key")
        self.assertIn("Creating archive", output)
        output = prune(settings.BACKUP_DIR, "key")
        self.assertIn("Keeping archive", output)
