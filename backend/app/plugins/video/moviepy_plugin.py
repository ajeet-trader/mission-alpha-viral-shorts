"""
MoviePy Video Provider

Assembles video with audio, background, and captions.
"""

# MoviePy 2.x imports
from moviepy import VideoFileClip, AudioFileClip, TextClip, CompositeVideoClip, ColorClip, ImageClip
from pathlib import Path
import os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from app.core.interfaces import IVideoProvider, MediaFile
from app.core.logger import log_step, log_success, step_progress, console
import logging

logger = logging.getLogger(__name__)


class MoviePyProvider(IVideoProvider):
    """MoviePy-based video assembly with gradients and captions."""
    
    def __init__(self, config):
        self.config = config
        self.output_dir = Path("output/videos")
        self.output_dir.mkdir(parents=True, exist_ok=True)
        log_success("MoviePy provider initialized")
    
    def _create_gradient_background(self, width, height, duration):
        """Create attractive gradient background."""
        # Create gradient image
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Gradient colors (dark blue to purple)
        color1 = (25, 25, 60)   # Dark blue
        color2 = (60, 25, 60)   # Purple
        
        for y in range(height):
            # Calculate interpolation
            ratio = y / height
            r = int(color1[0] * (1 - ratio) + color2[0] * ratio)
            g = int(color1[1] * (1 - ratio) + color2[1] * ratio)
            b = int(color1[2] * (1 - ratio) + color2[2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # Add subtle noise for texture
        pixels = np.array(img)
        noise = np.random.randint(-10, 10, pixels.shape, dtype=np.int16)
        pixels = np.clip(pixels.astype(np.int16) + noise, 0, 255).astype(np.uint8)
        img = Image.fromarray(pixels)
        
        # Save temporarily
        temp_path = self.output_dir / "temp_gradient.png"
        img.save(str(temp_path))
        
       # Create video clip from image
        clip = ImageClip(str(temp_path)).with_duration(duration)
        
        return clip
    
    def _create_caption_clip(self, text, width, height, duration, start_time=0):
        """Create styled caption with better formatting."""
        try:
            # Split text into chunks for better display
            words_per_line = 6
            words = text.split()
            lines = []
            for i in range(0, len(words), words_per_line):
                lines.append(' '.join(words[i:i+words_per_line]))
            
            caption_text = '\n'.join(lines[:4])  # Max 4 lines
            
            # Create text clip with styling
            txt_clip = TextClip(
                caption_text,
                font_size=self.config.captions.font_size,
                color=self.config.captions.color,
                stroke_color=self.config.captions.stroke_color,
                stroke_width=self.config.captions.stroke_width,
                size=(int(width * 0.85), None),
                method='caption'
            )
            
            # Position and timing
            txt_clip = txt_clip.with_position(('center', 'center'))
            txt_clip = txt_clip.with_start(start_time).with_duration(min(duration - start_time, 5))
            
            return txt_clip
        except Exception as e:
            logger.warning(f"Could not create caption: {e}")
            return None
    
    async def assemble_video(
        self,
        audio_path: str,
        script: str,
        background_url: str = None,
        output_path: str = None
    ) -> MediaFile:
        """Assemble final video with real backgrounds."""
        log_step("🎬 Assembling video with MoviePy", f"Duration: checking audio...")
        
        try:
            with step_progress("Loading audio..."):
                audio = AudioFileClip(audio_path)
                duration = audio.duration
                console.print(f"  Audio duration: {duration:.1f}s")
            
            w, h = map(int, self.config.resolution.split('x'))
            
            # Try to get Pexels background video
            background = None
            with step_progress("Fetching background video..."):
                try:
                    print("[DEBUG] Loading pexels_backgrounds module...")
                    from app.plugins.video.pexels_backgrounds import get_pexels_provider
                    
                    print("[DEBUG] Getting pexels provider...")
                    pexels = get_pexels_provider()
                    print(f"[DEBUG] Pexels provider ready, API key: {'SET' if pexels.api_key else 'NOT SET'}")
                    
                    if not pexels.api_key:
                        print("[DEBUG] No Pexels API key - skipping to gradient")
                        raise Exception("No PEXELS_API_KEY")
                    
                    # Request short videos (will be looped)
                    print("[DEBUG] Fetching video from Pexels...")
                    video_path = await pexels.fetch_video(
                        query=None,  # Random category
                        duration_min=5,  # Accept 5+ second videos, will loop
                        orientation="portrait"
                    )
                    
                    print(f"[DEBUG] Pexels returned: {video_path}")
                    
                    if video_path:
                        print(f"[DEBUG] Loading video clip: {video_path}")
                        bg_clip = VideoFileClip(video_path)
                        print(f"[DEBUG] Video loaded: {bg_clip.w}x{bg_clip.h}, {bg_clip.duration:.1f}s")
                        
                        # Loop if needed
                        if bg_clip.duration < duration:
                            from moviepy import concatenate_videoclips
                            loops_needed = int(duration / bg_clip.duration) + 1
                            print(f"[DEBUG] Looping {loops_needed}x to cover {duration:.1f}s")
                            bg_clip = concatenate_videoclips([bg_clip] * loops_needed)
                        
                        bg_clip = bg_clip.subclipped(0, duration)
                        bg_clip = bg_clip.resized(height=h)
                        print(f"[DEBUG] Resized to height={h}")
                        
                        # Center crop to fit width
                        if bg_clip.w > w:
                            x_center = bg_clip.w // 2
                            bg_clip = bg_clip.cropped(x1=x_center - w//2, x2=x_center + w//2)
                            print(f"[DEBUG] Cropped to width={w}")
                        
                        background = bg_clip
                        console.print(f"  [green]✓ Using Pexels background video[/green]")
                        print("[DEBUG] SUCCESS - Pexels background assigned!")
                    else:
                        print("[DEBUG] video_path is None - Pexels fetch failed")
                        console.print(f"  [yellow]No Pexels video returned[/yellow]")
                        
                except Exception as e:
                    print(f"[DEBUG] EXCEPTION in Pexels: {type(e).__name__}: {e}")
                    console.print(f"  [red]Pexels error: {e}[/red]")
                    logger.warning(f"Pexels failed, using gradient: {e}")
            
            # Fallback to gradient
            if background is None:
                with step_progress("Creating gradient background..."):
                    background = self._create_gradient_background(w, h, duration)
                    console.print(f"  [yellow]Using gradient background[/yellow]")
            
            clips = [background]
            
            with step_progress("Adding captions..."):
                if self.config.captions.enabled and script:
                    # Add caption for first part of script
                    caption = self._create_caption_clip(script, w, h, duration, start_time=0.5)
                    if caption:
                        clips.append(caption)
            
            with step_progress("Compositing final video..."):
                video = CompositeVideoClip(clips, size=(w, h))
                video = video.with_audio(audio)
                video = video.with_duration(duration)
            
            # Output path
            if not output_path:
                import hashlib
                import time
                timestamp = int(time.time())
                video_hash = hashlib.md5(script.encode()).hexdigest()[:8]
                output_path = str(self.output_dir / f"short_{timestamp}_{video_hash}.mp4")
            
            with step_progress(f"Exporting video to {Path(output_path).name}..."):
                video.write_videofile(
                    output_path,
                    fps=self.config.fps,
                    codec='libx264',
                    audio_codec='aac',
                    preset='ultrafast',  # Changed from 'medium' for speed
                    threads=2,  # Reduced from 4 to avoid CPU overload
                    logger='bar'  # Show progress bar instead of None
                )
            
            # Clean up temp files
            temp_gradient = self.output_dir / "temp_gradient.png"
            if temp_gradient.exists():
                temp_gradient.unlink()
            
            # Close clips
            audio.close()
            video.close()
            
            log_success(f"✓ Video created: {duration:.1f}s ({self.config.resolution})")
            console.print(f"  📁 Saved to: {output_path}")
            
            return MediaFile(
                path=output_path,
                duration=duration,
                provider="moviepy",
                metadata={
                    "resolution": self.config.resolution,
                    "fps": self.config.fps,
                    "captions": self.config.captions.enabled,
                    "size_mb": Path(output_path).stat().st_size / (1024 * 1024)
                }
            )
            
        except Exception as e:
            logger.error(f"Video assembly failed: {e}")
            raise
    
    def get_provider_name(self) -> str:
        return "MoviePy (Gradient + Captions)"
