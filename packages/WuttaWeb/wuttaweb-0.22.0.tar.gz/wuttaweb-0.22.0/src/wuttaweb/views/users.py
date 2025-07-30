# -*- coding: utf-8; -*-
################################################################################
#
#  wuttaweb -- Web App for Wutta Framework
#  Copyright © 2024-2025 Lance Edgar
#
#  This file is part of Wutta Framework.
#
#  Wutta Framework is free software: you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the Free
#  Software Foundation, either version 3 of the License, or (at your option) any
#  later version.
#
#  Wutta Framework is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
#  FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for
#  more details.
#
#  You should have received a copy of the GNU General Public License along with
#  Wutta Framework.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Views for users
"""

import colander

from wuttjamaican.db.model import User
from wuttaweb.views import MasterView
from wuttaweb.forms import widgets
from wuttaweb.forms.schema import PersonRef, RoleRefs


class UserView(MasterView):
    """
    Master view for users.

    Default route prefix is ``users``.

    Notable URLs provided by this class:

    * ``/users/``
    * ``/users/new``
    * ``/users/XXX``
    * ``/users/XXX/edit``
    * ``/users/XXX/delete``
    """
    model_class = User

    grid_columns = [
        'username',
        'person',
        'active',
    ]

    filter_defaults = {
        'username': {'active': True},
        'active': {'active': True, 'verb': 'is_true'},
    }
    sort_defaults = 'username'

    form_fields = [
        'username',
        'person',
        'active',
        'prevent_edit',
        'roles',
    ]

    def get_query(self, session=None):
        """ """
        query = super().get_query(session=session)

        # nb. always join Person
        model = self.app.model
        query = query.outerjoin(model.Person)

        return query

    def configure_grid(self, g):
        """ """
        super().configure_grid(g)
        model = self.app.model

        # never show these
        g.remove('person_uuid',
                 'role_refs',
                 'password')

        # username
        g.set_link('username')

        # person
        g.set_link('person')
        g.set_sorter('person', model.Person.full_name)
        g.set_filter('person', model.Person.full_name,
                     label="Person Full Name")

    def grid_row_class(self, user, data, i):
        """ """
        if not user.active:
            return 'has-background-warning'

    def is_editable(self, user):
        """ """

        # only root can edit certain users
        if user.prevent_edit and not self.request.is_root:
            return False

        return True

    def configure_form(self, f):
        """ """
        super().configure_form(f)
        user = f.model_instance

        # username
        f.set_validator('username', self.unique_username)

        # person
        if self.creating or self.editing:
            f.fields.insert_after('person', 'first_name')
            f.set_required('first_name', False)
            f.fields.insert_after('first_name', 'last_name')
            f.set_required('last_name', False)
            f.remove('person')
            if self.editing:
                person = user.person
                if person:
                    f.set_default('first_name', person.first_name)
                    f.set_default('last_name', person.last_name)
        else:
            f.set_node('person', PersonRef(self.request))

        # password
        # nb. we must avoid 'password' as field name since
        # ColanderAlchemy wants to handle the raw/hashed value
        f.remove('password')
        # nb. no need for password field if readonly
        if self.creating or self.editing:
            # nb. use 'set_password' as field name
            f.append('set_password')
            f.set_required('set_password', False)
            f.set_widget('set_password', widgets.CheckedPasswordWidget())

        # roles
        f.append('roles')
        f.set_node('roles', RoleRefs(self.request))
        if not self.creating:
            f.set_default('roles', [role.uuid.hex for role in user.roles])

    def unique_username(self, node, value):
        """ """
        model = self.app.model
        session = self.Session()

        query = session.query(model.User)\
                       .filter(model.User.username == value)

        if self.editing:
            uuid = self.request.matchdict['uuid']
            query = query.filter(model.User.uuid != uuid)

        if query.count():
            node.raise_invalid("Username must be unique")

    def objectify(self, form):
        """ """
        model = self.app.model
        auth = self.app.get_auth_handler()
        data = form.validated

        # normal logic first
        user = super().objectify(form)

        # maybe update person name
        if 'first_name' in form or 'last_name' in form:
            first_name = data.get('first_name')
            last_name = data.get('last_name')
            if self.creating and (first_name or last_name):
                user.person = auth.make_person(first_name=first_name, last_name=last_name)
            elif self.editing:
                if first_name or last_name:
                    if user.person:
                        person = user.person
                        if 'first_name' in form:
                            person.first_name = first_name
                        if 'last_name' in form:
                            person.last_name = last_name
                        person.full_name = self.app.make_full_name(person.first_name,
                                                                   person.last_name)
                    else:
                        user.person = auth.make_person(first_name=first_name, last_name=last_name)
                elif user.person:
                    user.person = None

        # maybe set user password
        if 'set_password' in form and data.get('set_password'):
            auth.set_user_password(user, data['set_password'])

        # update roles for user
        # TODO
        # if self.has_perm('edit_roles'):
        self.update_roles(user, form)

        return user

    def update_roles(self, user, form):
        """ """
        # TODO
        # if not self.has_perm('edit_roles'):
        #     return
        data = form.validated
        if 'roles' not in data:
            return

        model = self.app.model
        session = self.Session()
        auth = self.app.get_auth_handler()

        old_roles = set([role.uuid for role in user.roles])
        new_roles = data['roles']

        admin = auth.get_role_administrator(session)
        ignored = {
            auth.get_role_authenticated(session).uuid,
            auth.get_role_anonymous(session).uuid,
        }

        # add any new roles for the user, taking care to avoid certain
        # unwanted operations for built-in roles
        for uuid in new_roles:
            if uuid in ignored:
                continue
            if uuid in old_roles:
                continue
            if uuid == admin.uuid and not self.request.is_root:
                continue
            role = session.get(model.Role, uuid)
            user.roles.append(role)

        # remove any roles which were *not* specified, taking care to
        # avoid certain unwanted operations for built-in roles
        for uuid in old_roles:
            if uuid in new_roles:
                continue
            if uuid == admin.uuid and not self.request.is_root:
                continue
            role = session.get(model.Role, uuid)
            user.roles.remove(role)

    @classmethod
    def defaults(cls, config):
        """ """

        # nb. User may come from custom model
        wutta_config = config.registry.settings['wutta_config']
        app = wutta_config.get_app()
        cls.model_class = app.model.User

        cls._defaults(config)


def defaults(config, **kwargs):
    base = globals()

    UserView = kwargs.get('UserView', base['UserView'])
    UserView.defaults(config)


def includeme(config):
    defaults(config)
