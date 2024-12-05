from appium import webdriver
import traceback
from appium.options.android import UiAutomator2Options
from appium.webdriver.common.appiumby import AppiumBy
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import json
import os

def load_test_cases():
    with open('test_cases.json', 'r') as f:
        return json.load(f)['test_cases']

def run_seeing_ai_test(test_case, image_index):
    # Appium Server URL
    appium_server_url = 'http://127.0.0.1:4723'

    # Set up Appium Options
    options = UiAutomator2Options()
    options.platform_name = 'Android'
    options.device_name = 'emulator-5554'
    options.app_package = 'com.google.android.apps.nexuslauncher'
    options.app_activity = '.NexusLauncherActivity'
    options.no_reset = True

    try:
        print(f"\nStarting test for: {test_case['name']}")
        print(f"Looking for image: {test_case['image_file']}")
        print(f"Expected keywords: {test_case['expected_keywords']}")

        # Initialize Appium Driver
        driver = webdriver.Remote(command_executor=appium_server_url, options=options)
        wait = WebDriverWait(driver, 20)
        
        # Click Photos app
        ###### print("Clicked Photos app")

        time.sleep(3)  # Wait for Photos to load

        # Find and click photo
        print(f"Looking for image...")
        try:
            # Find image by index in the grid
            target_images = wait.until(EC.presence_of_all_elements_located(
                (AppiumBy.CLASS_NAME, "android.widget.ImageView")
            ))
            if image_index < len(target_images):
                # Ensure only the intended image is clicked
                target_image = target_images[image_index]
                print(f"Found image at index {image_index}")
                target_image.click()
            else:
                raise IndexError(f"No image found at index {image_index}")
        except IndexError:
            raise Exception(f"No image found at index {image_index}")

        print("Clicked image")
        time.sleep(2)  # Wait for image to open fully

        # Click share button
        print("\nLooking for share button...")
        share_button = wait.until(EC.presence_of_element_located(
            (AppiumBy.ACCESSIBILITY_ID, "Share")
        ))
        share_button.click()
        print("Clicked share button")
        time.sleep(2)  # Wait for share menu to fully appear

        # Try to find Seeing AI in share menu
        print("\nLooking for Seeing AI in share menu...")
        seeing_ai = None
        try:
            seeing_ai = wait.until(EC.presence_of_element_located(
                (AppiumBy.XPATH, "//android.widget.TextView[@text='Seeing AI']")
            ))
            print("Found Seeing AI")
        except:
            print("Seeing AI not immediately visible, trying to scroll...")
            share_menu = wait.until(EC.presence_of_element_located(
                (AppiumBy.CLASS_NAME, "android.widget.ScrollView")
            ))
            
            # Scroll until we find Seeing AI
            last_elements = None
            max_scrolls = 5
            for i in range(max_scrolls):
                print(f"Scroll attempt {i+1}/{max_scrolls}")
                try:
                    seeing_ai = driver.find_element(AppiumBy.XPATH, "//android.widget.TextView[@text='Seeing AI']")
                    print("Found Seeing AI after scrolling")
                    break
                except:
                    elements = share_menu.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
                    current_elements = [e.text for e in elements if e.text]
                    
                    if current_elements == last_elements:
                        print("Reached end of scrollable area")
                        break
                    
                    last_elements = current_elements
                    driver.swipe(500, 1500, 500, 500, 1000)
                    time.sleep(1)

        if not seeing_ai:
            raise Exception("Could not find Seeing AI in share menu")

        print("Clicking Seeing AI...")
        seeing_ai.click()
        print("Selected Seeing AI")
        time.sleep(3)

        # Wait for result text
        print("\nWaiting for result text...")
        try:
            # First try Scene section text
            scene_text = wait.until(EC.presence_of_element_located(
                (AppiumBy.XPATH, "//android.widget.TextView[@text='Scene']")
            ))
            # Get the next TextView after Scene
            all_text_elements = driver.find_elements(AppiumBy.CLASS_NAME, "android.widget.TextView")
            for i, element in enumerate(all_text_elements):
                if element.get_attribute('text') == 'Scene' and i + 1 < len(all_text_elements):
                    result_text = all_text_elements[i + 1]
                    break
        except:
            try:
                # Try finding text directly
                result_text = wait.until(EC.presence_of_element_located(
                    (AppiumBy.XPATH, "//android.widget.TextView[contains(@text, 'shelf') or contains(@text, 'drink')]")
                ))
            except:
                # Last resort - try any text element
                result_text = wait.until(EC.presence_of_element_located(
                    (AppiumBy.CLASS_NAME, "android.widget.TextView")
                ))

        description = result_text.text.lower()
        print(f"Found result text: {description}")
        
        # Check results
        found_keywords = [keyword for keyword in test_case['expected_keywords'] 
                         if keyword.lower() in description]
        
        print("\nTest Results:")
        print(f"Scene Description: {description}")
        print(f"Found keywords: {found_keywords}")
        print(f"Missing keywords: {set(test_case['expected_keywords']) - set(found_keywords)}")
        
        # Determine if test passed
        test_passed = len(found_keywords) >= 2
        print(f"Test {'PASSED' if test_passed else 'FAILED'}")

        # Navigate back to Photos
        print("\nNavigating back to Photos...")
        driver.press_keycode(4)  # Android back button keycode
        time.sleep(1)  # Wait between presses
        driver.press_keycode(4)  # Android back button keycode
        time.sleep(1)  # Wait between presses
        print("Returned to Photos app")

        return {
            'test_case': test_case['name'],
            'image_file': test_case['image_file'],
            'description': description,
            'found_keywords': found_keywords,
            'passed': test_passed
        }

    except Exception as e:
        print(f"Test failed: {str(e)}")
        traceback.print_exc()
        return {
            'test_case': test_case['name'],
            'image_file': test_case['image_file'],
            'error': str(e),
            'passed': False
        }

    finally:
        if 'driver' in locals():
            driver.quit()
            print("Driver closed")

def main():
    # Load and run test cases
    test_cases = load_test_cases()
    results = []
    
    for index, test_case in enumerate(test_cases, start=1):
        result = run_seeing_ai_test(test_case, index)
        results.append(result)
    
    # Save results
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    with open(f'test_results_{timestamp}.json', 'w') as f:
        json.dump(results, f, indent=4)
    
    # Print summary
    print("\nTest Summary:")
    passed_tests = sum(1 for r in results if r.get('passed', False))
    print(f"Passed: {passed_tests}/{len(results)}")
    print(f"Results saved to: test_results_{timestamp}.json")

if __name__ == "__main__":
    main()
