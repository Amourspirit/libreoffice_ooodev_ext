from __future__ import annotations
import pytest

if __name__ == "__main__":
    pytest.main([__file__])

from ooodev.office.draw import Draw
from ooodev.utils.lo import Lo
from ooodev.utils.gui import GUI


def test_rectangle(loader) -> None:
    x = 10
    y = 20
    width = 100
    height = 100
    doc = Draw.create_draw_doc(loader)
    if not Lo.bridge_connector.headless:
        GUI.set_visible(visible=True, doc=doc)
        Lo.delay(300)
    slide = Draw.get_slide(doc=doc, idx=0)

    num_shapes = slide.getCount()
    assert num_shapes == 0
    shape = Draw.draw_rectangle(slide=slide, x=x, y=y, width=width, height=height)
    pos1 = shape.getPosition()
    assert pos1.X == x * 100
    assert pos1.Y == y * 100
    size1 = shape.getSize()
    assert size1.Height == height * 100
    assert size1.Width == width * 100
    assert shape is not None

    num_shapes2 = slide.getCount()
    assert num_shapes2 == 1
    t_shape = Draw.find_top_shape(slide)
    pos2 = t_shape.getPosition()
    assert pos2.X == pos1.X
    assert pos2.Y == pos1.Y
    size2 = t_shape.getSize()
    assert size2.Width == size1.Width
    assert size2.Height == size1.Height

    Lo.close(doc)  # type: ignore
