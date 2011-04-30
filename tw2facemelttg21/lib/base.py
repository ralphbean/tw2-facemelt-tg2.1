# -*- coding: utf-8 -*-

"""The base Controller API."""

from tg import TGController, tmpl_context
from tg.render import render
from tg import request
from pylons.i18n import _, ungettext, N_
import tw2facemelttg21.model as model

from tw2.jqplugins.ui import set_ui_theme_name

__all__ = ['BaseController']


class BaseController(TGController):
    """
    Base class for the controllers in the application.

    Your web application should have one of these. The root of
    your application is used to compute URLs used by your app.

    """

    def __call__(self, environ, start_response):
        """Invoke the Controller"""
        # TGController.__call__ dispatches to the Controller method
        # the request is routed to. This routing information is
        # available in environ['pylons.routes_dict']

        set_ui_theme_name('hot-sneaks')

        entry = model.ServerHit(
            remote_addr=environ['REMOTE_ADDR'],
            path_info=environ['PATH_INFO'],
            query_string=environ['QUERY_STRING'],
        )
        model.DBSession.add(entry)

        request.identity = request.environ.get('repoze.who.identity')
        tmpl_context.identity = request.identity
        return TGController.__call__(self, environ, start_response)
