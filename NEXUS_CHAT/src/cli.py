"""
CLI Interface for NEXUS Multi-Agent Orchestrator
"""
import asyncio
import json
import logging
import uuid
from datetime import datetime
from typing import Optional, List

import click
from .orchestrator import NEXUSOrchestrator
from .models import TaskRequest, TaskStatus
from .config import get_config, validate_environment


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose logging')
@click.option('--config-dir', default='config', help='Configuration directory path')
@click.pass_context
def nexus(ctx, verbose, config_dir):
    """🧬 NEXUS Multi-Agent Orchestrator CLI
    
    Coordinate multiple AI agents for complex task execution.
    """
    # Ensure context exists
    ctx.ensure_object(dict)
    
    # Set up logging
    log_level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Store config
    ctx.obj['config_dir'] = config_dir
    ctx.obj['verbose'] = verbose


@nexus.command()
@click.option('--task', prompt='Task description', help='Describe the task for NEXUS')
@click.option('--technology', help='Technology stack to use')
@click.option('--timeline', help='Expected timeline (e.g., "2 hours", "1 day")')
@click.option('--priority', type=click.Choice(['low', 'medium', 'high']), default='medium', help='Task priority')
@click.option('--requirements', help='Comma-separated list of requirements')
@click.option('--context', help='Additional context for the task')
@click.pass_context
def execute(ctx, task, technology, timeline, priority, requirements, context):
    """Execute a task using NEXUS orchestration"""
    
    async def run_task():
        try:
            click.echo("🧬 Initializing NEXUS Multi-Agent Orchestrator...")
            
            # Load configuration
            config = get_config()
            orchestrator = NEXUSOrchestrator(config.workspace_path)
            
            # Initialize agents
            click.echo("🎯 Initializing AI agents...")
            await orchestrator.initialize_agents()
            
            click.echo(f"✅ NEXUS initialized with {len(orchestrator.agents)} agents")
            click.echo("👥 Active agents: " + ", ".join(orchestrator.agents.keys()))
            
            # Create task request
            task_id = f"task_{int(datetime.utcnow().timestamp())}_{uuid.uuid4().hex[:8]}"
            
            task_request = TaskRequest(
                task_id=task_id,
                description=task,
                requirements=requirements.split(',') if requirements else None,
                technology=technology,
                timeline=timeline,
                priority=priority,
                context=context
            )
            
            click.echo(f"\n🚀 Starting task coordination: {task_id}")
            click.echo(f"📋 Description: {task}")
            if technology:
                click.echo(f"💻 Technology: {technology}")
            if timeline:
                click.echo(f"⏰ Timeline: {timeline}")
            click.echo(f"🎯 Priority: {priority}")
            
            # Set up progress callback
            last_progress = -1
            
            async def progress_callback(progress_data):
                nonlocal last_progress
                if progress_data and 'overall_progress' in progress_data:
                    current_progress = int(progress_data['overall_progress'] * 100)
                    if current_progress != last_progress:
                        click.echo(f"📊 Progress: {current_progress}%")
                        last_progress = current_progress
                        
                        if 'completed_agents' in progress_data:
                            for agent in progress_data['completed_agents']:
                                click.echo(f"  ✅ {agent} completed")
                        
                        if 'active_agents' in progress_data:
                            for agent in progress_data['active_agents']:
                                click.echo(f"  🔄 {agent} in progress")
            
            # Subscribe to progress updates
            await orchestrator.feedback_system.progress_tracker.subscribe_to_progress(progress_callback)
            
            # Execute coordination
            click.echo("\n🎭 Phase 1: Analysis (Aria)")
            result = await orchestrator.coordinate_task(task_request)
            
            # Display results
            click.echo(f"\n✅ Task coordination completed!")
            click.echo(f"📊 Status: {result.status.value}")
            click.echo(f"🎯 Overall Progress: {result.overall_progress:.1%}")
            
            if result.started_at and result.completed_at:
                duration = result.completed_at - result.started_at
                click.echo(f"⏱️  Duration: {duration.total_seconds():.1f} seconds")
            
            if result.error_message:
                click.echo(f"❌ Error: {result.error_message}")
                return
            
            # Show results by phase
            click.echo("\n" + "="*60)
            click.echo("📊 NEXUS COORDINATION RESULTS")
            click.echo("="*60)
            
            if result.analysis:
                click.echo("\n🧭 ANALYSIS (Aria):")
                click.echo("-" * 40)
                click.echo(result.analysis[:500] + ("..." if len(result.analysis) > 500 else ""))
            
            if result.implementation:
                click.echo("\n💻 IMPLEMENTATION (Code):")
                click.echo("-" * 40)
                click.echo(result.implementation[:500] + ("..." if len(result.implementation) > 500 else ""))
            
            if result.tests:
                click.echo("\n🧪 TESTS (Alpha):")
                click.echo("-" * 40)
                click.echo(result.tests[:500] + ("..." if len(result.tests) > 500 else ""))
            
            if result.validation:
                click.echo("\n🛡️ VALIDATION (Beta):")
                click.echo("-" * 40)
                click.echo(result.validation[:500] + ("..." if len(result.validation) > 500 else ""))
            
            click.echo("\n" + "="*60)
            click.echo("🎉 NEXUS coordination complete!")
            
            # Cleanup
            await orchestrator.shutdown()
            
        except KeyboardInterrupt:
            click.echo("\n⚠️ Task interrupted by user")
        except Exception as e:
            click.echo(f"\n❌ Error: {e}")
            if ctx.obj.get('verbose'):
                import traceback
                click.echo(traceback.format_exc())
    
    asyncio.run(run_task())


@nexus.command()
@click.pass_context
def status(ctx):
    """Check NEXUS system status"""
    
    async def check_status():
        try:
            click.echo("🧬 Checking NEXUS system status...")
            
            config = get_config()
            orchestrator = NEXUSOrchestrator(config.workspace_path)
            
            # Initialize to get agent status
            await orchestrator.initialize_agents()
            
            # Get system status
            system_status = await orchestrator.get_system_status()
            agent_status = await orchestrator.get_all_agent_status()
            
            click.echo("\n🎯 NEXUS System Status:")
            click.echo(f"  Active Agents: {system_status['active_agents']}")
            click.echo(f"  Total Tasks: {system_status['tasks']['total_tasks']}")
            click.echo(f"  Timestamp: {system_status['timestamp']}")
            
            click.echo("\n👥 Agent Status:")
            for agent_id, status_data in agent_status.items():
                status_indicator = {
                    'active': '🟢',
                    'processing': '🟡',
                    'completed': '✅',
                    'error': '🔴',
                    'inactive': '⚫'
                }.get(status_data.get('status', 'unknown'), '❓')
                
                click.echo(f"  {status_indicator} {agent_id}: {status_data.get('status', 'unknown')}")
                if status_data.get('current_task'):
                    click.echo(f"    Current Task: {status_data['current_task']}")
            
            await orchestrator.shutdown()
            
        except Exception as e:
            click.echo(f"❌ Error checking status: {e}")
            if ctx.obj.get('verbose'):
                import traceback
                click.echo(traceback.format_exc())
    
    asyncio.run(check_status())


@nexus.command()
@click.option('--host', default='localhost', help='Host to bind to')
@click.option('--port', default=8000, help='Port to bind to')
@click.option('--reload', is_flag=True, help='Enable auto-reload')
@click.pass_context
def serve(ctx, host, port, reload):
    """Start NEXUS web interface"""
    try:
        import uvicorn
        from .web_interface import create_app
        
        click.echo(f"🧬 Starting NEXUS web interface on {host}:{port}")
        click.echo(f"📱 Open http://{host}:{port} in your browser")
        
        # Create FastAPI app
        app = create_app()
        
        # Start server
        uvicorn.run(
            app,
            host=host,
            port=port,
            reload=reload,
            log_level="info" if ctx.obj.get('verbose') else "warning"
        )
        
    except ImportError:
        click.echo("❌ uvicorn not installed. Install with: pip install uvicorn")
    except Exception as e:
        click.echo(f"❌ Error starting web interface: {e}")
        if ctx.obj.get('verbose'):
            import traceback
            click.echo(traceback.format_exc())


@nexus.command()
@click.pass_context
def validate(ctx):
    """Validate NEXUS environment and configuration"""
    try:
        click.echo("🧬 Validating NEXUS environment...")
        
        # Validate environment
        validation = validate_environment()
        
        click.echo(f"\n🎯 Environment Status: {'✅ Valid' if validation['environment_valid'] else '❌ Invalid'}")
        
        # System info
        if validation['system_info']:
            click.echo("\n💻 System Information:")
            for key, value in validation['system_info'].items():
                click.echo(f"  {key}: {value}")
        
        # Warnings
        if validation['warnings']:
            click.echo("\n⚠️  Warnings:")
            for warning in validation['warnings']:
                click.echo(f"  - {warning}")
        
        # Errors
        if validation['errors']:
            click.echo("\n❌ Errors:")
            for error in validation['errors']:
                click.echo(f"  - {error}")
        
        # Configuration validation
        try:
            config = get_config()
            click.echo("\n⚙️  Configuration: ✅ Valid")
            click.echo(f"  Workspace: {config.workspace_path}")
            click.echo(f"  Log Level: {config.log_level}")
            click.echo(f"  Agents Configured: {len(config.agents)}")
        except Exception as e:
            click.echo(f"\n⚙️  Configuration: ❌ Invalid - {e}")
        
        if validation['environment_valid']:
            click.echo("\n🎉 NEXUS is ready to use!")
        else:
            click.echo("\n⚠️  Please fix the errors before using NEXUS")
        
    except Exception as e:
        click.echo(f"❌ Validation failed: {e}")
        if ctx.obj.get('verbose'):
            import traceback
            click.echo(traceback.format_exc())


@nexus.command()
@click.option('--agent-id', help='Specific agent to message')
@click.option('--message', prompt='Message', help='Message to send')
@click.pass_context
def message(ctx, agent_id, message):
    """Send direct message to an agent"""
    
    async def send_message():
        try:
            config = get_config()
            orchestrator = NEXUSOrchestrator(config.workspace_path)
            
            await orchestrator.initialize_agents()
            
            if agent_id:
                if agent_id not in orchestrator.agents:
                    click.echo(f"❌ Agent '{agent_id}' not found")
                    click.echo(f"Available agents: {', '.join(orchestrator.agents.keys())}")
                    return
                
                click.echo(f"📤 Sending message to {agent_id}...")
                response = await orchestrator.delegate_to_agent(agent_id, {
                    "task": "direct_message",
                    "message": message
                })
                
                click.echo(f"\n📥 Response from {agent_id}:")
                click.echo(response)
            else:
                click.echo("Available agents:")
                for aid in orchestrator.agents.keys():
                    click.echo(f"  - {aid}")
                click.echo("\nUse --agent-id to specify which agent to message")
            
            await orchestrator.shutdown()
            
        except Exception as e:
            click.echo(f"❌ Error sending message: {e}")
            if ctx.obj.get('verbose'):
                import traceback
                click.echo(traceback.format_exc())
    
    asyncio.run(send_message())


@nexus.command()
@click.pass_context
def version(ctx):
    """Show NEXUS version information"""
    click.echo("🧬 NEXUS Multi-Agent Orchestrator")
    click.echo("Version: 1.0.0")
    click.echo("Revolutionary AI Collaboration Platform")
    click.echo("\nAgents:")
    click.echo("  🧭 Aria the Coordinator - Strategic planning and analysis")
    click.echo("  💻 Code the Developer - Implementation and coding")
    click.echo("  🧪 Alpha the Test Creator - Test strategy and creation")
    click.echo("  🛡️ Beta the Test Validator - Test execution and validation")


if __name__ == '__main__':
    nexus()