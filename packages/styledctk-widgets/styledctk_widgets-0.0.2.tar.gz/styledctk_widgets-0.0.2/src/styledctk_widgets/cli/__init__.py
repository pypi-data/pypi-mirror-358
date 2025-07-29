# SPDX-FileCopyrightText: 2025-present DigitalCreationsLibrary <aimosta.official@gmail.com>
#
# SPDX-License-Identifier: MIT
import click

from styledctk_widgets.__about__ import __version__
from styledctk_widgets.CTK_Buttons import CTK_Button_styles
from styledctk_widgets.CTK_Buttons import SCTkButton

from styledctk_widgets.CTK_Entrys import CTK_Entry_styles
from styledctk_widgets.CTK_Entrys import SCTKEntry



@click.group(context_settings={"help_option_names": ["-h", "--help"]}, invoke_without_command=True)
@click.version_option(version=__version__, prog_name="styledctk-widgets")
def styledctk_widgets():
    click.echo("Hello world!")


@styledctk_widgets.command("showb")
def showb():
    CTK_Button_styles.main()
    
    

@styledctk_widgets.command("showsb")
def showsb():
    SCTkButton.main()
        
    
    
@styledctk_widgets.command("showe")
def showe():
    CTK_Entry_styles.main() 