"""
WebDriver Manager for handling Chrome WebDriver setup and management
"""

import os
import logging
import platform
import subprocess
import zipfile
import tarfile
from urllib.request import urlopen, Request
from urllib.error import URLError
import shutil
from pathlib import Path
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class WebDriverManager:
    """
    Manages Chrome WebDriver download, setup, and configuration
    """
    
    def __init__(self, driver_dir: str = "drivers"):
        """
        Initialize WebDriver manager
        
        Args:
            driver_dir: Directory to store WebDriver binaries
        """
        self.driver_dir = Path(driver_dir)
        self.driver_dir.mkdir(exist_ok=True)
        self.chrome_version = None
        self.driver_version = None
        
    def get_chrome_version(self) -> Optional[str]:
        """
        Get installed Chrome version
        
        Returns:
            Chrome version string or None
        """
        try:
            system = platform.system()
            
            if system == "Windows":
                # Try multiple possible Chrome locations
                chrome_paths = [
                    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
                    os.path.expandvars(r"%LOCALAPPDATA%\Google\Chrome\Application\chrome.exe")
                ]
                
                for chrome_path in chrome_paths:
                    if os.path.exists(chrome_path):
                        # Get version from file properties
                        try:
                            result = subprocess.run([
                                "powershell", "-Command",
                                f"(Get-Item '{chrome_path}').VersionInfo.FileVersion"
                            ], capture_output=True, text=True)
                            
                            if result.returncode == 0:
                                version = result.stdout.strip()
                                if version:
                                    self.chrome_version = version
                                    return version
                        except Exception as e:
                            logger.warning(f"Error getting Chrome version from {chrome_path}: {str(e)}")
                            
            elif system == "Darwin":  # macOS
                try:
                    result = subprocess.run([
                        "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome", 
                        "--version"
                    ], capture_output=True, text=True)
                    
                    if result.returncode == 0:
                        version_line = result.stdout.strip()
                        # Extract version number
                        version_parts = version_line.split()
                        for part in version_parts:
                            if '.' in part and part.replace('.', '').isdigit():
                                self.chrome_version = part
                                return part
                                
                except Exception as e:
                    logger.warning(f"Error getting Chrome version on macOS: {str(e)}")
                    
            elif system == "Linux":
                try:
                    # Try multiple Chrome executables
                    chrome_executables = ["google-chrome", "google-chrome-stable", "chromium", "chromium-browser"]
                    
                    for executable in chrome_executables:
                        try:
                            result = subprocess.run([executable, "--version"], capture_output=True, text=True)
                            if result.returncode == 0:
                                version_line = result.stdout.strip()
                                version_parts = version_line.split()
                                for part in version_parts:
                                    if '.' in part and part.replace('.', '').isdigit():
                                        self.chrome_version = part
                                        return part
                        except FileNotFoundError:
                            continue
                            
                except Exception as e:
                    logger.warning(f"Error getting Chrome version on Linux: {str(e)}")
            
            logger.warning("Could not determine Chrome version")
            return None
            
        except Exception as e:
            logger.error(f"Error getting Chrome version: {str(e)}")
            return None
    
    def get_driver_download_url(self, chrome_version: str) -> Optional[str]:
        """
        Get ChromeDriver download URL for Chrome version
        
        Args:
            chrome_version: Chrome version string
            
        Returns:
            Download URL or None
        """
        try:
            system = platform.system()
            
            # Map system to ChromeDriver platform (new API)
            platform_map = {
                "Windows": "win64",
                "Darwin": "mac-x64",
                "Linux": "linux64"
            }
            
            if system not in platform_map:
                logger.error(f"Unsupported platform: {system}")
                return None
            
            platform_name = platform_map[system]
            
            # Use the new ChromeDriver API
            # Get major version number
            major_version = chrome_version.split('.')[0]
            
            # Try to get the latest compatible ChromeDriver version
            version_url = f"https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE_{major_version}"
            
            try:
                request = Request(version_url, headers={'User-Agent': 'Mozilla/5.0'})
                response = urlopen(request, timeout=30)
                driver_version = response.read().decode('utf-8').strip()
                self.driver_version = driver_version
                
                # Construct download URL using the new API
                download_url = f"https://storage.googleapis.com/chrome-for-testing-public/{driver_version}/{platform_name}/chromedriver-{platform_name}.zip"
                
                logger.info(f"ChromeDriver download URL: {download_url}")
                return download_url
                
            except URLError:
                # Fallback: try to get latest stable version
                fallback_url = "https://googlechromelabs.github.io/chrome-for-testing/LATEST_RELEASE"
                request = Request(fallback_url, headers={'User-Agent': 'Mozilla/5.0'})
                response = urlopen(request, timeout=30)
                driver_version = response.read().decode('utf-8').strip()
                self.driver_version = driver_version
                
                download_url = f"https://storage.googleapis.com/chrome-for-testing-public/{driver_version}/{platform_name}/chromedriver-{platform_name}.zip"
                logger.info(f"Using latest ChromeDriver version: {download_url}")
                return download_url
                
        except Exception as e:
            logger.error(f"Error getting driver download URL: {str(e)}")
            return None
    
    def download_driver(self, download_url: str) -> Optional[str]:
        """
        Download ChromeDriver
        
        Args:
            download_url: ChromeDriver download URL
            
        Returns:
            Path to downloaded driver or None
        """
        try:
            logger.info(f"Downloading ChromeDriver from {download_url}")
            
            # Create request with user agent
            request = Request(download_url, headers={'User-Agent': 'Mozilla/5.0'})
            response = urlopen(request, timeout=60)
            
            # Get filename from URL
            filename = download_url.split('/')[-1]
            download_path = self.driver_dir / filename
            
            # Download file
            with open(download_path, 'wb') as f:
                while True:
                    chunk = response.read(8192)
                    if not chunk:
                        break
                    f.write(chunk)
            
            logger.info(f"Downloaded ChromeDriver to {download_path}")
            return str(download_path)
            
        except Exception as e:
            logger.error(f"Error downloading ChromeDriver: {str(e)}")
            return None
    
    def extract_driver(self, archive_path: str) -> Optional[str]:
        """
        Extract ChromeDriver from archive
        
        Args:
            archive_path: Path to downloaded archive
            
        Returns:
            Path to extracted driver or None
        """
        try:
            archive_path = Path(archive_path)
            
            if archive_path.suffix == '.zip':
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(self.driver_dir)
            elif archive_path.suffix in ['.tar', '.gz', '.bz2']:
                with tarfile.open(archive_path, 'r:*') as tar_ref:
                    tar_ref.extractall(self.driver_dir)
            else:
                logger.error(f"Unsupported archive format: {archive_path.suffix}")
                return None
            
            # Find extracted driver
            driver_name = "chromedriver.exe" if platform.system() == "Windows" else "chromedriver"
            
            for file_path in self.driver_dir.rglob(driver_name):
                # Make driver executable on Unix systems
                if platform.system() != "Windows":
                    os.chmod(file_path, 0o755)
                
                logger.info(f"Extracted ChromeDriver to {file_path}")
                return str(file_path)
            
            logger.error("Could not find extracted ChromeDriver")
            return None
            
        except Exception as e:
            logger.error(f"Error extracting ChromeDriver: {str(e)}")
            return None
    
    def get_driver_path(self) -> Optional[str]:
        """
        Get path to ChromeDriver, downloading if necessary
        
        Returns:
            Path to ChromeDriver or None
        """
        try:
            # Check if driver already exists in drivers directory
            driver_name = "chromedriver.exe" if platform.system() == "Windows" else "chromedriver"
            
            # First check the drivers directory
            drivers_dir = Path("drivers")
            if drivers_dir.exists():
                for file_path in drivers_dir.rglob(driver_name):
                    logger.info(f"Found existing ChromeDriver at {file_path}")
                    return str(file_path)
            
            # Check the local driver directory
            for file_path in self.driver_dir.rglob(driver_name):
                logger.info(f"Found existing ChromeDriver at {file_path}")
                return str(file_path)
            
            # Get Chrome version
            chrome_version = self.get_chrome_version()
            if not chrome_version:
                logger.error("Could not determine Chrome version")
                return None
            
            # Get download URL
            download_url = self.get_driver_download_url(chrome_version)
            if not download_url:
                logger.error("Could not get ChromeDriver download URL")
                return None
            
            # Download driver
            archive_path = self.download_driver(download_url)
            if not archive_path:
                logger.error("Could not download ChromeDriver")
                return None
            
            # Extract driver
            driver_path = self.extract_driver(archive_path)
            if not driver_path:
                logger.error("Could not extract ChromeDriver")
                return None
            
            # Clean up archive
            try:
                os.remove(archive_path)
            except Exception as e:
                logger.warning(f"Could not remove archive: {str(e)}")
            
            return driver_path
            
        except Exception as e:
            logger.error(f"Error getting ChromeDriver path: {str(e)}")
            return None
    
    def setup_chrome_options(self, headless: bool = True, user_agent: str = None) -> Dict[str, Any]:
        """
        Setup Chrome options for optimal scraping
        
        Args:
            headless: Run in headless mode
            user_agent: Custom user agent
            
        Returns:
            Dictionary of Chrome options
        """
        options = {
            'arguments': [
                '--no-sandbox',
                '--disable-dev-shm-usage',
                '--disable-blink-features=AutomationControlled',
                '--disable-extensions',
                '--disable-plugins',
                '--disable-images',  # Speed up loading
                '--disable-javascript',  # Can be enabled per platform
                '--window-size=1920,1080',
                '--disable-notifications',
                '--disable-default-apps',
                '--disable-background-timer-throttling',
                '--disable-backgrounding-occluded-windows',
                '--disable-renderer-backgrounding',
                '--disable-features=TranslateUI',
                '--disable-component-extensions-with-background-pages',
            ],
            'experimental_options': {
                'excludeSwitches': ['enable-automation'],
                'useAutomationExtension': False,
                'prefs': {
                    'profile.managed_default_content_settings.images': 2,
                    'profile.default_content_setting_values.notifications': 2,
                    'profile.managed_default_content_settings.stylesheets': 2,
                    'profile.default_content_setting_values.cookies': 2,
                    'profile.default_content_setting_values.geolocation': 2,
                    'profile.default_content_setting_values.media_stream': 2,
                    'profile.default_content_setting_values.media_stream_mic': 2,
                    'profile.default_content_setting_values.media_stream_camera': 2,
                    'profile.default_content_setting_values.protocol_handlers': 2,
                    'profile.default_content_setting_values.midi_sysex': 2,
                    'profile.default_content_setting_values.push_messaging': 2,
                    'profile.default_content_setting_values.ssl_cert_decisions': 2,
                    'profile.default_content_setting_values.metro_switch_to_desktop': 2,
                    'profile.default_content_setting_values.protected_media_identifier': 2,
                    'profile.default_content_setting_values.app_banner': 2,
                    'profile.default_content_setting_values.site_engagement': 2,
                    'profile.default_content_setting_values.durable_storage': 2,
                }
            }
        }
        
        if headless:
            options['arguments'].append('--headless')
        
        # Set user agent
        if user_agent:
            options['arguments'].append(f'user-agent={user_agent}')
        else:
            # Default user agent that looks like a real browser
            options['arguments'].append('user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36')
        
        return options
    
    def cleanup_old_drivers(self):
        """Clean up old ChromeDriver files"""
        try:
            driver_name = "chromedriver.exe" if platform.system() == "Windows" else "chromedriver"
            
            # Find all driver files
            driver_files = list(self.driver_dir.rglob(driver_name))
            
            if len(driver_files) > 1:
                # Keep only the most recent one
                driver_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
                
                for old_driver in driver_files[1:]:
                    try:
                        old_driver.unlink()
                        logger.info(f"Removed old ChromeDriver: {old_driver}")
                    except Exception as e:
                        logger.warning(f"Could not remove old driver {old_driver}: {str(e)}")
                        
        except Exception as e:
            logger.error(f"Error cleaning up old drivers: {str(e)}")
    
    def verify_driver(self, driver_path: str) -> bool:
        """
        Verify that ChromeDriver is working
        
        Args:
            driver_path: Path to ChromeDriver
            
        Returns:
            True if driver is working
        """
        try:
            from selenium import webdriver
            from selenium.webdriver.chrome.options import Options
            
            # Setup minimal options
            options = Options()
            options.add_argument('--headless')
            options.add_argument('--no-sandbox')
            options.add_argument('--disable-dev-shm-usage')
            
            # Test driver
            driver = webdriver.Chrome(executable_path=driver_path, options=options)
            driver.quit()
            
            logger.info(f"ChromeDriver verification successful: {driver_path}")
            return True
            
        except Exception as e:
            logger.error(f"ChromeDriver verification failed: {str(e)}")
            return False