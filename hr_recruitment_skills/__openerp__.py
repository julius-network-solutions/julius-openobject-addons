# -*- coding: utf-8 -*-
#################################################################################
#
#    OpenERP, Open Source Management Solution
#    Copyright (C) 2013 Julius Network Solutions SARL <contact@julius.fr>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#################################################################################

{
    "name" : "HR recruitment skills",
    "version" : "0.1",
    "author" : "Julius Network Solutions",
    "website" : "http://julius.fr",
    "category" : "Human Resources",
    "depends" : [
        "web_filter_and_condition",
        "hr_recruitment",
    ],
    "description": """
Skills in recruitment
=====================

This module adds skills to the employees, applicants

This also add buttons to filter the applicants and jobs by their skills.
You can check/uncheck the skills in the search view.

E.g.:
-----

    * You need to recruit one person for one job which needs to have skills in PHP, Java and Python.
    * You've got 4 applicants for this job :
        * 1st got PHP, XML, HTML, CSS
        * 2nd got PHP, Java and C++
        * 3rd got Java, Python, CSS, HTML
        * 4th got Python and PHP

By default you will not found any of them when clicking on the button.
----------------------------------------------------------------------

    * If you uncheck Python for instance, you will find the 2nd one.
    * If you uncheck PHP for instance, you will find the 3rd one.
    * If you uncheck Java for instance, you will find the 4th one.
    """,
    "demo" : [],
    "data" : [
        "hr_view.xml",
    ],
    'installable' : True,
    'active' : False,
}

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: