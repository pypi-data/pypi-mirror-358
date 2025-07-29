# Keycloak OIDC Backend for restaurant management apps

Переисользуемый и гибкий Keycloak OIDC backend для Django.
Используются следующие иерархические группы для задания ролей
```
    /organization_<iikoid>/admin
    /organization_<iikoid>/manager
    /organization_<iikoid>/viewer
    /organization_<iikoid>/member - use it for restaurant only users
    /organization_<iikoid>/restaurant_<iikoid>/manager
    /organization_<iikoid>/restaurant_<iikoid>/staff
    /organization_<iikoid>/restaurant_<iikoid>/viewer
```

## Installation

GH_PAT - personal access token for GitHub
```
pip install git+https://$GH_PATgithub.com/ark-tm/keycloak-auth-backend.git
```

## Usage

1. Add to `INSTALLED_APPS`
    ```
    INSTALLED_APPS = [
        ...
        'mozilla_django_oidc',
        ...
    ]
    ```
    In User model there must be `keycloak_id` field \
    In restaurant: `iikoid` \
    In organization: `iiko_id`

    Example models for roles:

    ```
    class OrganizationRoleEnum(models.TextChoices):
        VIEWER = "viewer", "Viewer"
        MANAGER = "manager", "Manager"
        ADMIN = "admin", "Admin"
        MEMBER = "member", "Member"


    class RestaurantRoleEnum(models.TextChoices):
        VIEWER = "viewer", "Viewer"
        STAFF = "staff", "Staff"
        MANAGER = "manager", "Manager"

    class OrganizationRole(TimestampedModel):
        user = models.ForeignKey('core.User', on_delete=models.CASCADE)
        organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
        role = models.CharField(max_length=50, choices=OrganizationRoleEnum.choices)

        class Meta:
            unique_together = ('user', 'organization')

    class RestaurantRole(TimestampedModel):
        user = models.ForeignKey('core.User', on_delete=models.CASCADE)
        restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
        role = models.CharField(max_length=50, choices=RestaurantRoleEnum.choices)

        class Meta:
            unique_together = ('user', 'restaurant')
    ```

2. Configure `AUTHENTICATION_BACKENDS` in your Django `settings.py`:
    ```
    AUTHENTICATION_BACKENDS = (
        'keycloak-auth.backends.KeycloakOIDCBackend',
        'django.contrib.auth.backends.ModelBackend',
    )
    ```

3. Specify your models in `settings.py`:
    ```
    ORGANIZATION_MODEL = 'core.Organization'
    ORGANIZATION_ROLE_MODEL = 'core.OrganizationRole'
    RESTAURANT_MODEL = 'core.Restaurant'
    RESTAURANT_ROLE_MODEL = 'core.RestaurantRole'
    ```

4. Add the mozilla-django-oidc settings
```
OIDC_RP_CLIENT_ID
OIDC_RP_CLIENT_SECRET
KEYCLOAK_REALM

OIDC_OP_AUTHORIZATION_ENDPOINT
OIDC_OP_TOKEN_ENDPOINT 
OIDC_OP_USER_ENDPOINT
OIDC_OP_JWKS_ENDPOINT
OIDC_RP_SIGN_ALGO
OIDC_USERNAME_CLAIM
OIDC_USER_CREATION = True 
OIDC_AUTH_REQUEST_EXTRA_PARAMS = {"scope": "openid email profile roles"} 

LOGIN_REDIRECT_URL
LOGOUT_REDIRECT_URL
OIDC_LOGIN_REDIRECT_URL
OIDC_LOGOUT_REDIRECT_URL

OIDC_STORE_ACCESS_TOKEN = True
OIDC_STORE_ID_TOKEN = True
OIDC_RENEW_ID_TOKEN_EXPIRY_SECONDS = 3600


KEYCLOAK_SERVER_URL = getenv('KEYCLOAK_SERVER_URL')

KEYCLOAK_CLIENT_ID = OIDC_RP_CLIENT_ID
KEYCLOAK_CLIENT_SECRET = OIDC_RP_CLIENT_SECRET

```

