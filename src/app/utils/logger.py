import logging
from datetime import datetime
import os

# Log klasörü oluştur
log_directory = "logs"
if not os.path.exists(log_directory):
    os.makedirs(log_directory)

# Log dosyası adını tarihle oluştur
log_filename = f"logs/trading_{datetime.now().strftime('%Y%m%d')}.log"

# Logger'ı yapılandır
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()  # Konsola da yazdır
    ]
)

logger = logging.getLogger("trading_bot") 