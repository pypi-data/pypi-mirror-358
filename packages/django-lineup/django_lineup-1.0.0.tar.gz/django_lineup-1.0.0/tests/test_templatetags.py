#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
test_django-lineup
------------

Tests for `django-lineup` templatetags module.
"""

import json
from django.test import TestCase, RequestFactory
from lineup.templatetags.lineup_tags import get_all_user_permissions_id_list, set_active_voice
from django.contrib.auth.models import User, Group, Permission, AnonymousUser
from django.template import Context, Template

from lineup.models import MenuItem
from lineup import exceptions
from lineup.templatetags.lineup_tags import lineup_menu, lineup_breadcrumbs


class LineupTagsTest(TestCase):
    """
    The create_tree function is tested indirectly
    with all the test_lineup_menu_tag_* tests.
    The final output depends on the generated tree!
    """
    def setUp(self):
        self.factory = RequestFactory()
        self.superuser = User.objects.create(
            username='admin',
            password='Passw0rd!uau',
            email='admin@gmail.com',
            is_superuser=True,
        )
        self.user = User.objects.create(
            username='abidibo',
            password='Passw0rd!uau',
            email='abidibo@gmail.com',
        )

        # for p in Permission.objects.all():
        #     print(p.id, p.codename)
        self.permissions = Permission.objects.filter(codename__in=['add_permission', 'change_group', 'view_permission', 'view_session'])
        self.user.user_permissions.add(self.permissions[0])
        self.user.user_permissions.add(self.permissions[2])

        group = Group.objects.create(name='dev')
        group.permissions.add(self.permissions[1])
        group.permissions.add(self.permissions[3])

        self.user.groups.add(group)

        self.wrong_perm_user = User.objects.create(
            username='wrong',
            password='Passw0rd!uau',
            email='wrong@gmail.com',
        )
        self.wrong_perm_user.user_permissions.add(self.permissions[2])

        self.menu = {
            'label': 'Root',
            'slug': 'main-menu',
            'order': 0,
            'children': [
                {
                    'label': 'Tools',
                    'slug': 'tools',
                    'order': 0,
                    'children': [
                        {
                            'label': 'DNS Tools',
                            'slug': 'dns-tools',
                            'order': 0,
                            'login_required': True,
                            'children': [
                                {
                                    'label': 'DMARC DNS Tools',
                                    'slug': 'dmarc-dns-tools',
                                    'link': '/dmarc-tools/',
                                    'title': 'DMARC Rulez',
                                    'order': 0,
                                }
                            ]
                        },
                        {
                            'label': 'Password Generator',
                            'slug': 'password-generator',
                            'order': 1,
                        }
                    ]
                },
                {
                    'label': 'Disabled Item',
                    'slug': 'disabled-item',
                    'order': 1,
                    'enabled': False,
                    'children': [
                        {
                            'label': 'Disabled child',
                            'slug': 'disabled-child',
                            'order': 0,
                        }
                    ]
                },
                {
                    'label': 'Perm Item',
                    'slug': 'perm-item',
                    'order': 2,
                    'permissions': ['add_permission', 'view_session']
                }
            ]
        }

        self.tree = MenuItem.from_json(json.dumps(self.menu))

    def test_get_all_user_permissions_id_list(self):

        res_ids = sorted(get_all_user_permissions_id_list(self.user))
        expected_ids = sorted([p.id for p in self.permissions])

        self.assertEqual(res_ids, expected_ids)

    def test_from_json_invalid_json(self):
        try:
            invalid_json = "{\"key\" = \"prop\"}"
            MenuItem.from_json(invalid_json)
            self.fail()
        except exceptions.InvalidJson:
            pass

    def test_from_json_unsupported_json_data(self):
        try:
            invalid_json = self.menu.copy()
            MenuItem.from_json(json.dumps([invalid_json, invalid_json]))
            self.fail()
        except exceptions.UnsupportedJsonData:
            pass

    def test_from_json_missing_json_prop(self):
        try:
            invalid_json = self.menu.copy()
            invalid_json.pop('children')
            invalid_json.pop('slug')
            MenuItem.from_json(json.dumps(invalid_json))
            self.fail()
        except exceptions.MissingJsonRequiredProp:
            pass

    def test_from_json(self):
        self.assertEqual(self.tree.children.count(), 3)
        children = self.tree.children.all()
        self.assertEqual(children[0].slug, 'tools')
        self.assertEqual(children[0].children.all()[0].login_required, True)
        self.assertEqual(children[1].enabled, False)
        self.assertEqual(children[2].permissions.all()[0].codename, 'add_permission')
        self.assertEqual(children[2].permissions.all()[1].codename, 'view_session')

    def test_linup_menu_wrong_item_type(self):
        context = {}
        res = lineup_menu(context, [])
        self.assertEqual(res['items'], [])
        self.assertEqual(res['slug'], None)
        self.assertEqual(res['level'], None)

    def test_lineup_menu_tag_unexisting_menu(self):
        out = Template(
            "{% load lineup_tags %}"
            "{% lineup_menu 'main-menu_' %}"
        ).render(Context({
            'user': self.user
        }))
        self.assertEqual(out, '\n\n')

    def test_lineup_disabled_menu(self):
        menu = {
            'label': 'Menu',
            'slug': 'menu',
            'order': 0,
            'enabled': False,
            'children': [
                {
                    'label': 'A',
                    'slug': 'a',
                    'order': 0,
                },
            ]
        }

        MenuItem.from_json(json.dumps(menu))

        out = Template(
            "{% load lineup_tags %}"
            "{% lineup_menu 'menu' %}"
        ).render(Context({
            'user': self.user
        }))
        self.assertEqual(out, '\n\n')

    def test_lineup_menu_login_required(self):
        menu = {
            'label': 'Menu',
            'slug': 'menu',
            'order': 0,
            'login_required': True,
            'children': [
                {
                    'label': 'A',
                    'slug': 'a',
                    'order': 0,
                },
            ]
        }

        MenuItem.from_json(json.dumps(menu))

        out = Template(
            "{% load lineup_tags %}"
            "{% lineup_menu 'menu' %}"
        ).render(Context({
            'user': AnonymousUser()
        }))
        self.assertEqual(out, '\n\n')

    def test_lineup_menu_tag_not_logged_user(self):
        ''' sees just public items '''
        out = Template(
            "{% load lineup_tags %}"
            "{% lineup_menu 'main-menu' %}"
        ).render(Context({
            'user': AnonymousUser()
        }))
        expected = '\n<ul id="lineup-main-menu" class="level-0"><li class="has-children "><a>Tools</a><ul id="lineup-tools" class="level-1"><li class=""><a>Password Generator</a></li></ul></li></ul>\n'
        self.assertEqual(out, expected)

    def test_lineup_menu_tag_superuser_with_active(self):
        ''' sees all but disabled items '''
        request = self.factory.get('/dmarc-tools/')
        request.user = self.superuser

        out = Template(
            "{% load lineup_tags %}"
            "{% lineup_menu 'main-menu' %}"
        ).render(Context({
            'user': self.superuser,
            'request': request,
        }))
        expected = '\n<ul id="lineup-main-menu" class="level-0"><li class="has-active has-children "><a>Tools</a><ul id="lineup-tools" class="level-1"><li class="has-active has-children "><a>DNS Tools</a><ul id="lineup-dns-tools" class="level-2"><li class="active "><a href="/dmarc-tools/" title="DMARC Rulez">DMARC DNS Tools</a></li></ul></li><li class=""><a>Password Generator</a></li></ul></li><li class=""><a>Perm Item</a></li></ul>\n'
        self.assertEqual(out, expected)

    def test_lineup_menu_tag_logged_in_wrong_perms_user(self):
        out = Template(
            "{% load lineup_tags %}"
            "{% lineup_menu 'main-menu' %}"
        ).render(Context({
            'user': self.wrong_perm_user
        }))

        expected = '\n<ul id="lineup-main-menu" class="level-0"><li class="has-children "><a>Tools</a><ul id="lineup-tools" class="level-1"><li class="has-children "><a>DNS Tools</a><ul id="lineup-dns-tools" class="level-2"><li class=""><a href="/dmarc-tools/" title="DMARC Rulez">DMARC DNS Tools</a></li></ul></li><li class=""><a>Password Generator</a></li></ul></li></ul>\n'
        self.assertEqual(out, expected)

    def test_lineup_menu_tag_logged_in_user(self):
        out = Template(
            "{% load lineup_tags %}"
            "{% lineup_menu 'main-menu' %}"
        ).render(Context({
            'user': self.user
        }))

        expected = '\n<ul id="lineup-main-menu" class="level-0"><li class="has-children "><a>Tools</a><ul id="lineup-tools" class="level-1"><li class="has-children "><a>DNS Tools</a><ul id="lineup-dns-tools" class="level-2"><li class=""><a href="/dmarc-tools/" title="DMARC Rulez">DMARC DNS Tools</a></li></ul></li><li class=""><a>Password Generator</a></li></ul></li><li class=""><a>Perm Item</a></li></ul>\n'
        self.assertEqual(out, expected)

    def test_breadcrumbs(self):
        request = self.factory.get('/dmarc-tools/')
        out = Template(
            "{% load lineup_tags %}"
            "{% lineup_breadcrumbs 'main-menu' %}"
        ).render(Context({
            'user': self.wrong_perm_user,
            'request': request,
        }))

        expected = '<div class="lineup-breadcrumbs"><a>Tools</a> › <a>DNS Tools</a> › <a href="/dmarc-tools/" title="DMARC Rulez">DMARC DNS Tools</a></div>\n'
        self.assertEqual(out, expected)

    def test_breadcrumbs_no_active(self):
        request = self.factory.get('/wrong-dmarc-tools/')
        out = Template(
            "{% load lineup_tags %}"
            "{% lineup_breadcrumbs 'main-menu' %}"
        ).render(Context({
            'user': self.wrong_perm_user,
            'request': request,
        }))

        expected = '\n'
        self.assertEqual(out, expected)

    def test_breadcrumbs_active_in_other_menu(self):
        request = self.factory.get('/a/')
        menu = {
            'label': 'Menu',
            'slug': 'menu',
            'order': 0,
            'login_required': True,
            'children': [
                {
                    'label': 'A',
                    'slug': 'a',
                    'link': '/a/',
                    'order': 0,
                },
            ]
        }

        MenuItem.from_json(json.dumps(menu))

        context = {
            'user': self.superuser,
            'request': request,
        }

        res = lineup_breadcrumbs(context, 'main-menu')

        self.assertEqual(res['items'], [])

    def test_breadcrumbs_no_request(self):
        context = {'key': 'abcd'}
        res = lineup_breadcrumbs(context, 'main-menu')

        self.assertEqual(res, context)
