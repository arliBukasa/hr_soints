# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrSoints(models.Model):
    """Prise en charge médicale"""
    _name="hr.soints"
    _description="Prise en charge médicale"

    name=fields.Char("Code de prise en charge")
    categorie_beneficiaire=fields.Selection(string="Type de Bénéficiare", selection=[("agent","Agent"),("dependant","Dépendant")],default="agent")
    employe_id=fields.Many2one("hr.employee", string="Employé")
    familly_id=fields.Many2one("hr.employee.family",string="Bénéficiare")
    action_ids=fields.Many2one(comodel_name="hr.acte",inverse_name="soints_id",string="Actions prises")
    date_soints=fields.Date("Date de la prise en charge")
    etat=fields.Selection(string="Etat de la prise en charge",selection=[("draft","Brouillon"),("validate","Validé"),("done","Fait")],default="draft")
    age = fields.Integer(string="Age")

class ActeMedical(models.Model):
    _name = "hr.acte"
    _description = "Acte medical"

    name=fields.Char(string="Acte Medical")
    categorie=fields.Selection(string="Categorie d'acte", selection=[("examen","Examen"),("consultation","Consultaion"),("intervention","Intevention Chirurgicale")])
    montant=fields.Float(string="Montant")
    soints_id=fields.Many2one("hr.soints", string="Soints")


class HrEmployeeFamilyInfo(models.Model):
    _inherit = 'hr.employee.family'

    employee_id = fields.Many2one(invisible=0)
    employee_name = fields.Char(string="Employé(e)",related='employee_id.display_name', depends=['employee_id'], store=True)



class hr_soints_Hospital(models.Model):
    _name = 'hr.soints.hospital'
    _description = 'Hospital'

    name = fields.Char(string='Nom')
    


