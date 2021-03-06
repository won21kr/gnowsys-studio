
# Copyright (c) 2011,  2012 Free Software Foundation

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.

#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.


# Copyright (c) 2011,  2012 Free Software Foundation

#     This program is free software: you can redistribute it and/or modify
#     it under the terms of the GNU Affero General Public License as
#     published by the Free Software Foundation, either version 3 of the
#     License, or (at your option) any later version.

#     This program is distributed in the hope that it will be useful,
#     but WITHOUT ANY WARRANTY; without even the implied warranty of
#     MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#     GNU Affero General Public License for more details.

#     You should have received a copy of the GNU Affero General Public License
#     along with this program.  If not, see <http://www.gnu.org/licenses/>.


# This project incorporates work covered by the following copyright and permission notice:  

#    Copyright (c) 2009, Julien Fache
#    All rights reserved.

#    Redistribution and use in source and binary forms, with or without
#    modification, are permitted provided that the following conditions
#    are met:

#    * Redistributions of source code must retain the above copyright
#      notice, this list of conditions and the following disclaimer.
#    * Redistributions in binary form must reproduce the above copyright
#      notice, this list of conditions and the following disclaimer in
#      the documentation and/or other materials provided with the
#      distribution.
#    * Neither the name of the author nor the names of other
#      contributors may be used to endorse or promote products derived
#      from this software without specific prior written permission.

#    THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
#    "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
#    LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
#    FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
#    COPYRIGHT OWNER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
#    INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
#    (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
#    SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
#    HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT,
#    STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE)
#    ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED
#    OF THE POSSIBILITY OF SUCH DAMAGE.
"""Mollom spam checker backend for Gstudio"""
from django.conf import settings
from django.utils.encoding import smart_str
from django.core.exceptions import ImproperlyConfigured

try:
    from pymollom import MollomAPI
    from pymollom import MollomFault
except ImportError:
    raise ImproperlyConfigured('pymollom module is not available')

if not getattr(settings, 'MOLLOM_PUBLIC_KEY', ''):
    raise ImproperlyConfigured('You have to set a MOLLOM_PUBLIC_KEY setting')

if not getattr(settings, 'MOLLOM_PRIVATE_KEY', ''):
    raise ImproperlyConfigured('You have to set a MOLLOM_PRIVATE_KEY setting')

MOLLOM_PUBLIC_KEY = settings.MOLLOM_PUBLIC_KEY
MOLLOM_PRIVATE_KEY = settings.MOLLOM_PRIVATE_KEY


def backend(comment, content_object, request):
    """Mollom spam checker backend for Gstudio"""
    mollom_api = MollomAPI(
        publicKey=MOLLOM_PUBLIC_KEY,
        privateKey=MOLLOM_PRIVATE_KEY)
    if not mollom_api.verifyKey():
        raise MollomFault('Your MOLLOM credentials are invalid.')

    mollom_data = {'authorIP': request.META.get('REMOTE_ADDR', ''),
                   'authorName': smart_str(comment.userinfo.get('name', '')),
                   'authorMail': smart_str(comment.userinfo.get('email', '')),
                   'authorURL': smart_str(comment.userinfo.get('url', ''))}

    cc = mollom_api.checkContent(
        postTitle=smart_str(content_object.title),
        postBody=smart_str(comment.comment), **mollom_data)
    # cc['spam']: 1 for ham, 2 for spam, 3 for unsure;
    # http://mollom.com/blog/spam-vs-ham
    if cc['spam'] == 2:
        return True
    return False
