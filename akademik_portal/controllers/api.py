# -*- coding: utf-8 -*-
from odoo import http  # type: ignore
from odoo.http import request  # type: ignore


class AkademikApiController(http.Controller):
    """JSON API endpoints for all OWL interactive components in the student portal."""

    def _get_student_partner(self):
        return request.env.user.partner_id

    # ─── Profil ───────────────────────────────────────────────────────────────

    @http.route('/api/akademik/profil', auth='user', type='json')
    def api_profil(self, **kwargs):
        p = self._get_student_partner()
        latest_krs = request.env['akademik.krs'].search([
            ('student_id', '=', p.id)], order='id desc', limit=1)
        tesis = request.env['akademik.tesis'].search([
            ('student_id', '=', p.id)], limit=1)

        krs_data = {}
        if latest_krs:
            krs_data = {
                'id': latest_krs.id,
                'academic_year': latest_krs.academic_year_id.academic_year or '—',
                'semester': latest_krs.semester,
                'line_count': len(latest_krs.line_ids),
                'total_sks': sum(latest_krs.line_ids.mapped('credits')),
            }

        tesis_data = {}
        if tesis:
            tesis_data = {
                'id': tesis.id,
                'title': tesis.title,
                'stage': tesis.stage,
                'progress': tesis.progress or 0,
                'supervisor': tesis.supervisor_id.name if tesis.supervisor_id else '—',
            }

        return {
            'name': p.name,
            'nim': p.nim or '—',
            'study_program': p.study_program_id.study_program_name or '—',
            'entry_year': p.entry_year_id.academic_year if p.entry_year_id else '—',
            'email': p.email or '—',
            'phone': p.phone or '—',
            'status': p.status or 'draft',
            'achievement_level': int(p.achievement_level or 0),
            'supervisor': p.supervisor_id.name if p.supervisor_id else '—',
            'research_topic': p.research_topic or '—',
            'tags': [{'name': t.name} for t in p.student_tags],
            'avatar_url': f'/web/image/res.partner/{p.id}/image_128',
            'latest_krs': krs_data,
            'tesis': tesis_data,
        }

    # ─── KRS ──────────────────────────────────────────────────────────────────

    @http.route('/api/akademik/krs', auth='user', type='json')
    def api_krs(self, year_filter=None, **kwargs):
        p = self._get_student_partner()
        domain = [('student_id', '=', p.id)]
        if year_filter:
            domain.append(('academic_year_id.academic_year', 'ilike', year_filter))

        krs_list = request.env['akademik.krs'].search(domain, order='id desc')
        return [{
            'id': krs.id,
            'academic_year': krs.academic_year_id.academic_year or '—',
            'semester': krs.semester,
            'line_count': len(krs.line_ids),
            'total_sks': sum(krs.line_ids.mapped('credits')),
        } for krs in krs_list]

    @http.route('/api/akademik/krs_detail', auth='user', type='json')
    def api_krs_detail(self, krs_id, **kwargs):
        p = self._get_student_partner()
        krs = request.env['akademik.krs'].browse(int(krs_id))
        if not krs.exists() or krs.student_id.id != p.id:
            return {'error': 'Not found'}

        lines = []
        for i, line in enumerate(krs.line_ids):
            lines.append({
                'index': i + 1,
                'subject': line.subject_id.name if line.subject_id else '—',
                'schedule': line.jadwal_id.name if line.jadwal_id else '',
                'credits': line.credits,
                'is_thesis': line.is_thesis,
                'score_harian': round(line.score_harian, 1),
                'score_uts': round(line.score_uts, 1),
                'score_uas': round(line.score_uas, 1),
                'score': round(line.score, 1),
                'grade': line.grade or '—',
            })
        return {
            'id': krs.id,
            'academic_year': krs.academic_year_id.academic_year or '—',
            'semester': krs.semester,
            'total_sks': sum(krs.line_ids.mapped('credits')),
            'lines': lines,
        }

    # ─── Jadwal ───────────────────────────────────────────────────────────────

    @http.route('/api/akademik/jadwal', auth='user', type='json')
    def api_jadwal(self, day=None, **kwargs):
        p = self._get_student_partner()
        domain = [('study_program_id', '=', p.study_program_id.id)]
        if day:
            domain.append(('day', '=', day))

        jadwal_list = request.env['akademik.jadwal'].search(
            domain, order='day, start_time')
        return [{
            'id': j.id,
            'name': j.name,
            'subject': j.subject_id.name if j.subject_id else '—',
            'day': j.day,
            'start_time': j.start_time,
            'end_time': j.end_time,
            'room': j.ruangan_id.name if j.ruangan_id else '—',
            'lecturer': j.dosen_id.name if j.dosen_id else 'TBA',
            'enrolled': j.enrolled_count,
            'remaining': j.remaining_quota,
        } for j in jadwal_list]

    # ─── Tesis ────────────────────────────────────────────────────────────────

    @http.route('/api/akademik/tesis', auth='user', type='json')
    def api_tesis(self, **kwargs):
        p = self._get_student_partner()
        tesis = request.env['akademik.tesis'].search([
            ('student_id', '=', p.id)], limit=1)
        dosen_list = request.env['hr.employee'].search([
            ('is_dosen', '=', True),
            ('study_program_id', '=', p.study_program_id.id),
        ])

        return {
            'tesis': {
                'id': tesis.id,
                'title': tesis.title,
                'stage': tesis.stage,
                'progress': tesis.progress or 0,
                'supervisor': tesis.supervisor_id.name if tesis.supervisor_id else '—',
            } if tesis else None,
            'dosen_list': [{'id': d.id, 'name': d.name} for d in dosen_list],
        }
