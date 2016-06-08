from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import TimeoutException
from contextlib import contextmanager
from selenium.webdriver.support.expected_conditions import \
    staleness_of
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys

import unittest, time, re
import random


class wait_for_page_load(object):

    def __init__(self, driver):
        self.driver = driver

    def __enter__(self):
        self.old_page = self.driver.find_element_by_tag_name('html')

    def page_has_loaded(self):
        new_page = self.driver.find_element_by_tag_name('html')
        return new_page.id != self.old_page.id

    def __exit__(self, *_):
        wait_for(self.page_has_loaded)


class CloudInstanceTest(unittest.TestCase):

	def setUp(self):
		print 'In setUp()'
		self.driver = webdriver.Firefox()
		self.verificationErrors = []
		self.driver.get("URL")
		self.login()

	# return True if element is visible within 10 seconds, otherwise False
	def is_visible(self, locator, timeout=10):
		try:
			WebDriverWait(self.driver, timeout).until(EC.visibility_of_element_located((By.XPATH, locator)))
			return True
		except TimeoutException:
			return False

	def check_exists_by_xpath(xpath):
		try:
			webdriver.find_element_by_xpath(xpath)
		except NoSuchElementException:
			return False
		return True

	def delete_account(self, index):
		driver = self.driver
		delete_Element_xpath = "//md-menu-content/md-menu-item[3]/button[@aria-label='Delete']"
		js = "arguments[0].style.height='auto'; arguments[0].style.visibility='visible';" #hack for setting element into visible state within the DOM
		cloud_account_list = WebDriverWait(driver, 10).until(lambda driver: driver.find_elements(By.XPATH, "html/body/div[1]/md-content/md-content/div[1]/md-card/md-list"))
		# driver.implicitly_wait(10)
		deleteSelection = WebDriverWait(driver, 10).until(lambda driver: driver.find_element(By.XPATH, "//md-menu-content/md-menu-item[3]/button[@aria-label='Delete']"))
		#  Menu Drop Down for Cloud Account Selected by Index
		buttonItemListElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("html/body/div[1]/md-content/md-content/div[1]/md-card/md-list/md-list-item["+str(index)+"]/a/div[1]/div/div/md-menu/button"))
		if buttonItemListElement is not None and index > 2:
			# Selects on the index menu with the aria-label: # Open Sample menu
			buttonItemListElement.click()
			time.sleep(2)  # wait for selection menu items to become visible
			deleteSelectionList = WebDriverWait(driver, 10).until(lambda driver: driver.find_elements(By.XPATH, "//md-menu-content/md-menu-item[3]/button[@aria-label='Delete']"))
			if deleteSelectionList[index] is not None:
				try:
					deleteElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element(By.XPATH, "//div[4]/md-menu-content/md-menu-item[3]/button"))
					deleteElement.click()
					time.sleep(5) 
					confirmElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element(By.XPATH, "//div[5]/md-dialog/md-dialog-actions/button[2]"))
					confirmElement.send_keys(Keys.ENTER)
					time.sleep(5)
					driver.refresh() # or use driver.execute_script("location.reload()")
				except NoSuchElementException:
					print("Entered Exception")
					time.sleep(5)
					deleteSelectionList[index].send_keys(Keys.NULL)
					deleteSelectionList[index].click()

		# edge case where there are only two accounts registered --- index is 1 in the case where there are only two accounts registered for a user's account
		elif len(cloud_account_list) == 1 and index == 1:
			if buttonItemListElement is not None:
				buttonItemListElement.click()
				time.sleep(2)
				deleteSelectionList = WebDriverWait(driver, 10).until(lambda driver: driver.find_elements(By.XPATH, "//md-menu-content/md-menu-item[3]/button[@aria-label='Delete']"))
				try:
					deleteElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element(By.XPATH, "//div[4]/md-menu-content/md-menu-item[3]/button"))
					deleteElement.click()
					time.sleep(5) 
					confirmElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element(By.XPATH, "//div[5]/md-dialog/md-dialog-actions/button[2]"))
					confirmElement.send_keys(Keys.ENTER)
					time.sleep(5)
					driver.refresh() # or use driver.execute_script("location.reload()")
				except NoSuchElementException:
					print("Entered Exception")
					time.sleep(5)
					deleteSelectionList[index].send_keys(Keys.NULL)
					deleteSelectionList[index].click()

	def cloud_account_to_actions_side_nav(self, row_index):
		driver = self.driver
		time.sleep(2)
		WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('html/body/div[1]/md-content/md-content/div[1]/md-card/md-list/md-list-item[1]/a')).click()
		# wait for Cloud Element's xpath to be rendered?
		cloudElement = self.is_visible('//div[1]/md-content/div/div[1]/div[6]/md-card/md-card-content/div[1]')
		if cloudElement is not False:
			print 'Found Cloud Account Element to explore!'
			if driver.find_element_by_xpath("//*[starts-with(.,'Instances')]") is not None:
				WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//*[starts-with(.,'Instances')]")).click()
				if self.is_visible('//div[1]/md-content/div/div[3]/md-card/div/md-table-container/table/tbody/tr[2]/td[2]/button'):
					# select Explore Resources for Row Index # md-Side nav (resource panel) with Instance info
					WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//div[1]/md-content/div/div[3]/md-card/div/md-table-container/table/tbody/tr["+str(row_index)+"]/td[2]/button")).click()
					time.sleep(2)
					# Actions Tab
					WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('//div[1]/resource-panel/md-sidenav/md-tabs/md-tabs-wrapper/md-tabs-canvas/md-pagination-wrapper/md-tab-item[2]/span')).click()
	
	# removed the cloudElement Conditional ---> will adopt this in future tests
	def cloud_account_to_actions_side_nav_functional(self, cloud_account_index, resource_table_row_index):
		driver = self.driver
		time.sleep(2)
		WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('html/body/div[1]/md-content/md-content/div[1]/md-card/md-list/md-list-item['+str(cloud_account_index)+']/a')).click()
		# wait for Cloud Element's xpath to be rendered?
		print 'Found Cloud Account Element to explore!'
		driver.implicitly_wait(30)
		if driver.find_element_by_xpath("//*[starts-with(.,'Instances')]") is not None:
			WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//*[starts-with(.,'Instances')]")).click()
			if self.is_visible('//div[1]/md-content/div/div[3]/md-card/div/md-table-container/table/tbody/tr['+str(resource_table_row_index)+']/td[2]/button'):
				# select Explore Resources for Row Index ----> # md-Side nav (resource panel) with Instance info
				WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//div[1]/md-content/div/div[3]/md-card/div/md-table-container/table/tbody/tr["+str(resource_table_row_index)+"]/td[2]/button")).click()
				time.sleep(2)
				# Actions Tab -- md-item number 2
				WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('//div[1]/resource-panel/md-sidenav/md-tabs/md-tabs-wrapper/md-tabs-canvas/md-pagination-wrapper/md-tab-item[2]/span')).click()

	# removed the cloudElement Conditional ---> will adopt this in future tests
	def cloud_account_to_tags_side_nav_functional(self, cloud_account_index, resource_table_row_index):
		driver = self.driver
		time.sleep(2)
		WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('html/body/div[1]/md-content/md-content/div[1]/md-card/md-list/md-list-item['+str(cloud_account_index)+']/a')).click()
		# wait for Cloud Element's xpath to be rendered?
		print 'Found Cloud Account Element to explore!'
		driver.implicitly_wait(30)
		if driver.find_element_by_xpath("//*[starts-with(.,'Instances')]") is not None:
			WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//*[starts-with(.,'Instances')]")).click()
			if self.is_visible('//div[1]/md-content/div/div[3]/md-card/div/md-table-container/table/tbody/tr['+str(resource_table_row_index)+']/td[2]/button'):
				# select Explore Resources for Row Index ----> # md-Side nav (resource panel) with Instance info
				WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//div[1]/md-content/div/div[3]/md-card/div/md-table-container/table/tbody/tr["+str(resource_table_row_index)+"]/td[2]/button")).click()
				time.sleep(2)
				# Tags Tab -- md-item number 5
				WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('//div[1]/resource-panel/md-sidenav/md-tabs/md-tabs-wrapper/md-tabs-canvas/md-pagination-wrapper/md-tab-item[5]/span')).click()

	# removed the Conditional logic to move to sidenav
	def cloud_account_to_actions_to_instances(self, cloud_account_index, resource_table_row_index):
		driver = self.driver
		time.sleep(2)
		WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('html/body/div[1]/md-content/md-content/div[1]/md-card/md-list/md-list-item['+str(cloud_account_index)+']/a')).click()
		# wait for Cloud Element's xpath to be rendered?
		print 'Found Cloud Account Element to explore!'
		driver.implicitly_wait(30)
		if driver.find_element_by_xpath("//*[starts-with(.,'Instances')]") is not None:
			WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//*[starts-with(.,'Instances')]")).click()
			
	def login(self):
		print 'In login test'
		driver = self.driver
		divvyUsername = ""
		divyPassword = ""
		emailFieldName = "email"
		passFieldName = "password"
		buttonName = "login"

		emailFieldElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_name(emailFieldName))
		passFieldElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_name(passFieldName))
		loginButtonElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_name(buttonName))

		emailFieldElement.clear()
		emailFieldElement.send_keys(divvyUsername)
		passFieldElement.clear()
		passFieldElement.send_keys(divyPassword)
		loginButtonElement.click()


class TestE2E(CloudInstanceTest):

	@unittest.skip("Skip over Create Cloud test routine")
	def test_create_cloud_account(self):
		print 'In create_cloud_class test'
		driver = self.driver
		accountNumber = ''
		awsAccessKey = ''
		awsSecretKey = ''

		# Wait for Create Cloud Element to be Added to DOM --> Select that Element
		create_cloud_class_button = '//button[@aria-label="Add Cloud"]'
		WebDriverWait(driver, 10).until(lambda driver: driver.find_element(By.XPATH, create_cloud_class_button).is_displayed())
		cloudButtonElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element(By.XPATH, create_cloud_class_button))
		cloudButtonElement.click()
		# Wait for the Cloud Window to load (10s before TimeOut Exception) and for Create Cloud Element to be Added to DOM --> Select that Element
		driver.implicitly_wait(10);
		createCloudDropdown = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_tag_name('md-select'))
		createCloudDropdown.click()
		# # Select AWS Cloud Account -- > Select your Cloud Tab
		selectAWSCloud = WebDriverWait(driver, 10).until(lambda driver: driver.find_element(By.XPATH, ".//*[@value='AWS']"))
		selectAWSCloud.click()

		# # Enter Nickname Field
		nicknameFieldElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath(".//div[1]/md-content/md-sidenav/form/md-content[2]/md-input-container[2]/input")) 
		nicknameFieldElement.clear()
		nicknameFieldElement.send_keys('AWS Test QA ' + str(random.random()))

		# Enter Account Number
		accountNumberElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//div[1]/md-content/md-sidenav/form/md-content[2]/md-input-container[3]/input"))
		accountNumberElement.clear()
		accountNumberElement.send_keys(accountNumber)

		authenticationTypeDropdown = WebDriverWait(driver, 10).until(lambda driver: driver.find_element(By.XPATH, ".//*[@aria-label='Authentication Type']"))
		authenticationTypeDropdown.click()
		# # Select API Secret Key  -- > Select Authentication type to be API Secret Key
		WebDriverWait(driver, 10).until(lambda driver: driver.find_element(By.XPATH, ".//*[@value='standard']")).click()

		# # Enter API Key
		awsAccessKeyElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//div[1]/md-content/md-sidenav/form/md-content[2]/md-input-container[5]/input"))
		awsAccessKeyElement.clear()
		awsAccessKeyElement.send_keys(awsAccessKey)

		# Enter API Secret
		awsSecretKeyElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//div[1]/md-content/md-sidenav/form/md-content[2]/md-input-container[6]/input"))
		awsSecretKeyElement.clear()
		awsSecretKeyElement.send_keys(awsSecretKey)

		# Submit Account Details for AWS Cloud Registering
		driver.implicitly_wait(10);
		submitAccountDetailsButton = 'html/body/div[1]/md-content/md-sidenav/form/md-content[2]/div/button[2]'
		WebDriverWait(driver, 10).until(lambda driver: driver.find_element(By.XPATH, submitAccountDetailsButton).is_displayed())
		submitDetailsElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element(By.XPATH, submitAccountDetailsButton))
		submitDetailsElement.click()

	@unittest.skip("Skip over navigate to and explore and explore console output test")
	def test_navigate_to_new_account_get_console_output(self):
		print 'In navigate and explore new account'
		driver = self.driver
		try:
			newRegisteredAccountElement = self.is_visible("html/body/div[1]/md-content/md-content/div[1]/md-card/md-list/md-list-item[1]/a/div[1]/div/h3")
			# driver.refresh()
			print 'newRegisteredAccountElement is visible: ' + str(newRegisteredAccountElement)
			time.sleep(2) 
			# driver.refresh()
			# click on specific account
			if newRegisteredAccountElement == True:
				# md-list item 1
				WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('html/body/div[1]/md-content/md-content/div[1]/md-card/md-list/md-list-item[1]/a')).click()
				# wait for Instance Element's xpath to be rendered?
				instanceElement = self.is_visible('//div[1]/md-content/div/div[1]/div[6]/md-card/md-card-content/div[1]')
				if instanceElement is not False:
					print 'Found Instances Element'
					if driver.find_element_by_xpath("//*[starts-with(.,'Instances')]") is not None:
						WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//*[starts-with(.,'Instances')]")).click()
						if self.is_visible('//div[1]/md-content/div/div[3]/md-card/div/md-table-container/table/tbody/tr[2]/td[2]/button'):
							# select Explore Resources for Second row in Table tr[2] --> opens 	# md-Side nav (resource panel) with Instance info
							WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('//div[1]/md-content/div/div[3]/md-card/div/md-table-container/table/tbody/tr[2]/td[2]/button')).click()
							time.sleep(2)
							WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('//div[1]/resource-panel/md-sidenav/md-tabs/md-tabs-wrapper/md-tabs-canvas/md-pagination-wrapper/md-tab-item[2]/span')).click()
							# select Actions Tab  --> md-list item 1.... remember ng-model does not follow zero-based indexing!!!
							WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('//div[1]/resource-panel/md-sidenav/md-tabs/md-tabs-content-wrapper/md-tab-content[2]/div/md-content/md-list/md-list-item[1]/button')).click()
							time.sleep(2)
							# Get Console Output
							WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('//div[1]/resource-panel/md-sidenav/md-tabs/md-tabs-content-wrapper/md-tab-content[2]/div/md-content/md-list/md-list-item[1]/button')).click()
							time.sleep(3)
							# Screenshot of Console
							driver.get_screenshot_as_file('/Users/saran/Desktop/selenium/QATestBed/snapshots/ConsoleOutput.png')
				else:
					print 'There is not an Instance Element to explore information and statistics'
		except NoSuchElementException:
			if check_exists_by_xpath('//div[1]/md-content/div/div[1]/div[6]/md-card/md-card-content/div[1]') == True:
				WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('//div[1]/md-content/div/div[1]/div[6]/md-card/md-card-content/div[1]')).click()

	@unittest.skip("Skip over navigate to and rename instance action test")	
	def test_navigate_to_new_account_rename_instance(self):
		driver = self.driver
		# arbitrarily select row number 4
		self.cloud_account_to_actions_side_nav(4) # row index 4
		driver.implicitly_wait(30) 
		# item 3 is the rename instance action
		WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('//div[1]/resource-panel/md-sidenav/md-tabs/md-tabs-content-wrapper/md-tab-content[2]/div/md-content/md-list/md-list-item[3]/button')).click()
		driver.implicitly_wait(2)
		# rename modal
		rename_modal = WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath('//div[4]/md-dialog/form/md-dialog-content/md-input-container[2]/input'))
		driver.implicitly_wait(30)
		rename_modal.clear()
		rename_modal.send_keys('Hamsters Revolt Test - Thanks Peter Snelgrove!')
		driver.get_screenshot_as_file('/Users/saran/Desktop/selenium/QATestBed/snapshots/RenameInstance.png')
		driver.implicitly_wait(30)
		# submit button to be clicked
		WebDriverWait(driver, 10).until(lambda driver: driver.find_element_by_xpath("//div[4]/md-dialog/form/md-dialog-actions/div/button[@aria-label='Submit']")).click()

	@unittest.skip("Skip over modifying security group test")		
	def test_navigate_to_new_account_modify_security_group(self):
		driver =self.driver
		wait = WebDriverWait(driver, 10)
		self.cloud_account_to_actions_side_nav(5)
		driver.implicitly_wait(30)
		# Selection 2 to modify security group
		wait.until(lambda driver: driver.find_element_by_xpath('//div[1]/resource-panel/md-sidenav/md-tabs/md-tabs-content-wrapper/md-tab-content[2]/div/md-content/md-list/md-list-item[2]/button')).click()
		driver.implicitly_wait(30)
		# Select Dropdown Menu within Modify Security Group Modal
		wait.until(lambda driver: driver.find_element_by_xpath('html/body/div[4]/md-dialog/form/md-dialog-content/md-input-container/md-select/md-select-value/span[2]')).click()
		driver.implicitly_wait(30)
		test_option_default = driver.find_elements_by_tag_name('md-option') # notice its "find_elements" with an s
		css_option_locators = driver.find_elements_by_css_selector('div.md-text.ng-binding')
		for i in css_option_locators:
			if i.text == 'default':
				i.click()
		driver.implicitly_wait(30)

	@unittest.skip("Skip over stop server for resource test")		
	def test_navigate_to_new_account_stop_server(self):
		driver =self.driver
		wait = WebDriverWait(driver, 10)
		self.cloud_account_to_actions_side_nav(5)
		driver.implicitly_wait(30)
		# Selection 4 to stop server
		wait.until(lambda driver: driver.find_element_by_xpath('//div[1]/resource-panel/md-sidenav/md-tabs/md-tabs-content-wrapper/md-tab-content[2]/div/md-content/md-list/md-list-item[4]/button')).click()
		driver.implicitly_wait(30)
		# Select Submit button to confirm
		wait.until(lambda driver: driver.find_element_by_xpath('html/body/div[4]/md-dialog/form/md-dialog-actions/div/button[2]')).click()
		driver.implicitly_wait(30)
		time.sleep(2)

	@unittest.skip("Skip over resize instance test")		
	def test_navigate_to_new_account_resize(self):
		driver =self.driver
		wait = WebDriverWait(driver, 10)
		# 2nd Cloud Account; 2nd row in table
		self.cloud_account_to_actions_side_nav_functional(2, 2)
		driver.implicitly_wait(30)
		# Selection 5 to resize instance
		wait.until(lambda driver: driver.find_element_by_xpath('//div[1]/resource-panel/md-sidenav/md-tabs/md-tabs-content-wrapper/md-tab-content[2]/div/md-content/md-list/md-list-item[5]/button')).click()
		driver.implicitly_wait(30)
		# # Select Submit button to confirm
		wait.until(lambda driver: driver.find_element_by_xpath('//div[4]/md-dialog/form/md-dialog-content/md-input-container/md-select')).click()
		driver.implicitly_wait(30)
		# option 6
		wait.until(lambda driver: driver.find_element_by_xpath('//div[5]/md-select-menu/md-content/md-option[6]/div[1]')).click()
		time.sleep(2)

		# time.sleep(2)

	@unittest.skip("Skip over start server for resource test")
	def test_navigate_to_new_account_start_server(self):
		driver =self.driver
		wait = WebDriverWait(driver, 10)
		# 2nd Cloud Account; 1st row in table
		self.cloud_account_to_actions_side_nav_functional(2, 1)
		# Selection 1 to Start Server
		wait.until(lambda driver: driver.find_element_by_xpath('//div[1]/resource-panel/md-sidenav/md-tabs/md-tabs-content-wrapper/md-tab-content[2]/div/md-content/md-list/md-list-item[1]/button')).click()
		driver.implicitly_wait(30)
		# Select Submit button to confirm ---> same pattern! The modal occludes all other elements that are visible to the user...very cool!
		wait.until(lambda driver: driver.find_element_by_xpath('html/body/div[4]/md-dialog/form/md-dialog-actions/div/button[2]')).click()
		driver.implicitly_wait(30)
		time.sleep(2)

	@unittest.skip("Skip over Download CSV data for resource test")		
	def test_navigate_to_new_account_download_csv_data(self):
		driver =self.driver
		wait = WebDriverWait(driver, 10)
		# 1st Cloud Account; 1st row in table
		self.cloud_account_to_actions_to_instances(1, 1)
		downloadElement = WebDriverWait(driver, 10).until(lambda driver: driver.find_element(By.XPATH, ".//div[3]/md-card/md-toolbar[1]/div/md-menu/button[@aria-label='Open Download Resource Menu']"))
		driver.implicitly_wait(30)
		downloadElement.click()
		if self.is_visible('html/body/div[4]/md-menu-content/md-menu-item[1]/button[@filename="instance.csv"]'):
			wait.until(lambda driver: driver.find_element_by_xpath('html/body/div[4]/md-menu-content/md-menu-item[1]/button[@filename="instance.csv"]')).click()

	@unittest.skip("Skip over test for adding new tags for a given Instances's resource")
	def test_navigate_to_instance_add_new_tags(self):
		driver=self.driver
		wait=WebDriverWait(driver, 10)
		# First Cloud Account; 8th Table Row
		self.cloud_account_to_tags_side_nav_functional(1,8)
		test_key = 'testKey'
		test_value = 'test_value'
		keyFieldElement = '//div[1]/resource-panel/md-sidenav/md-tabs/md-tabs-content-wrapper/md-tab-content[5]/div/div/md-card/md-data-table-container/table/caption/form/md-input-container[1]/input'
		valueFieldElement = '//div[1]/resource-panel/md-sidenav/md-tabs/md-tabs-content-wrapper/md-tab-content[5]/div/div/md-card/md-data-table-container/table/caption/form/md-input-container[2]/input'
		driver.implicitly_wait(10)
		wait.until(lambda driver: driver.find_element(By.XPATH, keyFieldElement)).send_keys(test_key)
		wait.until(lambda driver: driver.find_element(By.XPATH, valueFieldElement)).send_keys(test_value)
		driver.implicitly_wait(10)
		if self.is_visible('.//button[@aria-label="Add Tag"]'):
			wait.until(lambda driver: driver.find_element_by_xpath('.//button[@aria-label="Add Tag"]')).click()
		driver.implicitly_wait(10)
		driver.find_element_by_xpath('.//button[@aria-label="Save"]').click()
		time.sleep(2)

	@unittest.skip("Skip over Delete Cloud Account test")
	def test_delete_cloud_account(self): # need to set 1 if cloud accounts listed is equal to 2 -- > TODO: need to figure out why!
		return self.delete_account(1)

	def tearDown(self):
		print 'In tearDown()'
		self.assertEqual([], self.verificationErrors)
		self.driver.close()


if __name__ == '__main__':
	unittest.main(verbosity=2)
