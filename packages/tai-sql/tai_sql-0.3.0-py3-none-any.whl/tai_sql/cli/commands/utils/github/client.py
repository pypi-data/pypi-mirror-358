"""
Utilidades para interactuar con la API de GitHub
"""
import subprocess
from typing import Optional, Dict, Any, List, Set
import click
import requests
from nacl import encoding, public
from base64 import b64encode
from .auth import GitHubAuth
from .models import RepositoryInfo

class GitHubClient:
    """Cliente para interactuar con la API de GitHub"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token or GitHubAuth.get_token()
        if not self.token:
            raise ValueError("No se pudo obtener token de GitHub")
        
        self.headers = {
            'Authorization': f'token {self.token}',
            'Accept': 'application/vnd.github.v3+json',
            'Content-Type': 'application/json'
        }

        self.base_url = 'https://api.github.com'
    
    def get_repo_info(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene información del repositorio actual
        
        Returns:
            Información del repositorio o None si no se encuentra
        """
        try:
            # Obtener remote origin
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                capture_output=True, text=True, timeout=5
            )
            
            if result.returncode != 0:
                click.echo("❌ No se encontró remote 'origin' en git")
                return None
            
            remote_url = result.stdout.strip()
            
            # Parsear URL para obtener owner/repo
            repo_info = self._parse_git_url(remote_url)
            if not repo_info:
                return None
            
            # Verificar que el repositorio existe en GitHub
            response = requests.get(
                f"{self.base_url}/repos/{repo_info.owner}/{repo_info.repo}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                click.echo(f"❌ Repositorio no encontrado en GitHub: {repo_info['owner']}/{repo_info['repo']}")
                return None
                
        except subprocess.TimeoutExpired:
            click.echo("❌ Timeout al obtener información de git")
            return None
        except Exception as e:
            click.echo(f"❌ Error al obtener información del repositorio: {e}")
            return None
    
    def _parse_git_url(self, url: str) -> Optional[RepositoryInfo]:
        """Parsea una URL de git para obtener información del repositorio"""
        try:
            # SSH format: git@github.com:owner/repo.git
            if url.startswith('git@github.com:'):
                path = url[15:]  # Remove 'git@github.com:'
                if path.endswith('.git'):
                    path = path[:-4]
                owner, repo = path.split('/')
                return RepositoryInfo(owner=owner, repo=repo)
            
            # HTTPS format: https://github.com/owner/repo.git
            elif 'github.com' in url:
                parts = url.rstrip('/').split('/')
                if len(parts) >= 2:
                    repo = parts[-1]
                    owner = parts[-2]
                    if repo.endswith('.git'):
                        repo = repo[:-4]
                    return RepositoryInfo(owner=owner, repo=repo)
            
            return None
            
        except:
            return None
    
    def create_environment(self, owner: str, repo: str, environment: str) -> bool:
        """
        Crea un entorno en GitHub si no existe
        
        Args:
            owner: Propietario del repositorio
            repo: Nombre del repositorio
            environment: Nombre del entorno
            
        Returns:
            True si se creó o ya existía
        """
        try:
            # Verificar si el entorno ya existe
            response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/environments/{environment}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                click.echo(f"   ℹ️  Entorno '{environment}' ya existe")
                return True
            elif response.status_code == 404:
                # Crear el entorno
                data = {}
                response = requests.put(
                    f"{self.base_url}/repos/{owner}/{repo}/environments/{environment}",
                    headers=self.headers,
                    json=data,
                    timeout=10
                )
                
                if response.status_code in [200, 201]:
                    click.echo(f"   ✅ Entorno '{environment}' creado")
                    return True
                else:
                    click.echo(f"   ❌ Error al crear entorno '{environment}': {response.status_code}")
                    return False
            else:
                click.echo(f"   ❌ Error al verificar entorno '{environment}': {response.status_code}")
                return False
                
        except Exception as e:
            click.echo(f"   ❌ Error al gestionar entorno '{environment}': {e}")
            return False
    
    def get_environment_variable(self, owner: str, repo: str, environment: str, variable_name: str) -> Optional[str]:
        """
        Obtiene una variable de entorno
        
        Returns:
            Valor de la variable o None si no existe
        """
        try:
            response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/environments/{environment}/variables/{variable_name}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('value')
            else:
                return None
                
        except Exception:
            return None
    
    def set_environment_variable(self, owner: str, repo: str, environment: str, 
                               variable_name: str, value: str) -> bool:
        """
        Establece una variable de entorno
        
        Returns:
            True si se estableció correctamente
        """
        try:
            data = {'name': variable_name, 'value': value}
            
            response = requests.post(
                f"{self.base_url}/repos/{owner}/{repo}/environments/{environment}/variables",
                headers=self.headers,
                json=data,
                timeout=10
            )
            
            return response.status_code in [200, 201]
            
        except Exception as e:
            return False
    
    def list_environment_variables(self, owner: str, repo: str, environment: str) -> List[Dict[str, Any]]:
        """
        Lista todas las variables de un entorno
        
        Returns:
            Lista de variables del entorno
        """
        try:
            response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/environments/{environment}/variables",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('variables', [])
            else:
                return []
                
        except Exception:
            return []

    def get_environment_secret(self, owner: str, repo: str, environment: str, secret_name: str) -> bool:
        """
        Verifica si un secret de entorno existe
        
        Returns:
            True si el secret existe, False si no existe
        """
        try:
            response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/environments/{environment}/secrets/{secret_name}",
                headers=self.headers,
                timeout=10
            )
            
            return response.status_code == 200
                
        except Exception as e:
            click.echo(e)
            return False
    
    def set_environment_secret(self, owner: str, repo: str, environment: str, 
                                secret_name: str, value: str) -> bool:
        """
        Establece un secret de entorno
        
        Returns:
            True si se estableció correctamente
        """
        try:
            # Para secrets necesitamos encriptar el valor
            # Primero obtenemos la clave pública del repositorio
            pub_key_response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/environments/{environment}/secrets/public-key",
                headers=self.headers,
                timeout=10
            )
            
            if pub_key_response.status_code != 200:
                return False
                
            pub_key_data = pub_key_response.json()
            
            # Encriptar el valor usando la clave pública
            public_key = public.PublicKey(pub_key_data['key'], encoding.Base64Encoder())
            sealed_box = public.SealedBox(public_key)
            encrypted = sealed_box.encrypt(value.encode('utf-8'))
            encrypted_value = b64encode(encrypted).decode("utf-8")
            
            data = {
                'encrypted_value': encrypted_value,
                'key_id': pub_key_data['key_id']
            }
            
            response = requests.put(
                f"{self.base_url}/repos/{owner}/{repo}/environments/{environment}/secrets/{secret_name}",
                headers=self.headers,
                json=data,
                timeout=10
            )
            
            return response.status_code in [200, 201, 204]
            
        except Exception as e:
            click.echo(e)
            return False
    
    def list_environment_secrets(self, owner: str, repo: str, environment: str) -> List[Dict[str, Any]]:
        """
        Lista todos los secrets de un entorno
        
        Returns:
            Lista de secrets del entorno (solo nombres, no valores)
        """
        try:
            response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/environments/{environment}/secrets",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('secrets', [])
            else:
                return []
                
        except Exception:
            return []

    def check_user_permissions(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Verifica los permisos del usuario en el repositorio
        
        Args:
            owner: Propietario del repositorio
            repo: Nombre del repositorio
            
        Returns:
            Diccionario con información de permisos y recomendaciones
        """
        try:
            # Obtener información del usuario actual
            user_info = self.get_current_user()
            if not user_info:
                return {
                    'has_sufficient_permissions': False,
                    'error': 'No se pudo obtener información del usuario',
                    'recommendations': ['Verificar que el token sea válido']
                }
            
            username = user_info['login']
            
            # Verificar permisos en el repositorio
            repo_permissions = self.get_repository_permissions(owner, repo, username)
            
            # Verificar scopes del token
            token_scopes = self.get_token_scopes()
            
            # Analizar permisos
            analysis = self._analyze_permissions(repo, repo_permissions, token_scopes, owner, username)
            
            return analysis
            
        except Exception as e:
            return {
                'has_sufficient_permissions': False,
                'error': f'Error verificando permisos: {str(e)}',
                'recommendations': ['Verificar conectividad con GitHub', 'Validar token de acceso']
            }
    
    def get_current_user(self) -> Optional[Dict[str, Any]]:
        """
        Obtiene información del usuario actual
        
        Returns:
            Información del usuario o None si hay error
        """
        try:
            response = requests.get(
                f"{self.base_url}/user",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return None
                
        except Exception:
            return None
    
    def get_repository_permissions(self, owner: str, repo: str, username: str) -> Dict[str, Any]:
        """
        Obtiene los permisos específicos del usuario en el repositorio
        
        Args:
            owner: Propietario del repositorio
            repo: Nombre del repositorio
            username: Usuario a verificar
            
        Returns:
            Diccionario con información de permisos
        """
        try:
            # Verificar si el usuario es colaborador
            response = requests.get(
                f"{self.base_url}/repos/{owner}/{repo}/collaborators/{username}/permission",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            
            # Si no es colaborador directo, verificar si es el owner
            if username.lower() == owner.lower():
                return {
                    'permission': 'admin',
                    'user': {'login': username},
                    'role_name': 'owner'
                }
            
            # Verificar si tiene acceso via organization
            org_permission = self._check_organization_permission(owner, repo, username)
            if org_permission:
                return org_permission
            
            return {
                'permission': 'none',
                'user': {'login': username},
                'role_name': 'none'
            }
            
        except Exception:
            return {
                'permission': 'unknown',
                'user': {'login': username},
                'role_name': 'unknown'
            }
    
    def get_token_scopes(self) -> Set[str]:
        """
        Obtiene los scopes del token actual
        
        Returns:
            Set con los scopes del token
        """
        try:
            response = requests.get(
                f"{self.base_url}/user",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                # Los scopes vienen en el header X-OAuth-Scopes
                scopes_header = response.headers.get('X-OAuth-Scopes', '')
                if scopes_header:
                    return set(scope.strip() for scope in scopes_header.split(','))
            
            return set()
            
        except Exception:
            return set()
    
    def _check_organization_permission(self, owner: str, repo: str, username: str) -> Optional[Dict[str, Any]]:
        """
        Verifica permisos via organización
        
        Args:
            owner: Propietario del repositorio (organización)
            repo: Nombre del repositorio
            username: Usuario a verificar
            
        Returns:
            Información de permisos o None
        """
        try:
            # Verificar si el owner es una organización
            response = requests.get(
                f"{self.base_url}/orgs/{owner}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code != 200:
                return None  # No es una organización
            
            # Verificar membresía en la organización
            response = requests.get(
                f"{self.base_url}/orgs/{owner}/members/{username}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                # Es miembro, verificar permisos en el repositorio
                response = requests.get(
                    f"{self.base_url}/repos/{owner}/{repo}",
                    headers=self.headers,
                    timeout=10
                )
                
                if response.status_code == 200:
                    repo_data = response.json()
                    permissions = repo_data.get('permissions', {})
                    
                    if permissions.get('admin'):
                        role = 'admin'
                    elif permissions.get('maintain'):
                        role = 'maintain'
                    elif permissions.get('push'):
                        role = 'write'
                    elif permissions.get('pull'):
                        role = 'read'
                    else:
                        role = 'none'
                    
                    return {
                        'permission': role,
                        'user': {'login': username},
                        'role_name': f'organization_{role}'
                    }
            
            return None
            
        except Exception:
            return None
    
    def _analyze_permissions(self, repo: str, repo_permissions: Dict[str, Any], token_scopes: Set[str], 
                           owner: str, username: str) -> Dict[str, Any]:
        """
        Analiza los permisos y genera recomendaciones
        
        Args:
            repo_permissions: Permisos en el repositorio
            token_scopes: Scopes del token
            owner: Propietario del repositorio
            username: Usuario actual
            
        Returns:
            Análisis completo de permisos
        """
        permission_level = repo_permissions.get('permission', 'none')
        role_name = repo_permissions.get('role_name', 'unknown')
        
        # Scopes requeridos para deploy-config
        required_scopes = {'repo', 'admin:repo_hook'}
        
        # Permisos mínimos requeridos en el repositorio
        required_repo_permissions = {'admin', 'maintain'}
        
        # Análisis de scopes
        missing_scopes = required_scopes - token_scopes
        has_sufficient_scopes = len(missing_scopes) == 0
        
        # Análisis de permisos en repositorio
        has_sufficient_repo_permissions = permission_level in required_repo_permissions
        
        # Determinar si tiene permisos suficientes
        has_sufficient_permissions = has_sufficient_scopes and has_sufficient_repo_permissions
        
        # Generar recomendaciones
        recommendations = []
        warnings = []
        
        if not has_sufficient_scopes:
            recommendations.append(f"Regenerar token con scopes: {', '.join(sorted(required_scopes))}")
            warnings.append(f"Scopes faltantes: {', '.join(sorted(missing_scopes))}")
        
        if not has_sufficient_repo_permissions:
            if permission_level == 'none':
                recommendations.append(f"Solicitar acceso al repositorio {owner}/{repo}")
                warnings.append("Sin acceso al repositorio")
            elif permission_level in ['read', 'triage']:
                recommendations.append("Solicitar permisos de 'Maintain' o 'Admin' en el repositorio")
                warnings.append(f"Permisos insuficientes: {permission_level} (se requiere admin/maintain)")
            elif permission_level == 'write':
                recommendations.append("Solicitar permisos de 'Maintain' o 'Admin' para gestionar environments")
                warnings.append("Permisos de 'Write' insuficientes para gestionar environments")
        
        # Información adicional
        info = []
        if username.lower() == owner.lower():
            info.append("Eres el propietario del repositorio")
        elif 'organization' in role_name:
            info.append("Acceso via organización")
        
        return {
            'has_sufficient_permissions': has_sufficient_permissions,
            'user': {
                'login': username,
                'is_owner': username.lower() == owner.lower()
            },
            'repository': {
                'permission': permission_level,
                'role_name': role_name,
                'required_permissions': list(required_repo_permissions)
            },
            'token': {
                'scopes': sorted(list(token_scopes)),
                'required_scopes': sorted(list(required_scopes)),
                'missing_scopes': sorted(list(missing_scopes))
            },
            'warnings': warnings,
            'recommendations': recommendations,
            'info': info
        }
    
    def display_permissions_report(self, owner: str, repo: str) -> bool:
        """
        Muestra un reporte completo de permisos
        
        Args:
            owner: Propietario del repositorio
            repo: Nombre del repositorio
            
        Returns:
            True si tiene permisos suficientes, False si no
        """
        click.echo("🔍 Verificando permisos de GitHub...")
        
        analysis = self.check_user_permissions(owner, repo)
        
        if analysis.get('error'):
            click.echo(f"❌ {analysis['error']}")
            for rec in analysis.get('recommendations', []):
                click.echo(f"   💡 {rec}")
            return False
        
        user = analysis['user']
        repo_info = analysis['repository']
        token_info = analysis['token']
        
        click.echo(f"👤 Usuario: {user['login']}")
        
        # Mostrar información adicional
        for info in analysis.get('info', []):
            click.echo(f"   ℹ️  {info}")
        
        # Mostrar permisos del repositorio
        click.echo(f"📂 Repositorio: {owner}/{repo}")
        click.echo(f"   🔑 Permisos: {repo_info['permission']}")
        click.echo(f"   👥 Rol: {repo_info['role_name']}")
        
        # Mostrar scopes del token
        click.echo(f"🎫 Token scopes:")
        for scope in token_info['scopes']:
            click.echo(f"   ✅ {scope}")
        
        # Mostrar warnings
        if analysis.get('warnings'):
            click.echo("⚠️  Advertencias:")
            for warning in analysis['warnings']:
                click.echo(f"   🚨 {warning}")
        
        # Mostrar recomendaciones
        if analysis.get('recommendations'):
            click.echo("💡 Recomendaciones:")
            for rec in analysis['recommendations']:
                click.echo(f"   📝 {rec}")
        
        # Resultado final
        if analysis['has_sufficient_permissions']:
            click.echo("✅ Permisos suficientes")
            return True
        else:
            click.echo("❌ Permisos insuficientes")
            click.echo()
            click.echo("🔧 Para resolver:")
            click.echo("   1. Regenerar token con scopes requeridos")
            click.echo("   2. Solicitar permisos de Admin/Maintain en el repositorio")
            click.echo("   3. Verificar que el repositorio existe y es accesible")
            return False