# -*- coding: utf-8 -*-
"""Main Controller"""

from tg import expose, flash, require, url, request, redirect
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates

from tw2facemelttg21.lib.base import BaseController
from tw2facemelttg21.model import DBSession, metadata
from tw2facemelttg21.model import ServerHit
from tw2facemelttg21 import model
from tw2facemelttg21.controllers.secure import SecureController

from tw2facemelttg21.controllers.error import ErrorController

from tw2facemelttg21.widgets import LogGrid
from tw2facemelttg21.widgets import LogPlot
import tw2.jqplugins.portlets as p

import sqlalchemy
import datetime
import time

__all__ = ['RootController']

def recursive_update(d1, d2):
    """ Little helper function that does what d1.update(d2) does,
    but works nice and recursively with dicts of dicts of dicts.

    It's not necessarily very efficient.  Should be rewritten.
    """

    for k in d1.keys():
        if k not in d2:
            continue

        if isinstance(d1[k], dict) and isinstance(d2[k], dict):
            d1[k] = recursive_update(d1[k], d2[k])
        else:
            d1[k] = d2[k]

    for k in d2.keys():
        if k not in d1:
            d1[k] = d2[k]

    return d1


class RootController(BaseController):
    """
    The root controller for the tw2-facemelt-tg2.1 application.

    All the other controllers and WSGI applications should be mounted on this
    controller. For example::

        panel = ControlPanelController()
        another_app = AnotherWSGIApplication()

    Keep in mind that WSGI applications shouldn't be mounted directly: They
    must be wrapped around with :class:`tg.controllers.WSGIAppController`.

    """
    secc = SecureController()

    error = ErrorController()

    @expose('tw2facemelttg21.templates.index')
    def index(self):
        """Handle the front-page."""
        jqplot_params = self.jqplot()
        plotwidget = LogPlot(data=jqplot_params['data'])
        plotwidget.options = recursive_update(
            plotwidget.options, jqplot_params['options'])

        colwidth = '50%'
        class LayoutWidget(p.ColumnLayout):
            id = 'awesome-layout'
            class col1(p.Column):
                width = colwidth
                class por1(p.Portlet):
                    title = 'DB Entries of Server Hits'
                    widget = LogGrid

            class col2(p.Column):
                width = colwidth
                class por2(p.Portlet):
                    title = 'Hits over the last hour'
                    widget = plotwidget

        return dict(page='index', layoutwidget=LayoutWidget)

    @expose('json')
    def jqgrid(self, *args, **kw):
        return LogGrid.request(request).body

    def jqplot(self, days=1/(24.0)):
        n_buckets = 15
        now = datetime.datetime.now()
        then = now - datetime.timedelta(days)
        delta = datetime.timedelta(days) / n_buckets

        entries = ServerHit.query.filter(ServerHit.timestamp>then).all()

        t_bounds = [(then+delta*i, then+delta*(i+1)) for i in range(n_buckets)]

        # Accumulate into buckets!  This is how I like to do it.
        buckets = dict([(lower, 0) for lower, upper in t_bounds])
        for entry in entries:
            for lower, upper in t_bounds:
                if entry.timestamp >= lower and entry.timestamp < upper:
                    buckets[lower] += 1

        # Only one series for now.. but you could do other stuff!
        series = [buckets[lower] for lower, upper in t_bounds]
        data = [
            series,
            # You could add another series here...
        ]

        options = { 'axes' : { 'xaxis': {
            'ticks': [u.strftime("%I:%M:%S") for l, u in t_bounds],
        }}}

        return dict(data=data, options=options)

    @expose('tw2facemelttg21.templates.about')
    def about(self):
        """Handle the 'about' page."""
        return dict(page='about')

    @expose('tw2facemelttg21.templates.environ')
    def environ(self):
        """This method showcases TG's access to the wsgi environment."""
        return dict(environment=request.environ)

    @expose('tw2facemelttg21.templates.data')
    @expose('json')
    def data(self, **kw):
        """This method showcases how you can use the same controller for a data page and a display page"""
        return dict(params=kw)

    @expose('tw2facemelttg21.templates.authentication')
    def auth(self):
        """Display some information about auth* on this application."""
        return dict(page='auth')
    @expose('tw2facemelttg21.templates.index')
    @require(predicates.has_permission('manage', msg=l_('Only for managers')))
    def manage_permission_only(self, **kw):
        """Illustrate how a page for managers only works."""
        return dict(page='managers stuff')

    @expose('tw2facemelttg21.templates.index')
    @require(predicates.is_user('editor', msg=l_('Only for the editor')))
    def editor_user_only(self, **kw):
        """Illustrate how a page exclusive for the editor works."""
        return dict(page='editor stuff')

    @expose('tw2facemelttg21.templates.login')
    def login(self, came_from=url('/')):
        """Start the user login."""
        login_counter = request.environ['repoze.who.logins']
        if login_counter > 0:
            flash(_('Wrong credentials'), 'warning')

        return dict(page='login', login_counter=str(login_counter),
                    came_from=came_from)

    @expose()
    def post_login(self, came_from='/'):
        """
        Redirect the user to the initially requested page on successful
        authentication or redirect her back to the login page if login failed.

        """
        if not request.identity:
            login_counter = request.environ['repoze.who.logins'] + 1
            redirect('/login', came_from=came_from, __logins=login_counter)

        userid = request.identity['repoze.who.userid']
        flash(_('Welcome back, %s!') % userid)
        redirect(came_from)

    @expose()
    def post_logout(self, came_from=url('/')):
        """
        Redirect the user to the initially requested page on logout and say
        goodbye as well.

        """
        flash(_('We hope to see you soon!'))
        redirect(came_from)
