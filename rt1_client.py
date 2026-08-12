import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import config

RT_CREATE_TICKET_URL = f"{config.RT_LOGIN_URL}Ticket/Create.html"


class RT1Client:
    def __init__(self, log_callback=None):
        chrome_options = webdriver.ChromeOptions()
        chrome_options.add_argument("--log-level=3")
        chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])

        self.driver = webdriver.Chrome(options=chrome_options)
        self.wait = WebDriverWait(self.driver, 40)
        self.log = log_callback or print

    def select_bootstrap_dropdown(self, field_data_id, option_text):
        button_locator = (By.XPATH, f"//button[contains(@data-id, '{field_data_id}')]")
        btn = self.wait.until(EC.element_to_be_clickable(button_locator))
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", btn)
        time.sleep(0.3)
        self.driver.execute_script("arguments[0].click();", btn)

        option_locator = (
            By.XPATH,
            f"//div[contains(@class, 'dropdown-menu show')]//span[@class='text' and text()='{option_text}']",
        )
        option = self.wait.until(EC.element_to_be_clickable(option_locator))
        self.driver.execute_script("arguments[0].click();", option)

    def set_content(self, text):
        html_text = text.replace("\n", "<br>")
        try:
            self.wait.until(lambda d: d.execute_script(
                "return typeof CKEDITOR !== 'undefined' && "
                "(CKEDITOR.instances.UpdateContent !== undefined || CKEDITOR.instances.Content !== undefined);"
            ))
            self.driver.execute_script(
                "var inst = CKEDITOR.instances.UpdateContent || CKEDITOR.instances.Content; "
                "if(inst) { inst.setData(arguments[0]); inst.updateElement(); }",
                html_text,
            )
        except Exception:
            self.wait.until(EC.frame_to_be_available_and_switch_to_it((By.CLASS_NAME, "cke_wysiwyg_frame")))
            editor = self.wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
            self.driver.execute_script("arguments[0].innerHTML = arguments[1];", editor, html_text)
            self.driver.switch_to.default_content()

    def login(self):
        self.log("Logging into RT1...")
        self.driver.get(config.RT_LOGIN_URL)
        self.wait.until(EC.visibility_of_element_located((By.NAME, "user"))).send_keys(config.RT_USERNAME)
        self.driver.find_element(By.NAME, "pass").send_keys(config.RT_PASSWORD)
        self.driver.find_element(By.XPATH, "//input[@type='submit']").click()
        self.wait.until(EC.visibility_of_element_located((By.ID, "li-home")))
        self.log("Logged into RT1 successfully.")

    def create_and_resolve_ticket(self, title, actual, op_link):
        subject = f"[Bug] {title}"
        body = (
            f"{actual}\n\n"
            f"Full details (steps to reproduce, expected/actual, environment):\n{op_link}"
        )

        self.log(f"Creating RT1 ticket: {subject}")

        self.driver.get(RT_CREATE_TICKET_URL)

        owner = self.wait.until(EC.visibility_of_element_located((By.NAME, "Owner")))
        owner.clear()
        owner.send_keys(config.RT_USERNAME)

        subj = self.wait.until(EC.visibility_of_element_located((By.NAME, "Subject")))
        subj.clear()
        subj.send_keys(subject)

        for field_id, value in config.CUSTOM_FIELDS.items():
            self.select_bootstrap_dropdown(field_id, value)

        self.set_content(body)

        submit_btn = self.wait.until(EC.presence_of_element_located((By.NAME, "SubmitTicket")))
        self.driver.execute_script("arguments[0].click();", submit_btn)

        time.sleep(1.5)
        import re
        id_match = re.search(r"id=(\d+)", self.driver.current_url)
        ticket_num = id_match.group(1) if id_match else "UNKNOWN"

        self.log(f"RT1 ticket #{ticket_num} created. Resolving...")

        try:
            resolve_btn = self.wait.until(EC.element_to_be_clickable(
                (By.XPATH, "//a[contains(@href, 'Status=resolved') or contains(text(), 'Resolve')]")
            ))
            self.driver.execute_script("arguments[0].click();", resolve_btn)
        except Exception:
            if ticket_num != "UNKNOWN":
                self.driver.get(
                    f"{config.RT_LOGIN_URL}Ticket/Update.html?Action=Respond&DefaultStatus=resolved&id={ticket_num}"
                )

        self.set_content("Good day!\nI will now resolve this ticket.\n\nThank you")

        submit_update = self.wait.until(EC.presence_of_element_located((By.NAME, "SubmitTicket")))
        self.driver.execute_script("arguments[0].click();", submit_update)

        self.log(f"RT1 ticket #{ticket_num} resolved.")
        return ticket_num

    def close(self):
        self.driver.quit()
