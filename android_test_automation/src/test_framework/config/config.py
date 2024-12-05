class Config:
    # Appium Configuration
    APPIUM_HOST = "http://localhost"
    APPIUM_PORT = "4723"
    PLATFORM_NAME = "Android"
    AUTOMATION_NAME = "UiAutomator2"
    DEVICE_NAME = "moto-one"  # Change to your device name
    APP_PACKAGE = "com.google.android.apps.nbu.files"
    APP_ACTIVITY = "com.google.android.apps.nbu.files.home.HomeActivity"

    # Test Configuration
    IMPLICIT_WAIT = 10
    EXPLICIT_WAIT = 15
    INITIAL_TEST_CASE_NUMBER = 1
    TEST_CASES_NUMBER = 22

    @classmethod
    def get_capabilities(cls):
        return {
            "platformName": cls.PLATFORM_NAME,
            "automationName": cls.AUTOMATION_NAME,
            "deviceName": cls.DEVICE_NAME,
            "appPackage": cls.APP_PACKAGE,
            "appActivity": cls.APP_ACTIVITY,
            "noReset": True
        }

    @classmethod
    def get_appium_url(cls):
        return f"{cls.APPIUM_HOST}:{cls.APPIUM_PORT}"