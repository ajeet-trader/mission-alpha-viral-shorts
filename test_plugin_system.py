"""
Demo Script - Test Plugin Swapping

This script demonstrates the power of the plugin architecture.
Change config.yaml and watch different providers load automatically!
"""

import sys
from pathlib import Path

# Add backend to path so we can import app
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv()

import asyncio
from app.core.config import load_config, get_settings
from app.core.logger import setup_logging, log_step, log_success, show_config_summary, console
from app.core.plugin_loader import PluginLoader
from rich.panel import Panel


async def main():
    """Test the plugin system with current config."""
    
    # Load config
    config = load_config("config.yaml")
    setup_logging(level=config.logging.level, colorize=config.logging.colorize)
    
    # Show welcome
    console.print(Panel.fit(
        "[bold cyan]Mission Alpha v2.0[/bold cyan]\n"
        "[dim]Modular Plugin Architecture Demo[/dim]",
        border_style="cyan"
    ))
    
    # Show active configuration
    show_config_summary({
        'content': {'provider': config.content.provider},
        'ai': {'provider': config.ai.provider},
        'tts': {'provider': config.tts.provider},
        'video': {'provider': config.video.provider},
        'upload': {'provider': config.upload.provider},
        'database': {'provider': config.database.provider},
    })
    
    console.print("\n[bold green]🔌 Testing Plugin Loading...[/bold green]\n")
    
    # Test loading each provider type
    try:
        # 1. Content Provider
        log_step("Loading Content Provider")
        content_provider = PluginLoader.load('content')
        items = await content_provider.fetch_content(limit=2)
        log_success(f"Fetched {len(items)} content items")
        
        if items:
            console.print(f"\n[dim]Sample: {items[0].title[:60]}...[/dim]")
        
        # 2. AI Provider
        log_step("\nLoading AI Provider")
        ai_provider = PluginLoader.load('ai')
        
        if items:
            script = await ai_provider.generate_script(items[0])
            log_success(f"Generated script with {ai_provider.get_provider_name()}")
            console.print(f"\n[dim]Hook: {script.hook[:80]}...[/dim]")
        
        # 3. TTS Provider
        log_step("\nLoading TTS Provider")
        tts_provider = PluginLoader.load('tts')
        
        if items:
            audio = await tts_provider.text_to_speech(script.hook[:100])
            log_success(f"Generated {audio.duration:.1f}s audio")
        
        # 4. Database Provider
        log_step("\nLoading Database Provider")
        db_provider = PluginLoader.load('database')
        
        # Test insert
        test_data = {
            'id': 'test_001',
            'type': 'story',
            'title': 'Test Content',
            'body': 'Testing database provider',
            'source': 'test',
            'score': 75.0,
            'created_at': '2024-12-25'
        }
        
        record_id = await db_provider.insert('content', test_data)
        log_success(f"Inserted record: {record_id}")
        
        # Success summary
        console.print("\n" + "="*60)
        console.print(Panel.fit(
            "[bold green]✓ All Providers Working![/bold green]\n\n"
            f"Content: {config.content.provider}\n"
            f"AI: {config.ai.provider}\n"
            f"TTS: {config.tts.provider}\n"
            f"Database: {config.database.provider}\n\n"
            "[dim]Change config.yaml to swap providers![/dim]",
            title="[green]Success[/green]",
            border_style="green"
        ))
        
        console.print("\n[bold cyan]💡 Try This:[/bold cyan]")
        console.print("1. Edit config.yaml")
        console.print("2. Change ai.provider from 'langchain' to 'crewai'")
        console.print("3. Run this script again")
        console.print("4. Watch multi-agent CrewAI load automatically!\n")
        
    except Exception as e:
        console.print(f"\n[bold red]Error: {str(e)}[/bold red]")
        raise


if __name__ == "__main__":
    asyncio.run(main())
