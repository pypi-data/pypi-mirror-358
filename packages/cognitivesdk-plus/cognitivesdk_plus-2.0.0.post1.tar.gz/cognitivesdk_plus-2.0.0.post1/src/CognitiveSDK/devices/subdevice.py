# devices/subdevice.py

from typing import Any, Dict, Optional
from ..core.publisher import Publisher
from ..utils.logger import logger
import asyncio
from ..utils.shared_state import SharedState

class SubDevice:
    def __init__(self, parent_device: Any, name: str, config: Dict):
        self.parent_device = parent_device
        self.name = name
        self.config = config
        self.publisher: Optional[Publisher] = None
        self.topic: Optional[str] = None
        self.stopped = False
        self.shared_state = SharedState.get_instance()

        # Store the channel indices specific to this subdevice
        self.channel_indices = config.get("ChannelsIndex")
        self.sampling_frequency = config.get("SamplingFrequency")

        
    def set_topic(self, topic: str):
        """Set up publisher with topic and start command listener."""
        if self.publisher:
            logger.info(f"Closing existing publisher for subdevice '{self.name}'")
            asyncio.create_task(self.publisher.close())
            
        self.topic = f"{topic}.{self.name}"
        logger.info(f"Creating publisher for subdevice '{self.name}' with topic '{self.topic}'")
        self.publisher = Publisher(self.topic, self.name)

        # Get ZMQ proxy address from SharedState and connect
        xsub_port = self.shared_state.get("Orcustrator.XSub")
        if xsub_port:
            asyncio.create_task(self.publisher.connect(xsub_port))
        else:
            logger.error(f"XSub port not available for publisher {self.topic}")

        # Start command listener if external control is enabled
        is_external_control = self.shared_state.get("Orcustrator.ExternalController")
        if is_external_control:
            logger.warning(f"Starting command listener for subdevice '{self.name}'")
            asyncio.create_task(self.publisher.start_command_listener())
        
    def on_data(self, data):
        """Handle incoming data - publisher handles pause state internally."""
        if self.stopped:
            return
            
        if not self.publisher:
            logger.error(f"Subdevice '{self.name}' has no publisher, cannot forward data")
            return
        try:
            data_to_publish = data
            if data_to_publish.size > 0:
                 self.publisher.publish(data_to_publish)
            else:
                 logger.warning(f"Subdevice '{self.name}' attempted to publish empty data array. Skipping.")

        except IndexError:
             # Fallback: publish original data if slicing failed unexpectedly
             if data.size > 0:
                 self.publisher.publish(data)
        except Exception as e:
            logger.error(f"Error processing or publishing data for {self.topic}: {e}", exc_info=True)

    def stop(self):
        """Stop the subdevice and its publisher."""
        self.stopped = True
        if self.publisher:
            logger.info(f"Stopping publisher for subdevice '{self.name}'")
            asyncio.create_task(self.publisher.close())
        logger.info(f"Subdevice {self.topic} stopped")