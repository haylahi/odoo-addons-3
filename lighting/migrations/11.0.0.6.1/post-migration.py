# Copyright NuoBiT Solutions, S.L. (<https://www.nuobit.com>)
# Eric Antones <eantones@nuobit.com>
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl)

from openupgradelib import openupgrade

@openupgrade.migrate(use_env=True)
def migrate(env, version):
    if not version:
        return

    # remove equipment brand field from product type
    openupgrade.drop_columns(
        env.cr,
        [('lighting_product', 'auxiliary_equipment_brand_id'),
        ]
    )
