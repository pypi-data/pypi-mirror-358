import winzy
import subprocess

import os


def run_apple_script():
    applescript = """
    tell application "Finder"
        set selectedFiles to selection as alias list
        set fileNames to {}
        repeat with aFile in selectedFiles
            set end of fileNames to name of aFile
        end repeat
        
        if (count of fileNames) > 0 then
            set fileHandle to open for access (POSIX file "/tmp/selected.txt") with write permission
            repeat with i from 1 to count of fileNames
                write (item i of fileNames & return) to fileHandle as «class utf8»
            end repeat
            close access fileHandle
        end if
    end tell
    """

    applescript_process = subprocess.Popen(
        ["osascript", "-e", applescript], stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    output, error = applescript_process.communicate()

    if error:
        print("An error occurred:", error.decode("utf-8"))
    return "/tmp/selected.txt"


def create_parser(subparser):
    parser = subparser.add_parser(
        "sfiles", description="Get selected files as a text file on mac os"
    )
    return parser


class WinzyPlugin:
    """Get selected files as a text file on mac os"""

    __name__ = "sfiles"

    @winzy.hookimpl
    def register_commands(self, subparser):
        self.parser = create_parser(subparser)
        self.parser.set_defaults(func=self.run)

    def run(self, args):
        # add actual call here
        if os.path.exists("/tmp/selected.txt"):
            os.remove("/tmp/selected.txt")
        tempf = run_apple_script()
        if os.path.exists(tempf):
            with open(tempf, "r") as fin:
                data = fin.read()
            print(data.strip())

    def hello(self, args):
        # this routine will be called when 'winzy sfiles' is called.
        print("Hello! This is an example ``winzy`` plugin.")


sfiles_plugin = WinzyPlugin()
