import uno
import unohelper
import sys
import os

from com.sun.star.task import XJob

implementation_name = "org.openoffice.extensions.ooodev.OooDevRunner"
implementation_services = ("com.sun.star.task.Job",)


class OooDevRunner(unohelper.Base, XJob):
    def __init__(self, ctx):
        self.ctx = ctx

    def execute(self, *args):
        pth = os.path.join(os.path.dirname(__file__), "pythonpath.zip")
        if not pth in sys.path:
            sys.path.append(pth)
        # sys.path.insert(0, sys.path.pop(sys.path.index(pth)))

        return


g_TypeTable = {}
# pythonloader looks for a static g_ImplementationHelper variable
g_ImplementationHelper = unohelper.ImplementationHelper()

# add the FormatFactory class to the implementation container,
# which the loader uses to register/instantiate the component.
g_ImplementationHelper.addImplementation(OooDevRunner, implementation_name, implementation_services)
