#!/usr/bin/env python3
"""Agent runner script that replaces AGENT.sh template.

This script:
1. Reads the workspace configuration to determine which agent to run
2. Loads the agent's YAML configuration
3. Ensures the agent is installed
4. Launches the agent with proper configuration
"""

import os
import sys
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# Add silica to path so we can import modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.agent_yaml import load_agent_config, install_agent, generate_launch_command
from config.multi_workspace import load_project_config
from rich.console import Console

console = Console()


def load_environment_variables():
    """Load environment variables from piku ENV and LIVE_ENV files."""
    top_dir = Path.cwd()
    app_name = top_dir.name

    # Load both ENV and LIVE_ENV files (LIVE_ENV takes precedence)
    env_files = [
        Path.home() / ".piku" / "envs" / app_name / "ENV",
        Path.home() / ".piku" / "envs" / app_name / "LIVE_ENV",
    ]

    loaded_vars = {}

    for env_file in env_files:
        if env_file.exists():
            console.print(f"[blue]Loading environment from {env_file}[/blue]")
            with open(env_file, "r") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        # Remove quotes if present
                        if value.startswith('"') and value.endswith('"'):
                            value = value[1:-1]
                        elif value.startswith("'") and value.endswith("'"):
                            value = value[1:-1]
                        loaded_vars[key] = value
                        os.environ[key] = value
        else:
            console.print(f"[dim]Environment file not found: {env_file}[/dim]")

    if loaded_vars:
        console.print(f"[green]Loaded {len(loaded_vars)} environment variables[/green]")
        # Debug: show some non-sensitive variable names
        safe_vars = [
            k
            for k in loaded_vars.keys()
            if not any(
                sensitive in k.lower()
                for sensitive in ["key", "token", "secret", "password"]
            )
        ]
        if safe_vars:
            console.print(
                f"[dim]Variables loaded: {', '.join(safe_vars[:5])}{' ...' if len(safe_vars) > 5 else ''}[/dim]"
            )
    else:
        console.print("[yellow]No environment variables loaded[/yellow]")


def sync_dependencies():
    """Synchronize UV dependencies."""
    console.print("[blue]Synchronizing dependencies with uv...[/blue]")
    try:
        result = subprocess.run(
            ["uv", "sync"],
            capture_output=True,
            text=True,
            timeout=300,
            env=os.environ.copy(),  # Pass current environment to subprocess
        )
        if result.returncode != 0:
            console.print(f"[yellow]uv sync warning: {result.stderr}[/yellow]")
    except Exception as e:
        console.print(f"[yellow]uv sync error: {e}[/yellow]")


def resolve_agent_executable_path(agent_config, workspace_config):
    """Resolve the full path to the agent executable before changing directories.

    This allows us to install from project root (where pyproject.toml exists)
    but then run the agent from ./code directory with the resolved path.

    Returns:
        str: Full path to the executable, or the original command if resolution fails
    """
    # Generate the launch command as we normally would
    launch_command = generate_launch_command(agent_config, workspace_config)

    # Parse the command to extract the executable part
    command_parts = launch_command.split()

    if len(command_parts) < 2 or command_parts[0] != "uv" or command_parts[1] != "run":
        # If it's not a uv run command, return as-is
        return launch_command

    # For "uv run <executable> [args...]", we need to resolve the executable path
    if len(command_parts) < 3:
        return launch_command

    executable = command_parts[2]
    args = command_parts[3:] if len(command_parts) > 3 else []

    try:
        # Use uv to find the full path to the executable
        result = subprocess.run(
            ["uv", "run", "which", executable],
            capture_output=True,
            text=True,
            timeout=10,
            env=os.environ.copy(),
        )

        if result.returncode == 0:
            executable_path = result.stdout.strip()
            if executable_path and Path(executable_path).exists():
                # Return the resolved path with arguments
                resolved_command = f'"{executable_path}"'
                if args:
                    resolved_command += " " + " ".join(args)
                console.print(f"[green]Resolved executable: {executable_path}[/green]")
                return resolved_command

    except (subprocess.TimeoutExpired, subprocess.SubprocessError, Exception) as e:
        console.print(f"[yellow]Could not resolve executable path: {e}[/yellow]")

    # Fallback: try to use uv run with full command from the code directory
    # This might work if the uv environment is properly set up
    console.print("[yellow]Using fallback: uv run from code directory[/yellow]")
    return launch_command


def get_workspace_agent_config() -> tuple[str, Dict[str, Any]]:
    """Get the agent type and configuration for current workspace.

    Returns:
        Tuple of (agent_type, workspace_config)
    """
    try:
        # Try to load workspace config from current .silica directory
        from silica.config import get_silica_dir

        silica_dir = get_silica_dir()
        if not silica_dir or not silica_dir.exists():
            raise Exception("No .silica directory found")
        workspace_config = load_project_config(silica_dir)

        # Get current workspace name from environment or default
        current_workspace = os.environ.get(
            "SILICA_WORKSPACE_NAME", workspace_config.get("default_workspace", "agent")
        )

        if current_workspace in workspace_config.get("workspaces", {}):
            ws_config = workspace_config["workspaces"][current_workspace]
            agent_type = ws_config.get("agent_type", "hdev")
            return agent_type, ws_config
        else:
            console.print(
                f"[yellow]Workspace '{current_workspace}' not found, using default[/yellow]"
            )
            return "hdev", {
                "agent_type": "hdev",
                "agent_config": {"flags": [], "args": {}},
            }

    except Exception as e:
        console.print(f"[yellow]Error loading workspace config: {e}[/yellow]")
        console.print("[yellow]Using default agent configuration[/yellow]")
        return "hdev", {"agent_type": "hdev", "agent_config": {"flags": [], "args": {}}}


def main():
    """Main agent runner function."""
    console.print(f"[cyan]Starting agent runner at {datetime.now()}[/cyan]")

    # Get directory information
    top_dir = Path.cwd()
    app_name = top_dir.name
    console.print(f"[blue]Working directory: {top_dir}[/blue]")
    console.print(f"[blue]App name: {app_name}[/blue]")

    # Load environment variables
    load_environment_variables()

    # Sync dependencies
    sync_dependencies()

    # Install and resolve agent from project root (where pyproject.toml exists)
    console.print(f"[blue]Working from project root: {top_dir}[/blue]")

    # Get workspace agent configuration
    agent_type, workspace_config = get_workspace_agent_config()
    console.print(f"[green]Using agent: {agent_type}[/green]")

    # Load agent configuration from YAML
    agent_config = load_agent_config(agent_type)
    if not agent_config:
        console.print(
            f"[red]✗ Failed to load configuration for agent: {agent_type}[/red]"
        )
        console.print("[red]Available agents:[/red]")
        from utils.agent_yaml import list_built_in_agents

        for agent in list_built_in_agents():
            console.print(f"[red]  - {agent}[/red]")
        sys.exit(1)

    console.print(f"[green]Loaded agent config: {agent_config.description}[/green]")

    # Ensure agent is installed
    if not install_agent(agent_config):
        console.print(f"[red]✗ Failed to install agent: {agent_type}[/red]")
        sys.exit(1)

    # Check environment variables
    from utils.agent_yaml import report_environment_status

    report_environment_status(agent_config)

    # Resolve the executable path while we're still in project root
    resolved_command = resolve_agent_executable_path(agent_config, workspace_config)
    console.print(f"[cyan]Resolved command: {resolved_command}[/cyan]")

    # Now change to code directory where the agent should run
    code_dir = top_dir / "code"
    if code_dir.exists():
        os.chdir(code_dir)
        console.print(f"[blue]Changed to code directory: {code_dir}[/blue]")
    else:
        console.print(
            f"[yellow]Code directory not found, staying in: {top_dir}[/yellow]"
        )

    # Launch the agent
    console.print(
        f"[green]Starting {agent_config.name} agent from {os.getcwd()} at {datetime.now()}[/green]"
    )

    try:
        # Run the agent command with the full environment
        result = subprocess.run(
            resolved_command,
            shell=True,
            env=os.environ.copy(),  # Pass current environment to subprocess
        )
        exit_code = result.returncode

        console.print(
            f"[yellow]Agent exited with status {exit_code} at {datetime.now()}[/yellow]"
        )

        if exit_code != 0:
            console.print(
                f"[red]Agent {agent_config.name} exited with error code {exit_code}[/red]"
            )

    except KeyboardInterrupt:
        console.print(f"[yellow]Agent {agent_config.name} interrupted by user[/yellow]")
    except Exception as e:
        console.print(f"[red]Error running agent {agent_config.name}: {e}[/red]")
        sys.exit(1)

    # Keep tmux session alive for debugging
    console.print(
        "[blue]Agent process has ended. Keeping tmux session alive for debugging.[/blue]"
    )
    console.print(
        "[blue]Press Ctrl+C to exit or run 'exit' to close this session.[/blue]"
    )

    # Wait for user input to keep session alive
    try:
        input()
    except (KeyboardInterrupt, EOFError):
        console.print("[blue]Exiting agent runner.[/blue]")


if __name__ == "__main__":
    main()
