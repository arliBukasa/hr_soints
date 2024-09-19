# -*- coding: utf-8 -*-
import logging
import qrcode
from io import BytesIO
import base64  # Add this line

from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError

_logger = logging.getLogger(__name__)


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    #carte_sante=fields.Binary(string="Carte de santé",depends="company_id",related="company_id.carteDesign")
    qr_code = fields.Char(string='Code QR')
    qr_image = fields.Binary(string='QR Image')

    @api.multi 
    def generate_qrcode(self):
        for item in self:

            url = str(item.numero_matricule)
            qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=2,
            )
            qr.add_data(url)
            qr.make(fit=True)
            img = qr.make_image(back_color="#015e4e")
            temp = BytesIO()
            img.save(temp, format="PNG")
            self.write({'qr_image':base64.b64encode(temp.getvalue()),
                        'qr_code':str(item.numero_matricule)})
    
    @api.model
    def create(self, values):
        result = super().create(values)
        result.generate_qrcode()
        return result
