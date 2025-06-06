"""
Visual Integration Area - Integrates visual processing
"""

import logging
from typing import Dict, Any, Optional
from Mind.CorpusCallosum.synaptic_pathways import SynapticPathways
from config import CONFIG
from .primary_visual_area import PrimaryVisualArea
from .secondary_visual_area import SecondaryVisualArea
from .associative_visual_area import AssociativeVisualArea
from Mind.FrontalLobe.PrefrontalCortex.system_journeling_manager import SystemJournelingManager
import asyncio
from PIL import Image, ImageDraw
from .splash_screen import SplashScreenManager
import random

logger = logging.getLogger(__name__)

# Initialize journaling manager
journaling_manager = SystemJournelingManager()

class IntegrationArea:
    """Integrates visual processing"""
    
    def __init__(self):
        """Initialize the visual integration area"""
        journaling_manager.recordScope("[Visual Cortex] IntegrationArea.__init__")
        self._initialized = False
        self._processing = False
        self.primary_area = PrimaryVisualArea()
        self.secondary_area = SecondaryVisualArea()
        self.associative_area = AssociativeVisualArea()
        self.grid = [[0 for _ in range(64)] for _ in range(64)]  # Initialize empty grid
        self.is_running = False
        self.splash_manager = None
        
    async def initialize(self, primary_area=None, associative_area=None):
        """Initialize the visual integration area with primary and associative areas"""
        if self._initialized:
            return True
            
        success = True
        
        # Set primary area if provided
        if primary_area:
            self.primary_area = primary_area
            logger.info("Primary visual area set from parameter")
        
        # Set associative area if provided
        if associative_area:
            self.associative_area = associative_area
            logger.info("Associative visual area set from parameter")
            
        # Initialize associative area if available
        if self.associative_area:
            try:
                # Pass primary_area to associative_area
                await self.associative_area.initialize(primary_area=self.primary_area)
                logger.info("Associative visual area initialized")
            except Exception as e:
                logger.error(f"Failed to initialize associative visual area: {e}")
                success = False
                
        # Initialize splash screen manager
        try:
            self.splash_manager = SplashScreenManager(self.primary_area)
            await self.splash_manager.initialize(self.primary_area)
            logger.info("Splash screen manager initialized")
        except Exception as e:
            logger.error(f"Failed to initialize splash screen manager: {e}")
            # Not critical, can continue without splash screen
        
        self._initialized = success
        journaling_manager.recordInfo("Visual integration area initialized")
        return success
            
    async def process_visual(self, visual_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process visual input through all areas"""
        try:
            # Process through primary area first
            primary_result = await self.primary_area.process_visual(visual_data)
            
            # Then through secondary area
            secondary_result = await self.secondary_area.process_visual(primary_result)
            
            # Combine results
            return {
                "primary": primary_result,
                "secondary": secondary_result,
                "status": "ok"
            }
            
        except Exception as e:
            journaling_manager.recordError(f"Error processing visual input: {e}")
            return {"status": "error", "message": str(e)}
            
    async def process_command(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Process a visual command"""
        if not self._initialized:
            raise RuntimeError("Integration area not initialized")
            
        if self._processing:
            raise RuntimeError("Already processing a command")
            
        try:
            self._processing = True
            
            # Process command based on type
            command_type = command.get("type")
            if command_type == "DISPLAY":
                return await self._process_display(command)
            elif command_type == "SPLASH":
                return await self._process_splash(command)
            else:
                raise ValueError(f"Unknown command type: {command_type}")
                
        except Exception as e:
            journaling_manager.recordError(f"Error processing command: {e}")
            return {"status": "error", "message": str(e)}
            
        finally:
            self._processing = False
            
    async def _process_display(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Process display command"""
        try:
            content = command.get("content")
            if not content:
                raise ValueError("No content provided for display")
                
            # Process display command
            return {"status": "ok", "message": "Display updated"}
            
        except Exception as e:
            journaling_manager.recordError(f"Error processing display command: {e}")
            return {"status": "error", "message": str(e)}
            
    async def _process_splash(self, command: Dict[str, Any]) -> Dict[str, Any]:
        """Process splash screen command"""
        try:
            # Display splash screen using the associative visual area
            await self.show_splash_screen()
            return {"status": "ok", "message": "Splash screen displayed"}
            
        except Exception as e:
            journaling_manager.recordError(f"Error processing splash command: {e}")
            return {"status": "error", "message": str(e)}
            
    async def show_splash_screen(self):
        """Show a splash screen on the LED matrix"""
        if not self._initialized:
            logger.warning("Cannot show splash screen: visual integration area not initialized")
            return False
            
        # Use the splash screen manager if available
        if self.splash_manager:
            try:
                # Show the initial startup splash
                await self.splash_manager.show_startup_splash(duration=2.0)
                
                # Start the loading animation
                await self.splash_manager.start_loading_animation("Initializing systems...")
                
                # Simulate loading steps with progress updates
                loading_steps = [
                    (10, "Loading visual cortex..."),
                    (25, "Initializing LED matrix..."),
                    (40, "Connecting components..."),
                    (60, "Starting synaptic pathways..."),
                    (80, "Preparing neural networks..."),
                    (95, "Starting mind processes..."),
                    (100, "System ready")
                ]
                
                # Display each loading step with a delay
                for progress, text in loading_steps:
                    await self.splash_manager.update_loading_progress(progress, text)
                    await asyncio.sleep(0.5)  # Show each step for half a second
                
                # Wait a moment at 100%
                await asyncio.sleep(1.0)
                
                # Stop the animation and show completion screen
                await self.splash_manager.stop_loading_animation()
                await self.splash_manager.show_complete_splash(duration=2.0)
                
                return True
                
            except Exception as e:
                logger.error(f"Error showing splash screen sequence: {e}")
                # Fall back to simple splash screen
        
        # Try the associative area first
        if self.associative_area:
            try:
                # If we have an associative area, try to use it for fancy visuals
                logger.info("Showing splash screen via associative area...")
                # Create a simple rectangle for now
                image = Image.new("RGB", (64, 64), (0, 0, 32))  # Dark blue background
                draw = ImageDraw.Draw(image)
                
                # Draw text
                draw.text((15, 20), "PM", fill=(255, 255, 255))
                draw.text((7, 35), "PENPHIN", fill=(200, 200, 255))
                draw.text((7, 45), "MIND", fill=(128, 200, 255))
                
                # Use the associative area's display capabilities
                result = True  # Track if display successful
                
                try:
                    # Show rectangles animation
                    for i in range(10):
                        x = random.randint(0, 56)
                        y = random.randint(0, 56)
                        w = random.randint(4, 8)
                        h = random.randint(4, 8)
                        color = (random.randint(0, 255), random.randint(0, 255), random.randint(100, 255))
                        draw.rectangle((x, y, x+w, y+h), fill=color)
                        
                        if hasattr(self.primary_area, 'set_image'):
                            await self.primary_area.set_image(image)
                        await asyncio.sleep(0.2)
                except Exception as e:
                    logger.error(f"Error in splash animation: {e}")
                
                return result
                
            except Exception as e:
                logger.error(f"Failed to show splash via associative area: {e}")
        
        # Fallback - try to use primary area directly
        if self.primary_area:
            try:
                logger.info("Showing basic splash screen via primary area...")
                
                # Create a simple splash screen image
                image = Image.new("RGB", (64, 64), (0, 0, 32))  # Dark blue background
                draw = ImageDraw.Draw(image)
                draw.text((15, 20), "PM", fill=(255, 255, 255))
                draw.text((5, 35), "PenphinMind", fill=(128, 200, 255))
                
                # Display directly through primary area
                result = await self.primary_area.set_image(image)
                if result:
                    logger.info("Basic splash screen displayed successfully")
                    await asyncio.sleep(2.0)  # Show for 2 seconds
                else:
                    logger.error("Failed to display basic splash screen")
                
                return result
                
            except Exception as e:
                logger.error(f"Failed to show basic splash screen: {e}")
                
        logger.error("No display method available for splash screen")
        return False
        
    async def trigger_splash_event(self, event_name):
        """
        Trigger a splash screen event to update the loading progress.
        
        Args:
            event_name: Name of the event to trigger (must match events in config)
            
        Returns:
            bool: True if the event was handled, False otherwise
        """
        if not self._initialized or not self.splash_manager:
            logger.warning(f"Cannot trigger splash event {event_name}: IntegrationArea not fully initialized")
            return False
            
        try:
            result = await self.splash_manager.handle_event(event_name)
            if result:
                logger.info(f"Triggered splash screen event: {event_name}")
            else:
                logger.warning(f"Unknown splash screen event: {event_name}")
            return result
        except Exception as e:
            logger.error(f"Error triggering splash event {event_name}: {e}")
            return False
            
    async def set_background(self, r: int, g: int, b: int) -> None:
        """Set the LED matrix background color"""
        try:
            await SynapticPathways.send_system_command(
                command_type="set_background",
                data={"r": r, "g": g, "b": b}
            )
        except Exception as e:
            raise Exception(f"Error setting background: {e}")
            
    async def clear(self) -> None:
        """Clear the LED matrix"""
        try:
            await SynapticPathways.send_system_command(
                command_type="clear_matrix"
            )
        except Exception as e:
            raise Exception(f"Error clearing matrix: {e}")
            
    async def set_brightness(self, brightness: int) -> None:
        """
        Set LED matrix brightness
        
        Args:
            brightness: Brightness level (0-100)
        """
        try:
            brightness = max(0, min(100, brightness))
            await SynapticPathways.send_system_command(
                command_type="set_brightness",
                data={"brightness": brightness}
            )
        except Exception as e:
            raise Exception(f"Error setting brightness: {e}")
            
    async def draw_pixel(self, x: int, y: int, r: int, g: int, b: int) -> None:
        """
        Draw a single pixel on the LED matrix
        
        Args:
            x: X coordinate
            y: Y coordinate
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
        """
        try:
            await SynapticPathways.send_system_command(
                command_type="draw_pixel",
                data={
                    "x": x,
                    "y": y,
                    "r": r,
                    "g": g,
                    "b": b
                }
            )
        except Exception as e:
            raise Exception(f"Error drawing pixel: {e}")
            
    async def draw_circle(self, x: int, y: int, radius: int, r: int, g: int, b: int) -> None:
        """
        Draw a circle on the LED matrix
        
        Args:
            x: Center X coordinate
            y: Center Y coordinate
            radius: Circle radius
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
        """
        try:
            await SynapticPathways.send_system_command(
                command_type="draw_circle",
                data={
                    "x": x,
                    "y": y,
                    "radius": radius,
                    "r": r,
                    "g": g,
                    "b": b
                }
            )
        except Exception as e:
            raise Exception(f"Error drawing circle: {e}")
            
    async def draw_line(self, x1: int, y1: int, x2: int, y2: int, r: int, g: int, b: int) -> None:
        """
        Draw a line on the LED matrix
        
        Args:
            x1: Start X coordinate
            y1: Start Y coordinate
            x2: End X coordinate
            y2: End Y coordinate
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
        """
        try:
            await SynapticPathways.send_system_command(
                command_type="draw_line",
                data={
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "r": r,
                    "g": g,
                    "b": b
                }
            )
        except Exception as e:
            raise Exception(f"Error drawing line: {e}")
            
    async def draw_text(self, x: int, y: int, text: str, r: int, g: int, b: int) -> None:
        """
        Draw text on the LED matrix
        
        Args:
            x: Starting X coordinate
            y: Starting Y coordinate
            text: Text to draw
            r: Red component (0-255)
            g: Green component (0-255)
            b: Blue component (0-255)
        """
        try:
            await SynapticPathways.send_system_command(
                command_type="draw_text",
                data={
                    "x": x,
                    "y": y,
                    "text": text,
                    "r": r,
                    "g": g,
                    "b": b
                }
            )
        except Exception as e:
            raise Exception(f"Error drawing text: {e}")
            
    async def create_sprite(self, width: int, height: int) -> Dict[str, Any]:
        """
        Create a sprite for animation
        
        Args:
            width: Sprite width
            height: Sprite height
            
        Returns:
            Dict containing sprite data and metadata
        """
        try:
            response = await SynapticPathways.send_system_command(
                command_type="create_sprite",
                data={
                    "width": width,
                    "height": height
                }
            )
            sprite_id = response.get("sprite_id")
            if sprite_id:
                self._sprite_cache[sprite_id] = response
            return response
        except Exception as e:
            raise Exception(f"Error creating sprite: {e}")
            
    async def draw_sprite(self, sprite_id: str, x: int, y: int) -> None:
        """
        Draw a sprite at the specified position
        
        Args:
            sprite_id: ID of the sprite to draw
            x: X coordinate
            y: Y coordinate
        """
        try:
            if sprite_id not in self._sprite_cache:
                raise Exception(f"Sprite {sprite_id} not found")
                
            await SynapticPathways.send_system_command(
                command_type="draw_sprite",
                data={
                    "sprite_id": sprite_id,
                    "x": x,
                    "y": y
                }
            )
        except Exception as e:
            raise Exception(f"Error drawing sprite: {e}")
            
    async def update_sprite(self, sprite_id: str, frame_data: bytes) -> None:
        """
        Update sprite frame data
        
        Args:
            sprite_id: ID of the sprite to update
            frame_data: New frame data
        """
        try:
            if sprite_id not in self._sprite_cache:
                raise Exception(f"Sprite {sprite_id} not found")
                
            await SynapticPathways.send_system_command(
                command_type="update_sprite",
                data={
                    "sprite_id": sprite_id,
                    "frame_data": frame_data
                }
            )
        except Exception as e:
            raise Exception(f"Error updating sprite: {e}")
            
    async def delete_sprite(self, sprite_id: str) -> None:
        """
        Delete a sprite
        
        Args:
            sprite_id: ID of the sprite to delete
        """
        try:
            if sprite_id in self._sprite_cache:
                await SynapticPathways.send_system_command(
                    command_type="delete_sprite",
                    data={"sprite_id": sprite_id}
                )
                del self._sprite_cache[sprite_id]
        except Exception as e:
            raise Exception(f"Error deleting sprite: {e}")
            
    async def start_animation(self, sprite_id: str, fps: Optional[int] = None) -> None:
        """
        Start sprite animation
        
        Args:
            sprite_id: ID of the sprite to animate
            fps: Optional frames per second (defaults to config)
        """
        try:
            if sprite_id not in self._sprite_cache:
                raise Exception(f"Sprite {sprite_id} not found")
                
            await SynapticPathways.send_system_command(
                command_type="start_animation",
                data={
                    "sprite_id": sprite_id,
                    "fps": fps or CONFIG.visual_animation_fps
                }
            )
        except Exception as e:
            raise Exception(f"Error starting animation: {e}")
            
    async def stop_animation(self, sprite_id: str) -> None:
        """
        Stop sprite animation
        
        Args:
            sprite_id: ID of the sprite to stop
        """
        try:
            if sprite_id not in self._sprite_cache:
                raise Exception(f"Sprite {sprite_id} not found")
                
            await SynapticPathways.send_system_command(
                command_type="stop_animation",
                data={"sprite_id": sprite_id}
            )
        except Exception as e:
            raise Exception(f"Error stopping animation: {e}")
            
    async def process_visual_input(self, image_data: bytes) -> Dict[str, Any]:
        """Process visual input data"""
        try:
            # Process basic features
            basic_features = await self.primary_area.process_raw_visual(image_data)
            
            # Process complex features
            complex_features = await self.secondary_area.analyze_complex_features(image_data)
            
            return {
                "basic_features": basic_features,
                "complex_features": complex_features,
                "status": "ok"
            }
        except Exception as e:
            journaling_manager.recordError(f"Error processing visual input: {e}")
            return {"status": "error", "message": str(e)}
            
    async def cleanup(self) -> None:
        """Clean up resources"""
        try:
            self._initialized = False
            journaling_manager.recordInfo("Visual integration area cleaned up")
            
        except Exception as e:
            journaling_manager.recordError(f"Error cleaning up visual integration area: {e}")
            raise

    async def update_cell(self, x: int, y: int, state: int) -> None:
        """
        Update a single cell in the grid
        
        Args:
            x: X coordinate (0-63)
            y: Y coordinate (0-63)
            state: Cell state (0 or 1)
        """
        journaling_manager.recordScope("[Visual Cortex] update_cell", x=x, y=y, state=state)
        try:
            if 0 <= x < 64 and 0 <= y < 64 and state in (0, 1):
                self.grid[y][x] = state
                journaling_manager.recordDebug(f"Updated cell at ({x}, {y}) to {state}")
            else:
                journaling_manager.recordError(f"Invalid cell update parameters: x={x}, y={y}, state={state}")
                
        except Exception as e:
            journaling_manager.recordError(f"Error updating cell: {e}")
            raise

    async def update_region(self, x: int, y: int, region: list[list[int]]) -> None:
        """
        Update a rectangular region of the grid
        
        Args:
            x: Starting X coordinate
            y: Starting Y coordinate
            region: 2D list of cell states (0s and 1s)
        """
        journaling_manager.recordScope("[Visual Cortex] update_region", x=x, y=y, region_size=f"{len(region)}x{len(region[0])}")
        try:
            height = len(region)
            width = len(region[0])
            
            for dy in range(height):
                for dx in range(width):
                    grid_x = x + dx
                    grid_y = y + dy
                    if 0 <= grid_x < 64 and 0 <= grid_y < 64:
                        self.grid[grid_y][grid_x] = region[dy][dx]
                        
            journaling_manager.recordDebug(f"Updated region at ({x}, {y}) with size {width}x{height}")
            
        except Exception as e:
            journaling_manager.recordError(f"Error updating region: {e}")
            raise

    async def set_grid(self, new_grid: list[list[int]]) -> None:
        """
        Replace the entire grid
        
        Args:
            new_grid: New 64x64 grid of cell states
        """
        journaling_manager.recordScope("[Visual Cortex] set_grid")
        try:
            if len(new_grid) == 64 and all(len(row) == 64 for row in new_grid):
                self.grid = [row[:] for row in new_grid]  # Deep copy
                journaling_manager.recordDebug("Grid replaced successfully")
            else:
                journaling_manager.recordError("Invalid grid dimensions")
                raise ValueError("Grid must be 64x64")
                
        except Exception as e:
            journaling_manager.recordError(f"Error setting grid: {e}")
            raise

    async def run_game_of_life(self):
        """Run the Game of Life simulation"""
        journaling_manager.recordScope("[Visual Cortex] run_game_of_life")
        try:
            self.is_running = True
            while self.is_running:
                # Create image from current grid state
                image = Image.new("RGB", (64, 64))
                pixels = image.load()
                
                for y in range(64):
                    for x in range(64):
                        if self.grid[y][x]:
                            # Calculate neighbors for color
                            neighbors = sum(
                                self.grid[(y + dy) % 64][(x + dx) % 64]
                                for dy in [-1, 0, 1]
                                for dx in [-1, 0, 1]
                                if not (dx == 0 and dy == 0)
                            )
                            color = (0, min(255, neighbors * 40), 255 - neighbors * 20)
                            pixels[x, y] = color
                
                # Display current state
                await self.primary_area.set_image(image)
                
                # Update grid for next generation
                new_grid = [[0]*64 for _ in range(64)]
                for y in range(64):
                    for x in range(64):
                        neighbors = sum(
                            self.grid[(y + dy) % 64][(x + dx) % 64]
                            for dy in [-1, 0, 1]
                            for dx in [-1, 0, 1]
                            if not (dx == 0 and dy == 0)
                        )
                        if self.grid[y][x]:
                            new_grid[y][x] = 1 if neighbors in [2, 3] else 0
                        else:
                            new_grid[y][x] = 1 if neighbors == 3 else 0
                
                self.grid = new_grid
                await asyncio.sleep(0.1)
                
        except Exception as e:
            journaling_manager.recordError(f"Error in game of life: {e}")
            raise
        finally:
            self.is_running = False
            await self.primary_area.clear()

    async def stop_game(self) -> None:
        """Stop the Game of Life simulation"""
        journaling_manager.recordScope("[Visual Cortex] stop_game")
        self.is_running = False
        journaling_manager.recordInfo("Game of Life stopped") 