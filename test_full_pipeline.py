"""
Full Pipeline Test - Content to Video

Tests the complete flow:
Content → AI Script → TTS Audio → Video Assembly → Database Save
"""

import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent / "backend"
sys.path.insert(0, str(backend_path))

from dotenv import load_dotenv
load_dotenv()

import asyncio
from app.core.config import load_config, get_settings
from app.core.logger import setup_logging, log_step, log_success, show_config_summary, console
from app.core.plugin_loader import PluginLoader
from rich.panel import Panel
from rich.table import Table
import time


async def main():
    """Run full pipeline test."""
    
    # Setup
    config = load_config("config.yaml")
    setup_logging(level="INFO", colorize=True)
    
    # Welcome
    console.print(Panel.fit(
        "[bold cyan]Mission Alpha - Full Pipeline Test[/bold cyan]\n"
        "[dim]Content → AI → TTS → VIDEO → Database[/dim]",
        border_style="cyan"
    ))
    
    console.print()
    
    # Show what's running
    show_config_summary({
        'content': {'provider': config.content.provider},
        'ai': {'provider': config.ai.provider, 'model': config.ai.model},
        'tts': {'provider': config.tts.provider},
        'video': {'provider': config.video.provider},
        'database': {'provider': config.database.provider},
    })
    
    console.print("\n[bold green]🚀 Running Full Pipeline...[/bold green]\n")
    
    start_time = time.time()
    
    # Step 1: Content
    log_step("1️⃣ Fetching Content")
    content_provider = PluginLoader.load('content')
    items = await content_provider.fetch_content(limit=1)
    
    if not items:
        console.print("[red]✗ No content fetched![/red]")
        return
    
    content = items[0]
    log_success(f"✓ Got content: {content.title[:50]}...")
    
    # Step 2: AI Script (with fallback!)
    log_step("2️⃣ Generating AI Script (with fallback)")
    from app.core.ai_fallback import get_ai_provider
    ai_provider = get_ai_provider()  # Uses fallback wrapper
    script_result = await ai_provider.generate_script(content)
    log_success(f"✓ Script generated ({len(script_result.full_script)} chars)")
    console.print(f"\n[dim]Hook: {script_result.hook[:80]}...[/dim]\n")
    
    # Step 3: TTS Audio
    log_step("3️⃣ Creating Audio")
    tts_provider = PluginLoader.load('tts')
    audio_file = await tts_provider.text_to_speech(script_result.full_script)
    log_success(f"✓ Audio created: {audio_file.duration:.1f}s")
    console.print(f"[dim]  📁 {audio_file.path}[/dim]\n")
    
    # Step 4: VIDEO Assembly
    log_step("4️⃣ Assembling Video")
    video_provider = PluginLoader.load('video')
    video_file = await video_provider.assemble_video(
        audio_path=audio_file.path,
        script=script_result.full_script
    )
    log_success(f"✓ Video created: {video_file.duration:.1f}s ({video_file.metadata.get('resolution')})")
    console.print(f"[dim]  📁 {video_file.path}[/dim]")
    console.print(f"[dim]  💾 Size: {video_file.metadata.get('size_mb', 0):.2f} MB[/dim]\n")
    
    # Step 5: Database
    log_step("5️⃣ Saving to Database")
    db_provider = PluginLoader.load('database')
    
    video_data = {
        "id": f"video_{int(time.time())}",
        "content_title": content.title[:100],
        "script_hook": script_result.hook,
        "audio_path": audio_file.path,
        "video_path": video_file.path,
        "duration": video_file.duration,
        "resolution": video_file.metadata.get('resolution'),
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    
    record_id = await db_provider.insert('videos', video_data)
    log_success(f"✓ Saved to database: {record_id}")
    
    # Summary
    total_time = time.time() - start_time
    
    console.print("\n" + "="*70)
    console.print(Panel.fit(
        f"[bold green]✅ FULL PIPELINE COMPLETE![/bold green]\n\n"
        f"[cyan]Results:[/cyan]\n"
        f"  • Content: {content.type}\n"
        f"  • Script: {len(script_result.full_script)} characters\n"
        f"  • Audio: {audio_file.duration:.1f}s\n"
        f"  • Video: {video_file.duration:.1f}s @ {video_file.metadata.get('resolution')}\n"
        f"  • File: {Path(video_file.path).name}\n"
        f"  • Size: {video_file.metadata.get('size_mb', 0):.2f} MB\n\n"
        f"[yellow]Total time: {total_time:.1f}s[/yellow]\n\n"
        f"[dim]🎬 Video ready to watch at:[/dim]\n"
        f"[cyan]{video_file.path}[/cyan]",
        title="[green]Success![/green]",
        border_style="green"
    ))
    
    # Performance breakdown
    console.print("\n[bold]📊 Performance Breakdown:[/bold]")
    table = Table(show_header=True)
    table.add_column("Step", style="cyan")
    table.add_column("Provider", style="yellow")
    table.add_column("Output", style="green")
    
    table.add_row("1. Content", config.content.provider, f"{len(items)} items")
    table.add_row("2. AI Script", f"{config.ai.provider} ({config.ai.model})", f"{len(script_result.full_script)} chars")
    table.add_row("3. TTS Audio", config.tts.provider, f"{audio_file.duration:.1f}s")
    table.add_row("4. Video", config.video.provider, f"{video_file.metadata.get('size_mb', 0):.2f} MB")
    table.add_row("5. Database", config.database.provider, "Saved")
    
    console.print(table)
    console.print()


if __name__ == "__main__":
    asyncio.run(main())
