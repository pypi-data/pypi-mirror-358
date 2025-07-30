# SPDX-FileCopyrightText: 2008-2025 Luis Falcón <falcon@gnuhealth.org>
# SPDX-FileCopyrightText: 2011-2025 GNU Solidario <health@gnusolidario.org>
#
# SPDX-License-Identifier: GPL-3.0-or-later
#########################################################################
#   Hospital Management Information System (HMIS) component of the      #
#                       GNU Health project                              #
#                   https://www.gnuhealth.org                           #
#########################################################################
#                      HEALTH INSURANCE package                         #
#              __init__.py: Package declaration file                    #
#########################################################################

from trytond.pool import Pool
from . import health_insurance
from . import wizard


def register():
    Pool.register(
        health_insurance.InsurancePlanProductPolicy,
        health_insurance.InsurancePlan,
        health_insurance.HealthService,
        health_insurance.PatientProcedure,
        module='health_insurance', type_='model')
    Pool.register(
        wizard.wizard_health_insurance.CreateServiceInvoice,
        module='health_services', type_='wizard')
