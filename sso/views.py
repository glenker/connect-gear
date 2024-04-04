from authlib.oauth2.rfc6749 import grants, AuthorizationCodeMixin, ClientMixin, TokenMixin
from authlib.integrations.django_oauth2 import AuthorizationServer
from authlib.oauth2.rfc7662 import IntrospectionEndpoint
from authlib.common.security import generate_token

from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_http_methods, require_POST
from django.db.models import ForeignKey, CASCADE, CharField, TextField, BooleanField, IntegerField, Model
from django.contrib.auth.models import User

import time
import asyncio

def now_timestamp():
    return int(time.time())

async def current_datetime(request):
    return HttpResponse(f'<html><body>current time is {now_timestamp()}.</body></html>')

@require_POST()
async def post_function(request):
    return HttpResponse(f'<html><body>post</body></html>')

class OAuth2Token(Model, TokenMixin):
    user = ForeignKey(User, on_delete=CASCADE)
    client_id = CharField(max_length=48, db_index=True)
    token_type = CharField(max_length=40)
    access_token = CharField(max_length=255, unique=True, null=False)
    refresh_token = CharField(max_length=255, db_index=True)
    scope = TextField(default='')
    revoked = BooleanField(default=False)
    issued_at = IntegerField(null=False, default=now_timestamp)
    expires_in = IntegerField(null=False, default=0)

    def get_client_id(self):
        return self.client_id

    def get_scope(self):
        return self.scope

    def get_expires_in(self):
        return self.expires_in

    def get_expires_at(self):
        return self.issued_at + self.expires_in

class OAuth2Client(Model, ClientMixin):
    user = ForeignKey(User, on_delete=CASCADE)
    client_id = CharField(max_length=48, unique=True, db_index=True)
    client_secret = CharField(max_length=48, blank=True)
    client_name = CharField(max_length=120)
    redirect_uris = TextField(default='')
    default_redirect_uri = TextField(blank=False, default='')
    scope = TextField(default='')
    response_type = TextField(default='')
    grant_type = TextField(default='')
    token_endpoint_auth_method = CharField(max_length=120, default='')

    # you can add more fields according to your own need
    # check https://tools.ietf.org/html/rfc7591#section-2

    def get_client_id(self):
        return self.client_id

    def get_default_redirect_uri(self):
        return self.default_redirect_uri

    def get_allowed_scope(self, scope):
        if not scope:
            return ''
        allowed = set(self.scope)
        scopes = set(scope.split())
        allowed = scopes.intersection(allowed)
        return allowed.pop() if len(allowed) > 0 else ''

    def check_redirect_uri(self, redirect_uri):
        if redirect_uri == self.default_redirect_uri:
            return True
        return redirect_uri in self.redirect_uris

    def check_client_secret(self, client_secret):
        return self.client_secret == client_secret

    def check_endpoint_auth_method(self, method, endpoint):
        if endpoint == 'token':
          return self.token_endpoint_auth_method == method
        # TODO: developers can update this check method
        return True

    def check_response_type(self, response_type):
        allowed = self.response_type.split()
        return response_type in allowed

    def check_grant_type(self, grant_type):
        allowed = self.grant_type.split()
        return grant_type in allowed

server = AuthorizationServer(OAuth2Client, OAuth2Token)

class PasswordGrant(grants.ResourceOwnerPasswordCredentialsGrant):
    def authenticate_user(self, username, password):
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                return user
        except User.DoesNotExist:
            return None

# register it to grant endpoint
server.register_grant(PasswordGrant)



class AuthorizationCode(Model, AuthorizationCodeMixin):
    user = ForeignKey(User, on_delete=CASCADE)
    client_id = CharField(max_length=48, db_index=True)
    code = CharField(max_length=120, unique=True, null=False)
    redirect_uri = TextField(default='', null=True)
    response_type = TextField(default='')
    scope = TextField(default='', null=True)
    auth_time = IntegerField(null=False, default=now_timestamp)

    def is_expired(self):
        return self.auth_time + 300 < time.time()

    def get_redirect_uri(self):
        return self.redirect_uri

    def get_scope(self):
        return self.scope or ''

    def get_auth_time(self):
        return self.auth_time

class AuthorizationCodeGrant(grants.AuthorizationCodeGrant):
    def save_authorization_code(self, code, request):
        client = request.client
        auth_code = AuthorizationCode(
            code=code,
            client_id=client.client_id,
            redirect_uri=request.redirect_uri,
            response_type=request.response_type,
            scope=request.scope,
            user=request.user,
        )
        auth_code.save()
        return auth_code

    def query_authorization_code(self, code, client):
        try:
            item = AuthorizationCode.objects.get(code=code, client_id=client.client_id)
        except AuthorizationCode.DoesNotExist:
            return None

        if not item.is_expired():
            return item

    def delete_authorization_code(self, authorization_code):
        authorization_code.delete()

    def authenticate_user(self, authorization_code):
        return authorization_code.user

# register it to grant endpoint
server.register_grant(AuthorizationCodeGrant)

class MyIntrospectionEndpoint(IntrospectionEndpoint):
    def query_token(self, token, token_type_hint):
        if token_type_hint == 'access_token':
            tok = Token.query.filter_by(access_token=token).first()
        elif token_type_hint == 'refresh_token':
            tok = Token.query.filter_by(refresh_token=token).first()
        else:
            # without token_type_hint
            tok = Token.query.filter_by(access_token=token).first()
            if not tok:
                tok = Token.query.filter_by(refresh_token=token).first()
        return tok

    def introspect_token(self, token):
        return {
            'active': True,
            'client_id': token.client_id,
            'token_type': token.token_type,
            'username': get_token_username(token),
            'scope': token.get_scope(),
            'sub': get_token_user_sub(token),
            'aud': token.client_id,
            'iss': 'https://server.example.com/',
            'exp': token.expires_at,
            'iat': token.issued_at,
        }

    def check_permission(self, token, client, request):
        # for example, we only allow internal client to access introspection endpoint
        return client.client_type == 'internal'


# register it to authorization server
server.register_endpoint(MyIntrospectionEndpoint)
def index(request):
    return HttpResponse("sso")

def authorize(request):
    if request.method == 'GET':
        grant = server.get_consent_grant(request, end_user=request.user)
        client = grant.client
        scope = client.get_allowed_scope(grant.request.scope)
        context = dict(grant=grant, client=client, scope=scope, user=request.user)
        return render(request, 'authorize.html', context)

    if is_user_confirmed(request):
        # granted by resource owner
        return server.create_authorization_response(request, grant_user=request.user)

    # denied by resource owner
    return server.create_authorization_response(request, grant_user=None)

# use ``server.create_token_response`` to handle token endpoint

@require_http_methods(["POST"])  # we only allow POST for token endpoint
def issue_token(request):
    return server.create_token_response(request)

server.register_grant(grants.ImplicitGrant)

class ClientCredentialsGrant(grants.ClientCredentialsGrant):
    TOKEN_ENDPOINT_AUTH_METHODS = [
        'client_secret_basic', 'client_secret_post'
    ]

server.register_grant(grants.ClientCredentialsGrant)
