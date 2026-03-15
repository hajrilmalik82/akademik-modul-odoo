# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal


class AkademikPortalController(CustomerPortal):
    """Student portal controller.
    Uses sudo() for all model reads — security enforced via domain filters.
    This is the standard Odoo portal pattern."""

    @http.route(['/my', '/my/home'], type='http', auth='user', website=True)
    def home(self, **kwargs):
        """Redirect students to /my/akademik/ on login."""
        partner = request.env.user.partner_id
        if partner.is_student:
            return request.redirect('/my/akademik/')
        return super().home(**kwargs)

    # ─── Portal Pages ─────────────────────────────────────────────────────────

    @http.route('/my/akademik/', auth='user', website=True)
    def profil(self, **kwargs):
        partner = request.env.user.partner_id
        # Safe portal pattern via ORM rules
        latest_krs = request.env['akademik.krs'].search([
            ('student_id', '=', partner.id),
        ], order='id desc', limit=1)
        tesis = request.env['akademik.tesis'].search([
            ('student_id', '=', partner.id),
        ], limit=1)
        return request.render('akademik_portal.portal_profil', {
            'partner': partner,
            'latest_krs': latest_krs,
            'tesis': tesis,
            'active_menu': 'profil',
        })

    @http.route('/my/akademik/krs/', auth='user', website=True)
    def krs_list(self, **kwargs):
        partner = request.env.user.partner_id
        krs_list = request.env['akademik.krs'].search([
            ('student_id', '=', partner.id),
        ], order='id desc')
        return request.render('akademik_portal.portal_krs_list', {
            'partner': partner,
            'krs_list': krs_list,
            'active_menu': 'krs',
        })

    @http.route('/my/akademik/krs/<int:krs_id>/', auth='user', website=True)
    def krs_detail(self, krs_id, **kwargs):
        partner = request.env.user.partner_id
        krs = request.env['akademik.krs'].browse(krs_id)
        # Security: only own KRS
        if not krs.exists() or krs.student_id.id != partner.id:
            return request.not_found()
        total_sks = sum(krs.line_ids.mapped('credits'))
        return request.render('akademik_portal.portal_krs_detail', {
            'partner': partner,
            'krs': krs,
            'krs_id': krs_id,
            'total_sks': total_sks,
            'active_menu': 'krs',
        })

    @http.route('/my/akademik/jadwal/', auth='user', website=True)
    def jadwal(self, **kwargs):
        partner = request.env.user.partner_id
        jadwal_list = request.env['akademik.jadwal'].search([
            ('study_program_id', '=', partner.study_program_id.id),
        ], order='day, start_time')
        return request.render('akademik_portal.portal_jadwal', {
            'partner': partner,
            'jadwal_list': jadwal_list,
            'active_menu': 'jadwal',
        })

    @http.route('/my/akademik/tesis/', auth='user', website=True)
    def tesis(self, **kwargs):
        partner = request.env.user.partner_id
        tesis = request.env['akademik.tesis'].search([
            ('student_id', '=', partner.id),
        ], limit=1)
        dosen_list = request.env['hr.employee'].search([
            ('is_lecturer', '=', True),
            ('study_program_id', '=', partner.study_program_id.id),
        ])
        return request.render('akademik_portal.portal_tesis', {
            'partner': partner,
            'tesis': tesis,
            'dosen_list': dosen_list,
            'active_menu': 'tesis',
        })

    @http.route('/my/akademik/tesis/submit', auth='user',
                website=True, methods=['POST'], csrf=True)
    def tesis_submit(self, title='', supervisor_id=None, **kwargs):
        partner = request.env.user.partner_id
        if title:
            vals = {'title': title, 'student_id': partner.id}
            if supervisor_id:
                vals['supervisor_id'] = int(supervisor_id)
            request.env['akademik.tesis'].sudo().create(vals)
        return request.redirect('/my/akademik/tesis/')
