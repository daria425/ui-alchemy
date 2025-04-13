import logging

class Logger:
    @staticmethod
    def configure_logging():
        logging.basicConfig(
            level=logging.INFO,  # Default log level
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.StreamHandler()  # Default handler to stream logs to console
            ]
        )

    @staticmethod
    def get_logger():
        # Return the root logger when no name is provided
        return logging.getLogger()

def shut_up_azure_logging():
    """
        Suppress Azure SDK logging to avoid cluttering the console.
    """
    logging.getLogger("azure").setLevel(logging.WARNING)
    logging.getLogger("msrest").setLevel(logging.WARNING)
    logging.getLogger("msrest.authentication").setLevel(logging.WARNING)
    logging.getLogger("azure.core.pipeline.policies.http_logging_policy").setLevel(logging.WARNING)

Logger.configure_logging()

logger = Logger.get_logger()