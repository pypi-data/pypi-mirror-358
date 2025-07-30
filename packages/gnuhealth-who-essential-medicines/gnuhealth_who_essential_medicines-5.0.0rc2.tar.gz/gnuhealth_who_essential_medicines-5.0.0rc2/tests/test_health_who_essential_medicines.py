# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later

import unittest
import trytond.tests.test_tryton
from trytond.tests.test_tryton import ModuleTestCase


class HealthWHOEssentialMedicinesTestCase(ModuleTestCase):
    '''
    Test Health WHO Essential Medicines module.
    '''
    module = 'health_who_essential_medicines'


del ModuleTestCase


def suite():
    suite = trytond.tests.test_tryton.suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
        HealthWHOEssentialMedicinesTestCase))
    return suite
