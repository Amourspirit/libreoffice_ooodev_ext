import os
import pytest
from ooodev.utils.lo import Lo
from ooodev.office.write import Write
from unittest.mock import patch

# from ooodev.office.write import Write
if __name__ == "__main__":
    pytest.main([__file__])


def test_hello(loader) -> None:
    from app import hello

    doc = Write.create_doc()

    # patch Lo.load_office so it does not attempt to load office again.
    with patch.object(Lo, "load_office") as load_office:
        load_office.return_value = None

        # patch Write so it does not create a second document
        with patch.object(Write, "create_doc") as create_doc:
            create_doc.return_value = doc
            hello.write_hello(show_msg=False)
            cursor = Write.get_cursor(doc)
            cursor.gotoStart(False)
            cursor.gotoEnd(True)
            assert cursor.getString().startswith("Hello World!")
    Lo.close_doc(doc)
