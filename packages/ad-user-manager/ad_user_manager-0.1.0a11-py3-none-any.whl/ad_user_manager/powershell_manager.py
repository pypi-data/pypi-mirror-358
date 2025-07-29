"""
PowerShell-based Active Directory User Manager for Domain Controllers.
"""

import json
import logging
import platform
import subprocess
from typing import Any

import structlog

from .config import ADConfig
from .exceptions import (PowerShellExecutionError, SearchError,
                         UserCreationError, UserExistsError)
from .models import UserCreationResult, UserInfo


class PowerShellADManager:
    """PowerShell-based Active Directory User Manager for Domain Controllers."""

    def __init__(self, config: ADConfig):
        """Initialize PowerShell AD Manager with configuration."""
        self.config = config
        self.logger = structlog.get_logger(__name__)
        self._setup_logging()

        # Check if running on Windows
        if platform.system() != "Windows":
            raise Exception("PowerShell AD Manager requires Windows")

        # Check if AD module is available
        if not self._check_ad_module():
            raise Exception("Active Directory PowerShell module not available")

    def _setup_logging(self):
        """Setup structured logging."""
        logging.basicConfig(
            level=getattr(logging, self.config.log_level), format="%(message)s"
        )

        if self.config.log_format == "json":
            structlog.configure(
                processors=[
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="iso"),
                    structlog.processors.StackInfoRenderer(),
                    structlog.processors.format_exc_info,
                    structlog.processors.JSONRenderer(),
                ],
                wrapper_class=structlog.stdlib.BoundLogger,
                logger_factory=structlog.stdlib.LoggerFactory(),
                cache_logger_on_first_use=True,
            )
        else:
            structlog.configure(
                processors=[
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="%Y-%m-%d %H:%M:%S"),
                    structlog.dev.ConsoleRenderer(),
                ],
                wrapper_class=structlog.stdlib.BoundLogger,
                logger_factory=structlog.stdlib.LoggerFactory(),
                cache_logger_on_first_use=True,
            )

    def _check_ad_module(self) -> bool:
        """Check if Active Directory PowerShell module is available."""
        try:
            cmd = [
                "powershell",
                "-Command",
                "Get-Module -ListAvailable -Name ActiveDirectory",
            ]
            result = subprocess.run(
                cmd, capture_output=True, text=True, timeout=10, check=False
            )
            return result.returncode == 0 and "ActiveDirectory" in result.stdout
        except Exception as e:
            self.logger.debug("AD module check failed", error=str(e))
            return False

    def _run_powershell(self, command: str) -> subprocess.CompletedProcess:
        """Execute PowerShell command and return result."""
        cmd = ["powershell", "-Command", command]
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.config.connection_timeout,
                check=False,
            )

            if result.returncode != 0:
                self.logger.error(
                    "PowerShell command failed",
                    command=command,
                    stderr=result.stderr,
                    stdout=result.stdout,
                )

            return result
        except subprocess.TimeoutExpired:
            self.logger.error("PowerShell command timed out", command=command)
            raise PowerShellExecutionError(
                command,
                -1,
                "Command timed out",
                {"timeout": self.config.connection_timeout},
            )
        except Exception as e:
            self.logger.error(
                "PowerShell execution failed", command=command, error=str(e)
            )
            raise PowerShellExecutionError(command, -1, str(e))

    def test_connection(self) -> bool:
        """Test AD connection by running a simple PowerShell command."""
        try:
            result = self._run_powershell("Get-ADDomain")
            success = result.returncode == 0
            if success:
                self.logger.info("PowerShell AD connection test successful")
            else:
                self.logger.error(
                    "PowerShell AD connection test failed", stderr=result.stderr
                )
            return success
        except Exception as e:
            self.logger.error("PowerShell AD connection test failed", error=str(e))
            return False

    def search_user(self, username: str) -> UserInfo | None:
        """Search for a user in AD using PowerShell."""
        try:
            # Use Get-ADUser to search for the user
            command = f"Get-ADUser -Filter \"SamAccountName -eq '{username}'\" -Properties * | ConvertTo-Json -Depth 3"
            result = self._run_powershell(command)

            if result.returncode != 0:
                if "Cannot find an object with identity" in result.stderr:
                    self.logger.debug("User not found", username=username)
                    return None
                raise SearchError(f"SamAccountName -eq '{username}'", result.stderr)

            if not result.stdout.strip():
                self.logger.debug("User not found", username=username)
                return None

            # Parse JSON output
            user_data = json.loads(result.stdout)

            user_info = UserInfo(
                username=username,
                dn=user_data.get("DistinguishedName", ""),
                attributes=user_data,
                exists=True,
            )

            self.logger.debug("User found", username=username, dn=user_info.dn)
            return user_info

        except json.JSONDecodeError as e:
            self.logger.error(
                "Failed to parse PowerShell output", username=username, error=str(e)
            )
            raise SearchError(
                f"SamAccountName -eq '{username}'", f"JSON parse error: {str(e)}"
            )
        except Exception as e:
            self.logger.error(
                "PowerShell user search failed", username=username, error=str(e)
            )
            raise SearchError(f"SamAccountName -eq '{username}'", str(e))

    def user_exists(self, username: str) -> bool:
        """Check if a user exists in AD."""
        user_info = self.search_user(username)
        return user_info is not None

    def create_user(
        self,
        username: str,
        first_name: str,
        last_name: str,
        email: str,
        password: str | None = None,
        additional_attributes: dict[str, Any] | None = None,
        resolve_conflicts: bool = True,
        dry_run: bool = False,
    ) -> UserCreationResult:
        """Create a new user in AD using PowerShell."""
        original_username = username
        conflicts_resolved = 0

        # Check if user already exists and handle conflicts
        if resolve_conflicts and self.user_exists(username):
            from .validators import UserValidator

            validator = UserValidator(self.config)
            username, conflicts_resolved = validator.resolve_username_conflict(
                username, self
            )
        elif self.user_exists(username):
            raise UserExistsError(username)

        # Build display name and UPN
        display_name = f"{first_name} {last_name}"

        # Use host from server config for UPN
        if hasattr(self.config.server, "host") and self.config.server.host:
            domain = self.config.server.host
        else:
            # For DC mode, try to get domain from AD
            try:
                domain_result = self._run_powershell("(Get-ADDomain).DNSRoot")
                if domain_result.returncode == 0 and domain_result.stdout.strip():
                    domain = domain_result.stdout.strip()
                else:
                    domain = "local.domain"  # Fallback
            except Exception:
                domain = "local.domain"  # Fallback

        upn = f"{username}@{domain}"

        if dry_run:
            user_dn = f"CN={display_name},{self.config.server.base_dn}"
            self.logger.info(
                "Dry run - would create user", username=username, dn=user_dn
            )
            return UserCreationResult(
                username=username,
                created=False,
                original_username=original_username,
                dn=user_dn,
                conflicts_resolved=conflicts_resolved,
                message="Dry run - user would be created",
            )

        try:
            # Build PowerShell command for user creation
            ps_command_parts = [
                "New-ADUser",
                f"-Name '{display_name}'",
                f"-SamAccountName '{username}'",
                f"-UserPrincipalName '{upn}'",
                f"-GivenName '{first_name}'",
                f"-Surname '{last_name}'",
                f"-EmailAddress '{email}'",
                f"-Path '{self.config.server.base_dn}'",
                "-Enabled $true",
            ]

            # Add password if provided
            if password:
                # Escape single quotes in password
                escaped_password = password.replace("'", "''")
                ps_command_parts.append(
                    f"-AccountPassword (ConvertTo-SecureString '{escaped_password}' -AsPlainText -Force)"
                )

            # Add additional attributes if provided
            if additional_attributes:
                for key, value in additional_attributes.items():
                    if isinstance(value, str):
                        escaped_value = value.replace("'", "''")
                        ps_command_parts.append(f"-{key} '{escaped_value}'")
                    else:
                        ps_command_parts.append(f"-{key} {value}")

            ps_command = " ".join(ps_command_parts)

            result = self._run_powershell(ps_command)

            if result.returncode != 0:
                error_msg = f"Failed to create user: {result.stderr}"
                self.logger.error(
                    "User creation failed", username=username, error=error_msg
                )
                raise UserCreationError(username, error_msg)

            # Get the created user's DN
            user_info = self.search_user(username)
            user_dn = (
                user_info.dn
                if user_info
                else f"CN={display_name},{self.config.server.base_dn}"
            )

            self.logger.info("User created successfully", username=username, dn=user_dn)
            return UserCreationResult(
                username=username,
                created=True,
                original_username=original_username,
                dn=user_dn,
                conflicts_resolved=conflicts_resolved,
                message="User created successfully",
            )

        except Exception as e:
            self.logger.error(
                "PowerShell user creation failed", username=username, error=str(e)
            )
            raise UserCreationError(username, str(e))

    def close_connections(self):
        """Close connections (no-op for PowerShell manager)."""
        self.logger.debug("PowerShell manager connections closed (no-op)")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close_connections()
