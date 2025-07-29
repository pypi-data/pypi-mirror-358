# devices/base.py
import asyncio
from typing import Optional, List, Dict, Any
import copy
from .subdevice import SubDevice
from ..utils.logger import logger
from .middlewares.brainflow import BrainflowInterface
from ..utils.shared_state import SharedState
from .middlewares.synthetic import SyntheticInterface

class Device:
    def __init__(self, topic: Optional[str] = None):
        self.shared_state = SharedState.get_instance()
        self.subdevices: List[SubDevice] = []
        
        self.topic = topic
        self.selected_middleware = self.shared_state.get(f"Devices.{topic}.SelectedMiddleware")
        device_metadata = self.shared_state.get(f"Devices.{topic}", {})
        # Process device data to keep only selected middleware and flatten structure
        self.device_metadata = self._process_device_metadata(device_metadata, self.selected_middleware)
        self.device_name = self.device_metadata.get("ManufacturerModelName")
        self.device_serial_number = self.device_metadata.get("DeviceSerialNumber")
        self.epoch_length = self.device_metadata.get("EpochLength", 0)
        self.device_manager = None  # Will be set by DeviceManager when created
        self.middleware = None # Will be set by setup()

    async def setup(self):
        if self.selected_middleware:
            # Dynamically create middleware instance based on name
            middleware_class = self._get_middleware_class(self.selected_middleware)
            if middleware_class:
                self.middleware = middleware_class(self)
                # Get subdevices from the metadata
                subdev_dict = self.device_metadata.get("SubDevices", {})
                for subdev_name, subdev_conf in subdev_dict.items():
                    sd = SubDevice(parent_device=self, name=subdev_name, config=subdev_conf)
                    self.subdevices.append(sd)
            else:
                logger.error(f"Middleware '{self.selected_middleware}' is not implemented.")

    async def connect(self):
        """Prepare the device session (e.g. BrainFlow prepare_session)."""
        logger.info(f"Connecting device '{self.device_name}_{self.device_serial_number}'...")
        if self.middleware:
            await self.middleware.prepare()
        else:
            logger.warning(f"No middleware for device '{self.device_name}_{self.device_serial_number}', skipping connection.")
        self.shared_state.set(f"Devices.{self.topic}.DeviceStatus", "CONNECTED")
        return self
            
    async def disconnect(self):
        """Close the device session and stop all subdevices."""
        logger.info(f"Disconnecting device '{self.device_name}_{self.device_serial_number}'...")
        
        # Stop the middleware first (e.g., stop BrainFlow stream)
        if self.middleware:
            try:
                 await self.middleware.stop_stream()
                 self.shared_state.set(f"Devices.{self.topic}.DeviceStatus", "DISCONNECTED")
                 logger.debug(f"Middleware stopped for device '{self.device_name}'")
            except Exception as e:
                 logger.error(f"Error stopping middleware for {self.device_name}: {e}")

        # Release the middleware session (e.g., BrainFlow release_session)
        if self.middleware and hasattr(self.middleware, 'release_session'):
             try:
                  await self.middleware.release_session()
                  logger.debug(f"Middleware session released for device '{self.device_name}'")
             except Exception as e:
                  logger.error(f"Error releasing middleware session for {self.device_name}: {e}")
        elif not self.middleware:
             logger.debug(f"No middleware found for device '{self.device_name}', cannot release session.")
            
        # Explicitly stop all subdevices to close their publishers
        logger.debug(f"Stopping {len(self.subdevices)} subdevices for {self.device_name}...")
        for sd in self.subdevices:
            try:
                sd.stop() # This should call publisher.close()
            except Exception as e:
                logger.error(f"Error stopping subdevice {sd.name}: {e}")
                
        logger.info(f"Disconnected device '{self.device_name}'")
        return self

    async def start_stream(self):
        """
        Begin streaming for this device and all subdevices.
        Waits for the stream to complete (either by finite duration or middleware termination)
        and ensures disconnection afterwards.
        """
            
        # Check middleware
        if not self.middleware:
            logger.error(f"No middleware for '{self.device_name}_{self.device_serial_number}', skipping stream start.")
            return

        # Ensure metadata responder is started when streaming begins
        if self.device_manager and hasattr(self.device_manager, 'ensure_metadata_responder_started'):
            await self.device_manager.ensure_metadata_responder_started()

        # Set topic and initialize publishers for subdevices
        control_enabled = self.shared_state.get("Orcustrator.ExternalController", False)
        for sd in self.subdevices:
            sd.set_topic(self.topic)

        # Start command listeners *after* publishers are created by set_topic
        if control_enabled:
            logger.info(f"[{self.device_name}] External control enabled. Starting command listeners for subdevice publishers...")
            listener_tasks = []
            for sd in self.subdevices:
                if hasattr(sd, 'publisher') and sd.publisher:
                    # Start listener and store task if needed (though publisher manages its own task)
                    listener_tasks.append(asyncio.create_task(sd.publisher.start_command_listener()))
                else:
                    logger.warning(f"[{self.device_name}] Subdevice {sd.name} has no publisher, cannot start command listener.")
            # Optionally wait briefly for listeners to connect? Or assume connection is fast.
            # await asyncio.gather(*listener_tasks) # Don't wait here, let them run in background

        # Get current stream duration from shared state
        stream_duration = self.shared_state.get("StreamDuration", float('inf'))
        duration_str = f"{stream_duration}s" if stream_duration != float('inf') else 'infinite'
        logger.info(f"Starting stream for device '{self.device_name}' on topic '{self.topic}' (duration: {duration_str}, buffer: {self.epoch_length})")

        try:
            # Start the middleware's streaming (which typically creates a background read task)
            await self.middleware.start_stream()

            # Wait for the stream to complete
            read_task = getattr(self.middleware, 'read_task', None)
            if not read_task:
                 logger.error(f"Middleware {self.selected_middleware} did not create a 'read_task'. Cannot monitor stream completion.")
                 # Proceed to finally block for immediate disconnect
                 return 
            
            wait_tasks = [read_task]
            sleep_task = None

            if stream_duration != float('inf'):
                 logger.info(f"Waiting for stream duration ({stream_duration}s) OR read task completion.")
                 sleep_task = asyncio.create_task(asyncio.sleep(stream_duration), name=f"{self.device_name}_sleep")
                 wait_tasks.append(sleep_task)
            else:
                 logger.info(f"Waiting indefinitely for middleware read task completion.")
                 
            # Wait for the first task to complete (either read_task finishes or sleep_task finishes)
            done, pending = await asyncio.wait(wait_tasks, return_when=asyncio.FIRST_COMPLETED)
            
            # --- Determine why we stopped waiting --- 
            completed_task = done.pop() # Get the task that finished
            logger.debug(f"[{self.device_name}] First task completed: {completed_task.get_name()}")

            # --- Clean up pending tasks --- 
            for task in pending:
                 logger.debug(f"[{self.device_name}] Cancelling pending task: {task.get_name()}")
                 task.cancel()
                 try:
                      await task # Allow cancellation to propagate
                 except asyncio.CancelledError:
                      pass # Expected
            
            # Log state of the completed read_task if it was the one that finished first
            if completed_task is read_task:
                 task_state = f"Done={read_task.done()}, Cancelled={read_task.cancelled()}, Exc={read_task.exception()}"
                 logger.debug(f"[{self.device_name}] read_task completed. State: {task_state}")
            elif sleep_task and completed_task is sleep_task:
                 logger.info(f"[{self.device_name}] Finite stream duration ({stream_duration}s) completed.")
                 # read_task was cancelled in the pending loop above

        except asyncio.CancelledError:
            logger.info(f"Stream task for {self.device_name} cancelled.")
            # Cancellation is handled by the finally block
            raise # Re-raise cancellation
        except Exception as e:
            logger.error(f"Error during streaming for device '{self.device_name}': {e}", exc_info=True)
            # Error is handled by the finally block
        finally:
            # DEBUG: Use critical level to ensure visibility
            logger.critical(f"[{self.device_name}] ENTERING finally block in start_stream")
            logger.info(f"Stream ended or was interrupted for device '{self.device_name}'. Initiating disconnect...")
            await self.disconnect() # Ensure disconnect happens reliably
            logger.critical(f"[{self.device_name}] EXITED finally block in start_stream")

    def _get_middleware_class(self, middleware_name):
        """
        Dynamically get the middleware class based on the middleware name.
        
        Args:
            middleware_name: Name of the middleware to instantiate
            
        Returns:
            The middleware class or None if not found
        """
        middleware_map = {
            "brainflow": BrainflowInterface,
            "synthetic": SyntheticInterface
        }
        return middleware_map.get(middleware_name.lower())
    
    def _process_device_metadata(self, device_metadata: Dict[str, Any], selected_middleware: Optional[str]) -> Dict[str, Any]:
        """
        Process device data to keep only the selected middleware and flatten its structure.
        
        Args:
            device_metadata: The original device data dictionary
            selected_middleware: The name of the selected middleware
            
        Returns:
            Processed device data with flattened structure
        """
        processed_data = copy.deepcopy(device_metadata)
        
        # If no middleware selected or no available middlewares, return as is
        if not selected_middleware or "AvailableMiddlewares" not in processed_data:
            return processed_data
            
        # Get the selected middleware data
        middleware_data = processed_data.get("AvailableMiddlewares", {}).get(selected_middleware, {})
        
        # Remove all available middlewares
        if "AvailableMiddlewares" in processed_data:
            del processed_data["AvailableMiddlewares"]
            
        # Merge middleware data directly into device_metadata
        processed_data.update(middleware_data)
        
        return processed_data